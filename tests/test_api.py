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
