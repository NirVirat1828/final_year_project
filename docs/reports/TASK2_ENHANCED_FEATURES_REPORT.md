# Task 2: Enhanced Features Tournament Evaluation

## Overview

Comparison of 11 baseline features vs 16+ enhanced features using tournament methodology.

## Feature Sets

### Baseline (11 features)
- Peak_0.85V, Mean, Std_Dev, Energy, Skewness, Kurtosis
- DCT_1, DCT_2, DCT_3, DCT_4, DCT_5

### Enhanced (16+ features)
- All baseline features +
- Peak_Height, Min_Value, Range, Coeff_Variation
- Gradient_Mean, Gradient_Std, Gradient_Max, Entropy
- Interaction features (Energy_Std, Mean_Skewness)
- Polynomial features (Energy_Squared, Mean_Squared, etc.)

## Classification Results

| Algorithm | Baseline Accuracy | Enhanced Accuracy | Improvement |
|-----------|-------------------|-------------------|-------------|
| RandomForest | 0.7610 | 0.7488 | -1.22%  |
| LDA | 0.7780 | 0.7756 | -0.24%  |
| SVM | 0.7683 | 0.7659 | -0.24%  |
| XGBoost | 0.7415 | 0.7512 | +0.98% ✨ |

## Regression Results

| Algorithm | Baseline RMSE | Enhanced RMSE | Improvement |
|-----------|---------------|---------------|-------------|
| RandomForest | 1.5281 | 1.5265 | +0.11% ✨ |
| SVR | 1.5181 | 1.5357 | -1.16%  |
| XGBoost | 1.5289 | 1.5354 | -0.43%  |

## Conclusions

- Classification: 1/4 algorithms improved
- Regression: 1/3 algorithms improved

**Recommendation**: Enhanced features show mixed results. Baseline may be sufficient.
