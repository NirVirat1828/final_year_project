from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app
from app.core.ml_engine import OrangeFreshnessPredictor


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(OrangeFreshnessPredictor, "__init__", lambda self, *args, **kwargs: None)
    monkeypatch.setattr(
        OrangeFreshnessPredictor,
        "predict_both",
        lambda self, X_features: (5.0, 120.0),
    )

    with TestClient(app) as test_client:
        yield test_client



def test_health_check(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_analyze_batch_success(client: TestClient) -> None:
    payload = {
        "batch_id": "batch-001",
        "sensor_readings": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
        "preprocessing_strategy": "raw",
        "storage_temperature_c": 4.0,
    }

    response = client.post("/api/v1/analyze-batch", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "results" in body
    assert "freshness_grade" in body["results"]
    assert "logistics" in body


def test_analyze_batch_advanced_strategy_applies_penalty(client: TestClient) -> None:
    payload = {
        "batch_id": "batch-003",
        "sensor_readings": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
        "preprocessing_strategy": "advanced",
        "storage_temperature_c": 4.0,
    }

    response = client.post("/api/v1/analyze-batch", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["logistics"]["confidence_score_percent"] == 80.0
    assert body["logistics"]["remaining_shelf_life_days"] == 11.5


def test_analyze_batch_invalid_sensor_data(client: TestClient) -> None:
    payload = {
        "batch_id": "batch-002",
        "sensor_readings": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
        "preprocessing_strategy": "raw",
        "storage_temperature_c": 4.0,
    }

    response = client.post("/api/v1/analyze-batch", json=payload)

    assert response.status_code == 422


def test_explain_prediction_success(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.api import endpoints
    def mock_process_explanation(request, ml_engine):
        return {
            "prediction": {"estimated_age_days": 5.0, "folic_acid_uM": 120.0, "freshness_grade": "B"},
            "explanation": {
                "day_model": {
                    "base_value": 0.0, 
                    "top_features": [{"feature_name": "A", "shap_value": 0.5, "impact": "increase", "absolute_importance": 0.5, "rank": 1}]
                },
                "folic_model": {
                    "base_value": 0.0, 
                    "top_features": []
                }
            }
        }
    monkeypatch.setattr(endpoints, "process_explanation", mock_process_explanation)
    
    payload = {
        "batch_id": "batch-explain",
        "sensor_readings": [1.0] * 11,
        "preprocessing_strategy": "raw",
        "storage_temperature_c": 4.0,
    }
    response = client.post("/api/v1/explain", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert "explanation" in body
    assert body["explanation"]["day_model"]["top_features"][0]["rank"] == 1
    # Check that PredictionSummary was populated including freshness_grade
    assert "freshness_grade" in body["prediction"]


def test_explain_prediction_invalid_request(client: TestClient) -> None:
    payload = {
        "batch_id": "batch-explain",
        "sensor_readings": [1.0] * 5, # invalid length
    }
    response = client.post("/api/v1/explain", json=payload)
    assert response.status_code == 422


def test_explain_prediction_wrong_datatype(client: TestClient) -> None:
    payload = {
        "batch_id": "batch-explain",
        "sensor_readings": ["not-a-float"] * 11, # invalid datatype
    }
    response = client.post("/api/v1/explain", json=payload)
    assert response.status_code == 422


def test_explain_prediction_model_error(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.api import endpoints
    def mock_process_explanation_error(request, ml_engine):
        raise ValueError("Model unavailable")
    monkeypatch.setattr(endpoints, "process_explanation", mock_process_explanation_error)
    
    payload = {
        "batch_id": "batch-explain",
        "sensor_readings": [1.0] * 11,
        "preprocessing_strategy": "raw",
        "storage_temperature_c": 4.0,
    }
    response = client.post("/api/v1/explain", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "Explanation generation failed"


def test_analyze_csv_success(client: TestClient) -> None:
    csv_content = (
        "voltage,current_1,current_2,current_3,current_4,current_5,current_6,current_7,current_8,current_9,current_10,current_11,current_12,current_13,current_14,current_15\n"
        "0.6,14.9,14.6,15.0,14.3,15.0,14.5,14.9,14.7,14.7,14.6,15.2,14.3,14.9,15.0,14.8\n"
        "0.6,15.2,14.8,15.5,14.7,14.9,15.4,15.1,15.4,14.6,14.6,15.2,14.9,15.4,15.2,15.0\n"
    )
    
    file_payload = {
        "file": ("test.csv", csv_content, "text/csv")
    }
    data_payload = {
        "preprocessing_strategy": "raw",
        "storage_temperature_c": 4.0
    }
    
    response = client.post(
        "/api/v1/analyze-csv",
        files=file_payload,
        data=data_payload
    )
    
    assert response.status_code == 200
    body = response.json()
    assert body["total_samples"] == 2
    assert len(body["predictions"]) == 2
    assert body["predictions"][0]["results"]["freshness_grade"] in ["A", "B", "C", "D"]
    assert "remaining_shelf_life_days" in body["predictions"][0]["logistics"]


def test_analyze_csv_validation_error(client: TestClient) -> None:
    csv_content = ""
    file_payload = {
        "file": ("test.csv", csv_content, "text/csv")
    }
    data_payload = {
        "preprocessing_strategy": "raw",
        "storage_temperature_c": 4.0
    }
    
    response = client.post(
        "/api/v1/analyze-csv",
        files=file_payload,
        data=data_payload
    )
    
    assert response.status_code == 400
    assert "detail" in response.json()

