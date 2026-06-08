"""
task1_blind_test_preprocessing.py

TASK 1: Blind Test Dataset Evaluation with Proper Feature Extraction

PROBLEM: 
- Training data (X_features.csv): 11 pre-extracted features per sample
- Blind test data: Raw sensor data (voltage + 15 current readings)
- Feature format mismatch prevents direct model evaluation

SOLUTION:
Apply the same preprocessing pipeline used for training:
1. Savitzky-Golay smoothing (window=11, polyorder=3)
2. DCT coefficients extraction (top 5)
3. Statistical features (Mean, Std, Energy, Skewness, Kurtosis)
4. Peak detection

This creates a properly formatted blind test dataset for model evaluation.

Author: ML Engineer
Date: December 2025
"""

import numpy as np
import pandas as pd
import os
from pathlib import Path
from scipy.signal import savgol_filter
from scipy.fftpack import dct
from scipy.stats import skew, kurtosis
import warnings
warnings.filterwarnings('ignore')


class BlindTestPreprocessor:
    """
    Converts raw sensor data to engineered features matching training data.
    Follows the exact preprocessing pipeline from track_a_preprocessing.py
    """
    
    def __init__(self, savgol_window=11, savgol_polyorder=3, dct_keep=5):
        self.savgol_window = savgol_window
        self.savgol_polyorder = savgol_polyorder
        self.dct_keep = dct_keep
    
    def apply_savgol_filter(self, signal):
        """Apply Savitzky-Golay smoothing"""
        if len(signal) < self.savgol_window:
            return signal
        return savgol_filter(signal, window_length=self.savgol_window, 
                            polyorder=self.savgol_polyorder)
    
    def extract_dct_features(self, signal, n_coefficients=5):
        """Extract DCT coefficients"""
        dct_vals = dct(signal, type=2, norm='ortho')
        dct_features = {}
        for i in range(min(n_coefficients, len(dct_vals))):
            dct_features[f'DCT_{i}'] = dct_vals[i]
        return dct_features
    
    def extract_features(self, signal):
        """
        Extract 11 features matching X_features.csv:
        - Peak_0.85V
        - Mean
        - Std_Dev
        - Energy
        - Skewness
        - Kurtosis
        - DCT_1 to DCT_5
        """
        # Step 1: Smoothing
        smoothed = self.apply_savgol_filter(signal)
        
        # Step 2: Extract features
        features = {
            'Peak_0.85V': float(np.max(smoothed)),
            'Mean': float(np.mean(smoothed)),
            'Std_Dev': float(np.std(smoothed)),
            'Energy': float(np.sum(smoothed ** 2)),
            'Skewness': float(skew(smoothed)),
            'Kurtosis': float(kurtosis(smoothed)),
        }
        
        # Step 3: DCT features (1-5, skip 0)
        dct_feats = self.extract_dct_features(smoothed, n_coefficients=6)
        for i in range(1, 6):
            features[f'DCT_{i}'] = dct_feats.get(f'DCT_{i}', 0.0)
        
        return features


def load_blind_test_raw():
    """Load raw blind test files"""
    print("\n" + "="*80)
    print("📂 LOADING BLIND TEST DATASET (RAW DATA)")
    print("="*80)
    
    blind_dir = 'datasets/test_dataset_blind/'
    files = sorted([f for f in os.listdir(blind_dir) if f.endswith('.csv')])
    
    print(f"  Found {len(files)} blind test files")
    
    all_samples = []
    
    for file in files:
        # Parse batch and day from filename
        parts = file.replace('.csv', '').split('_')
        batch = int(parts[0].replace('batch', ''))
        day = int(parts[1].replace('day', ''))
        
        # Load raw data
        df = pd.read_csv(os.path.join(blind_dir, file))
        
        # Extract current columns (15 readings per row)
        current_cols = [c for c in df.columns if c.startswith('current_')]
        
        # Each row is one sample
        for idx, row in df.iterrows():
            signal = row[current_cols].values.astype(float)
            all_samples.append({
                'batch': batch,
                'day': day,
                'signal': signal
            })
        
        print(f"    ✓ {file}: {len(df)} samples (day {day})")
    
    print(f"\n  Total samples loaded: {len(all_samples)}")
    return all_samples


def preprocess_blind_test():
    """Main preprocessing function"""
    print("\n" + "="*80)
    print("🔧 PREPROCESSING BLIND TEST DATASET")
    print("="*80)
    
    # Load raw data
    samples = load_blind_test_raw()
    
    # Initialize preprocessor (same params as training)
    preprocessor = BlindTestPreprocessor(savgol_window=11, savgol_polyorder=3, dct_keep=5)
    
    # Extract features for each sample
    feature_list = []
    metadata_list = []
    
    print("\n  Extracting features...")
    for i, sample in enumerate(samples):
        signal = sample['signal']
        features = preprocessor.extract_features(signal)
        
        feature_list.append(features)
        metadata_list.append({
            'batch': sample['batch'],
            'day': sample['day']
        })
        
        if (i + 1) % 500 == 0:
            print(f"    Processed {i + 1}/{len(samples)} samples")
    
    # Convert to DataFrames
    X_blind = pd.DataFrame(feature_list)
    meta_df = pd.DataFrame(metadata_list)
    
    # Reorder columns to match X_features.csv
    expected_cols = ['Peak_0.85V', 'Mean', 'Std_Dev', 'Energy', 'Skewness', 
                     'Kurtosis', 'DCT_1', 'DCT_2', 'DCT_3', 'DCT_4', 'DCT_5']
    X_blind = X_blind[expected_cols]
    
    # Create grade labels (same heuristic as training)
    y_days = meta_df['day'].values
    y_grade = np.where(y_days <= 3, 0,  # A
                       np.where(y_days <= 7, 1,  # B
                                np.where(y_days <= 10, 2,  # C
                                         3)))  # D
    
    print(f"\n✅ Feature extraction complete!")
    print(f"  Blind test features: {X_blind.shape}")
    print(f"  Expected format: (n_samples, 11)")
    print(f"\n  Feature columns: {list(X_blind.columns)}")
    print(f"\n  Grade distribution:")
    print(f"    A (≤3 days): {np.sum(y_grade==0)}")
    print(f"    B (4-7 days): {np.sum(y_grade==1)}")
    print(f"    C (8-10 days): {np.sum(y_grade==2)}")
    print(f"    D (>10 days): {np.sum(y_grade==3)}")
    
    return X_blind, y_grade, y_days, meta_df


def save_preprocessed_blind_test(X_blind, y_grade, y_days, meta_df):
    """Save preprocessed blind test data"""
    output_dir = Path('datasets/preprocessed_blind_test/')
    output_dir.mkdir(exist_ok=True)
    
    # Save features
    X_blind.to_csv(output_dir / 'X_blind_features.csv', index=False)
    
    # Save targets
    targets_df = pd.DataFrame({
        'batch': meta_df['batch'],
        'day': y_days,
        'grade': y_grade
    })
    targets_df.to_csv(output_dir / 'y_blind_targets.csv', index=False)
    
    print(f"\n💾 Saved preprocessed blind test data:")
    print(f"  Features: {output_dir / 'X_blind_features.csv'}")
    print(f"  Targets: {output_dir / 'y_blind_targets.csv'}")


def verify_feature_compatibility():
    """Verify that preprocessed features match training format"""
    print("\n" + "="*80)
    print("✓ VERIFYING FEATURE COMPATIBILITY")
    print("="*80)
    
    # Load training features
    X_train = pd.read_csv('datasets/X_features.csv')
    
    # Load preprocessed blind test
    X_blind = pd.read_csv('datasets/preprocessed_blind_test/X_blind_features.csv')
    
    print(f"\n  Training data shape: {X_train.shape}")
    print(f"  Blind test shape: {X_blind.shape}")
    
    print(f"\n  Training columns: {list(X_train.columns)}")
    print(f"  Blind test columns: {list(X_blind.columns)}")
    
    # Check column match
    if list(X_train.columns) == list(X_blind.columns):
        print(f"\n  ✅ Column names match perfectly!")
    else:
        print(f"\n  ⚠️  Column mismatch detected")
        missing = set(X_train.columns) - set(X_blind.columns)
        extra = set(X_blind.columns) - set(X_train.columns)
        if missing:
            print(f"    Missing in blind test: {missing}")
        if extra:
            print(f"    Extra in blind test: {extra}")
    
    # Check feature statistics
    print(f"\n  Feature statistics comparison:")
    for col in X_train.columns:
        if col in X_blind.columns:
            train_mean = X_train[col].mean()
            blind_mean = X_blind[col].mean()
            print(f"    {col}: Train={train_mean:.2f}, Blind={blind_mean:.2f}")


if __name__ == '__main__':
    print("="*80)
    print("TASK 1: BLIND TEST PREPROCESSING FOR MODEL EVALUATION")
    print("="*80)
    print("""
OVERVIEW:
This script solves the feature format mismatch between training and blind test data.

PROBLEM:
- Training data: 11 pre-extracted features (Peak, Mean, Std, DCT, etc.)
- Blind test: Raw sensor readings (voltage + 15 current values)
- Cannot directly evaluate models on blind test without preprocessing

SOLUTION:
Apply the same Savitzky-Golay + DCT pipeline to blind test data.
""")
    
    try:
        # Preprocess blind test
        X_blind, y_grade, y_days, meta_df = preprocess_blind_test()
        
        # Save results
        save_preprocessed_blind_test(X_blind, y_grade, y_days, meta_df)
        
        # Verify compatibility
        verify_feature_compatibility()
        
        print("\n" + "="*80)
        print("✅ SUCCESS: Blind test preprocessing complete!")
        print("="*80)
        print("""
NEXT STEPS:
1. Use X_blind_features.csv for model evaluation
2. Run: python blind_test_evaluation_fixed.py
3. Compare performance: trained models vs blind test
        """)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
