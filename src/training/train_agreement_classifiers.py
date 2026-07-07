"""
train_agreement_classifiers.py

Re-trains the top 3 classification algorithms from the tournament benchmarking
(LDA, SVM-RBF, RandomForest) using the EXACT production preprocessing pipeline
so they are directly compatible with the Model Agreement Engine.

Production pipeline:
  raw 11 features → StandardScaler (scaler.pkl) → RFE indices (selected_features.pkl) → 5 features

Each saved classifier expects 5 input features (n_features_in_ == 5),
making them auto-discoverable by the agreement engine.

Usage:
  cd final_year_project/final_year_project
  python -m src.training.train_agreement_classifiers
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report


def resolve_project_root() -> Path:
    """Resolve to the inner final_year_project directory (the one containing datasets/)."""
    script_dir = Path(__file__).resolve().parent
    # script is in src/training/, so go up 2 levels
    return script_dir.parent.parent


def load_production_artifacts(project_root: Path):
    """
    Load the EXACT production scaler and RFE feature indices
    so our new classifiers see the identical feature space.
    """
    models_dir = project_root / "model" / "models"

    scaler_path = models_dir / "scaler.pkl"
    selected_features_path = models_dir / "selected_features.pkl"

    if not scaler_path.exists():
        raise FileNotFoundError(f"Production scaler not found: {scaler_path}")
    if not selected_features_path.exists():
        raise FileNotFoundError(f"Production feature indices not found: {selected_features_path}")

    scaler = joblib.load(scaler_path)
    selected_indices = np.asarray(joblib.load(selected_features_path), dtype=np.int64)

    print(f"  ✓ Loaded production scaler from {scaler_path}")
    print(f"  ✓ Loaded RFE feature indices: {selected_indices} (shape: {selected_indices.shape})")

    return scaler, selected_indices, models_dir


def load_dataset(project_root: Path):
    """Load the project dataset and create grade labels."""
    features_path = project_root / "datasets" / "X_features.csv"
    targets_path = project_root / "datasets" / "y_targets.csv"

    if not features_path.exists() or not targets_path.exists():
        raise FileNotFoundError(f"Dataset not found at {features_path} / {targets_path}")

    X_df = pd.read_csv(features_path)
    y_df = pd.read_csv(targets_path)

    # Impute NaN values
    X_values = X_df.values
    nan_count = np.isnan(X_values).sum()
    if nan_count > 0:
        print(f"  ⚠ Found {nan_count} NaN values, imputing with column means...")
        imputer = SimpleImputer(strategy='mean')
        X_values = imputer.fit_transform(X_values)

    # Create grade labels: Days ≤ 3 → 0, 4-7 → 1, 8-10 → 2, > 10 → 3
    days = y_df['day'].values
    grades = np.where(days <= 3, 0,
                      np.where(days <= 7, 1,
                               np.where(days <= 10, 2, 3)))

    print(f"  ✓ Loaded {X_values.shape[0]} samples × {X_values.shape[1]} features")
    print(f"  ✓ Grade distribution: {dict(zip(*np.unique(grades, return_counts=True)))}")

    return X_values, grades


def preprocess_with_production_pipeline(X, scaler, selected_indices):
    """
    Apply the EXACT production preprocessing:
      1. StandardScaler transform
      2. Select RFE feature indices → 5 features
    """
    X_scaled = scaler.transform(X)
    X_selected = X_scaled[:, selected_indices]
    print(f"  ✓ Preprocessed: {X.shape} → scaled → selected → {X_selected.shape}")
    return X_selected


def train_and_save_classifiers(X_train, X_test, y_train, y_test, models_dir: Path):
    """
    Train LDA, SVM-RBF, and RandomForest classifiers on the
    5-feature production feature space and save to models_dir.
    """
    classifiers = {
        "model_grade_lda": LinearDiscriminantAnalysis(),
        "model_grade_svm": SVC(
            kernel='rbf', C=1.0, probability=True, random_state=42
        ),
        "model_grade_rf": RandomForestClassifier(
            n_estimators=100, random_state=42, n_jobs=-1
        ),
    }

    results = []

    for name, clf in classifiers.items():
        print(f"\n  🔧 Training {name}...")
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')

        # Verify feature count
        n_features = getattr(clf, "n_features_in_", None)
        print(f"     n_features_in_ = {n_features}")
        print(f"     Accuracy = {accuracy:.4f}")
        print(f"     F1 (weighted) = {f1:.4f}")

        # Save to production models directory
        save_path = models_dir / f"{name}.pkl"
        joblib.dump(clf, save_path)
        print(f"     ✓ Saved → {save_path}")

        results.append({
            "name": name,
            "accuracy": accuracy,
            "f1_weighted": f1,
            "n_features": n_features,
        })

    return results


def main():
    print("\n" + "=" * 70)
    print("🏆 AGREEMENT ENGINE: RE-TRAINING TOP TOURNAMENT CLASSIFIERS")
    print("=" * 70)

    # Step 1: Resolve paths
    project_root = resolve_project_root()
    print(f"\n📂 Project root: {project_root}")

    # Step 2: Load production artifacts
    print("\n[1/4] Loading production preprocessing artifacts...")
    scaler, selected_indices, models_dir = load_production_artifacts(project_root)

    # Step 3: Load dataset
    print("\n[2/4] Loading dataset...")
    X_raw, y_grades = load_dataset(project_root)

    # Step 4: Preprocess using production pipeline
    print("\n[3/4] Applying production preprocessing pipeline...")
    X_selected = preprocess_with_production_pipeline(X_raw, scaler, selected_indices)

    # Step 5: Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_selected, y_grades,
        test_size=0.2,
        random_state=42,
        stratify=y_grades
    )
    print(f"  ✓ Train: {X_train.shape[0]} samples | Test: {X_test.shape[0]} samples")

    # Step 6: Train and save classifiers
    print("\n[4/4] Training classifiers on 5-feature production space...")
    results = train_and_save_classifiers(X_train, X_test, y_train, y_test, models_dir)

    # Summary
    print("\n" + "=" * 70)
    print("📊 TRAINING SUMMARY")
    print("=" * 70)
    print(f"\n  {'Model':<25} {'Accuracy':>10} {'F1 (Weighted)':>15} {'Features':>10}")
    print(f"  {'-'*60}")
    for r in results:
        print(f"  {r['name']:<25} {r['accuracy']:>10.4f} {r['f1_weighted']:>15.4f} {r['n_features']:>10}")

    print(f"\n  ✅ All 3 classifiers saved to: {models_dir}")
    print("  ✅ The Agreement Engine will auto-discover them on next server restart.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
