from __future__ import annotations

import pickle
import threading
from pathlib import Path
from typing import Any, Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

try:
    import joblib
except ImportError:  # pragma: no cover
    joblib = None


class _FallbackModel:
    def __init__(self, scale: float, offset: float) -> None:
        self.scale = scale
        self.offset = offset

    def predict(self, X_features: Any) -> np.ndarray:
        X_array = np.asarray(X_features, dtype=np.float32)
        if X_array.ndim == 1:
            X_array = X_array.reshape(1, -1)

        mean_signal = np.mean(X_array, axis=1)
        return np.asarray(mean_signal * self.scale + self.offset, dtype=np.float32)


def _load_serialized_object(file_path: Path) -> Any:
    if not file_path.exists():
        raise FileNotFoundError(f"Required model artifact not found: {file_path}")

    if joblib is not None:
        try:
            return joblib.load(file_path)
        except Exception:
            pass

    with file_path.open("rb") as file_handle:
        return pickle.load(file_handle)


class OptimizedPreprocessor:
    __slots__ = ("scaler",)

    def __init__(self, scaler: StandardScaler | None = None) -> None:
        self.scaler = scaler if scaler is not None else StandardScaler()

    @classmethod
    def from_file(cls, scaler_path: Path) -> "OptimizedPreprocessor":
        scaler = _load_serialized_object(scaler_path)
        return cls(scaler=scaler)

    @staticmethod
    def _to_array(X_features: Any) -> np.ndarray:
        if isinstance(X_features, pd.DataFrame):
            array = X_features.to_numpy(dtype=np.float32, copy=False)
        else:
            array = np.asarray(X_features, dtype=np.float32)

        if array.ndim == 1:
            array = array.reshape(1, -1)

        if array.ndim != 2:
            raise ValueError("X_features must be a 2D array-like structure.")

        return array

    def transform(self, X_features: Any) -> np.ndarray:
        return self.scaler.transform(self._to_array(X_features))

    def fit_transform(self, X_features: Any) -> np.ndarray:
        return self.scaler.fit_transform(self._to_array(X_features))


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

        base_dir = Path(models_dir) if models_dir is not None else Path(__file__).resolve().parents[3] / "models"
        self.models_dir = base_dir

        day_model_path = self.models_dir / "model_day_rf.pkl"
        folic_model_path = self.models_dir / "model_folic_rf.pkl"
        scaler_path = self.models_dir / "scaler.pkl"

        if day_model_path.exists() and folic_model_path.exists() and scaler_path.exists():
            self.day_model = _load_serialized_object(day_model_path)
            self.folic_model = _load_serialized_object(folic_model_path)
            self.preprocessor = OptimizedPreprocessor.from_file(scaler_path)
            self.using_fallback_models = False
        else:
            self.day_model = _FallbackModel(scale=0.002, offset=7.0)
            self.folic_model = _FallbackModel(scale=0.45, offset=90.0)
            self.preprocessor = OptimizedPreprocessor()
            self.preprocessor.scaler.fit(np.zeros((1, 11), dtype=np.float32))
            self.using_fallback_models = True

        self.__class__._initialized = True

    def predict_both(self, X_features: Any) -> dict[str, np.ndarray]:
        X_scaled = self.preprocessor.transform(X_features)

        days_pred = self.day_model.predict(X_scaled)
        folic_pred = self.folic_model.predict(X_scaled)

        return {
            "days": days_pred,
            "folic_acid_uM": folic_pred,
        }
