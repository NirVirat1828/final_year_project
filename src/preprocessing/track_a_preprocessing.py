"""
track_a_preprocessing.py

Track A: Preprocessing module for freshness grade classification.
Includes:
  - Savitzky–Golay smoothing (window_length=11, polyorder=3)
  - DCT (Discrete Cosine Transform) → top 10 coefficients
  - Peak height extraction
  - Energy calculation
  - Statistical features

Total: 12 engineered features (before RFE selection).
"""

import numpy as np
from scipy.signal import savgol_filter
from scipy.fftpack import dct
from scipy.stats import skew, kurtosis


class TrackAPreprocessor:
    """
    Handles raw optical sensor signals and produces engineered features.
    """

    def __init__(self, savgol_window=11, savgol_polyorder=3, dct_keep=10):
        """
        Parameters
        ----------
        savgol_window : int
            Window length for Savitzky-Goyal smoothing (must be odd).
        savgol_polyorder : int
            Polynomial order for smoothing.
        dct_keep : int
            Number of DCT coefficients to keep.
        """
        self.savgol_window = savgol_window
        self.savgol_polyorder = savgol_polyorder
        self.dct_keep = dct_keep

    def apply_savgol_filter(self, signal):
        """
        Apply Savitzky–Golay smoothing to raw signal.

        Parameters
        ----------
        signal : array-like, shape (n_readings,)
            Raw optical sensor readings.

        Returns
        -------
        smoothed : array-like, shape (n_readings,)
            Smoothed signal.
        """
        # Ensure signal is long enough for the window
        if len(signal) < self.savgol_window:
            return signal
        return savgol_filter(signal, window_length=self.savgol_window, polyorder=self.savgol_polyorder)

    def extract_dct_features(self, signal, n_coefficients=None):
        """
        Extract DCT coefficients (temporal frequency patterns).

        Parameters
        ----------
        signal : array-like, shape (n_readings,)
            Smoothed signal.
        n_coefficients : int, optional
            Number of DCT coefficients to extract (default: self.dct_keep).

        Returns
        -------
        dct_features : dict
            Keys: 'DCT_0', 'DCT_1', ..., 'DCT_n' with coefficient values.
        """
        if n_coefficients is None:
            n_coefficients = self.dct_keep

        # Compute DCT
        dct_vals = dct(signal, type=2, norm='ortho')

        # Keep top n coefficients
        dct_features = {}
        for i in range(min(n_coefficients, len(dct_vals))):
            dct_features[f'DCT_{i}'] = dct_vals[i]

        return dct_features

    def extract_peak_height(self, signal):
        """
        Extract maximum peak height (proxy for optical density).

        Parameters
        ----------
        signal : array-like
            Smoothed signal.

        Returns
        -------
        peak_height : float
        """
        return float(np.max(signal))

    def extract_energy(self, signal):
        """
        Extract total signal energy: sum(signal^2).

        Parameters
        ----------
        signal : array-like
            Smoothed signal.

        Returns
        -------
        energy : float
        """
        return float(np.sum(signal ** 2))

    def extract_statistical_features(self, signal):
        """
        Extract statistical summary features.

        Parameters
        ----------
        signal : array-like
            Smoothed signal.

        Returns
        -------
        stats : dict
            Keys: 'Mean', 'Std', 'Skewness', 'Kurtosis'.
        """
        return {
            'Mean': float(np.mean(signal)),
            'Std': float(np.std(signal)),
            'Skewness': float(skew(signal)),
            'Kurtosis': float(kurtosis(signal)),
        }

    def extract_all_features(self, signal):
        """
        Complete preprocessing pipeline: smoothing → feature extraction.
        
        IMPORTANT: Returns features matching the 11-feature training dataset.

        Parameters
        ----------
        signal : array-like, shape (n_readings,)
            Raw optical sensor readings (e.g., 15 voltage measurements).

        Returns
        -------
        features : dict
            11 engineered features (matching X_features.csv):
              - 10 DCT coefficients (DCT_0 to DCT_9)
              - 1 Energy (or Mean or Std, depending on existing dataset)

        Outputs (in order for consistency):
              - DCT_0, DCT_1, ..., DCT_9
              - Energy
        """
        # Step 1: Smoothing
        smoothed = self.apply_savgol_filter(signal)

        # Step 2: DCT features
        dct_feats = self.extract_dct_features(smoothed, n_coefficients=self.dct_keep)

        # Step 3: Energy
        energy = self.extract_energy(smoothed)

        # Combine all features in order (11 total: 10 DCT + 1 Energy)
        features = {}
        features.update(dct_feats)  # DCT_0 to DCT_9
        features['Energy'] = energy

        return features

    def extract_all_features_extended(self, signal):
        """
        Extended feature set: 12 total.
        
        Returns dict with keys in order suitable for DataFrame conversion.
        """
        smoothed = self.apply_savgol_filter(signal)
        dct_feats = self.extract_dct_features(smoothed, n_coefficients=self.dct_keep)
        peak_height = self.extract_peak_height(smoothed)
        energy = self.extract_energy(smoothed)
        stats = self.extract_statistical_features(smoothed)

        features = {}
        features.update(dct_feats)
        features['Peak_Height'] = peak_height
        features['Energy'] = energy
        # Note: stats features (Mean, Std, Skewness, Kurtosis) can be added 
        # but keep total at 12 by selecting subset if needed
        
        return features


if __name__ == '__main__':
    # Example: process a synthetic signal
    print("=" * 60)
    print("TRACK A PREPROCESSING - EXAMPLE")
    print("=" * 60)

    # Create a synthetic signal (15 readings, like real sensor)
    np.random.seed(42)
    raw_signal = np.sin(np.linspace(0, 4*np.pi, 15)) + 0.3*np.random.randn(15)

    preprocessor = TrackAPreprocessor(savgol_window=5, savgol_polyorder=2, dct_keep=10)
    
    features = preprocessor.extract_all_features(raw_signal)
    
    print(f"\nRaw signal shape: {raw_signal.shape}")
    print(f"Extracted features: {len(features)} (11 total)")
    for key, val in features.items():
        print(f"  {key}: {val:.4f}")
