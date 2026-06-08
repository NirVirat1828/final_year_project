"""
blind_test_evaluation.py

Evaluate best models on completely unseen blind test dataset (batches 6-7).
This is the final validation to assess production readiness.

Tests:
1. Best Classification Model: Random Forest + Raw preprocessing (77.32%)
2. Best Regression Model: Stacking Ensemble + Raw preprocessing (1.4947 days)
3. Tournament Winner Classification: LDA + Raw (78.05%)
4. Tournament Winner Regression: SVR + Raw (1.493 days)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, StackingRegressor
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC, SVR
from sklearn.metrics import (accuracy_score, f1_score, classification_report,
                             confusion_matrix, mean_squared_error, r2_score, mean_absolute_error)
import os
import warnings
warnings.filterwarnings('ignore')


def load_blind_test_data():
    """Load all blind test CSV files from batches 6-7"""
    print("\n" + "="*80)
    print("📂 LOADING BLIND TEST DATASET (BATCHES 6-7)")
    print("="*80)
    
    blind_dir = 'datasets/test_dataset_blind/'
    files = [f for f in os.listdir(blind_dir) if f.endswith('.csv')]
    files.sort()
    
    print(f"  Found {len(files)} blind test files")
    
    all_data = []
    for file in files:
        df = pd.read_csv(os.path.join(blind_dir, file))
        # Extract batch and day from filename (e.g., "batch6_day3.csv")
        parts = file.replace('.csv', '').split('_')
        batch = int(parts[0].replace('batch', ''))
        day = int(parts[1].replace('day', ''))
        
        df['batch'] = batch
        df['day'] = day
        all_data.append(df)
        print(f"    ✓ {file}: {len(df)} samples")
    
    # Concatenate all data
    blind_df = pd.concat(all_data, ignore_index=True)
    
    print(f"\n  Total blind test samples: {len(blind_df)}")
    print(f"  Batches: {sorted(blind_df['batch'].unique())}")
    print(f"  Days: {sorted(blind_df['day'].unique())}")
    
    return blind_df


def extract_features_from_blind(blind_df):
    """Extract same 11 features as training data"""
    print("\n" + "="*80)
    print("🔧 EXTRACTING FEATURES FROM BLIND TEST DATA")
    print("="*80)
    
    # Check if data has voltage/current format (raw) or feature format
    if 'voltage' in blind_df.columns:
        print("  Format: Raw voltage/current data (need to extract features)")
        # Get current columns
        current_cols = [c for c in blind_df.columns if c.startswith('current_')]
        print(f"  Current columns detected: {len(current_cols)}")
        
        # Group by batch and day, aggregate currents
        features = []
        for (batch, day), group in blind_df.groupby(['batch', 'day']):
            # Average all current readings for this batch-day combination
            signal = group[current_cols].values.flatten()  # All current measurements
            
            # Extract same 11 features as training
            feat = {
                'Mean': np.mean(signal),
                'Std_Dev': np.std(signal),
                'Energy': np.sum(signal**2),
                'Skewness': pd.Series(signal).skew(),
                'Kurtosis': pd.Series(signal).kurtosis(),
                'Peak_0.85V': np.max(signal),
                'Q1': np.percentile(signal, 25),
                'Median': np.median(signal),
                'Q3': np.percentile(signal, 75),
                'IQR': np.percentile(signal, 75) - np.percentile(signal, 25),
                'Range': np.max(signal) - np.min(signal)
            }
            features.append((batch, day, feat))
    else:
        # Already have features
        print("  Format: Pre-extracted features")
        signal_cols = [c for c in blind_df.columns if c.startswith('f') and c != 'filename']
        print(f"  Signal columns detected: {len(signal_cols)}")
        
        features = []
        for idx, row in blind_df.iterrows():
            signal = row[signal_cols].values
            
            # Extract same 11 features as training
            feat = {
                'Mean': np.mean(signal),
                'Std_Dev': np.std(signal),
                'Energy': np.sum(signal**2),
                'Skewness': pd.Series(signal).skew(),
                'Kurtosis': pd.Series(signal).kurtosis(),
                'Peak_0.85V': np.max(signal),
                'Q1': np.percentile(signal, 25),
                'Median': np.median(signal),
                'Q3': np.percentile(signal, 75),
                'IQR': np.percentile(signal, 75) - np.percentile(signal, 25),
                'Range': np.max(signal) - np.min(signal)
            }
            batch = row['batch']
            day = row['day']
            features.append((batch, day, feat))
    
    # Extract batch, day, and feature dict from tuples
    batches = [f[0] for f in features]
    days = [f[1] for f in features]
    feat_dicts = [f[2] for f in features]
    
    X_blind = pd.DataFrame(feat_dicts)
    
    # Create grade labels (same heuristic as training)
    y_days = np.array(days)
    y_grade = np.where(y_days <= 3, 0,  # A
                       np.where(y_days <= 7, 1,  # B
                                np.where(y_days <= 10, 2,  # C
                                         3)))  # D
    
    print(f"\n  Features extracted: {X_blind.shape}")
    print(f"  Grade distribution: A={np.sum(y_grade==0)}, B={np.sum(y_grade==1)}, "
          f"C={np.sum(y_grade==2)}, D={np.sum(y_grade==3)}")
    
    return X_blind.values, y_grade, y_days


def load_training_data_for_models():
    """Load training data to train models"""
    print("\n" + "="*80)
    print("📊 LOADING TRAINING DATA (FOR MODEL TRAINING)")
    print("="*80)
    
    X_train = pd.read_csv('datasets/X_features.csv').values
    y_targets = pd.read_csv('datasets/y_targets.csv')
    
    # Create grade labels
    days = y_targets['day'].values
    y_grade = np.where(days <= 3, 0,
                       np.where(days <= 7, 1,
                                np.where(days <= 10, 2, 3)))
    
    y_days = days
    
    print(f"  Training samples: {X_train.shape[0]}")
    print(f"  Features: {X_train.shape[1]}")
    
    return X_train, y_grade, y_days


def train_and_evaluate_models(X_train, y_train_grade, y_train_days, X_blind, y_blind_grade, y_blind_days):
    """Train best models and evaluate on blind test"""
    
    # Preprocess with Raw + StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_blind_scaled = scaler.transform(X_blind)
    
    results = {}
    
    # ========================================================================
    # MODEL 1: Random Forest Classification (Best Individual Classifier)
    # ========================================================================
    print("\n" + "="*80)
    print("🎯 MODEL 1: Random Forest Classification (Tournament Runner-up)")
    print("="*80)
    
    rf_clf = RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_split=5, 
                                   random_state=42, n_jobs=-1)
    rf_clf.fit(X_train_scaled, y_train_grade)
    y_pred_rf = rf_clf.predict(X_blind_scaled)
    
    rf_acc = accuracy_score(y_blind_grade, y_pred_rf)
    rf_f1 = f1_score(y_blind_grade, y_pred_rf, average='weighted')
    
    print(f"  ✅ Accuracy: {rf_acc*100:.2f}%")
    print(f"  ✅ F1-Score: {rf_f1:.4f}")
    
    results['RF_Classification'] = {
        'accuracy': rf_acc,
        'f1': rf_f1,
        'y_pred': y_pred_rf,
        'report': classification_report(y_blind_grade, y_pred_rf, target_names=['A', 'B', 'C', 'D'])
    }
    
    # ========================================================================
    # MODEL 2: LDA Classification (Tournament Winner)
    # ========================================================================
    print("\n" + "="*80)
    print("🏆 MODEL 2: LDA Classification (Tournament Winner)")
    print("="*80)
    
    lda_clf = LinearDiscriminantAnalysis()
    lda_clf.fit(X_train_scaled, y_train_grade)
    y_pred_lda = lda_clf.predict(X_blind_scaled)
    
    lda_acc = accuracy_score(y_blind_grade, y_pred_lda)
    lda_f1 = f1_score(y_blind_grade, y_pred_lda, average='weighted')
    
    print(f"  ✅ Accuracy: {lda_acc*100:.2f}%")
    print(f"  ✅ F1-Score: {lda_f1:.4f}")
    
    results['LDA_Classification'] = {
        'accuracy': lda_acc,
        'f1': lda_f1,
        'y_pred': y_pred_lda,
        'report': classification_report(y_blind_grade, y_pred_lda, target_names=['A', 'B', 'C', 'D'])
    }
    
    # ========================================================================
    # MODEL 3: Stacking Regression (Optimized Winner)
    # ========================================================================
    print("\n" + "="*80)
    print("🏆 MODEL 3: Stacking Ensemble Regression (Best Overall)")
    print("="*80)
    
    svr_base = SVR(kernel='rbf', C=10.0, gamma='scale', epsilon=0.1)
    rf_base = RandomForestRegressor(n_estimators=200, max_depth=25, min_samples_split=3,
                                   random_state=42, n_jobs=-1)
    
    stacking_reg = StackingRegressor(
        estimators=[('svr', svr_base), ('rf', rf_base)],
        final_estimator=SVR(C=10.0, gamma='scale'),
        cv=5,
        n_jobs=-1
    )
    
    stacking_reg.fit(X_train_scaled, y_train_days)
    y_pred_stack = stacking_reg.predict(X_blind_scaled)
    
    stack_rmse = np.sqrt(mean_squared_error(y_blind_days, y_pred_stack))
    stack_r2 = r2_score(y_blind_days, y_pred_stack)
    stack_mae = mean_absolute_error(y_blind_days, y_pred_stack)
    
    print(f"  ✅ RMSE: {stack_rmse:.4f} days")
    print(f"  ✅ R²: {stack_r2:.4f}")
    print(f"  ✅ MAE: {stack_mae:.4f} days")
    
    results['Stacking_Regression'] = {
        'rmse': stack_rmse,
        'r2': stack_r2,
        'mae': stack_mae,
        'y_pred': y_pred_stack
    }
    
    # ========================================================================
    # MODEL 4: SVR Regression (Tournament Winner)
    # ========================================================================
    print("\n" + "="*80)
    print("🏆 MODEL 4: SVR Regression (Tournament Winner)")
    print("="*80)
    
    svr_reg = SVR(kernel='rbf', C=10.0, gamma='scale', epsilon=0.1)
    svr_reg.fit(X_train_scaled, y_train_days)
    y_pred_svr = svr_reg.predict(X_blind_scaled)
    
    svr_rmse = np.sqrt(mean_squared_error(y_blind_days, y_pred_svr))
    svr_r2 = r2_score(y_blind_days, y_pred_svr)
    svr_mae = mean_absolute_error(y_blind_days, y_pred_svr)
    
    print(f"  ✅ RMSE: {svr_rmse:.4f} days")
    print(f"  ✅ R²: {svr_r2:.4f}")
    print(f"  ✅ MAE: {svr_mae:.4f} days")
    
    results['SVR_Regression'] = {
        'rmse': svr_rmse,
        'r2': svr_r2,
        'mae': svr_mae,
        'y_pred': y_pred_svr
    }
    
    return results, y_blind_grade, y_blind_days


def generate_visualizations(results, y_true_grade, y_true_days):
    """Generate comparison visualizations"""
    print("\n" + "="*80)
    print("📊 GENERATING VISUALIZATIONS")
    print("="*80)
    
    os.makedirs('blind_test_results', exist_ok=True)
    
    # 1. Classification Confusion Matrices
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # LDA
    cm_lda = confusion_matrix(y_true_grade, results['LDA_Classification']['y_pred'])
    sns.heatmap(cm_lda, annot=True, fmt='d', cmap='Blues', ax=axes[0],
                xticklabels=['A', 'B', 'C', 'D'], yticklabels=['A', 'B', 'C', 'D'])
    axes[0].set_title(f"LDA Classification\nAccuracy: {results['LDA_Classification']['accuracy']*100:.2f}%", 
                     fontsize=14, fontweight='bold')
    axes[0].set_ylabel('True Grade', fontsize=12)
    axes[0].set_xlabel('Predicted Grade', fontsize=12)
    
    # Random Forest
    cm_rf = confusion_matrix(y_true_grade, results['RF_Classification']['y_pred'])
    sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Greens', ax=axes[1],
                xticklabels=['A', 'B', 'C', 'D'], yticklabels=['A', 'B', 'C', 'D'])
    axes[1].set_title(f"Random Forest Classification\nAccuracy: {results['RF_Classification']['accuracy']*100:.2f}%",
                     fontsize=14, fontweight='bold')
    axes[1].set_ylabel('True Grade', fontsize=12)
    axes[1].set_xlabel('Predicted Grade', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('blind_test_results/classification_confusion_matrices.png', dpi=300, bbox_inches='tight')
    print("  ✅ Saved: classification_confusion_matrices.png")
    plt.close()
    
    # 2. Regression Parity Plots
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Stacking
    axes[0].scatter(y_true_days, results['Stacking_Regression']['y_pred'], 
                   alpha=0.6, edgecolors='k', linewidth=0.5)
    axes[0].plot([0, 14], [0, 14], 'r--', lw=2, label='Perfect Prediction')
    axes[0].set_xlabel('True Days', fontsize=12)
    axes[0].set_ylabel('Predicted Days', fontsize=12)
    axes[0].set_title(f"Stacking Ensemble Regression\nRMSE: {results['Stacking_Regression']['rmse']:.3f}, "
                     f"R²: {results['Stacking_Regression']['r2']:.3f}", fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # SVR
    axes[1].scatter(y_true_days, results['SVR_Regression']['y_pred'],
                   alpha=0.6, edgecolors='k', linewidth=0.5, color='green')
    axes[1].plot([0, 14], [0, 14], 'r--', lw=2, label='Perfect Prediction')
    axes[1].set_xlabel('True Days', fontsize=12)
    axes[1].set_ylabel('Predicted Days', fontsize=12)
    axes[1].set_title(f"SVR Regression\nRMSE: {results['SVR_Regression']['rmse']:.3f}, "
                     f"R²: {results['SVR_Regression']['r2']:.3f}", fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('blind_test_results/regression_parity_plots.png', dpi=300, bbox_inches='tight')
    print("  ✅ Saved: regression_parity_plots.png")
    plt.close()
    
    # 3. Performance Comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Classification comparison
    models = ['LDA', 'Random Forest']
    accuracies = [results['LDA_Classification']['accuracy']*100, 
                  results['RF_Classification']['accuracy']*100]
    colors = ['#3498db', '#2ecc71']
    
    bars = axes[0].bar(models, accuracies, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
    axes[0].set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    axes[0].set_title('Classification Performance on Blind Test', fontsize=14, fontweight='bold')
    axes[0].set_ylim([0, 100])
    axes[0].grid(axis='y', alpha=0.3)
    
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2., height,
                    f'{acc:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Regression comparison
    models_reg = ['Stacking', 'SVR']
    rmses = [results['Stacking_Regression']['rmse'], results['SVR_Regression']['rmse']]
    colors_reg = ['#e74c3c', '#f39c12']
    
    bars = axes[1].bar(models_reg, rmses, color=colors_reg, alpha=0.8, edgecolor='black', linewidth=2)
    axes[1].set_ylabel('RMSE (days)', fontsize=12, fontweight='bold')
    axes[1].set_title('Regression Performance on Blind Test', fontsize=14, fontweight='bold')
    axes[1].set_ylim([0, max(rmses)*1.3])
    axes[1].grid(axis='y', alpha=0.3)
    axes[1].invert_yaxis()  # Lower is better
    
    for bar, rmse in zip(bars, rmses):
        height = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2., height,
                    f'{rmse:.3f}', ha='center', va='top', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('blind_test_results/performance_comparison.png', dpi=300, bbox_inches='tight')
    print("  ✅ Saved: performance_comparison.png")
    plt.close()


def generate_report(results):
    """Generate comprehensive report"""
    print("\n" + "="*80)
    print("📝 GENERATING BLIND TEST EVALUATION REPORT")
    print("="*80)
    
    report = f"""# 🔬 Blind Test Evaluation Results

**Date:** December 13, 2025  
**Test Dataset:** Batches 6-7 (Completely Unseen During Training)  
**Purpose:** Final production readiness validation

---

## 📊 Executive Summary

**Test Set Size:** {len(results['LDA_Classification']['y_pred'])} samples (15 CSV files)  
**Batches:** 6-7  
**Days Coverage:** 0-14 (full temporal range)  
**Validation Type:** True blind test (never seen during training/validation)

---

## 🎯 Classification Results

### Model 1: LDA (Tournament Winner)
- **Accuracy:** {results['LDA_Classification']['accuracy']*100:.2f}%
- **F1-Score:** {results['LDA_Classification']['f1']:.4f}
- **Status:** {'✅ Production Ready' if results['LDA_Classification']['accuracy'] > 0.70 else '⚠️ Below Target'}

**Classification Report:**
```
{results['LDA_Classification']['report']}
```

### Model 2: Random Forest
- **Accuracy:** {results['RF_Classification']['accuracy']*100:.2f}%
- **F1-Score:** {results['RF_Classification']['f1']:.4f}
- **Status:** {'✅ Production Ready' if results['RF_Classification']['accuracy'] > 0.70 else '⚠️ Below Target'}

**Classification Report:**
```
{results['RF_Classification']['report']}
```

---

## 📈 Regression Results

### Model 3: Stacking Ensemble (Optimized Winner)
- **RMSE:** {results['Stacking_Regression']['rmse']:.4f} days
- **R²:** {results['Stacking_Regression']['r2']:.4f}
- **MAE:** {results['Stacking_Regression']['mae']:.4f} days
- **Status:** {'✅ Excellent' if results['Stacking_Regression']['rmse'] < 2.0 else '⚠️ Above Target'}

### Model 4: SVR (Tournament Winner)
- **RMSE:** {results['SVR_Regression']['rmse']:.4f} days
- **R²:** {results['SVR_Regression']['r2']:.4f}
- **MAE:** {results['SVR_Regression']['mae']:.4f} days
- **Status:** {'✅ Excellent' if results['SVR_Regression']['rmse'] < 2.0 else '⚠️ Above Target'}

---

## 🏆 Best Model Selection

**For Classification:**  
{'✅ **LDA**' if results['LDA_Classification']['accuracy'] >= results['RF_Classification']['accuracy'] else '✅ **Random Forest**'} - {max(results['LDA_Classification']['accuracy'], results['RF_Classification']['accuracy'])*100:.2f}% accuracy

**For Regression:**  
{'✅ **Stacking Ensemble**' if results['Stacking_Regression']['rmse'] <= results['SVR_Regression']['rmse'] else '✅ **SVR**'} - {min(results['Stacking_Regression']['rmse'], results['SVR_Regression']['rmse']):.4f} days RMSE

---

## 📊 Comparison: Test Set vs Blind Test

| Model | Test Set (Stratified 20%) | Blind Test (Batches 6-7) | Difference |
|-------|---------------------------|---------------------------|------------|
| **LDA Classification** | 78.05% | {results['LDA_Classification']['accuracy']*100:.2f}% | {results['LDA_Classification']['accuracy']*100 - 78.05:+.2f}pp |
| **RF Classification** | 77.32% | {results['RF_Classification']['accuracy']*100:.2f}% | {results['RF_Classification']['accuracy']*100 - 77.32:+.2f}pp |
| **Stacking Regression** | 1.4947 days | {results['Stacking_Regression']['rmse']:.4f} days | {results['Stacking_Regression']['rmse'] - 1.4947:+.4f} |
| **SVR Regression** | 1.5225 days | {results['SVR_Regression']['rmse']:.4f} days | {results['SVR_Regression']['rmse'] - 1.5225:+.4f} |

---

## 💡 Key Findings

1. **Generalization Assessment:**
   - Models {'generalize well' if abs(results['LDA_Classification']['accuracy']*100 - 78.05) < 5 else 'show some overfitting'} to unseen batches
   - Classification accuracy {'maintained' if results['LDA_Classification']['accuracy']*100 > 73 else 'decreased'} on blind test
   - Regression RMSE {'maintained' if results['Stacking_Regression']['rmse'] < 2.0 else 'increased'} on blind test

2. **Production Readiness:**
   - ✅ Classification: {'Ready for deployment' if results['LDA_Classification']['accuracy'] > 0.70 else 'Needs improvement'}
   - ✅ Regression: {'Ready for deployment' if results['Stacking_Regression']['rmse'] < 2.5 else 'Needs improvement'}

3. **Model Stability:**
   - Performance drop from test to blind: {abs(results['LDA_Classification']['accuracy']*100 - 78.05):.2f}pp (classification)
   - Performance drop from test to blind: {abs(results['Stacking_Regression']['rmse'] - 1.4947):.4f} days (regression)

---

## 📁 Generated Files

1. **classification_confusion_matrices.png** - LDA vs RF confusion matrices
2. **regression_parity_plots.png** - Stacking vs SVR parity plots
3. **performance_comparison.png** - Side-by-side comparison bars
4. **BLIND_TEST_EVALUATION_REPORT.md** - This comprehensive report

---

## ✅ Recommendations

**Production Deployment:**
- Use {'LDA' if results['LDA_Classification']['accuracy'] >= results['RF_Classification']['accuracy'] else 'Random Forest'} for classification (simpler, {'better' if results['LDA_Classification']['accuracy'] >= results['RF_Classification']['accuracy'] else 'comparable'} performance)
- Use {'Stacking Ensemble' if results['Stacking_Regression']['rmse'] <= results['SVR_Regression']['rmse'] else 'SVR'} for regression (best RMSE)

**Confidence Level:**
- Classification: {'High' if results['LDA_Classification']['accuracy'] > 0.75 else 'Medium' if results['LDA_Classification']['accuracy'] > 0.65 else 'Low'}
- Regression: {'High' if results['Stacking_Regression']['rmse'] < 1.8 else 'Medium' if results['Stacking_Regression']['rmse'] < 2.5 else 'Low'}

---

*Evaluation Completed: December 13, 2025*  
*Status: ✅ Blind test validation complete*
"""
    
    with open('blind_test_results/BLIND_TEST_EVALUATION_REPORT.md', 'w') as f:
        f.write(report)
    
    print("  ✅ Saved: BLIND_TEST_EVALUATION_REPORT.md")


def main():
    """Main execution pipeline"""
    print("\n" + "="*80)
    print("🔬 BLIND TEST EVALUATION - PRODUCTION READINESS VALIDATION")
    print("="*80)
    
    # Step 1: Load blind test data
    blind_df = load_blind_test_data()
    
    # Step 2: Extract features
    X_blind, y_blind_grade, y_blind_days = extract_features_from_blind(blind_df)
    
    # Step 3: Load training data
    X_train, y_train_grade, y_train_days = load_training_data_for_models()
    
    # Step 4: Train and evaluate
    results, y_true_grade, y_true_days = train_and_evaluate_models(
        X_train, y_train_grade, y_train_days,
        X_blind, y_blind_grade, y_blind_days
    )
    
    # Step 5: Generate visualizations
    generate_visualizations(results, y_true_grade, y_true_days)
    
    # Step 6: Generate report
    generate_report(results)
    
    # Final summary
    print("\n" + "="*80)
    print("✅ BLIND TEST EVALUATION COMPLETE!")
    print("="*80)
    print(f"\n📊 CLASSIFICATION RESULTS:")
    print(f"  LDA: {results['LDA_Classification']['accuracy']*100:.2f}% accuracy")
    print(f"  Random Forest: {results['RF_Classification']['accuracy']*100:.2f}% accuracy")
    
    print(f"\n📈 REGRESSION RESULTS:")
    print(f"  Stacking: {results['Stacking_Regression']['rmse']:.4f} days RMSE (R²={results['Stacking_Regression']['r2']:.4f})")
    print(f"  SVR: {results['SVR_Regression']['rmse']:.4f} days RMSE (R²={results['SVR_Regression']['r2']:.4f})")
    
    print(f"\n📁 Output directory: blind_test_results/")
    print(f"  • classification_confusion_matrices.png")
    print(f"  • regression_parity_plots.png")
    print(f"  • performance_comparison.png")
    print(f"  • BLIND_TEST_EVALUATION_REPORT.md")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
