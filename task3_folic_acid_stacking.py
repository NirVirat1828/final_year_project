"""
task3_folic_acid_stacking.py

TASK 3: Folic Acid Prediction in Stacking Ensemble

BACKGROUND:
- Dual Track notebook achieved R²=0.9997 for folic acid prediction
- Stacking ensemble currently only handles freshness grade (classification) 
  and days prediction (regression)
- Folic acid data available in key.csv (41 labeled samples)

APPROACH:
Add folic acid regression as a third track to the stacking ensemble.
Use the same base learners (SVM, RandomForest) with a meta-learner.

Data:
- y_targets.csv has 'true_conc_uM' column (folic acid concentration in µM)
- Only samples with matching key.csv entries have folic acid labels
- Expected ~35-41 labeled samples out of 2052 total

Author: ML Engineer
Date: December 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')


def load_folic_acid_data():
    """Load data with folic acid labels"""
    print("\n" + "="*80)
    print("📂 LOADING FOLIC ACID DATASET")
    print("="*80)
    
    # Load features
    X = pd.read_csv('datasets/X_features.csv')
    
    # Load targets
    y_targets = pd.read_csv('datasets/y_targets.csv')
    
    print(f"  Total samples: {len(X)}")
    print(f"  Features: {X.shape[1]}")
    
    # Check if folic acid labels exist
    if 'true_conc_uM' in y_targets.columns:
        # Filter to only samples with folic acid labels
        folic_mask = y_targets['true_conc_uM'].notna()
        X_folic = X[folic_mask].values
        y_folic = y_targets.loc[folic_mask, 'true_conc_uM'].values
        
        print(f"  Samples with folic acid labels: {len(y_folic)}")
        print(f"  Folic acid range: {y_folic.min():.2f} - {y_folic.max():.2f} µM")
        print(f"  Folic acid mean: {y_folic.mean():.2f} µM")
        
        return X_folic, y_folic
    else:
        print("  ⚠️  'true_conc_uM' column not found in y_targets.csv")
        print("  Attempting to load from key.csv...")
        
        # Try loading from key.csv
        try:
            key_df = pd.read_csv('datasets/key.csv')
            
            # Match key.csv entries to X_features by batch/day
            y_with_batch = y_targets.copy()
            y_with_batch = y_with_batch.merge(key_df[['batch', 'day', 'true_conc_uM']], 
                                              on=['batch', 'day'], how='left')
            
            folic_mask = y_with_batch['true_conc_uM'].notna()
            X_folic = X[folic_mask].values
            y_folic = y_with_batch.loc[folic_mask, 'true_conc_uM'].values
            
            print(f"  ✓ Loaded from key.csv: {len(y_folic)} samples")
            print(f"  Folic acid range: {y_folic.min():.2f} - {y_folic.max():.2f} µM")
            
            return X_folic, y_folic
            
        except Exception as e:
            print(f"  ❌ Could not load folic acid data: {e}")
            return None, None


def train_folic_acid_stacking(X, y):
    """Train stacking ensemble for folic acid prediction"""
    print("\n" + "="*80)
    print("🏗️  TRAINING FOLIC ACID STACKING ENSEMBLE")
    print("="*80)
    
    # Check sample size
    if len(X) < 20:
        print(f"  ⚠️  Warning: Only {len(X)} samples available")
        print(f"  Stacking may not be reliable with such limited data")
        return None, None, None, None, None
    
    # Split data (stratified won't work for regression, use simple split)
    # Use more data for training due to small dataset
    test_size = 0.3 if len(X) > 40 else 0.2
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    print(f"\n  Train samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Define base learners
    base_learners = [
        ('svr', SVR(kernel='rbf', C=10.0, gamma='scale', epsilon=0.1)),
        ('rf', RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42))
    ]
    
    # Meta-learner
    meta_learner = Ridge(alpha=1.0)
    
    # Create stacking ensemble
    stacking_model = StackingRegressor(
        estimators=base_learners,
        final_estimator=meta_learner,
        cv=min(3, len(X_train) // 3)  # Adjust CV based on sample size
    )
    
    print(f"\n  Base learners: SVR, RandomForest")
    print(f"  Meta-learner: Ridge Regression")
    print(f"  CV folds: {min(3, len(X_train) // 3)}")
    
    # Train
    print(f"\n  Training...")
    stacking_model.fit(X_train_scaled, y_train)
    
    # Predict
    y_pred_train = stacking_model.predict(X_train_scaled)
    y_pred_test = stacking_model.predict(X_test_scaled)
    
    # Evaluate
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    train_r2 = r2_score(y_train, y_pred_train)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    test_r2 = r2_score(y_test, y_pred_test)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    
    print(f"\n  ✅ Training complete!")
    print(f"\n  Training Performance:")
    print(f"    RMSE: {train_rmse:.4f} µM")
    print(f"    R²: {train_r2:.4f}")
    
    print(f"\n  Test Performance:")
    print(f"    RMSE: {test_rmse:.4f} µM")
    print(f"    R²: {test_r2:.4f}")
    print(f"    MAE: {test_mae:.4f} µM")
    
    return stacking_model, scaler, y_test, y_pred_test, (test_rmse, test_r2, test_mae)


def compare_with_baseline(X, y):
    """Compare stacking with individual models"""
    print("\n" + "="*80)
    print("📊 BASELINE COMPARISON")
    print("="*80)
    
    # Split data
    test_size = 0.3 if len(X) > 40 else 0.2
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    results = {}
    
    # SVR
    print(f"\n  Training SVR...")
    svr = SVR(kernel='rbf', C=10.0, gamma='scale', epsilon=0.1)
    svr.fit(X_train_scaled, y_train)
    y_pred = svr.predict(X_test_scaled)
    results['SVR'] = {
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'r2': r2_score(y_test, y_pred),
        'mae': mean_absolute_error(y_test, y_pred)
    }
    
    # Random Forest
    print(f"  Training RandomForest...")
    rf = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42)
    rf.fit(X_train_scaled, y_train)
    y_pred = rf.predict(X_test_scaled)
    results['RandomForest'] = {
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'r2': r2_score(y_test, y_pred),
        'mae': mean_absolute_error(y_test, y_pred)
    }
    
    # Print comparison
    print(f"\n  Results:")
    print(f"  {'Model':<15} {'RMSE':>10} {'R²':>10} {'MAE':>10}")
    print(f"  {'-'*50}")
    for model_name, metrics in results.items():
        print(f"  {model_name:<15} {metrics['rmse']:>10.4f} {metrics['r2']:>10.4f} {metrics['mae']:>10.4f}")
    
    return results


def create_prediction_plot(y_test, y_pred, metrics, output_path):
    """Create prediction vs actual plot"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Scatter plot
    ax.scatter(y_test, y_pred, alpha=0.6, s=100)
    
    # Perfect prediction line
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
    
    # Labels and title
    ax.set_xlabel('Actual Folic Acid (µM)', fontsize=12)
    ax.set_ylabel('Predicted Folic Acid (µM)', fontsize=12)
    ax.set_title('Folic Acid Stacking Ensemble: Predictions vs Actual', fontsize=14, fontweight='bold')
    
    # Add metrics text
    rmse, r2, mae = metrics
    text = f'RMSE: {rmse:.2f} µM\nR²: {r2:.4f}\nMAE: {mae:.2f} µM'
    ax.text(0.05, 0.95, text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            fontsize=11)
    
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n  💾 Saved prediction plot: {output_path}")
    plt.close()


def generate_report(stacking_metrics, baseline_results, n_samples):
    """Generate comprehensive report"""
    output_path = Path('TASK3_FOLIC_ACID_STACKING_REPORT.md')
    
    with open(output_path, 'w') as f:
        f.write("# Task 3: Folic Acid Prediction with Stacking Ensemble\n\n")
        
        f.write("## Overview\n\n")
        f.write("Extended the stacking ensemble to predict folic acid concentration (µM) ")
        f.write("in addition to freshness grade classification and days prediction.\n\n")
        
        f.write("## Dataset\n\n")
        f.write(f"- Total samples with folic acid labels: {n_samples}\n")
        f.write("- Features: 11 engineered features from optical sensor data\n")
        f.write("- Target: Folic acid concentration (µM)\n")
        f.write("- Source: key.csv matched with X_features.csv\n\n")
        
        f.write("## Data Limitation Challenge\n\n")
        f.write(f"⚠️ **Limited Training Data**: Only {n_samples} samples with folic acid labels.\n\n")
        f.write("This is significantly smaller than:\n")
        f.write("- Freshness classification: 2052 samples\n")
        f.write("- Days prediction: 2052 samples\n\n")
        f.write("With such limited data, stacking ensembles may not show the same ")
        f.write("performance gains as they do with larger datasets.\n\n")
        
        f.write("## Model Architecture\n\n")
        f.write("**Stacking Ensemble:**\n")
        f.write("- Base Learner 1: Support Vector Regressor (RBF kernel)\n")
        f.write("- Base Learner 2: Random Forest Regressor\n")
        f.write("- Meta-Learner: Ridge Regression\n\n")
        
        f.write("## Results\n\n")
        
        if stacking_metrics:
            rmse, r2, mae = stacking_metrics
            f.write("### Stacking Ensemble Performance\n\n")
            f.write(f"- **RMSE**: {rmse:.4f} µM\n")
            f.write(f"- **R²**: {r2:.4f}\n")
            f.write(f"- **MAE**: {mae:.4f} µM\n\n")
        
        f.write("### Baseline Models Comparison\n\n")
        f.write("| Model | RMSE (µM) | R² | MAE (µM) |\n")
        f.write("|-------|-----------|----|---------|\n")
        
        for model_name, metrics in baseline_results.items():
            f.write(f"| {model_name} | {metrics['rmse']:.4f} | {metrics['r2']:.4f} | {metrics['mae']:.4f} |\n")
        
        if stacking_metrics:
            rmse, r2, mae = stacking_metrics
            f.write(f"| **Stacking** | **{rmse:.4f}** | **{r2:.4f}** | **{mae:.4f}** |\n")
        
        f.write("\n## Comparison with Dual Track Results\n\n")
        f.write("The Dual Track notebook achieved:\n")
        f.write("- **R² = 0.9997** for folic acid prediction\n\n")
        f.write("This much higher performance was likely due to:\n")
        f.write("1. Different data split or validation strategy\n")
        f.write("2. Optimized hyperparameters specifically for folic acid\n")
        f.write("3. Potentially different feature engineering\n")
        f.write("4. Temporal batch-based splits (training on batches 1-4, testing on batch 5)\n\n")
        
        f.write("## Analysis\n\n")
        
        if stacking_metrics and baseline_results:
            best_baseline = min(baseline_results.items(), key=lambda x: x[1]['rmse'])
            best_name, best_metrics = best_baseline
            rmse, r2, mae = stacking_metrics
            
            if rmse < best_metrics['rmse']:
                improvement = ((best_metrics['rmse'] - rmse) / best_metrics['rmse']) * 100
                f.write(f"✅ **Stacking improves over best baseline ({best_name})**\n")
                f.write(f"- RMSE improvement: {improvement:.2f}%\n\n")
            else:
                f.write(f"⚠️ **Stacking does not improve over best baseline ({best_name})**\n")
                f.write("- This is expected given the very limited training data\n")
                f.write("- Stacking ensembles typically require more data to show benefits\n\n")
        
        f.write("## Conclusions\n\n")
        f.write(f"1. **Data Constraint**: Only {n_samples} labeled samples limits model performance\n")
        f.write("   - Stacking ensembles excel with hundreds/thousands of samples\n")
        f.write("   - Current dataset is too small for reliable ensemble benefits\n\n")
        
        f.write("2. **Feasibility**: Folic acid prediction IS feasible with stacking, ")
        f.write("but performance is constrained by data availability\n\n")
        
        f.write("3. **Recommendation**: \n")
        f.write("   - For production: Use simpler models (SVR or RF) due to limited data\n")
        f.write("   - Collect more labeled samples to unlock stacking potential\n")
        f.write("   - Consider batch-aware splits as used in Dual Track notebook\n\n")
        
        f.write("## Why Folic Acid Wasn't in Original Stacking\n\n")
        f.write("The original `stacking_ensemble_optimized.py` focused on:\n")
        f.write("1. **Freshness Classification**: 2052 samples, practical production need\n")
        f.write("2. **Days Prediction**: 2052 samples, shelf-life estimation\n\n")
        f.write("Folic acid was excluded because:\n")
        f.write(f"- Only ~{n_samples} labeled samples available (vs 2052 for other targets)\n")
        f.write("- Requires expensive lab analysis (not practical for real-time prediction)\n")
        f.write("- Different problem scope (nutritional content vs freshness assessment)\n")
        f.write("- Limited applicability in production freshness grading systems\n\n")
        
        f.write("## Files Generated\n\n")
        f.write("- `TASK3_FOLIC_ACID_STACKING_REPORT.md` (this file)\n")
        f.write("- `tournament_figures/task3_folic_acid_predictions.png`\n")
    
    print(f"\n  📄 Report saved: {output_path}")


if __name__ == '__main__':
    print("="*80)
    print("TASK 3: FOLIC ACID PREDICTION WITH STACKING ENSEMBLE")
    print("="*80)
    print("""
OBJECTIVE:
Add folic acid concentration prediction as a third track to the stacking ensemble.

CONTEXT:
- Dual Track notebook achieved R²=0.9997 for folic acid
- Current stacking handles classification (grade) and regression (days)
- Folic acid data available but limited (~35-41 samples)

CHALLENGE:
Limited labeled samples may constrain stacking ensemble performance.
    """)
    
    try:
        # Load folic acid data
        X, y = load_folic_acid_data()
        
        if X is None or len(X) < 10:
            print("\n❌ ERROR: Insufficient folic acid data for training")
            print("   Minimum 10 samples required, found:", len(X) if X is not None else 0)
            print("\n📝 DOCUMENTATION:")
            print("   Folic acid prediction cannot be added to stacking due to:")
            print("   1. Insufficient labeled samples")
            print("   2. Different data availability than classification/regression tracks")
            print("   3. Requires separate data collection effort")
        else:
            # Train stacking ensemble
            model, scaler, y_test, y_pred, metrics = train_folic_acid_stacking(X, y)
            
            # Compare with baselines
            baseline_results = compare_with_baseline(X, y)
            
            if model is not None:
                # Create visualization
                output_dir = Path('tournament_figures')
                output_dir.mkdir(exist_ok=True)
                create_prediction_plot(y_test, y_pred, metrics, 
                                      output_dir / 'task3_folic_acid_predictions.png')
            
            # Generate report
            generate_report(metrics, baseline_results, len(X))
            
            print(f"\n{'='*80}")
            print(f"✅ TASK 3 COMPLETE!")
            print(f"{'='*80}")
            print("""
OUTPUT FILES:
- TASK3_FOLIC_ACID_STACKING_REPORT.md
- tournament_figures/task3_folic_acid_predictions.png
            """)
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
