from __future__ import annotations

import io
import pandas as pd
import numpy as np
from typing import Any, Dict, List
from scipy.signal import savgol_filter
from scipy.fftpack import dct
from scipy.stats import skew, kurtosis
from app.core.ml_engine import OrangeFreshnessPredictor
from app.services.grading_service import (
    _grade_from_days,
    _nutritional_status_from_folic,
    _temperature_adjusted_remaining_shelf_life,
    _confidence_interval,
    GRADE_DESCRIPTIONS,
    REFERENCE_TEMP_C,
)
from app.services.decision_engine import DecisionEngine

EXPECTED_FEATURE_COLS = [
    "Peak_0.85V",
    "Mean",
    "Std_Dev",
    "Energy",
    "Skewness",
    "Kurtosis",
    "DCT_1",
    "DCT_2",
    "DCT_3",
    "DCT_4",
    "DCT_5",
]


class CSVPreprocessor:
    """
    Extracts engineered features from raw sensor currents (columns: current_1...current_15)
    matching the training pipeline in src/preprocessing/task1_blind_test_preprocessing.py
    """
    def __init__(self, savgol_window: int = 11, savgol_polyorder: int = 3, dct_keep: int = 5):
        self.savgol_window = savgol_window
        self.savgol_polyorder = savgol_polyorder
        self.dct_keep = dct_keep

    def apply_savgol_filter(self, signal: np.ndarray) -> np.ndarray:
        if len(signal) < self.savgol_window:
            return signal
        return savgol_filter(signal, window_length=self.savgol_window, polyorder=self.savgol_polyorder)

    def extract_dct_features(self, signal: np.ndarray, n_coefficients: int = 5) -> Dict[str, float]:
        dct_vals = dct(signal, type=2, norm='ortho')
        dct_features = {}
        for i in range(min(n_coefficients, len(dct_vals))):
            dct_features[f'DCT_{i}'] = float(dct_vals[i])
        return dct_features

    def extract_features(self, signal: np.ndarray) -> Dict[str, float]:
        # Step 1: Smooth the signal
        smoothed = self.apply_savgol_filter(signal)
        
        # Step 2: Extract statistical features
        features = {
            'Peak_0.85V': float(np.max(smoothed)),
            'Mean': float(np.mean(smoothed)),
            'Std_Dev': float(np.std(smoothed)),
            'Energy': float(np.sum(smoothed ** 2)),
            'Skewness': float(skew(smoothed)),
            'Kurtosis': float(kurtosis(smoothed)),
        }
        
        # Step 3: DCT features (1-5, skipping DCT_0)
        dct_feats = self.extract_dct_features(smoothed, n_coefficients=6)
        for i in range(1, 6):
            features[f'DCT_{i}'] = dct_feats.get(f'DCT_{i}', 0.0)
            
        return features


def process_csv_batch(
    file_bytes: bytes,
    preprocessing_strategy: str,
    storage_temperature_c: float,
    ml_engine: OrangeFreshnessPredictor,
) -> Dict[str, Any]:
    """
    Parses a CSV file, detects the format, preprocesses if raw signals,
    and runs predictions on all samples.
    """
    # Load into pandas DataFrame
    df = pd.read_csv(io.BytesIO(file_bytes))
    
    if df.empty:
        raise ValueError("The uploaded CSV file is empty.")

    current_cols = [col for col in df.columns if col.startswith("current_")]
    
    # Check if this is a raw sensor sweep CSV (has current_1...current_15)
    if len(current_cols) >= 5:
        # Preprocess each column to extract 11 features per sensor
        preprocessor = CSVPreprocessor()
        extracted_features = []
        for col in current_cols:
            # Get currents as numeric values
            signal = df[col].values.astype(float)
            feats = preprocessor.extract_features(signal)
            extracted_features.append(feats)
        df_features = pd.DataFrame(extracted_features)
    else:
        # Check if engineered features already exist
        missing_cols = [col for col in EXPECTED_FEATURE_COLS if col not in df.columns]
        if missing_cols:
            raise ValueError(
                f"CSV must contain either raw currents (e.g. current_1...current_15) "
                f"or all engineered feature columns. Missing columns: {missing_cols}"
            )
        df_features = df[EXPECTED_FEATURE_COLS].copy()

    # Reorder columns to ensure exact expected match
    df_features = df_features[EXPECTED_FEATURE_COLS]
    
    # Perform predictions
    predictions_list = []
    confidence_score_percent = 100.0
    if preprocessing_strategy.strip().lower() == "advanced":
        confidence_score_percent = max(0.0, confidence_score_percent - 20.0)
        
    decision_engine = DecisionEngine()

    for idx, row in df_features.iterrows():
        sensor_readings = row.tolist()
        
        # Predict age (days) and folic acid (uM)
        predicted_days, folic_acid_uM = ml_engine.predict_both(sensor_readings)
        
        freshness_grade = _grade_from_days(predicted_days)
        grade_description = GRADE_DESCRIPTIONS[freshness_grade]
        nutritional_status = _nutritional_status_from_folic(folic_acid_uM)
        remaining_shelf_life_days = _temperature_adjusted_remaining_shelf_life(
            predicted_days=predicted_days,
            storage_temperature_c=storage_temperature_c,
        )
        
        if preprocessing_strategy.strip().lower() == "advanced":
            remaining_shelf_life_days += 2.5
            
        ci = _confidence_interval(
            remaining_shelf_life_days=remaining_shelf_life_days,
            storage_temperature_c=storage_temperature_c,
        )
        
        temperature_warning = (
            "Temperature above refrigerated baseline may accelerate spoilage."
            if storage_temperature_c > REFERENCE_TEMP_C
            else "Temperature within refrigerated baseline range."
        )

        business_decision = decision_engine.generate_decision(
            predicted_class=freshness_grade,
            prediction_probabilities={freshness_grade: float(confidence_score_percent) / 100.0},
            shap_feature_importance=[],
            sensor_values=[float(val) for val in sensor_readings]
        )

        agreement_analysis = None
        try:
            from app.services.model_agreement import analyze_model_agreement
            if hasattr(ml_engine, "preprocess") and hasattr(ml_engine, "scaler") and ml_engine.scaler is not None:
                sensor_features = np.asarray(sensor_readings, dtype=np.float32).reshape(1, -1)
                X_selected = ml_engine.preprocess(sensor_features)
                res_obj = analyze_model_agreement(X_selected)
                if res_obj:
                    agreement_analysis = res_obj.model_dump()
        except Exception as e:
            from app.core.logging_config import logger
            logger.error(f"Failed running prediction agreement analysis in CSV batch: {e}")

        predictions_list.append({
            "sample_index": int(idx),
            "sensor_readings": [float(val) for val in sensor_readings],
            "results": {
                "freshness_grade": freshness_grade,
                "grade_description": grade_description,
                "folic_acid_uM": float(folic_acid_uM),
                "nutritional_status": nutritional_status,
            },
            "logistics": {
                "estimated_age_days": float(predicted_days),
                "remaining_shelf_life_days": float(remaining_shelf_life_days),
                "confidence_score_percent": float(confidence_score_percent),
                "confidence_interval": {
                    "lower_bound": float(ci.lower_bound),
                    "upper_bound": float(ci.upper_bound),
                },
                "temperature_warning": temperature_warning,
            },
            "business_decision": business_decision.model_dump(),
            "agreement_analysis": agreement_analysis
        })

    return {
        "total_samples": len(predictions_list),
        "predictions": predictions_list,
    }
