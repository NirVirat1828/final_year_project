"""
task2_enhanced_features_tournament.py

TASK 2: Enhanced Features (16+) Tournament Evaluation

Tests the enhanced 16-feature set against the baseline 11-feature set
using the tournament framework methodology.

Enhanced Features (from generate_enhanced_features.py):
- Original 11: Peak, Mean, Std, Energy, Skewness, Kurtosis, DCT_1-5
- Additional 5+: Peak_Height, Min_Value, Range, Coeff_Variation, 
  Gradient_Mean, Gradient_Std, Gradient_Max, Entropy, interactions, etc.

Comparison Metrics:
- Classification: Accuracy, F1-score, Confusion Matrix
- Regression: RMSE, R², MAE

Author: ML Engineer
Date: December 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC, SVR
from sklearn.metrics import (accuracy_score, f1_score, classification_report,
                             confusion_matrix, mean_squared_error, r2_score, 
                             mean_absolute_error)
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')


def load_baseline_data():
    """Load baseline 11-feature dataset"""
    print("\n📊 Loading Baseline Features (11 features)...")
    X = pd.read_csv('datasets/X_features.csv')
    y_targets = pd.read_csv('datasets/y_targets.csv')
    
    # Handle NaN values
    if X.isnull().any().any():
        print(f"  ⚠️  Warning: {X.isnull().sum().sum()} NaN values found, filling with 0")
        X = X.fillna(0)
    
    # Create grade labels
    days = y_targets['day'].values
    grades = np.where(days <= 3, 0,
                     np.where(days <= 7, 1,
                             np.where(days <= 10, 2, 3)))
    
    print(f"  ✓ Shape: {X.shape}")
    print(f"  ✓ Features: {list(X.columns)[:3]}... ({len(X.columns)} total)")
    
    return X.values, grades, days


def load_enhanced_data():
    """Load enhanced 16+ feature dataset"""
    print("\n✨ Loading Enhanced Features (16+ features)...")
    X = pd.read_csv('datasets/X_features_enhanced.csv')
    y_targets = pd.read_csv('datasets/y_targets.csv')
    
    # Handle NaN values
    if X.isnull().any().any():
        print(f"  ⚠️  Warning: {X.isnull().sum().sum()} NaN values found, filling with 0")
        X = X.fillna(0)
    
    # Handle infinite values
    X = X.replace([np.inf, -np.inf], 0)
    
    # Create grade labels
    days = y_targets['day'].values
    grades = np.where(days <= 3, 0,
                     np.where(days <= 7, 1,
                             np.where(days <= 10, 2, 3)))
    
    print(f"  ✓ Shape: {X.shape}")
    print(f"  ✓ Features: {list(X.columns)[:3]}... ({len(X.columns)} total)")
    
    # Show new features
    baseline_cols = pd.read_csv('datasets/X_features.csv').columns
    new_features = set(X.columns) - set(baseline_cols)
    if new_features:
        print(f"  ✓ New features: {sorted(new_features)[:5]}... ({len(new_features)} new)")
    
    return X.values, grades, days


def evaluate_classifier(X_train, X_test, y_train, y_test, model_name="Model"):
    """Evaluate classification performance"""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Select model
    if model_name == "RandomForest":
        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    elif model_name == "LDA":
        model = LinearDiscriminantAnalysis()
    elif model_name == "SVM":
        model = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)
    elif model_name == "XGBoost":
        model = xgb.XGBClassifier(n_estimators=100, max_depth=6, 
                                 learning_rate=0.1, random_state=42, eval_metric='mlogloss')
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    # Train and predict
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    
    # Metrics
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    return acc, f1, y_pred


def evaluate_regressor(X_train, X_test, y_train, y_test, model_name="Model"):
    """Evaluate regression performance"""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Select model
    if model_name == "RandomForest":
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=15)
    elif model_name == "SVR":
        model = SVR(kernel='rbf', C=10.0, gamma='scale', epsilon=0.1)
    elif model_name == "XGBoost":
        model = xgb.XGBRegressor(n_estimators=100, max_depth=6, 
                                learning_rate=0.1, random_state=42)
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    # Train and predict
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    
    # Metrics
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    return rmse, r2, mae, y_pred


def run_tournament(feature_set_name, X, y_grade, y_days):
    """Run tournament for a feature set"""
    print(f"\n{'='*80}")
    print(f"🏆 TOURNAMENT: {feature_set_name}")
    print(f"{'='*80}")
    
    # Split data
    X_train, X_test, y_train_grade, y_test_grade, y_train_days, y_test_days = \
        train_test_split(X, y_grade, y_days, test_size=0.2, random_state=42, stratify=y_grade)
    
    print(f"\n  Train: {X_train.shape[0]} samples")
    print(f"  Test: {X_test.shape[0]} samples")
    
    # Classification results
    print(f"\n  📊 CLASSIFICATION (Freshness Grade A/B/C/D)")
    print(f"  {'-'*60}")
    
    classifiers = ["RandomForest", "LDA", "SVM", "XGBoost"]
    clf_results = {}
    
    for clf_name in classifiers:
        acc, f1, y_pred = evaluate_classifier(X_train, X_test, 
                                              y_train_grade, y_test_grade, clf_name)
        clf_results[clf_name] = {'accuracy': acc, 'f1': f1}
        print(f"  {clf_name:15s}: Accuracy={acc:.4f}, F1={f1:.4f}")
    
    # Regression results
    print(f"\n  📈 REGRESSION (Days Prediction)")
    print(f"  {'-'*60}")
    
    regressors = ["RandomForest", "SVR", "XGBoost"]
    reg_results = {}
    
    for reg_name in regressors:
        rmse, r2, mae, y_pred = evaluate_regressor(X_train, X_test, 
                                                    y_train_days, y_test_days, reg_name)
        reg_results[reg_name] = {'rmse': rmse, 'r2': r2, 'mae': mae}
        print(f"  {reg_name:15s}: RMSE={rmse:.4f}, R²={r2:.4f}, MAE={mae:.4f}")
    
    return clf_results, reg_results


def compare_results(baseline_clf, baseline_reg, enhanced_clf, enhanced_reg):
    """Compare baseline vs enhanced features"""
    print(f"\n{'='*80}")
    print(f"📊 COMPARISON: 11 Features vs 16+ Enhanced Features")
    print(f"{'='*80}")
    
    # Classification comparison
    print(f"\n  🎯 CLASSIFICATION WINNERS:")
    print(f"  {'-'*60}")
    
    for clf_name in baseline_clf.keys():
        base_acc = baseline_clf[clf_name]['accuracy']
        enh_acc = enhanced_clf[clf_name]['accuracy']
        improvement = (enh_acc - base_acc) * 100
        
        winner = "✨ ENHANCED" if enh_acc > base_acc else "📊 BASELINE"
        print(f"  {clf_name:15s}: {base_acc:.4f} → {enh_acc:.4f} "
              f"({improvement:+.2f}%) {winner}")
    
    # Regression comparison
    print(f"\n  📈 REGRESSION WINNERS:")
    print(f"  {'-'*60}")
    
    for reg_name in baseline_reg.keys():
        base_rmse = baseline_reg[reg_name]['rmse']
        enh_rmse = enhanced_reg[reg_name]['rmse']
        improvement = ((base_rmse - enh_rmse) / base_rmse) * 100
        
        winner = "✨ ENHANCED" if enh_rmse < base_rmse else "📊 BASELINE"
        print(f"  {reg_name:15s}: {base_rmse:.4f} → {enh_rmse:.4f} "
              f"({improvement:+.2f}%) {winner}")


def create_comparison_plots(baseline_clf, baseline_reg, enhanced_clf, enhanced_reg):
    """Create visualization comparing baseline vs enhanced"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Classification comparison
    ax1 = axes[0]
    clf_names = list(baseline_clf.keys())
    base_acc = [baseline_clf[name]['accuracy'] for name in clf_names]
    enh_acc = [enhanced_clf[name]['accuracy'] for name in clf_names]
    
    x = np.arange(len(clf_names))
    width = 0.35
    
    ax1.bar(x - width/2, base_acc, width, label='11 Features (Baseline)', alpha=0.8)
    ax1.bar(x + width/2, enh_acc, width, label='16+ Features (Enhanced)', alpha=0.8)
    ax1.set_xlabel('Classifier')
    ax1.set_ylabel('Accuracy')
    ax1.set_title('Classification: Baseline vs Enhanced Features')
    ax1.set_xticks(x)
    ax1.set_xticklabels(clf_names, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim([0, 1])
    
    # Regression comparison
    ax2 = axes[1]
    reg_names = list(baseline_reg.keys())
    base_rmse = [baseline_reg[name]['rmse'] for name in reg_names]
    enh_rmse = [enhanced_reg[name]['rmse'] for name in reg_names]
    
    x = np.arange(len(reg_names))
    
    ax2.bar(x - width/2, base_rmse, width, label='11 Features (Baseline)', alpha=0.8)
    ax2.bar(x + width/2, enh_rmse, width, label='16+ Features (Enhanced)', alpha=0.8)
    ax2.set_xlabel('Regressor')
    ax2.set_ylabel('RMSE (days)')
    ax2.set_title('Regression: Baseline vs Enhanced Features (Lower is Better)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(reg_names, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    output_dir = Path('tournament_figures')
    output_dir.mkdir(exist_ok=True)
    plt.savefig(output_dir / 'task2_enhanced_features_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\n  💾 Saved comparison plot: {output_dir / 'task2_enhanced_features_comparison.png'}")
    
    plt.close()


def generate_summary_report(baseline_clf, baseline_reg, enhanced_clf, enhanced_reg):
    """Generate summary report"""
    output_path = Path('TASK2_ENHANCED_FEATURES_REPORT.md')
    
    with open(output_path, 'w') as f:
        f.write("# Task 2: Enhanced Features Tournament Evaluation\n\n")
        f.write("## Overview\n\n")
        f.write("Comparison of 11 baseline features vs 16+ enhanced features using tournament methodology.\n\n")
        
        f.write("## Feature Sets\n\n")
        f.write("### Baseline (11 features)\n")
        f.write("- Peak_0.85V, Mean, Std_Dev, Energy, Skewness, Kurtosis\n")
        f.write("- DCT_1, DCT_2, DCT_3, DCT_4, DCT_5\n\n")
        
        f.write("### Enhanced (16+ features)\n")
        f.write("- All baseline features +\n")
        f.write("- Peak_Height, Min_Value, Range, Coeff_Variation\n")
        f.write("- Gradient_Mean, Gradient_Std, Gradient_Max, Entropy\n")
        f.write("- Interaction features (Energy_Std, Mean_Skewness)\n")
        f.write("- Polynomial features (Energy_Squared, Mean_Squared, etc.)\n\n")
        
        f.write("## Classification Results\n\n")
        f.write("| Algorithm | Baseline Accuracy | Enhanced Accuracy | Improvement |\n")
        f.write("|-----------|-------------------|-------------------|-------------|\n")
        
        for clf_name in baseline_clf.keys():
            base_acc = baseline_clf[clf_name]['accuracy']
            enh_acc = enhanced_clf[clf_name]['accuracy']
            imp = (enh_acc - base_acc) * 100
            winner = "✨" if enh_acc > base_acc else ""
            f.write(f"| {clf_name} | {base_acc:.4f} | {enh_acc:.4f} | {imp:+.2f}% {winner} |\n")
        
        f.write("\n## Regression Results\n\n")
        f.write("| Algorithm | Baseline RMSE | Enhanced RMSE | Improvement |\n")
        f.write("|-----------|---------------|---------------|-------------|\n")
        
        for reg_name in baseline_reg.keys():
            base_rmse = baseline_reg[reg_name]['rmse']
            enh_rmse = enhanced_reg[reg_name]['rmse']
            imp = ((base_rmse - enh_rmse) / base_rmse) * 100
            winner = "✨" if enh_rmse < base_rmse else ""
            f.write(f"| {reg_name} | {base_rmse:.4f} | {enh_rmse:.4f} | {imp:+.2f}% {winner} |\n")
        
        f.write("\n## Conclusions\n\n")
        
        # Count improvements
        clf_improvements = sum(1 for name in baseline_clf.keys() 
                              if enhanced_clf[name]['accuracy'] > baseline_clf[name]['accuracy'])
        reg_improvements = sum(1 for name in baseline_reg.keys() 
                              if enhanced_reg[name]['rmse'] < baseline_reg[name]['rmse'])
        
        f.write(f"- Classification: {clf_improvements}/{len(baseline_clf)} algorithms improved\n")
        f.write(f"- Regression: {reg_improvements}/{len(baseline_reg)} algorithms improved\n\n")
        
        if clf_improvements > len(baseline_clf) / 2 or reg_improvements > len(baseline_reg) / 2:
            f.write("**Recommendation**: Enhanced features show improvement and should be considered for production.\n")
        else:
            f.write("**Recommendation**: Enhanced features show mixed results. Baseline may be sufficient.\n")
    
    print(f"\n  📄 Report saved: {output_path}")


if __name__ == '__main__':
    print("="*80)
    print("TASK 2: ENHANCED FEATURES TOURNAMENT EVALUATION")
    print("="*80)
    print("""
OBJECTIVE:
Test whether 16+ enhanced features improve model performance compared to 
the baseline 11-feature set using tournament-style evaluation.

METHODOLOGY:
1. Load baseline (11 features) and enhanced (16+ features) datasets
2. Run tournament with 4 classifiers and 3 regressors
3. Compare performance metrics
4. Identify best feature set for each algorithm
    """)
    
    try:
        # Load data
        X_baseline, y_grade_base, y_days_base = load_baseline_data()
        X_enhanced, y_grade_enh, y_days_enh = load_enhanced_data()
        
        # Run tournaments
        baseline_clf, baseline_reg = run_tournament("11 Features (Baseline)", 
                                                     X_baseline, y_grade_base, y_days_base)
        enhanced_clf, enhanced_reg = run_tournament("16+ Features (Enhanced)", 
                                                     X_enhanced, y_grade_enh, y_days_enh)
        
        # Compare results
        compare_results(baseline_clf, baseline_reg, enhanced_clf, enhanced_reg)
        
        # Create visualizations
        create_comparison_plots(baseline_clf, baseline_reg, enhanced_clf, enhanced_reg)
        
        # Generate report
        generate_summary_report(baseline_clf, baseline_reg, enhanced_clf, enhanced_reg)
        
        print(f"\n{'='*80}")
        print(f"✅ TASK 2 COMPLETE!")
        print(f"{'='*80}")
        print("""
OUTPUT FILES:
- tournament_figures/task2_enhanced_features_comparison.png
- TASK2_ENHANCED_FEATURES_REPORT.md
        """)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
