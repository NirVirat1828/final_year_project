"""
track_a_inference.py

Track A: Inference module for freshness grade prediction.

Loads the trained StackingClassifier and produces predictions with probabilities:
  {
    "grade": "A",
    "probabilities": {"A": 0.85, "B": 0.10, "C": 0.05, "D": 0.00},
    "selected_features": ["DCT_3", "DCT_2", "Energy", "Mean", "Peak_Height"]
  }
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
import joblib

from src.preprocessing.track_a_preprocessing import TrackAPreprocessor


class TrackAInference:
    """
    Inference pipeline for Track A freshness grade classification.
    """

    def __init__(self, models_dir='models/track_a'):
        """
        Initialize by loading all artifacts.

        Parameters
        ----------
        models_dir : str
            Directory containing saved models and configuration.
        """
        self.models_dir = Path(models_dir)

        # Load imputer
        self.imputer = joblib.load(self.models_dir / 'imputer.pkl')

        # Load scaler
        self.scaler = joblib.load(self.models_dir / 'scaler.pkl')

        # Load RFE selector
        self.rfe_selector = joblib.load(self.models_dir / 'rfe_selector.pkl')

        # Load stacking model
        self.stacking_clf = joblib.load(self.models_dir / 'stacking_model.pkl')

        # Load feature metadata
        with open(self.models_dir / 'feature_names.json', 'r') as f:
            self.metadata = json.load(f)

        self.feature_names = self.metadata['feature_names']
        self.selected_features = self.metadata['selected_features']
        self.label_mapping = self.metadata['label_mapping']
        self.reverse_label_mapping = {int(k): v for k, v in self.label_mapping.items()}

        # Preprocessor for raw signals
        self.preprocessor = TrackAPreprocessor(
            savgol_window=11,
            savgol_polyorder=3,
            dct_keep=10
        )

        print(f"✓ Track A Inference loaded from {models_dir}")
        print(f"  Selected features: {self.selected_features}")

    def predict_from_raw_signal(self, raw_signal):
        """
        End-to-end prediction from raw optical sensor readings.

        Parameters
        ----------
        raw_signal : array-like, shape (n_readings,)
            Raw sensor readings (e.g., 15 voltage measurements).

        Returns
        -------
        prediction : dict
            {
              "grade": str (A/B/C/D),
              "probabilities": dict {A: float, B: float, C: float, D: float},
              "selected_features": list of feature names
            }
        """
        # Step 1: Extract engineered features
        features_dict = self.preprocessor.extract_all_features(np.array(raw_signal))
        features_array = np.array([features_dict[name] for name in self.feature_names]).reshape(1, -1)

        # Step 2: Impute missing values
        features_imputed = self.imputer.transform(features_array)

        # Step 3: Scale
        features_scaled = self.scaler.transform(features_imputed)

        # Step 4: Select top 5 features
        features_selected = self.rfe_selector.transform(features_scaled)

        # Step 4: Predict
        pred_class_idx = self.stacking_clf.predict(features_selected)[0]
        pred_proba = self.stacking_clf.predict_proba(features_selected)[0]

        # Step 5: Format output
        grade = self.reverse_label_mapping[int(pred_class_idx)]
        probabilities = {
            self.reverse_label_mapping[i]: float(prob)
            for i, prob in enumerate(pred_proba)
        }

        return {
            'grade': grade,
            'probabilities': probabilities,
            'selected_features': self.selected_features
        }

    def predict_from_features(self, engineered_features):
        """
        Prediction from already-engineered features (12-dim vector).

        Parameters
        ----------
        engineered_features : array-like, shape (n_features,)
            Pre-extracted features (e.g., DCT, Energy, etc.).

        Returns
        -------
        prediction : dict
        """
        features_array = np.array(engineered_features).reshape(1, -1)

        # Impute
        features_imputed = self.imputer.transform(features_array)

        # Scale
        features_scaled = self.scaler.transform(features_imputed)

        # Select
        features_selected = self.rfe_selector.transform(features_scaled)

        # Predict
        pred_class_idx = self.stacking_clf.predict(features_selected)[0]
        pred_proba = self.stacking_clf.predict_proba(features_selected)[0]

        grade = self.reverse_label_mapping[int(pred_class_idx)]
        probabilities = {
            self.reverse_label_mapping[i]: float(prob)
            for i, prob in enumerate(pred_proba)
        }

        return {
            'grade': grade,
            'probabilities': probabilities,
            'selected_features': self.selected_features
        }

    def batch_predict_from_raw_signals(self, raw_signals):
        """
        Predict freshness grades for multiple raw signals.

        Parameters
        ----------
        raw_signals : array-like, shape (n_samples, n_readings)
            Batch of raw sensor readings.

        Returns
        -------
        predictions : list of dict
            List of prediction dictionaries.
        """
        predictions = []
        for i, signal in enumerate(raw_signals):
            pred = self.predict_from_raw_signal(signal)
            predictions.append(pred)
        return predictions


def main():
    """
    Example: Load inference pipeline and predict on sample data.
    """
    print("=" * 70)
    print("TRACK A INFERENCE - EXAMPLE")
    print("=" * 70)

    # Initialize inference
    try:
        inference = TrackAInference(models_dir='models/track_a')
    except FileNotFoundError as e:
        print(f"⚠ Models not found: {e}")
        print("  Please run track_a_train_classifier.py first.")
        return

    # Example 1: Single raw signal
    print("\n[Example 1] Predicting from a raw sensor signal...")
    np.random.seed(42)
    raw_signal = np.sin(np.linspace(0, 4*np.pi, 15)) + 0.2*np.random.randn(15)

    prediction = inference.predict_from_raw_signal(raw_signal)
    print(f"  Grade: {prediction['grade']}")
    print(f"  Probabilities: {prediction['probabilities']}")
    print(f"  Selected Features: {prediction['selected_features']}")

    # Example 2: Batch prediction
    print("\n[Example 2] Batch prediction (5 samples)...")
    raw_signals = [np.sin(np.linspace(0, 4*np.pi, 15)) + 0.2*np.random.randn(15) for _ in range(5)]
    batch_predictions = inference.batch_predict_from_raw_signals(raw_signals)

    for i, pred in enumerate(batch_predictions):
        print(f"  Sample {i+1}: Grade {pred['grade']} (confidence: {max(pred['probabilities'].values()):.2%})")

    print("\n✅ Inference examples complete!")


if __name__ == '__main__':
    main()
