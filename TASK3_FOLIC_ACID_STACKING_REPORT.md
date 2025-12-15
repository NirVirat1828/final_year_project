# Task 3: Folic Acid Prediction with Stacking Ensemble

## Overview

Extended the stacking ensemble to predict folic acid concentration (µM) in addition to freshness grade classification and days prediction.

## Dataset

- Total samples with folic acid labels: 35
- Features: 11 engineered features from optical sensor data
- Target: Folic acid concentration (µM)
- Source: key.csv matched with X_features.csv

## Data Limitation Challenge

⚠️ **Limited Training Data**: Only 35 samples with folic acid labels.

This is significantly smaller than:
- Freshness classification: 2052 samples
- Days prediction: 2052 samples

With such limited data, stacking ensembles may not show the same performance gains as they do with larger datasets.

## Model Architecture

**Stacking Ensemble:**
- Base Learner 1: Support Vector Regressor (RBF kernel)
- Base Learner 2: Random Forest Regressor
- Meta-Learner: Ridge Regression

## Results

### Stacking Ensemble Performance

- **RMSE**: 5.1733 µM
- **R²**: 0.9913
- **MAE**: 4.2404 µM

### Baseline Models Comparison

| Model | RMSE (µM) | R² | MAE (µM) |
|-------|-----------|----|---------|
| SVR | 16.7423 | 0.9085 | 12.8598 |
| RandomForest | 4.2981 | 0.9940 | 3.5667 |
| **Stacking** | **5.1733** | **0.9913** | **4.2404** |

## Comparison with Dual Track Results

The Dual Track notebook achieved:
- **R² = 0.9997** for folic acid prediction

This much higher performance was likely due to:
1. Different data split or validation strategy
2. Optimized hyperparameters specifically for folic acid
3. Potentially different feature engineering
4. Temporal batch-based splits (training on batches 1-4, testing on batch 5)

## Analysis

⚠️ **Stacking does not improve over best baseline (RandomForest)**
- This is expected given the very limited training data
- Stacking ensembles typically require more data to show benefits

## Conclusions

1. **Data Constraint**: Only 35 labeled samples limits model performance
   - Stacking ensembles excel with hundreds/thousands of samples
   - Current dataset is too small for reliable ensemble benefits

2. **Feasibility**: Folic acid prediction IS feasible with stacking, but performance is constrained by data availability

3. **Recommendation**: 
   - For production: Use simpler models (SVR or RF) due to limited data
   - Collect more labeled samples to unlock stacking potential
   - Consider batch-aware splits as used in Dual Track notebook

## Why Folic Acid Wasn't in Original Stacking

The original `stacking_ensemble_optimized.py` focused on:
1. **Freshness Classification**: 2052 samples, practical production need
2. **Days Prediction**: 2052 samples, shelf-life estimation

Folic acid was excluded because:
- Only ~35 labeled samples available (vs 2052 for other targets)
- Requires expensive lab analysis (not practical for real-time prediction)
- Different problem scope (nutritional content vs freshness assessment)
- Limited applicability in production freshness grading systems

## Files Generated

- `TASK3_FOLIC_ACID_STACKING_REPORT.md` (this file)
- `tournament_figures/task3_folic_acid_predictions.png`
