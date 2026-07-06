from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core import ml_engine
from app.core.ml_engine import OrangeFreshnessPredictor
from app.services.grading_service import (  # noqa: E402
    _grade_from_days,
    _nutritional_status_from_folic,
    _temperature_adjusted_remaining_shelf_life,
)


def test_grade_mapping() -> None:
    assert _grade_from_days(2) == "A"
    assert _grade_from_days(5) == "B"
    assert _grade_from_days(9) == "C"
    assert _grade_from_days(12) == "D"


def test_nutritional_status_mapping() -> None:
    assert _nutritional_status_from_folic(160) == "High Value"
    assert _nutritional_status_from_folic(100) == "Acceptable"
    assert _nutritional_status_from_folic(60) == "Declining"
    assert _nutritional_status_from_folic(20) == "Depleted"


def test_temperature_adjusted_shelf_life() -> None:
    adjusted_shelf_life = _temperature_adjusted_remaining_shelf_life(
        predicted_days=4.0,
        storage_temperature_c=14.0,
    )

    assert adjusted_shelf_life == pytest.approx(5.0, rel=1e-6)


def test_predictor_uses_selected_rfe_features(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyScaler:
        def transform(self, X):
            return X

    class DummyModel:
        def __init__(self):
            self.last_input = None

        def predict(self, X):
            self.last_input = X
            return [1.0]

    day_model = DummyModel()
    folic_model = DummyModel()
    fake_selected_indices = [1, 3, 6, 7, 8]

    def fake_load_serialized_object(file_path):
        if file_path.name == "model_day_rf.pkl":
            return day_model
        if file_path.name == "model_folic_rf.pkl":
            return folic_model
        if file_path.name == "scaler.pkl":
            return DummyScaler()
        if file_path.name == "selected_features.pkl":
            return fake_selected_indices
        raise AssertionError(f"Unexpected artifact requested: {file_path}")

    monkeypatch.setattr(ml_engine, "_load_serialized_object", fake_load_serialized_object)
    monkeypatch.setattr(OrangeFreshnessPredictor, "_instance", None)
    monkeypatch.setattr(OrangeFreshnessPredictor, "_initialized", False)

    predictor = OrangeFreshnessPredictor(models_dir=Path("/tmp/models"))

    sensor_readings = [[
        10.0,
        11.0,
        12.0,
        13.0,
        14.0,
        15.0,
        16.0,
        17.0,
        18.0,
        19.0,
        20.0,
    ]]

    predictor.predict_both(sensor_readings)

    assert predictor.selected_feature_indices.tolist() == fake_selected_indices
    assert day_model.last_input.shape == (1, 5)
    assert folic_model.last_input.shape == (1, 5)
    assert day_model.last_input[0].tolist() == [11.0, 13.0, 16.0, 17.0, 18.0]
    assert folic_model.last_input[0].tolist() == [11.0, 13.0, 16.0, 17.0, 18.0]
