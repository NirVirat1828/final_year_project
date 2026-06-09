from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Union

import joblib
import numpy as np


def _load_serialized_object(file_path: Path) -> Any:
    if not file_path.exists():
        raise FileNotFoundError(f"Required model artifact not found: {file_path}")
    return joblib.load(file_path)


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

        base_dir = Path(models_dir) if models_dir is not None else Path(__file__).resolve().parents[2] / "models"
        self.models_dir = base_dir

        day_model_path = self.models_dir / "model_day_rf.pkl"
        folic_model_path = self.models_dir / "model_folic_rf.pkl"
        scaler_path = self.models_dir / "scaler.pkl"

        self.day_model = _load_serialized_object(day_model_path)
        self.folic_model = _load_serialized_object(folic_model_path)
        self.scaler = _load_serialized_object(scaler_path)

        self.__class__._initialized = True

    @staticmethod
    def _to_2d_array(sensor_readings: Any) -> np.ndarray:
        sensor_array = np.asarray(sensor_readings, dtype=np.float32)

        if sensor_array.ndim == 1:
            sensor_array = sensor_array.reshape(1, -1)

        if sensor_array.ndim != 2:
            raise ValueError("sensor_readings must be convertible to a 2D array.")

        return sensor_array

    def predict_both(self, sensor_readings: Any) -> tuple[float, float]:
        sensor_array = self._to_2d_array(sensor_readings)
        X_scaled = self.scaler.transform(sensor_array)

        days_pred = float(np.asarray(self.day_model.predict(X_scaled), dtype=np.float32).reshape(-1)[0])
        folic_pred = float(np.asarray(self.folic_model.predict(X_scaled), dtype=np.float32).reshape(-1)[0])

        return days_pred, folic_pred
