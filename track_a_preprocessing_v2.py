"""
track_a_preprocessing_v2.py

IMPROVED Track A Preprocessing module with enhanced feature engineering.

This version includes:
  - Original 11 features (compatibility)
  - Phase 1 improvements: 5 new high-impact features
  - Total: 16 engineered features (before RFE selection)

New features:
  1. Range (max - min)
  2. Min value
  3. Coefficient of Variation (Std/Mean)
  4. Gradient Mean (|df/dt|)
  5. DCT coefficients 6-8 (additional frequency info)

These features provide:
  ✓ Better amplitude information
  ✓ Normalized spread metrics
  ✓ Temporal dynamics
  ✓ More frequency components
  ✓ Better discrimination between freshness grades
"""

import numpy as np
from scipy.signal import savgol_filter
from scipy.fftpack import dct
from scipy.stats import skew, kurtosis, entropy


class TrackAPreprocessorV2:
    """
    Enhanced preprocessing with improved feature engineering.
    Backward compatible with original module.
    """

    def __init__(self, savgol_window=11, savgol_polyorder=3, dct_keep=10):
        """
        Parameters
        ----------
        savgol_window : int
            Window length for Savitzky-Golay smoothing (must be odd).
        savgol_polyorder : int
            Polynomial order for smoothing.
        dct_keep : int
            Number of DCT coefficients to keep.
        """
        self.savgol_window = savgol_window
        self.savgol_polyorder = savgol_polyorder
        self.dct_keep = dct_keep

    def apply_savgol_filter(self, signal):
        """Apply Savitzky–Golay smoothing to raw signal."""
        if len(signal) < self.savgol_window:
            return signal
        return savgol_filter(signal, window_length=self.savgol_window, 
                            polyorder=self.savgol_polyorder)

    def extract_dct_features(self, signal, n_coefficients=None):
        """Extract DCT coefficients (temporal frequency patterns)."""
        if n_coefficients is None:
            n_coefficients = self.dct_keep

        dct_vals = dct(signal, type=2, norm='ortho')
        dct_features = {}
        for i in range(min(n_coefficients, len(dct_vals))):
            dct_features[f'DCT_{i}'] = float(dct_vals[i])

        return dct_features

    def extract_peak_height(self, signal):
        """Extract maximum peak height."""
        return float(np.max(signal))

    def extract_min_value(self, signal):
        """NEW: Extract minimum value."""
        return float(np.min(signal))

    def extract_range(self, signal):
        """NEW: Extract signal range (max - min)."""
        return float(np.max(signal) - np.min(signal))

    def extract_energy(self, signal):
        """Extract total signal energy: sum(signal^2)."""
        return float(np.sum(signal ** 2))

    def extract_statistical_features(self, signal):
        """Extract statistical summary features."""
        return {
            'Mean': float(np.mean(signal)),
            'Std': float(np.std(signal)),
            'Skewness': float(skew(signal)),
            'Kurtosis': float(kurtosis(signal)),
        }

    def extract_coefficient_of_variation(self, signal):
        """
        NEW: Coefficient of Variation = Std / Mean (normalized spread).
        Useful for comparing variability across different scales.
        """
        mean_val = np.mean(signal)
        if mean_val == 0:
            return 0.0
        return float(np.std(signal) / mean_val)

    def extract_gradient_features(self, signal):
        """
        NEW: Extract features based on signal gradients (temporal dynamics).
        Captures how quickly the signal changes.
        """
        # First derivative (rate of change)
        gradient = np.diff(signal)
        
        return {
            'Gradient_Mean': float(np.mean(np.abs(gradient))),  # Mean absolute gradient
            'Gradient_Std': float(np.std(gradient)),             # Gradient variation
            'Gradient_Max': float(np.max(np.abs(gradient))),     # Max change rate
        }

    def extract_entropy_feature(self, signal):
        """
        NEW: Shannon entropy - measures signal complexity/randomness.
        Higher entropy = more complex/random signal
        Lower entropy = more ordered/predictable signal
        """
        # Normalize signal to [0, 1] for entropy calculation
        signal_normalized = signal - np.min(signal)
        signal_normalized = signal_normalized / (np.max(signal_normalized) + 1e-10)
        
        # Bin the signal into discrete values for entropy calculation
        hist, _ = np.histogram(signal_normalized, bins=5, range=(0, 1))
        hist = hist / np.sum(hist)  # Normalize to probabilities
        
        # Shannon entropy
        signal_entropy = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0] + 1e-10))
        
        return float(signal_entropy)

    def extract_all_features(self, signal):
        """
        Complete preprocessing pipeline: smoothing → enhanced feature extraction.

        Parameters
        ----------
        signal : array-like, shape (n_readings,)
            Raw optical sensor readings (e.g., 15 voltage measurements).

        Returns
        -------
        features : dict
            16 engineered features (improved version):
              - 10 DCT coefficients (DCT_0 to DCT_9)
              - Peak_Height, Min_Value, Range
              - Energy, Coefficient_of_Variation
              - Gradient_Mean, Gradient_Std, Gradient_Max
              - Entropy

        Total: 16 features before RFE selection
        """
        # Step 1: Smoothing
        smoothed = self.apply_savgol_filter(signal)

        # Step 2: DCT features (original)
        dct_feats = self.extract_dct_features(smoothed, n_coefficients=self.dct_keep)

        # Step 3: Amplitude features (original + new)
        peak_height = self.extract_peak_height(smoothed)
        min_value = self.extract_min_value(smoothed)
        signal_range = self.extract_range(smoothed)
        energy = self.extract_energy(smoothed)

        # Step 4: Normalized spread (new)
        coeff_variation = self.extract_coefficient_of_variation(smoothed)

        # Step 5: Temporal dynamics (new)
        gradient_feats = self.extract_gradient_features(smoothed)

        # Step 6: Complexity (new)
        signal_entropy = self.extract_entropy_feature(smoothed)

        # Combine all features in order
        features = {}
        features.update(dct_feats)           # DCT_0 to DCT_9
        features['Peak_Height'] = peak_height
        features['Min_Value'] = min_value
        features['Range'] = signal_range
        features['Energy'] = energy
        features['Coeff_Variation'] = coeff_variation
        features.update(gradient_feats)      # Gradient_Mean, Std, Max
        features['Entropy'] = signal_entropy

        return features

    def get_feature_names(self):
        """Return ordered list of feature names (for DataFrame construction)."""
        names = [f'DCT_{i}' for i in range(self.dct_keep)]
        names.extend(['Peak_Height', 'Min_Value', 'Range', 'Energy', 'Coeff_Variation'])
        names.extend(['Gradient_Mean', 'Gradient_Std', 'Gradient_Max', 'Entropy'])
        return names


if __name__ == '__main__':
    # Example: process a synthetic signal
    print("=" * 70)
    print("TRACK A PREPROCESSING V2 - ENHANCED FEATURES")
    print("=" * 70)

    # Create a synthetic signal (15 readings, like real sensor)
    np.random.seed(42)
    raw_signal = np.sin(np.linspace(0, 4*np.pi, 15)) + 0.3*np.random.randn(15)

    preprocessor = TrackAPreprocessorV2(savgol_window=5, savgol_polyorder=2, dct_keep=10)
    
    features = preprocessor.extract_all_features(raw_signal)
    
    print(f"\nRaw signal shape: {raw_signal.shape}")
    print(f"Extracted features: {len(features)} total")
    
    print("\n--- Original Features (11) ---")
    original = ['DCT_0', 'DCT_1', 'DCT_2', 'DCT_3', 'DCT_4', 'DCT_5', 
                'DCT_6', 'DCT_7', 'DCT_8', 'DCT_9', 'Energy']
    for key in original:
        if key in features:
            print(f"  {key:20s}: {features[key]:10.4f}")
    
    print("\n--- New Phase 1 Features (5) ---")
    new_features = ['Peak_Height', 'Min_Value', 'Range', 'Coeff_Variation', 'Entropy']
    for key in new_features:
        if key in features:
            print(f"  {key:20s}: {features[key]:10.4f}")
    
    print("\n--- New Temporal Features (3) ---")
    temporal = ['Gradient_Mean', 'Gradient_Std', 'Gradient_Max']
    for key in temporal:
        if key in features:
            print(f"  {key:20s}: {features[key]:10.4f}")
    
    print("\n✅ Feature extraction complete! Total: 16 features")
    print(f"Feature names: {preprocessor.get_feature_names()}")
