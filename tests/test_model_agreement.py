from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services import model_agreement
from app.services.model_agreement import (
    get_or_discover_classification_models,
    analyze_model_agreement,
)


class MockClassifier:
    def __init__(self, pred_val, has_proba=True, classes=None, n_features=5):
        self._estimator_type = "classifier"
        self.n_features_in_ = n_features
        self.pred_val = pred_val
        self.has_proba = has_proba
        self.classes_ = classes if classes is not None else [1, 2, 3, 4, 5]

    def predict(self, X):
        return [self.pred_val]

    def predict_proba(self, X):
        if not self.has_proba:
            raise AttributeError("predict_proba is not supported")
        # Return probability array matching classes_
        proba = np.zeros(len(self.classes_))
        try:
            idx = self.classes_.index(self.pred_val)
            proba[idx] = 0.90
            other_idx = (idx + 1) % len(self.classes_)
            proba[other_idx] = 0.10
        except ValueError:
            proba[0] = 1.0
        return [proba]


class MockRegressor:
    def __init__(self):
        self._estimator_type = "regressor"
        self.n_features_in_ = 5

    def predict(self, X):
        return [5.0]


def test_get_or_discover_classification_models(monkeypatch: pytest.MonkeyPatch) -> None:
    # Setup state
    monkeypatch.setattr(model_agreement, "_CLASSIFICATION_MODELS", {})
    monkeypatch.setattr(model_agreement, "_MODELS_LOADED", False)

    mock_models_dir = Path("/fake/models")
    
    # Mock resolve models dir
    monkeypatch.setattr(model_agreement, "_resolve_models_dir", lambda: mock_models_dir)
    
    # Mock Path.glob to return fake files
    fake_pkl_files = [
        mock_models_dir / "scaler.pkl",
        mock_models_dir / "selected_features.pkl",
        mock_models_dir / "model_grade_stacking.pkl",
        mock_models_dir / "model_quantity_rf.pkl",
    ]
    monkeypatch.setattr(Path, "glob", lambda self, pattern: fake_pkl_files)
    monkeypatch.setattr(Path, "exists", lambda self: True)

    # Mock joblib.load
    def fake_joblib_load(file_path):
        name = file_path.name
        if name == "model_grade_stacking.pkl":
            return MockClassifier(pred_val=1)
        elif name == "model_quantity_rf.pkl":
            return MockRegressor()
        raise FileNotFoundError(f"Fake file not found: {file_path}")

    monkeypatch.setattr(model_agreement, "joblib", type("joblib", (), {"load": fake_joblib_load}))

    discovered = get_or_discover_classification_models()
    
    # Should only discover model_grade_stacking (classifier with n_features_in_ = 5)
    # Scaler and selected features are excluded, quantity_rf is excluded because it's a regressor
    assert "model_grade_stacking" in discovered
    assert "model_quantity_rf" not in discovered
    assert len(discovered) == 1


def test_analyze_model_agreement_consensus_and_levels(monkeypatch: pytest.MonkeyPatch) -> None:
    # Define three mock classifiers
    clf1 = MockClassifier(pred_val=1)  # predicts 1
    clf2 = MockClassifier(pred_val=1)  # predicts 1
    clf3 = MockClassifier(pred_val=2)  # predicts 2

    mock_discovered = {
        "model_a": clf1,
        "model_b": clf2,
        "model_c": clf3,
    }

    # Inject mock discovered models
    monkeypatch.setattr(model_agreement, "_CLASSIFICATION_MODELS", mock_discovered)
    monkeypatch.setattr(model_agreement, "_MODELS_LOADED", True)

    X_dummy = np.zeros((1, 5))
    res = analyze_model_agreement(X_dummy)

    assert res is not None
    assert res.consensus_prediction == "1"
    # 2 out of 3 models predicted "1", so agreement = 2/3 * 100 = 66.67%
    assert res.agreement_percentage == pytest.approx(66.67, abs=0.01)
    assert res.agreement_level == "Moderate"
    assert res.total_discovered_models == 3
    assert res.successfully_executed_models == 3
    assert res.failed_models == 0


class MockClassifierNoProba:
    def __init__(self, pred_val, classes=None, n_features=5):
        self._estimator_type = "classifier"
        self.n_features_in_ = n_features
        self.pred_val = pred_val
        self.classes_ = classes if classes is not None else [1, 2, 3, 4, 5]

    def predict(self, X):
        return [self.pred_val]


def test_analyze_model_agreement_no_proba(monkeypatch: pytest.MonkeyPatch) -> None:
    # Model without predict_proba method attribute
    clf_no_proba = MockClassifierNoProba(pred_val=3)

    mock_discovered = {
        "model_no_proba": clf_no_proba,
    }

    monkeypatch.setattr(model_agreement, "_CLASSIFICATION_MODELS", mock_discovered)
    monkeypatch.setattr(model_agreement, "_MODELS_LOADED", True)

    X_dummy = np.zeros((1, 5))
    res = analyze_model_agreement(X_dummy)

    assert res is not None
    assert res.consensus_prediction == "3"
    assert res.agreement_percentage == 100.0
    assert res.agreement_level == "Very Strong"
    assert res.model_predictions[0].prediction_probabilities is None
    assert res.model_predictions[0].confidence_score == 1.0


def test_analyze_model_agreement_model_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    # One successful model, one failing model
    clf_ok = MockClassifier(pred_val=2)
    
    class FailingClassifier:
        def __init__(self):
            self._estimator_type = "classifier"
            self.n_features_in_ = 5

        def predict(self, X):
            raise RuntimeError("Hardware/Model simulation failure")

    mock_discovered = {
        "model_ok": clf_ok,
        "model_fail": FailingClassifier(),
    }

    monkeypatch.setattr(model_agreement, "_CLASSIFICATION_MODELS", mock_discovered)
    monkeypatch.setattr(model_agreement, "_MODELS_LOADED", True)

    X_dummy = np.zeros((1, 5))
    res = analyze_model_agreement(X_dummy)

    assert res is not None
    assert res.consensus_prediction == "2"
    assert res.agreement_percentage == 100.0  # 1 out of 1 successful predictions matches consensus
    assert res.successfully_executed_models == 1
    assert res.failed_models == 1
    assert res.model_predictions[0].inference_status == "success"
    assert res.model_predictions[1].inference_status == "failed"
    assert res.model_predictions[1].predicted_class == "N/A"
