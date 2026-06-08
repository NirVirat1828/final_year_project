"""
tournament_director.py

SENIOR ML ENGINEER - ALGORITHM TOURNAMENT DIRECTOR

A comprehensive benchmarking system to compare multiple ML algorithms across:
- **Method A: Raw Data** (StandardScaler only)
- **Method B: Preprocessed Data** (Savitzky-Golay → DCT → RFE)

Tracks:
- Track A: CLASSIFICATION (Freshness Grade A/B/C/D)
- Track B: REGRESSION (Shelf-Life Days Prediction)

Author: Senior ML Engineer
Date: December 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Scikit-learn imports
from sklearn.preprocessing import StandardScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC, SVR
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.decomposition import PCA
from sklearn.feature_selection import RFE
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import (
    accuracy_score, f1_score, confusion_matrix, 
    mean_squared_error, r2_score, classification_report
)

# XGBoost
import xgboost as xgb

# Signal processing
from scipy.signal import savgol_filter
from scipy.fftpack import dct

# TensorFlow/Keras for 1D-CNN
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


# ============================================================================
# SECTION 1: PREPROCESSING FUNCTIONS
# ============================================================================

class PreprocessorRaw:
    """Method A: Raw Data Processing - StandardScaler only"""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def fit_transform(self, X_train, y_train=None):
        """Fit and transform training data"""
        return self.scaler.fit_transform(X_train)
    
    def transform(self, X_test):
        """Transform test data"""
        return self.scaler.transform(X_test)
    
    def get_name(self):
        return "Raw_StandardScaler"


class PreprocessorAdvanced:
    """Method B: Advanced Preprocessing - SavGol → DCT → RFE"""
    
    def __init__(self, savgol_window=11, savgol_poly=3, dct_keep=5, rfe_features=5):
        self.savgol_window = savgol_window
        self.savgol_poly = savgol_poly
        self.dct_keep = dct_keep
        self.rfe_features = rfe_features
        self.scaler = StandardScaler()
        self.rfe_selector = None
        
    def apply_savgol(self, X):
        """Apply Savitzky-Golay filter to smooth signals"""
        X_smoothed = np.zeros_like(X)
        for i in range(X.shape[0]):
            if X.shape[1] >= self.savgol_window:
                X_smoothed[i] = savgol_filter(X[i], 
                                             window_length=self.savgol_window,
                                             polyorder=self.savgol_poly)
            else:
                X_smoothed[i] = X[i]
        return X_smoothed
    
    def apply_dct(self, X):
        """Apply DCT and keep top N coefficients"""
        X_dct = np.zeros((X.shape[0], self.dct_keep))
        for i in range(X.shape[0]):
            dct_coeffs = dct(X[i], type=2, norm='ortho')
            X_dct[i] = dct_coeffs[:self.dct_keep]
        return X_dct
    
    def fit_transform(self, X_train, y_train=None):
        """Full preprocessing pipeline for training data"""
        # Step 1: Savitzky-Golay smoothing
        X_smooth = self.apply_savgol(X_train)
        
        # Step 2: DCT transformation
        X_dct = self.apply_dct(X_smooth)
        
        # Step 3: Standardize
        X_scaled = self.scaler.fit_transform(X_dct)
        
        # Step 4: RFE (Recursive Feature Elimination) - needs labels
        if y_train is not None and X_scaled.shape[1] > self.rfe_features:
            # Use RandomForest as base estimator for RFE
            base_estimator = RandomForestClassifier(n_estimators=50, random_state=42)
            self.rfe_selector = RFE(estimator=base_estimator, 
                                   n_features_to_select=self.rfe_features)
            X_rfe = self.rfe_selector.fit_transform(X_scaled, y_train)
            return X_rfe
        else:
            return X_scaled
    
    def transform(self, X_test):
        """Transform test data using fitted parameters"""
        # Apply same pipeline
        X_smooth = self.apply_savgol(X_test)
        X_dct = self.apply_dct(X_smooth)
        X_scaled = self.scaler.transform(X_dct)
        
        if self.rfe_selector is not None:
            X_rfe = self.rfe_selector.transform(X_scaled)
            return X_rfe
        return X_scaled
    
    def get_name(self):
        return "Advanced_SavGol_DCT_RFE"


# ============================================================================
# SECTION 2: ALGORITHM DEFINITIONS (The Contenders)
# ============================================================================

class AlgorithmRegistry:
    """Registry of all algorithms for classification and regression"""
    
    @staticmethod
    def get_classification_models():
        """Track A: Classification algorithms"""
        models = {
            '1_LDA_Baseline': LinearDiscriminantAnalysis(),
            '2_SVM_RBF': SVC(kernel='rbf', C=1.0, probability=True, random_state=42),
            '3_RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
            '4_XGBoost': xgb.XGBClassifier(random_state=42, eval_metric='mlogloss'),
        }
        return models
    
    @staticmethod
    def get_regression_models():
        """Track B: Regression algorithms"""
        models = {
            '1_PLS_Industry_Standard': PLSRegression(n_components=5),
            '2_SVR_RBF': SVR(kernel='rbf'),
            '3_RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
            '4_XGBoost': xgb.XGBRegressor(random_state=42),
        }
        return models
    
    @staticmethod
    def build_1dcnn_classifier(input_shape, num_classes):
        """Build 1D-CNN for time-series classification"""
        model = keras.Sequential([
            layers.Input(shape=(input_shape, 1)),
            layers.Conv1D(filters=32, kernel_size=3, activation='relu', padding='same'),
            layers.MaxPooling1D(pool_size=2),
            layers.Conv1D(filters=64, kernel_size=3, activation='relu', padding='same'),
            layers.MaxPooling1D(pool_size=2),
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(num_classes, activation='softmax')
        ])
        model.compile(optimizer='adam',
                     loss='sparse_categorical_crossentropy',
                     metrics=['accuracy'])
        return model


# ============================================================================
# SECTION 3: TOURNAMENT EXECUTION ENGINE
# ============================================================================

class TournamentDirector:
    """Main tournament orchestrator"""
    
    def __init__(self, results_path='results_comparison.csv', 
                 figures_path='tournament_figures/'):
        self.results_path = results_path
        self.figures_path = Path(figures_path)
        self.figures_path.mkdir(exist_ok=True)
        self.results = []
        
    def run_tournament(self, X_train, X_test, y_train_grade, y_test_grade, 
                      y_train_days, y_test_days):
        """
        Main tournament execution loop
        
        Parameters
        ----------
        X_train, X_test : array-like
            Raw feature matrices
        y_train_grade, y_test_grade : array-like
            Classification labels (grades)
        y_train_days, y_test_days : array-like
            Regression targets (storage days)
        """
        print("="*80)
        print("🏆 TOURNAMENT DIRECTOR: ALGORITHM BENCHMARKING SYSTEM")
        print("="*80)
        
        # Define preprocessing methods
        preprocessors = [
            PreprocessorRaw(),
            PreprocessorAdvanced()
        ]
        
        # Run tournament for each preprocessing method
        for preprocessor in preprocessors:
            print(f"\n{'='*80}")
            print(f"📊 PREPROCESSING METHOD: {preprocessor.get_name()}")
            print(f"{'='*80}\n")
            
            # Transform data
            print("Transforming training data...")
            X_train_proc = preprocessor.fit_transform(X_train, y_train_grade)
            X_test_proc = preprocessor.transform(X_test)
            
            print(f"  Original shape: {X_train.shape} → Processed shape: {X_train_proc.shape}\n")
            
            # TRACK A: Classification
            self._run_classification_track(
                X_train_proc, X_test_proc, 
                y_train_grade, y_test_grade,
                preprocessor.get_name()
            )
            
            # TRACK B: Regression
            self._run_regression_track(
                X_train_proc, X_test_proc,
                y_train_days, y_test_days,
                preprocessor.get_name()
            )
        
        # Save results
        self._save_results()
        print(f"\n✅ Results saved to: {self.results_path}")
        print(f"✅ Figures saved to: {self.figures_path}/")
        
    def _run_classification_track(self, X_train, X_test, y_train, y_test, 
                                  preproc_name):
        """Execute Track A: Classification algorithms"""
        print("🎯 TRACK A: CLASSIFICATION (Freshness Grade)")
        print("-" * 80)
        
        models = AlgorithmRegistry.get_classification_models()
        
        for model_name, model in models.items():
            print(f"\n  Training: {model_name}...")
            try:
                # Train
                model.fit(X_train, y_train)
                
                # Predict
                y_pred = model.predict(X_test)
                
                # Metrics
                accuracy = accuracy_score(y_test, y_pred)
                f1_weighted = f1_score(y_test, y_pred, average='weighted')
                
                # Store results
                self.results.append({
                    'Preprocessing': preproc_name,
                    'Track': 'Classification',
                    'Algorithm': model_name,
                    'Accuracy': accuracy,
                    'F1_Weighted': f1_weighted,
                    'RMSE': None,
                    'R2': None
                })
                
                print(f"    ✓ Accuracy: {accuracy:.4f} | F1-Score: {f1_weighted:.4f}")
                
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                continue
        
        # 1D-CNN (Special handling for deep learning)
        print(f"\n  Training: 5_1D_CNN...")
        try:
            # Reshape for CNN
            X_train_cnn = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
            X_test_cnn = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
            
            # Build and train
            num_classes = len(np.unique(y_train))
            cnn_model = AlgorithmRegistry.build_1dcnn_classifier(X_train.shape[1], num_classes)
            
            history = cnn_model.fit(
                X_train_cnn, y_train,
                validation_split=0.2,
                epochs=30,
                batch_size=32,
                verbose=0
            )
            
            # Predict
            y_pred_proba = cnn_model.predict(X_test_cnn, verbose=0)
            y_pred = np.argmax(y_pred_proba, axis=1)
            
            # Metrics
            accuracy = accuracy_score(y_test, y_pred)
            f1_weighted = f1_score(y_test, y_pred, average='weighted')
            
            self.results.append({
                'Preprocessing': preproc_name,
                'Track': 'Classification',
                'Algorithm': '5_1D_CNN',
                'Accuracy': accuracy,
                'F1_Weighted': f1_weighted,
                'RMSE': None,
                'R2': None
            })
            
            print(f"    ✓ Accuracy: {accuracy:.4f} | F1-Score: {f1_weighted:.4f}")
            
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
    
    def _run_regression_track(self, X_train, X_test, y_train, y_test, 
                             preproc_name):
        """Execute Track B: Regression algorithms"""
        print("\n📈 TRACK B: REGRESSION (Shelf-Life Days)")
        print("-" * 80)
        
        models = AlgorithmRegistry.get_regression_models()
        
        for model_name, model in models.items():
            print(f"\n  Training: {model_name}...")
            try:
                # Train
                model.fit(X_train, y_train)
                
                # Predict
                y_pred = model.predict(X_test)
                
                # Metrics
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                r2 = r2_score(y_test, y_pred)
                
                # Store results
                self.results.append({
                    'Preprocessing': preproc_name,
                    'Track': 'Regression',
                    'Algorithm': model_name,
                    'Accuracy': None,
                    'F1_Weighted': None,
                    'RMSE': rmse,
                    'R2': r2
                })
                
                print(f"    ✓ RMSE: {rmse:.4f} | R²: {r2:.4f}")
                
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                continue
    
    def _save_results(self):
        """Save tournament results to CSV"""
        df_results = pd.DataFrame(self.results)
        df_results.to_csv(self.results_path, index=False)
        
        # Display summary
        print("\n" + "="*80)
        print("📊 TOURNAMENT SUMMARY")
        print("="*80 + "\n")
        print(df_results.to_string(index=False))


# ============================================================================
# SECTION 4: VISUALIZATION GENERATORS
# ============================================================================

class TournamentVisualizer:
    """Generate visualization artifacts for tournament results"""
    
    def __init__(self, figures_path='tournament_figures/'):
        self.figures_path = Path(figures_path)
        self.figures_path.mkdir(exist_ok=True)
        sns.set_style("whitegrid")
        
    def generate_pca_scatter(self, X_test_raw, X_test_processed, y_test, 
                            preprocessing_names=['Raw', 'Processed']):
        """PCA 2D scatter plot comparing raw vs processed data"""
        print("📊 Generating PCA Scatter Plot...")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        datasets = [X_test_raw, X_test_processed]
        
        for idx, (X, name) in enumerate(zip(datasets, preprocessing_names)):
            # Apply PCA
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X)
            
            # Plot
            scatter = axes[idx].scatter(X_pca[:, 0], X_pca[:, 1], 
                                       c=y_test, cmap='viridis', 
                                       alpha=0.7, edgecolors='k', s=50)
            axes[idx].set_title(f'PCA Projection - {name}', fontsize=14, fontweight='bold')
            axes[idx].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%})')
            axes[idx].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%})')
            plt.colorbar(scatter, ax=axes[idx], label='Grade')
        
        plt.tight_layout()
        save_path = self.figures_path / 'pca_scatter_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Saved: {save_path}")
        
    def generate_confusion_matrix(self, y_test, y_pred, model_name):
        """Confusion matrix heatmap"""
        print(f"📊 Generating Confusion Matrix for {model_name}...")
        
        cm = confusion_matrix(y_test, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   cbar_kws={'label': 'Count'})
        plt.title(f'Confusion Matrix - {model_name}', fontsize=14, fontweight='bold')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        save_path = self.figures_path / f'confusion_matrix_{model_name.replace(" ", "_")}.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Saved: {save_path}")
        
    def generate_signal_comparison(self, raw_signal, smoothed_signal):
        """Line plot comparing raw vs smoothed signal"""
        print("📊 Generating Signal Comparison Plot...")
        
        plt.figure(figsize=(12, 5))
        x = np.arange(len(raw_signal))
        
        plt.plot(x, raw_signal, 'o-', label='Raw Signal', alpha=0.6, linewidth=2)
        plt.plot(x, smoothed_signal, 's-', label='Smoothed (Savitzky-Golay)', 
                linewidth=2, markersize=6)
        
        plt.title('Signal Preprocessing: Raw vs Smoothed', fontsize=14, fontweight='bold')
        plt.xlabel('Sample Index')
        plt.ylabel('Signal Amplitude')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        save_path = self.figures_path / 'signal_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Saved: {save_path}")
        
    def generate_regression_parity_plot(self, y_test, y_pred, model_name):
        """Parity plot for regression (Predicted vs Actual)"""
        print(f"📊 Generating Parity Plot for {model_name}...")
        
        plt.figure(figsize=(8, 8))
        
        # Scatter plot
        plt.scatter(y_test, y_pred, alpha=0.6, edgecolors='k', s=50)
        
        # y=x reference line
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        plt.plot([min_val, max_val], [min_val, max_val], 
                'r--', linewidth=2, label='Perfect Prediction (y=x)')
        
        # Metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        plt.title(f'Regression Parity Plot - {model_name}', fontsize=14, fontweight='bold')
        plt.xlabel('Actual Shelf-Life Days')
        plt.ylabel('Predicted Shelf-Life Days')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Add metrics text box
        textstr = f'RMSE = {rmse:.2f}\nR² = {r2:.3f}'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(0.05, 0.95, textstr, transform=plt.gca().transAxes, 
                fontsize=12, verticalalignment='top', bbox=props)
        
        save_path = self.figures_path / f'parity_plot_{model_name.replace(" ", "_")}.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Saved: {save_path}")
        
    def generate_performance_comparison(self, results_df):
        """Bar charts comparing algorithm performance"""
        print("📊 Generating Performance Comparison Charts...")
        
        # Classification comparison
        clf_data = results_df[results_df['Track'] == 'Classification'].copy()
        if not clf_data.empty:
            fig, axes = plt.subplots(1, 2, figsize=(15, 5))
            
            for idx, metric in enumerate(['Accuracy', 'F1_Weighted']):
                pivot = clf_data.pivot(index='Algorithm', 
                                      columns='Preprocessing', 
                                      values=metric)
                pivot.plot(kind='bar', ax=axes[idx], rot=45)
                axes[idx].set_title(f'Classification: {metric}', 
                                   fontsize=12, fontweight='bold')
                axes[idx].set_ylabel(metric)
                axes[idx].legend(title='Preprocessing')
                axes[idx].grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            save_path = self.figures_path / 'classification_performance.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  ✓ Saved: {save_path}")
        
        # Regression comparison
        reg_data = results_df[results_df['Track'] == 'Regression'].copy()
        if not reg_data.empty:
            fig, axes = plt.subplots(1, 2, figsize=(15, 5))
            
            for idx, metric in enumerate(['RMSE', 'R2']):
                pivot = reg_data.pivot(index='Algorithm', 
                                      columns='Preprocessing', 
                                      values=metric)
                pivot.plot(kind='bar', ax=axes[idx], rot=45)
                axes[idx].set_title(f'Regression: {metric}', 
                                   fontsize=12, fontweight='bold')
                axes[idx].set_ylabel(metric)
                axes[idx].legend(title='Preprocessing')
                axes[idx].grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            save_path = self.figures_path / 'regression_performance.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  ✓ Saved: {save_path}")


# ============================================================================
# SECTION 5: MAIN EXECUTION & DEMO
# ============================================================================

def load_project_data():
    """Load data from the existing project structure"""
    print("📂 Loading project data...")
    
    # Load features and targets
    X_df = pd.read_csv('datasets/X_features.csv')
    y_targets = pd.read_csv('datasets/y_targets.csv')
    
    # Handle NaN values - fill with column mean
    if X_df.isnull().any().any():
        print("  ⚠️  Found NaN values, filling with column means...")
        X_df = X_df.fillna(X_df.mean())
    
    X_features = X_df.values
    
    # Create grade labels based on storage days
    # Heuristic: Days <= 3 → A(0), Days 4-7 → B(1), Days 8-10 → C(2), Days > 10 → D(3)
    days = y_targets['day'].values
    grades = np.where(days <= 3, 0,
                     np.where(days <= 7, 1,
                             np.where(days <= 10, 2, 3)))
    
    print(f"  ✓ Loaded {X_features.shape[0]} samples with {X_features.shape[1]} features")
    print(f"  ✓ Grade distribution: {np.bincount(grades)}")
    
    return X_features, grades, days


def create_train_test_split(X, y_grade, y_days, test_size=0.2, random_state=42):
    """Create stratified train-test split"""
    from sklearn.model_selection import train_test_split
    
    indices = np.arange(len(X))
    train_idx, test_idx = train_test_split(
        indices, test_size=test_size, 
        stratify=y_grade, random_state=random_state
    )
    
    X_train = X[train_idx]
    X_test = X[test_idx]
    y_train_grade = y_grade[train_idx]
    y_test_grade = y_grade[test_idx]
    y_train_days = y_days[train_idx]
    y_test_days = y_days[test_idx]
    
    print(f"\n📊 Train-Test Split:")
    print(f"  Training: {len(X_train)} samples")
    print(f"  Testing: {len(X_test)} samples")
    
    return X_train, X_test, y_train_grade, y_test_grade, y_train_days, y_test_days


def main():
    """Main execution pipeline"""
    print("\n" + "="*80)
    print("🚀 TOURNAMENT DIRECTOR - COMPREHENSIVE ML BENCHMARKING")
    print("="*80 + "\n")
    
    # Step 1: Load data
    X, y_grade, y_days = load_project_data()
    
    # Step 2: Create train-test split
    X_train, X_test, y_train_grade, y_test_grade, y_train_days, y_test_days = \
        create_train_test_split(X, y_grade, y_days)
    
    # Step 3: Run tournament
    tournament = TournamentDirector()
    tournament.run_tournament(
        X_train, X_test,
        y_train_grade, y_test_grade,
        y_train_days, y_test_days
    )
    
    # Step 4: Generate visualizations
    print("\n" + "="*80)
    print("🎨 GENERATING VISUALIZATIONS")
    print("="*80 + "\n")
    
    visualizer = TournamentVisualizer()
    
    # Prepare data for visualizations
    preprocessor_raw = PreprocessorRaw()
    preprocessor_adv = PreprocessorAdvanced()
    
    # Transform test data for visualizations
    preprocessor_raw.fit_transform(X_train)
    X_test_raw = preprocessor_raw.transform(X_test)
    
    preprocessor_adv.fit_transform(X_train, y_train_grade)
    X_test_adv = preprocessor_adv.transform(X_test)
    
    # Transform train data for model training
    preprocessor_train = PreprocessorAdvanced()
    X_train_adv = preprocessor_train.fit_transform(X_train, y_train_grade)
    X_test_adv_train = preprocessor_train.transform(X_test)
    
    # Generate plots
    visualizer.generate_pca_scatter(X_test_raw, X_test_adv, y_test_grade)
    
    # Train best models for confusion matrix and parity plot
    # Classification: RandomForest
    rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_clf.fit(X_train_adv, y_train_grade)  # Using advanced preprocessing
    y_pred_clf = rf_clf.predict(X_test_adv_train)
    visualizer.generate_confusion_matrix(y_test_grade, y_pred_clf, 'RandomForest_Classifier')
    
    # Regression: RandomForest
    rf_reg = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_reg.fit(X_train_adv, y_train_days)
    y_pred_reg = rf_reg.predict(X_test_adv_train)
    visualizer.generate_regression_parity_plot(y_test_days, y_pred_reg, 'RandomForest_Regressor')
    
    # Signal comparison
    if X_train.shape[1] >= 11:  # Has enough features for smoothing
        raw_sample = X_train[0]
        preprocessor_for_viz = PreprocessorAdvanced()
        smoothed_sample = savgol_filter(raw_sample, window_length=11, polyorder=3)
        visualizer.generate_signal_comparison(raw_sample, smoothed_sample)
    
    # Performance comparison charts
    results_df = pd.read_csv('results_comparison.csv')
    visualizer.generate_performance_comparison(results_df)
    
    print("\n" + "="*80)
    print("✅ TOURNAMENT COMPLETE!")
    print("="*80)
    print("\n📁 Output Files:")
    print(f"  - Results CSV: results_comparison.csv")
    print(f"  - Figures: tournament_figures/")
    print("\n🎯 Next Steps:")
    print("  1. Review results_comparison.csv to identify best performers")
    print("  2. Check tournament_figures/ for visual insights")
    print("  3. Select top models for production deployment")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
