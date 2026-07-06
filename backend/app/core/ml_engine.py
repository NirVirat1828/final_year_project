from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Union

import joblib
import numpy as np
import shap

from app.core.logging_config import logger


def _load_serialized_object(file_path: Path) -> Any:
    if not file_path.exists():
        raise FileNotFoundError(f"Required model artifact not found: {file_path}")
    return joblib.load(file_path)


def _resolve_models_dir(models_dir: Union[str, Path] | None = None) -> Path:
    if models_dir is not None:
        return Path(models_dir)

    project_root = Path(__file__).resolve().parents[3]
    candidate_dirs = (
        project_root / "model" / "models",
        project_root / "backend" / "models",
        project_root / "models",
    )

    for candidate_dir in candidate_dirs:
        if (candidate_dir / "model_day_rf.pkl").exists():
            return candidate_dir

    return candidate_dirs[0]


class OrangeFreshnessPredictor:
    _instance: "OrangeFreshnessPredictor | None" = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, models_dir: Union[str, Path] | None = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, models_dir: Union[str, Path] | None = None) -> None:
        if self.__class__._initialized:
            return

        self.models_dir = _resolve_models_dir(models_dir)

        day_model_path = self.models_dir / "model_day_rf.pkl"
        folic_model_path = self.models_dir / "model_folic_rf.pkl"
        scaler_path = self.models_dir / "scaler.pkl"
        selected_features_path = self.models_dir / "selected_features.pkl"

        self.day_model = _load_serialized_object(day_model_path)
        self.folic_model = _load_serialized_object(folic_model_path)
        self.scaler = _load_serialized_object(scaler_path)
        self.selected_feature_indices = np.asarray(
            _load_serialized_object(selected_features_path),
            dtype=np.int64,
        )

        try:
            self.day_explainer = shap.TreeExplainer(self.day_model)
            self.folic_explainer = shap.TreeExplainer(self.folic_model)
            logger.info("SHAP TreeExplainers initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize TreeExplainers (expected during tests): {e}")
            # Fallback for testing with DummyModel
            self.day_explainer = None
            self.folic_explainer = None

        self.__class__._initialized = True

    @staticmethod
    def _to_2d_array(sensor_readings: Any) -> np.ndarray:
        sensor_array = np.asarray(sensor_readings, dtype=np.float32)

        if sensor_array.ndim == 1:
            sensor_array = sensor_array.reshape(1, -1)

        if sensor_array.ndim != 2:
            raise ValueError("sensor_readings must be convertible to a 2D array.")

        return sensor_array

    def preprocess(self, sensor_readings: Any) -> np.ndarray:
        """
        Preprocesses raw sensor readings into a feature matrix suitable for prediction or explanation.
        
        Steps:
        1. Validates shape and converts to a 2D numpy array.
        2. Applies the trained StandardScaler.
        3. Selects the appropriate feature indices using RFE outputs.
        
        Args:
            sensor_readings (Any): Raw sensor readings. Can be a list or 1D/2D array.
            
        Returns:
            np.ndarray: A 2D array with scaled, selected features (shape: n_samples x 5).
        """
        sensor_array = self._to_2d_array(sensor_readings)
        X_scaled = self.scaler.transform(sensor_array)
        X_selected = X_scaled[:, self.selected_feature_indices]
        return X_selected

    def predict_both(self, sensor_readings: Any) -> tuple[float, float]:
        """
        Predicts both storage days and folic acid concentration from raw sensor readings.
        
        Args:
            sensor_readings (Any): Raw sensor readings.
            
        Returns:
            tuple[float, float]: A tuple containing (predicted_days, predicted_folic_acid_uM).
        """
        X_selected = self.preprocess(sensor_readings)

        days_pred = float(np.asarray(self.day_model.predict(X_selected), dtype=np.float32).reshape(-1)[0])
        folic_pred = float(np.asarray(self.folic_model.predict(X_selected), dtype=np.float32).reshape(-1)[0])

        return days_pred, folic_pred

    def _compute_shap_values(self, X_selected: np.ndarray, target: str) -> np.ndarray:
        """
        Computes SHAP values for the specified model target using the cached TreeExplainer.
        
        Args:
            X_selected (np.ndarray): The preprocessed, selected feature matrix.
            target (str): The model to explain ('day' or 'folic').
            
        Returns:
            np.ndarray: SHAP values corresponding to the selected features.
        """
        if target == "day":
            return self.day_explainer.shap_values(X_selected)
        elif target == "folic":
            return self.folic_explainer.shap_values(X_selected)
        else:
            raise ValueError("target must be 'day' or 'folic'")

    def explain(self, sensor_readings: Any) -> dict[str, Any]:
        """
        Predicts freshness metrics and computes their SHAP explanations.
        
        Args:
            sensor_readings (Any): Raw sensor readings.
            
        Returns:
            dict[str, Any]: A dictionary containing predictions, raw SHAP values, base values, and indices.
        """
        X_selected = self.preprocess(sensor_readings)
        
        days_pred, folic_pred = self.predict_both(sensor_readings)
        
        day_shap = self._compute_shap_values(X_selected, "day")
        folic_shap = self._compute_shap_values(X_selected, "folic")
        
        def _get_base_value(explainer: Any) -> float:
            if explainer is None:
                return 0.0
            val = explainer.expected_value
            if isinstance(val, (list, np.ndarray)):
                return float(val[0])
            return float(val)
            
        return {
            "day_prediction": days_pred,
            "folic_prediction": folic_pred,
            "day_shap_values": day_shap,
            "folic_shap_values": folic_shap,
            "day_base_value": _get_base_value(self.day_explainer),
            "folic_base_value": _get_base_value(self.folic_explainer),
            "selected_feature_indices": self.selected_feature_indices
        }
