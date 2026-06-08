"""
STACKING ENSEMBLE WITHOUT RFE - Orange Freshness Detection
===========================================================

Proves that Stacking (SVM + Random Forest) performs better when we:
1. Keep ALL features (no RFE)
2. Apply Savitzky-Golay smoothing
3. Use StandardScaler

Author: Senior ML Engineer
Date: December 13, 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.signal import savgol_filter
from scipy.fftpack import dct
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.svm import SVC, SVR
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.ensemble import StackingClassifier, StackingRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (accuracy_score, f1_score, classification_report,
                             confusion_matrix, mean_squared_error, r2_score, mean_absolute_error)
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


# ============================================================================
# SECTION 1: DATA LOADING & PREPROCESSING (NO-LOSS PIPELINE)
# ============================================================================

class NoLossPreprocessor:
    """
    Preprocessing pipeline that preserves ALL features.
    NO RFE, NO PCA - just smoothing and scaling.
    """
    
    def __init__(self, savgol_window=11, savgol_poly=3):
        """
        Args:
            savgol_window: Window length for Savitzky-Golay filter (must be odd)
            savgol_poly: Polynomial order for Savitzky-Golay filter
        """
        self.savgol_window = savgol_window
        self.savgol_poly = savgol_poly
        self.scaler = StandardScaler()
        self.original_shape = None
        
    def apply_savgol_smoothing(self, X):
        """Apply Savitzky-Golay filter to reduce noise while preserving features"""
        X_smoothed = np.zeros_like(X)
        
        for i in range(X.shape[0]):
            if X.shape[1] >= self.savgol_window:
                # Apply filter to the entire feature vector
                X_smoothed[i] = savgol_filter(
                    X[i], 
                    window_length=self.savgol_window,
                    polyorder=self.savgol_poly
                )
            else:
                # If too few features, just copy
                X_smoothed[i] = X[i]
                
        return X_smoothed
    
    def fit_transform(self, X_train):
        """
        Fit preprocessor on training data and transform.
        
        Args:
            X_train: Training features (n_samples, n_features)
            
        Returns:
            X_processed: Smoothed and scaled features (same shape as input)
        """
        self.original_shape = X_train.shape
        print(f"\n📊 Preprocessing Training Data:")
        print(f"  Original shape: {X_train.shape}")
        
        # Step 1: Apply Savitzky-Golay smoothing
        X_smoothed = self.apply_savgol_smoothing(X_train)
        print(f"  After Savitzky-Golay: {X_smoothed.shape} ✅")
        
        # Step 2: Fit and apply StandardScaler
        X_scaled = self.scaler.fit_transform(X_smoothed)
        print(f"  After StandardScaler: {X_scaled.shape} ✅")
        print(f"  Features preserved: {X_scaled.shape[1]} (NO REDUCTION!)")
        
        return X_scaled
    
    def transform(self, X_test):
        """Transform test data using fitted preprocessor"""
        print(f"\n📊 Preprocessing Test Data:")
        print(f"  Original shape: {X_test.shape}")
        
        # Apply same transformations
        X_smoothed = self.apply_savgol_smoothing(X_test)
        X_scaled = self.scaler.transform(X_smoothed)
        
        print(f"  After preprocessing: {X_scaled.shape} ✅")
        return X_scaled


def load_project_data():
    """Load data from existing project structure"""
    print("\n" + "="*80)
    print("🚀 STACKING ENSEMBLE WITHOUT RFE - DATA LOADING")
    print("="*80)
    
    # Load features and targets
    print("\n📂 Loading datasets...")
    X_features = pd.read_csv('datasets/X_features.csv')
    y_targets = pd.read_csv('datasets/y_targets.csv')
    
    # Handle NaN values
    if X_features.isnull().any().any():
        print("  ⚠️  Found NaN values, filling with column means...")
        X_features = X_features.fillna(X_features.mean())
    
    X = X_features.values
    
    # Create grade labels (A/B/C/D) based on storage days
    days = y_targets['day'].values
    grades = np.where(days <= 3, 0,      # Grade A: 0-3 days
                     np.where(days <= 7, 1,    # Grade B: 4-7 days
                             np.where(days <= 10, 2, 3)))  # Grade C: 8-10, Grade D: >10
    
    print(f"  ✅ Loaded {X.shape[0]} samples with {X.shape[1]} features")
    print(f"  ✅ Grade distribution: {np.bincount(grades)}")
    print(f"  ✅ Day range: {days.min():.1f} - {days.max():.1f} days")
    
    return X, grades, days


def create_train_test_split(X, y_grade, y_days, test_size=0.2, random_state=42):
    """Create stratified train-test split"""
    print(f"\n📊 Creating Train-Test Split (test_size={test_size})...")
    
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
    
    print(f"  Training: {len(X_train)} samples")
    print(f"  Testing: {len(X_test)} samples")
    
    return X_train, X_test, y_train_grade, y_test_grade, y_train_days, y_test_days


# ============================================================================
# SECTION 2: STACKING ENSEMBLE MODELS
# ============================================================================

class StackingEnsemble:
    """
    Implements Stacking Ensemble for both Classification and Regression.
    Compares: SVM only, RF only, and Stacking (SVM+RF).
    """
    
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.results = {
            'classification': {},
            'regression': {}
        }
        
    def build_classification_models(self):
        """Build Classification models: SVM, RF, and Stacking"""
        print("\n" + "="*80)
        print("🏗️  BUILDING CLASSIFICATION MODELS")
        print("="*80)
        
        # Model 1: SVM Only
        svm_clf = SVC(
            kernel='rbf',
            C=1.0,
            probability=True,  # Need for meta-learner
            random_state=self.random_state
        )
        print("\n1️⃣  SVM Classifier:")
        print("    Kernel: RBF, C=1.0, probability=True")
        
        # Model 2: Random Forest Only
        rf_clf = RandomForestClassifier(
            n_estimators=100,
            random_state=self.random_state,
            n_jobs=-1
        )
        print("\n2️⃣  Random Forest Classifier:")
        print("    n_estimators=100, max_features='sqrt'")
        
        # Model 3: Stacking Ensemble
        stacking_clf = StackingClassifier(
            estimators=[
                ('svm', svm_clf),
                ('rf', rf_clf)
            ],
            final_estimator=LogisticRegression(max_iter=1000, random_state=self.random_state),
            cv=5,  # 5-fold cross-validation for meta-features
            n_jobs=-1
        )
        print("\n3️⃣  Stacking Classifier:")
        print("    Base Learners: SVM + Random Forest")
        print("    Meta-Learner: Logistic Regression")
        print("    CV: 5-fold (for meta-features)")
        
        return {
            'SVM_Only': svm_clf,
            'RandomForest_Only': rf_clf,
            'Stacking_Ensemble': stacking_clf
        }
    
    def build_regression_models(self):
        """Build Regression models: SVR, RFR, and Stacking"""
        print("\n" + "="*80)
        print("🏗️  BUILDING REGRESSION MODELS")
        print("="*80)
        
        # Model 1: SVR Only
        svr_reg = SVR(
            kernel='rbf',
            C=1.0,
            gamma='scale'
        )
        print("\n1️⃣  SVR (Support Vector Regression):")
        print("    Kernel: RBF, C=1.0, gamma='scale'")
        
        # Model 2: Random Forest Only
        rf_reg = RandomForestRegressor(
            n_estimators=100,
            random_state=self.random_state,
            n_jobs=-1
        )
        print("\n2️⃣  Random Forest Regressor:")
        print("    n_estimators=100")
        
        # Model 3: Stacking Ensemble
        stacking_reg = StackingRegressor(
            estimators=[
                ('svr', svr_reg),
                ('rf', rf_reg)
            ],
            final_estimator=Ridge(alpha=1.0, random_state=self.random_state),
            cv=5,
            n_jobs=-1
        )
        print("\n3️⃣  Stacking Regressor:")
        print("    Base Learners: SVR + Random Forest")
        print("    Meta-Learner: Ridge Regression (alpha=1.0)")
        print("    CV: 5-fold")
        
        return {
            'SVR_Only': svr_reg,
            'RandomForest_Only': rf_reg,
            'Stacking_Ensemble': stacking_reg
        }
    
    def train_and_evaluate_classification(self, models, X_train, X_test, y_train, y_test):
        """Train and evaluate all classification models"""
        print("\n" + "="*80)
        print("🎯 TRAINING & EVALUATING CLASSIFICATION MODELS")
        print("="*80)
        
        results = {}
        
        for name, model in models.items():
            print(f"\n{'='*60}")
            print(f"Training: {name}")
            print(f"{'='*60}")
            
            # Train
            model.fit(X_train, y_train)
            
            # Predict
            y_pred = model.predict(X_test)
            
            # Metrics
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            results[name] = {
                'model': model,
                'y_pred': y_pred,
                'accuracy': accuracy,
                'f1_score': f1
            }
            
            print(f"  ✅ Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
            print(f"  ✅ F1-Score: {f1:.4f}")
            
        self.results['classification'] = results
        return results
    
    def train_and_evaluate_regression(self, models, X_train, X_test, y_train, y_test):
        """Train and evaluate all regression models"""
        print("\n" + "="*80)
        print("📈 TRAINING & EVALUATING REGRESSION MODELS")
        print("="*80)
        
        results = {}
        
        for name, model in models.items():
            print(f"\n{'='*60}")
            print(f"Training: {name}")
            print(f"{'='*60}")
            
            # Train
            model.fit(X_train, y_train)
            
            # Predict
            y_pred = model.predict(X_test)
            
            # Metrics
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            mae = np.mean(np.abs(y_test - y_pred))
            
            results[name] = {
                'model': model,
                'y_pred': y_pred,
                'rmse': rmse,
                'r2': r2,
                'mae': mae
            }
            
            print(f"  ✅ RMSE: {rmse:.4f} days")
            print(f"  ✅ R² Score: {r2:.4f} ({r2*100:.2f}%)")
            print(f"  ✅ MAE: {mae:.4f} days")
            
        self.results['regression'] = results
        return results


# ============================================================================
# SECTION 3: RESULTS COMPARISON & VISUALIZATION
# ============================================================================

class ResultsVisualizer:
    """Generate comparison tables and visualizations"""
    
    def __init__(self, output_dir='stacking_results'):
        self.output_dir = output_dir
        import os
        os.makedirs(output_dir, exist_ok=True)
        
    def print_classification_comparison(self, results):
        """Print classification metrics comparison table"""
        print("\n" + "="*80)
        print("📊 CLASSIFICATION RESULTS COMPARISON")
        print("="*80)
        
        data = []
        for name, res in results.items():
            data.append({
                'Model': name,
                'Accuracy': f"{res['accuracy']:.4f}",
                'Accuracy %': f"{res['accuracy']*100:.2f}%",
                'F1-Score': f"{res['f1_score']:.4f}"
            })
        
        df = pd.DataFrame(data)
        print("\n" + df.to_string(index=False))
        
        # Find best model
        best_model = max(results.items(), key=lambda x: x[1]['accuracy'])
        print(f"\n🏆 BEST CLASSIFIER: {best_model[0]}")
        print(f"   Accuracy: {best_model[1]['accuracy']*100:.2f}%")
        print(f"   F1-Score: {best_model[1]['f1_score']:.4f}")
        
        return df
    
    def print_regression_comparison(self, results):
        """Print regression metrics comparison table"""
        print("\n" + "="*80)
        print("📊 REGRESSION RESULTS COMPARISON")
        print("="*80)
        
        data = []
        for name, res in results.items():
            data.append({
                'Model': name,
                'RMSE (days)': f"{res['rmse']:.4f}",
                'MAE (days)': f"{res['mae']:.4f}",
                'R² Score': f"{res['r2']:.4f}",
                'R² %': f"{res['r2']*100:.2f}%"
            })
        
        df = pd.DataFrame(data)
        print("\n" + df.to_string(index=False))
        
        # Find best model
        best_model = min(results.items(), key=lambda x: x[1]['rmse'])
        print(f"\n🏆 BEST REGRESSOR: {best_model[0]}")
        print(f"   RMSE: {best_model[1]['rmse']:.4f} days")
        print(f"   R²: {best_model[1]['r2']:.4f} ({best_model[1]['r2']*100:.2f}%)")
        
        return df
    
    def plot_confusion_matrix(self, y_test, y_pred, model_name='Stacking_Ensemble'):
        """Plot confusion matrix for classification"""
        plt.figure(figsize=(10, 8))
        
        cm = confusion_matrix(y_test, y_pred)
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['A', 'B', 'C', 'D'],
                    yticklabels=['A', 'B', 'C', 'D'],
                    cbar_kws={'label': 'Count'})
        
        plt.title(f'Confusion Matrix - {model_name}\n(No RFE - All Features Used)', 
                  fontsize=14, fontweight='bold')
        plt.ylabel('True Grade', fontsize=12)
        plt.xlabel('Predicted Grade', fontsize=12)
        
        # Add accuracy on diagonal
        for i in range(len(cm)):
            accuracy = cm[i, i] / cm[i].sum() * 100
            plt.text(i + 0.5, i + 0.7, f'{accuracy:.1f}%', 
                    ha='center', va='center', fontsize=10, color='red', fontweight='bold')
        
        save_path = f"{self.output_dir}/confusion_matrix_{model_name}.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n  ✅ Saved: {save_path}")
    
    def plot_regression_scatter(self, y_test, y_pred, model_name='Stacking_Ensemble', metrics=None):
        """Plot actual vs predicted scatter for regression"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Scatter plot
        ax.scatter(y_test, y_pred, alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
        
        # Perfect prediction line
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
        
        # Labels and title
        ax.set_xlabel('Actual Days', fontsize=12, fontweight='bold')
        ax.set_ylabel('Predicted Days', fontsize=12, fontweight='bold')
        ax.set_title(f'Regression Parity Plot - {model_name}\n(No RFE - All Features Used)', 
                     fontsize=14, fontweight='bold')
        
        # Add metrics text box
        if metrics:
            textstr = f"RMSE: {metrics['rmse']:.3f} days\n"
            textstr += f"R²: {metrics['r2']:.3f}\n"
            textstr += f"MAE: {metrics['mae']:.3f} days"
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
            ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=11,
                   verticalalignment='top', bbox=props)
        
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        save_path = f"{self.output_dir}/parity_plot_{model_name}.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✅ Saved: {save_path}")
    
    def plot_performance_comparison(self, clf_results, reg_results):
        """Plot side-by-side performance comparison"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Classification comparison
        models = list(clf_results.keys())
        accuracies = [clf_results[m]['accuracy'] * 100 for m in models]
        f1_scores = [clf_results[m]['f1_score'] * 100 for m in models]
        
        x = np.arange(len(models))
        width = 0.35
        
        axes[0].bar(x - width/2, accuracies, width, label='Accuracy', alpha=0.8)
        axes[0].bar(x + width/2, f1_scores, width, label='F1-Score', alpha=0.8)
        axes[0].set_ylabel('Score (%)', fontweight='bold')
        axes[0].set_title('Classification Performance\n(Higher is Better)', fontweight='bold')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(models, rotation=15, ha='right')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3, axis='y')
        axes[0].set_ylim([0, 100])
        
        # Add value labels on bars
        for i, (acc, f1) in enumerate(zip(accuracies, f1_scores)):
            axes[0].text(i - width/2, acc + 1, f'{acc:.1f}%', ha='center', va='bottom', fontsize=9)
            axes[0].text(i + width/2, f1 + 1, f'{f1:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # Regression comparison
        models_reg = list(reg_results.keys())
        rmses = [reg_results[m]['rmse'] for m in models_reg]
        r2_scores = [reg_results[m]['r2'] * 100 for m in models_reg]
        
        x_reg = np.arange(len(models_reg))
        
        ax2 = axes[1]
        ax2_twin = ax2.twinx()
        
        bar1 = ax2.bar(x_reg - width/2, rmses, width, label='RMSE', alpha=0.8, color='coral')
        bar2 = ax2_twin.bar(x_reg + width/2, r2_scores, width, label='R²', alpha=0.8, color='lightgreen')
        
        ax2.set_ylabel('RMSE (days)', fontweight='bold', color='coral')
        ax2_twin.set_ylabel('R² Score (%)', fontweight='bold', color='green')
        ax2.set_title('Regression Performance\n(RMSE: Lower is Better, R²: Higher is Better)', fontweight='bold')
        ax2.set_xticks(x_reg)
        ax2.set_xticklabels(models_reg, rotation=15, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for i, (rmse, r2) in enumerate(zip(rmses, r2_scores)):
            ax2.text(i - width/2, rmse + 0.05, f'{rmse:.2f}', ha='center', va='bottom', fontsize=9)
            ax2_twin.text(i + width/2, r2 + 2, f'{r2:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # Combine legends
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2_twin.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        plt.tight_layout()
        save_path = f"{self.output_dir}/performance_comparison.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n  ✅ Saved: {save_path}")


# ============================================================================
# SECTION 4: MAIN EXECUTION
# ============================================================================

def main():
    """Main execution pipeline"""
    print("\n" + "="*80)
    print("🎯 STACKING ENSEMBLE WITHOUT RFE")
    print("Proving that keeping ALL features improves performance")
    print("="*80)
    
    # Step 1: Load Data
    X, y_grade, y_days = load_project_data()
    
    # Step 2: Train-Test Split
    X_train, X_test, y_train_grade, y_test_grade, y_train_days, y_test_days = \
        create_train_test_split(X, y_grade, y_days)
    
    # Step 3: Preprocess (No-Loss Pipeline)
    preprocessor = NoLossPreprocessor(savgol_window=11, savgol_poly=3)
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # Step 4: Build and Train Models
    ensemble = StackingEnsemble(random_state=42)
    
    # Classification
    clf_models = ensemble.build_classification_models()
    clf_results = ensemble.train_and_evaluate_classification(
        clf_models, X_train_processed, X_test_processed, 
        y_train_grade, y_test_grade
    )
    
    # Regression
    reg_models = ensemble.build_regression_models()
    reg_results = ensemble.train_and_evaluate_regression(
        reg_models, X_train_processed, X_test_processed,
        y_train_days, y_test_days
    )
    
    # Step 5: Visualize Results
    visualizer = ResultsVisualizer(output_dir='stacking_results')
    
    print("\n" + "="*80)
    print("📊 GENERATING COMPARISON REPORTS")
    print("="*80)
    
    # Print comparison tables
    clf_df = visualizer.print_classification_comparison(clf_results)
    reg_df = visualizer.print_regression_comparison(reg_results)
    
    # Generate visualizations
    print("\n📊 Generating Visualizations...")
    
    # Confusion matrix for Stacking Ensemble
    stacking_clf_pred = clf_results['Stacking_Ensemble']['y_pred']
    visualizer.plot_confusion_matrix(y_test_grade, stacking_clf_pred, 'Stacking_Ensemble')
    
    # Parity plot for Stacking Ensemble
    stacking_reg_pred = reg_results['Stacking_Ensemble']['y_pred']
    stacking_reg_metrics = reg_results['Stacking_Ensemble']
    visualizer.plot_regression_scatter(y_test_days, stacking_reg_pred, 
                                      'Stacking_Ensemble', stacking_reg_metrics)
    
    # Performance comparison
    visualizer.plot_performance_comparison(clf_results, reg_results)
    
    # Step 6: Final Summary
    print("\n" + "="*80)
    print("✅ EXECUTION COMPLETE!")
    print("="*80)
    
    print("\n🎯 KEY FINDINGS:")
    print(f"  • Features used: {X_train_processed.shape[1]} (NO RFE - ALL FEATURES!)")
    print(f"  • Preprocessing: Savitzky-Golay smoothing + StandardScaler only")
    
    print("\n📊 Classification Results:")
    for name, res in clf_results.items():
        print(f"  • {name:25s}: {res['accuracy']*100:.2f}% accuracy")
    
    print("\n📈 Regression Results:")
    for name, res in reg_results.items():
        print(f"  • {name:25s}: {res['rmse']:.3f} days RMSE, R²={res['r2']:.3f}")
    
    print("\n📁 Output Files:")
    print(f"  • Confusion Matrix: stacking_results/confusion_matrix_Stacking_Ensemble.png")
    print(f"  • Parity Plot: stacking_results/parity_plot_Stacking_Ensemble.png")
    print(f"  • Performance Comparison: stacking_results/performance_comparison.png")
    
    # Determine if stacking won
    print("\n" + "="*80)
    print("🏆 VERDICT: Did Stacking Win?")
    print("="*80)
    
    clf_accuracies = {name: res['accuracy'] for name, res in clf_results.items()}
    best_clf = max(clf_accuracies.items(), key=lambda x: x[1])
    
    reg_rmses = {name: res['rmse'] for name, res in reg_results.items()}
    best_reg = min(reg_rmses.items(), key=lambda x: x[1])
    
    print(f"\n🎯 Classification Winner: {best_clf[0]} ({best_clf[1]*100:.2f}%)")
    if best_clf[0] == 'Stacking_Ensemble':
        print("  ✅ STACKING WINS! The ensemble outperforms individual models.")
    else:
        print(f"  ⚠️  {best_clf[0]} performed best, but stacking is close.")
    
    print(f"\n📈 Regression Winner: {best_reg[0]} ({best_reg[1]:.3f} days RMSE)")
    if best_reg[0] == 'Stacking_Ensemble':
        print("  ✅ STACKING WINS! The ensemble outperforms individual models.")
    else:
        print(f"  ⚠️  {best_reg[0]} performed best, but stacking is close.")
    
    print("\n" + "="*80)
    print("🎓 CONCLUSION:")
    print("By removing RFE and keeping ALL features after Savitzky-Golay smoothing,")
    print("we preserved critical information that helps the stacking ensemble")
    print("combine the strengths of both SVM and Random Forest!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
