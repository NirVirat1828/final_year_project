import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.ml_engine import OrangeFreshnessPredictor
from app.schemas.payload import InferenceRequest
from app.services.explain_service import (
    ORIGINAL_FEATURE_NAMES,
    _extract_top_features,
    _map_selected_feature_names,
    process_explanation,
)


def test_map_selected_feature_names():
    indices = [1, 3, 6, 7, 8]
    expected = ["Mean", "Energy", "DCT_1", "DCT_2", "DCT_3"]
    assert _map_selected_feature_names(indices) == expected


def test_extract_top_features_sorting_and_top_three():
    names = ["A", "B", "C", "D", "E"]
    values = [0.1, -0.9, 0.5, 0.05, -0.8]
    top_features = _extract_top_features(names, values)
    
    assert len(top_features) == 3
    # Absolute magnitudes: B (0.9), E (0.8), C (0.5), A (0.1), D (0.05)
    assert top_features[0]["feature_name"] == "B"
    assert top_features[0]["absolute_importance"] == 0.9
    assert top_features[0]["impact"] == "decrease"
    assert top_features[0]["rank"] == 1
    
    assert top_features[1]["feature_name"] == "E"
    assert top_features[1]["absolute_importance"] == 0.8
    assert top_features[1]["impact"] == "decrease"
    assert top_features[1]["rank"] == 2
    
    assert top_features[2]["feature_name"] == "C"
    assert top_features[2]["absolute_importance"] == 0.5
    assert top_features[2]["impact"] == "increase"
    assert top_features[2]["rank"] == 3


def test_extract_top_features_duplicate_magnitudes():
    names = ["A", "B", "C", "D"]
    values = [0.5, -0.5, 0.2, 0.1]
    top_features = _extract_top_features(names, values)
    
    # Absolute magnitudes: A and B are 0.5
    assert top_features[0]["absolute_importance"] == 0.5
    assert top_features[1]["absolute_importance"] == 0.5
    assert top_features[2]["absolute_importance"] == 0.2
    
    # Ensure properties are preserved
    a_feat = next(f for f in top_features if f["feature_name"] == "A")
    assert a_feat["impact"] == "increase"
    
    b_feat = next(f for f in top_features if f["feature_name"] == "B")
    assert b_feat["impact"] == "decrease"


def test_process_explanation(monkeypatch):
    # Mock request
    request = InferenceRequest(
        batch_id="test-123",
        sensor_readings=[1.0] * 11,
        preprocessing_strategy="raw",
        storage_temperature_c=4.0
    )
    
    from unittest.mock import MagicMock
    
    dummy_predictor = MagicMock(spec=OrangeFreshnessPredictor)
    dummy_predictor.explain.return_value = {
        "day_prediction": 4.5,
        "folic_prediction": 120.0,
        "day_shap_values": [[0.1, -0.9, 0.5, 0.05, -0.8]], # 2D array representation
        "folic_shap_values": [[-1.0, 2.0, -3.0, 4.0, -5.0]],
        "day_base_value": 3.0,
        "folic_base_value": 60.0,
        "selected_feature_indices": [1, 3, 6, 7, 8]
    }
    
    # Process
    result = process_explanation(request, dummy_predictor)
    
    # Validate top-level keys
    assert "prediction" in result
    assert "explanation" in result
    assert "day_model" in result["explanation"]
    assert "folic_model" in result["explanation"]
    
    # Validate predictions
    assert result["prediction"]["estimated_age_days"] == 4.5
    assert result["prediction"]["folic_acid_uM"] == 120.0
    assert "freshness_grade" in result["prediction"]
    
    # Validate day_model explanation
    assert result["explanation"]["day_model"]["base_value"] == 3.0
    day_top = result["explanation"]["day_model"]["top_features"]
    assert len(day_top) == 3
    # absolute magnitudes: 0.9 (Energy), 0.8 (DCT_3), 0.5 (DCT_1)
    assert day_top[0]["feature_name"] == "Energy"
    assert day_top[0]["impact"] == "decrease"
    assert day_top[1]["feature_name"] == "DCT_3"
    assert day_top[1]["impact"] == "decrease"
    assert day_top[2]["feature_name"] == "DCT_1"
    assert day_top[2]["impact"] == "increase"
    
    # Validate folic_model explanation
    assert result["explanation"]["folic_model"]["base_value"] == 60.0
    folic_top = result["explanation"]["folic_model"]["top_features"]
    assert len(folic_top) == 3
    # absolute magnitudes: 5.0 (DCT_3), 4.0 (DCT_2), 3.0 (DCT_1)
    assert folic_top[0]["feature_name"] == "DCT_3"
    assert folic_top[0]["impact"] == "decrease"
    assert folic_top[1]["feature_name"] == "DCT_2"
    assert folic_top[1]["impact"] == "increase"
    assert folic_top[2]["feature_name"] == "DCT_1"
    assert folic_top[2]["impact"] == "decrease"
