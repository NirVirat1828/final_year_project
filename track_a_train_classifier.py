"""
track_a_train_classifier.py

Track A: Training pipeline for freshness grade StackingClassifier.

Pipeline:
  1. Load dataset (real + synthetic)
  2. Extract 12 engineered features per sample (Savitzky-Golay + DCT)
  3. Apply RFE to select top 5 features
  4. Train StackingClassifier:
     - Base models: RandomForestClassifier, SVM (SVC with probability=True)
     - Meta-model: RandomForestClassifier
  5. Evaluate on test set (confusion matrix, accuracy, classification report)
  6. Save all artifacts (scaler, RFE, stacking model, feature names)
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    confusion_matrix, accuracy_score, classification_report,
    ConfusionMatrixDisplay
)
import joblib

from track_a_preprocessing import TrackAPreprocessor
from track_a_feature_selection import TrackAFeatureSelector


def load_or_generate_dataset(data_path='datasets/X_features.csv', targets_path='datasets/y_targets.csv'):
    """
    Load preprocessed dataset and create freshness grade labels.

    If real data unavailable, generates synthetic dataset.

    Parameters
    ----------
    data_path : str
        Path to feature CSV.
    targets_path : str
        Path to targets CSV.

    Returns
    -------
    X : array, shape (n_samples, n_features)
        Features (already engineered from preprocessing step).
    y : array, shape (n_samples,)
        Grade labels encoded: A=0, B=1, C=2, D=3.
    y_labels : dict
        Mapping from encoded int to grade string.
    """
    if os.path.exists(data_path) and os.path.exists(targets_path):
        # Load real data
        print(f"✓ Loading data from {data_path}")
        X = pd.read_csv(data_path).values
        y_df = pd.read_csv(targets_path)

        # Create grade labels based on 'day' column
        # Heuristic: Days <= 3 → A, Days 4-7 → B, Days 8-10 → C, Days > 10 → D
        days = y_df['day'].values
        grades = np.where(days <= 3, 0,  # A
                          np.where(days <= 7, 1,  # B
                                   np.where(days <= 10, 2,  # C
                                            3)))  # D

        y = grades
        y_labels = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
        print(f"  Loaded {X.shape[0]} samples with {X.shape[1]} features")
        print(f"  Grade distribution: {np.bincount(y)}")
        return X, y, y_labels

    else:
        # Generate synthetic dataset
        print("⚠ Real data not found. Generating synthetic dataset...")
        np.random.seed(42)
        n_samples = 200
        n_features = 12

        X = np.random.randn(n_samples, n_features)
        # Simulate grades (unbalanced)
        y = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.3, 0.35, 0.2, 0.15])
        y_labels = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}

        print(f"  Generated {n_samples} synthetic samples with {n_features} features")
        print(f"  Grade distribution: {np.bincount(y)}")
        return X, y, y_labels


def create_stacking_classifier(random_state=42):
    """
    Build StackingClassifier with RandomForest + SVM as base models,
    RandomForest as meta-model.

    Parameters
    ----------
    random_state : int
        Seed for reproducibility.

    Returns
    -------
    stacking_clf : StackingClassifier
    """
    # Base models
    rf_base = RandomForestClassifier(n_estimators=100, random_state=random_state, n_jobs=-1)
    svm_base = SVC(kernel='rbf', probability=True, random_state=random_state)

    # Meta-model
    rf_meta = RandomForestClassifier(n_estimators=100, random_state=random_state, n_jobs=-1)

    # Stacking
    stacking_clf = StackingClassifier(
        estimators=[
            ('rf', rf_base),
            ('svm', svm_base)
        ],
        final_estimator=rf_meta,
        cv=5
    )

    print("✓ StackingClassifier created:")
    print("    Base models: RandomForestClassifier, SVM (RBF)")
    print("    Meta-model: RandomForestClassifier")
    return stacking_clf


def train_track_a(data_path='datasets/X_features.csv',
                  targets_path='datasets/y_targets.csv',
                  models_dir='models/track_a',
                  test_size=0.2,
                  random_state=42):
    """
    Full Track A pipeline: load data → preprocess → select features → train stacking → evaluate.

    Parameters
    ----------
    data_path : str
        Path to feature CSV.
    targets_path : str
        Path to targets CSV.
    models_dir : str
        Directory to save artifacts.
    test_size : float
        Fraction for test split.
    random_state : int
        Seed.

    Returns
    -------
    results : dict
        Training results including accuracy, confusion matrix, etc.
    """
    print("\n" + "=" * 70)
    print("TRACK A: FRESHNESS GRADE CLASSIFICATION")
    print("=" * 70)

    # ===== STEP 1: Load Data =====
    print("\n[1/6] Loading dataset...")
    X, y, y_labels = load_or_generate_dataset(data_path, targets_path)

    # ===== STEP 2: Feature Scaling =====
    print("\n[2/6] Handling missing values and scaling features...")
    # Impute NaN values
    imputer = SimpleImputer(strategy='mean')
    X_imputed = imputer.fit_transform(X)
    
    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    # ===== STEP 3: Train/Test Split =====
    print("\n[3/6] Splitting data (train/test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"  Train: {X_train.shape[0]} samples")
    print(f"  Test: {X_test.shape[0]} samples")

    # ===== STEP 4: Feature Selection (RFE) =====
    print("\n[4/6] Applying RFE to select top 5 features...")
    feature_names = [f'DCT_{i}' for i in range(10)] + ['Energy']
    selector = TrackAFeatureSelector(n_features_to_select=5, random_state=random_state)
    X_train_selected = selector.fit_transform(X_train, y_train, feature_names=feature_names)
    X_test_selected = selector.transform(X_test)

    selected_feature_names = selector.get_selected_feature_names()
    print(f"  Selected features: {selected_feature_names}")

    # ===== STEP 5: Train StackingClassifier =====
    print("\n[5/6] Training StackingClassifier...")
    stacking_clf = create_stacking_classifier(random_state=random_state)
    stacking_clf.fit(X_train_selected, y_train)
    print("✓ StackingClassifier trained successfully")

    # ===== STEP 6: Evaluate =====
    print("\n[6/6] Evaluating on test set...")
    y_pred = stacking_clf.predict(X_test_selected)
    y_pred_proba = stacking_clf.predict_proba(X_test_selected)

    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    class_report = classification_report(y_test, y_pred, target_names=[y_labels[i] for i in range(4)])

    print(f"\n📊 RESULTS:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"\n  Confusion Matrix:\n{cm}")
    print(f"\n  Classification Report:\n{class_report}")

    # ===== SAVE ARTIFACTS =====
    print("\n" + "=" * 70)
    print("SAVING ARTIFACTS")
    print("=" * 70)
    os.makedirs(models_dir, exist_ok=True)

    imputer_path = os.path.join(models_dir, 'imputer.pkl')
    scaler_path = os.path.join(models_dir, 'scaler.pkl')
    rfe_path = os.path.join(models_dir, 'rfe_selector.pkl')
    model_path = os.path.join(models_dir, 'stacking_model.pkl')
    features_path = os.path.join(models_dir, 'feature_names.json')

    joblib.dump(imputer, imputer_path)
    print(f"✓ Imputer saved to {imputer_path}")

    joblib.dump(scaler, scaler_path)
    print(f"✓ Scaler saved to {scaler_path}")

    selector.save(rfe_path)
    print(f"✓ RFE selector saved to {rfe_path}")

    joblib.dump(stacking_clf, model_path)
    print(f"✓ StackingClassifier saved to {model_path}")

    with open(features_path, 'w') as f:
        json.dump({'feature_names': feature_names, 'selected_features': selected_feature_names, 'label_mapping': y_labels}, f, indent=2)
    print(f"✓ Feature names saved to {features_path}")

    results = {
        'accuracy': accuracy,
        'confusion_matrix': cm.tolist(),
        'class_report': class_report,
        'selected_features': selected_feature_names,
        'y_labels': y_labels,
    }

    return results


if __name__ == '__main__':
    # Change to project root if needed
    base_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_path)

    # Run full pipeline
    results = train_track_a(
        data_path='datasets/X_features.csv',
        targets_path='datasets/y_targets.csv',
        models_dir='models/track_a',
        test_size=0.2,
        random_state=42
    )

    print("\n✅ Track A training complete!")
    print(f"Final Accuracy: {results['accuracy']:.4f}")
