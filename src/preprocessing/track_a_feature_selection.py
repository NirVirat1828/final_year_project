"""
track_a_feature_selection.py

Track A: RFE-based feature selection for freshness grade classification.

Uses RandomForestClassifier as base estimator to select top 5 features
from 12 engineered features.
"""

import numpy as np
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier
import joblib


class TrackAFeatureSelector:
    """
    Recursive Feature Elimination (RFE) for Track A.
    """

    def __init__(self, n_features_to_select=5, random_state=42):
        """
        Parameters
        ----------
        n_features_to_select : int
            Number of top features to retain.
        random_state : int
            Random seed for reproducibility.
        """
        self.n_features_to_select = n_features_to_select
        self.random_state = random_state
        self.rfe = None
        self.feature_names = None

    def fit(self, X, y, feature_names=None):
        """
        Fit RFE selector on training data.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training feature matrix.
        y : array-like, shape (n_samples,)
            Training target labels (grade: A, B, C, D or encoded as 0, 1, 2, 3).
        feature_names : list, optional
            Human-readable feature names (e.g., ['DCT_0', 'DCT_1', ..., 'Energy']).

        Returns
        -------
        self
        """
        # Initialize base estimator: RandomForestClassifier
        base_estimator = RandomForestClassifier(
            n_estimators=100,
            random_state=self.random_state,
            n_jobs=-1
        )

        # Initialize RFE
        self.rfe = RFE(
            estimator=base_estimator,
            n_features_to_select=self.n_features_to_select,
            step=1
        )

        # Fit RFE
        self.rfe.fit(X, y)
        self.feature_names = feature_names

        print(f"✓ RFE fitted. Selected {self.n_features_to_select} features.")
        return self

    def get_selected_indices(self):
        """
        Get boolean mask or indices of selected features.

        Returns
        -------
        selected_indices : array, shape (n_features,)
            Boolean mask where True indicates selected feature.
        """
        if self.rfe is None:
            raise ValueError("RFE not fitted. Call fit() first.")
        return self.rfe.get_support(indices=False)

    def get_selected_feature_names(self):
        """
        Get names of selected features.

        Returns
        -------
        selected_names : list
            Names of top 5 selected features.
        """
        if self.rfe is None:
            raise ValueError("RFE not fitted. Call fit() first.")
        if self.feature_names is None:
            return [f"Feature_{i}" for i in range(self.n_features_to_select)]

        mask = self.rfe.get_support(indices=False)
        return [self.feature_names[i] for i, selected in enumerate(mask) if selected]

    def transform(self, X):
        """
        Select features from data using fitted RFE.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Data to transform.

        Returns
        -------
        X_selected : array-like, shape (n_samples, n_features_to_select)
            Transformed data with only selected features.
        """
        if self.rfe is None:
            raise ValueError("RFE not fitted. Call fit() first.")
        return self.rfe.transform(X)

    def fit_transform(self, X, y, feature_names=None):
        """
        Fit and transform in one step.
        """
        self.fit(X, y, feature_names=feature_names)
        return self.transform(X)

    def save(self, filepath):
        """
        Save fitted RFE selector to disk.

        Parameters
        ----------
        filepath : str
            Path to .pkl file.
        """
        joblib.dump(self.rfe, filepath)
        print(f"✓ RFE selector saved to {filepath}")

    @staticmethod
    def load(filepath):
        """
        Load a saved RFE selector.

        Parameters
        ----------
        filepath : str
            Path to .pkl file.

        Returns
        -------
        rfe : RFE object
        """
        rfe = joblib.load(filepath)
        print(f"✓ RFE selector loaded from {filepath}")
        return rfe


if __name__ == '__main__':
    # Example: fit RFE on synthetic data
    print("=" * 60)
    print("TRACK A FEATURE SELECTION - EXAMPLE")
    print("=" * 60)

    np.random.seed(42)
    
    # Synthetic training data: 100 samples, 12 features
    X_train = np.random.randn(100, 12)
    y_train = np.random.randint(0, 4, 100)  # 4 classes: A(0), B(1), C(2), D(3)

    feature_names = [f'DCT_{i}' for i in range(10)] + ['Peak_Height', 'Energy']

    selector = TrackAFeatureSelector(n_features_to_select=5, random_state=42)
    selector.fit(X_train, y_train, feature_names=feature_names)

    print(f"\nSelected features: {selector.get_selected_feature_names()}")
    print(f"Selected indices mask: {selector.get_selected_indices()}")

    # Transform new data
    X_selected = selector.transform(X_train[:10])
    print(f"\nTransformed shape (first 10 samples): {X_selected.shape}")
