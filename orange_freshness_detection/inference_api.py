"""
inference_api.py

Minimal inference API for the dual-regression orange freshness models.
Loads pre-trained day and folic acid regression models to make predictions
on new sensor data.
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path


class OrangeFreshnessPredictor:
    def __init__(self, models_dir='models'):
        """
        Initialize the predictor by loading trained models and scaler.
        
        Parameters:
        -----------
        models_dir : str
            Path to directory containing .pkl model files
        """
        self.models_dir = Path(models_dir)
        
        # Load models
        self.day_model = pickle.load(open(self.models_dir / 'model_day_rf.pkl', 'rb'))
        self.folic_model = pickle.load(open(self.models_dir / 'model_folic_rf.pkl', 'rb'))
        self.scaler = pickle.load(open(self.models_dir / 'scaler.pkl', 'rb'))
        self.selected_features = pickle.load(open(self.models_dir / 'selected_features.pkl', 'rb'))
        
    def predict_day(self, X_features):
        """
        Predict storage days from sensor features.
        
        Parameters:
        -----------
        X_features : array-like, shape (n_samples, n_features)
            Engineered features (11 features per sample)
            
        Returns:
        --------
        predictions : array, shape (n_samples,)
            Predicted storage days for each sample
        """
        # Scale features
        X_scaled = self.scaler.transform(X_features)
        
        # Select top features
        X_selected = X_scaled[:, self.selected_features]
        
        # Predict
        return self.day_model.predict(X_selected)
    
    def predict_folic_acid(self, X_features):
        """
        Predict folic acid concentration (µM) from sensor features.
        
        Parameters:
        -----------
        X_features : array-like, shape (n_samples, n_features)
            Engineered features (11 features per sample)
            
        Returns:
        --------
        predictions : array, shape (n_samples,)
            Predicted folic acid concentration (µM) for each sample
        """
        # Scale features
        X_scaled = self.scaler.transform(X_features)
        
        # Select top features
        X_selected = X_scaled[:, self.selected_features]
        
        # Predict
        return self.folic_model.predict(X_selected)
    
    def predict_both(self, X_features):
        """
        Predict both storage days and folic acid concentration.
        
        Parameters:
        -----------
        X_features : array-like, shape (n_samples, n_features)
            Engineered features (11 features per sample)
            
        Returns:
        --------
        dict with keys:
            'days': predicted storage days
            'folic_acid_uM': predicted folic acid (µM)
        """
        return {
            'days': self.predict_day(X_features),
            'folic_acid_uM': self.predict_folic_acid(X_features)
        }


if __name__ == '__main__':
    # Example usage
    from pathlib import Path
    
    # Initialize predictor
    predictor = OrangeFreshnessPredictor(models_dir='models')
    
    # Load features
    X_features = pd.read_csv('datasets/X_features.csv').values
    
    # Make predictions
    predictions = predictor.predict_both(X_features[:5])  # First 5 samples
    
    print("Day Predictions:", predictions['days'])
    print("Folic Acid Predictions (µM):", predictions['folic_acid_uM'])
