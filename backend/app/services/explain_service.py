from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from app.core.ml_engine import OrangeFreshnessPredictor
from app.schemas.payload import InferenceRequest
from app.services.grading_service import _grade_from_days

ORIGINAL_FEATURE_NAMES: List[str] = [
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


def _map_selected_feature_names(selected_indices: List[int]) -> List[str]:
    """
    Maps the selected integer indices to their corresponding original feature names.
    """
    return [ORIGINAL_FEATURE_NAMES[i] for i in selected_indices]


def _extract_top_features(feature_names: List[str], shap_values: List[float]) -> List[Dict[str, Any]]:
    """
    Pairs features with their SHAP values, sorts them by absolute magnitude descending,
    and returns the top 3 contributing features.
    """
    paired_features = []
    for name, value in zip(feature_names, shap_values):
        paired_features.append({
            "feature_name": name,
            "shap_value": float(value),
            "impact": "increase" if value > 0 else "decrease" if value < 0 else "neutral",
            "absolute_importance": abs(float(value))
        })
        
    # Sort by absolute_importance descending
    sorted_features = sorted(paired_features, key=lambda x: x["absolute_importance"], reverse=True)
    
    # Return top 3 with rank assigned
    top_3 = sorted_features[:3]
    for i, feature in enumerate(top_3):
        feature["rank"] = i + 1
        
    return top_3


def process_explanation(request: InferenceRequest, ml_engine: OrangeFreshnessPredictor) -> Dict[str, Any]:
    """
    Retrieves the raw SHAP explanation from the ML engine and formats it into a 
    business-friendly dictionary.
    """
    # ml_engine.explain returns a dict with predictions, shap arrays, and indices.
    explanation_raw = ml_engine.explain(request.sensor_readings)
    
    selected_indices = explanation_raw["selected_feature_indices"]
    if isinstance(selected_indices, np.ndarray):
        selected_indices = selected_indices.tolist()
        
    feature_names = _map_selected_feature_names(selected_indices)
    
    day_shap = explanation_raw["day_shap_values"]
    if isinstance(day_shap, np.ndarray):
        day_shap = day_shap.flatten().tolist()
    else:
        # If it's a list of lists (e.g. from tests or TreeExplainer structure), flatten it
        day_shap = np.array(day_shap).flatten().tolist()
        
    folic_shap = explanation_raw["folic_shap_values"]
    if isinstance(folic_shap, np.ndarray):
        folic_shap = folic_shap.flatten().tolist()
    else:
        folic_shap = np.array(folic_shap).flatten().tolist()
        
    top_day_features = _extract_top_features(feature_names, day_shap)
    top_folic_features = _extract_top_features(feature_names, folic_shap)
    
    days_pred = explanation_raw["day_prediction"]
    folic_pred = explanation_raw["folic_prediction"]
    
    return {
        "prediction": {
            "estimated_age_days": days_pred,
            "folic_acid_uM": folic_pred,
            "freshness_grade": _grade_from_days(days_pred)
        },
        "explanation": {
            "day_model": {
                "base_value": explanation_raw.get("day_base_value", 0.0),
                "top_features": top_day_features
            },
            "folic_model": {
                "base_value": explanation_raw.get("folic_base_value", 0.0),
                "top_features": top_folic_features
            }
        }
    }
