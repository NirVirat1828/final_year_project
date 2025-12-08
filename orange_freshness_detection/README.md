# Orange Freshness Detection System

## Overview

This module implements a **dual-regression machine learning system** for predicting orange freshness indicators using non-destructive optical sensor data.

### Key Objectives

- **Storage Day Prediction**: Estimate how many days have passed since harvest based on spectral data
- **Folic Acid (µM) Prediction**: Quantify folic acid concentration as a freshness biomarker

---

## System Architecture

```
Raw Sensor Data (15 readings/sample)
        ↓
Feature Extraction (11 engineered features)
  ├─ Savitzky-Golay filtering
  ├─ Voltage peak detection
  ├─ Statistical summaries (mean, std, skewness, kurtosis)
  └─ DCT coefficients (temporal patterns)
        ↓
Feature Scaling (StandardScaler)
        ↓
Feature Selection (RFE → top 5 features)
        ↓
Dual-Track Regressors:
  ├─ Storage Day Model: RandomForest (batches 1-5 train → 6-7 test)
  └─ Folic Acid Model: RandomForest (batches 1-4 train → 5 hold-out)
        ↓
Validation & Explainability (SHAP)
```

---

## Current Performance Metrics

### Storage Day Regression
- **Dataset**: Test on batches 6-7 (unseen)
- **RMSE**: 1.65 days
- **MAE**: 1.14 days
- **R² Score**: 0.837

### Folic Acid Regression
- **Dataset**: Hold-out batch 5
- **RMSE**: 0.79 µM
- **MAE**: 0.73 µM
- **R² Score**: 0.9997

### Top Features (by SHAP)
1. DCT_3
2. DCT_2
3. Mean
4. Energy
5. DCT_1

---

## File Structure

```
orange_freshness_detection/
├── notebooks/
│   ├── Preprocessing_and_Features.ipynb      # Data ingestion & feature engineering
│   ├── Dual_Track_Modelling.ipynb            # Model training (day + folic)
│   ├── Validation_and_Reporting.ipynb        # Evaluation & SHAP
│   └── generate_data.py                      # Synthetic data generation
├── models/
│   ├── model_day_rf.pkl                      # Trained day regression model
│   ├── model_folic_rf.pkl                    # Trained folic acid regression model
│   ├── scaler.pkl                            # StandardScaler for features
│   └── selected_features.pkl                 # RFE-selected feature indices
├── datasets/
│   ├── X_features.csv                        # 50 samples × 11 features
│   ├── y_targets.csv                         # 50 samples × targets (day, folic acid)
│   ├── master_all_batches.csv                # Training data (batches 1-5)
│   ├── key.csv                               # Folic acid labels & metadata
│   ├── synthetic_augmented_data.csv          # Augmented training data
│   └── test_dataset_blind/                   # Blind test set (batches 6-7)
│       ├── batch6_day*.csv                   # 8 samples from batch 6
│       └── batch7_day*.csv                   # 7 samples from batch 7
├── FINAL_REPORT_AND_RECOMMENDATIONS.md       # Production roadmap
├── PROJECT_FIXES_SUMMARY.md                  # Implementation details
├── SYNTHETIC_DATA_STRATEGIES.md              # Data augmentation approaches
└── README.md                                 # This file
```

---

## Usage

### 1. Data Preprocessing
```bash
cd notebooks
jupyter notebook Preprocessing_and_Features.ipynb
# Outputs: X_features.csv (50×11), y_targets.csv (50×2)
```

### 2. Model Training
```bash
jupyter notebook Dual_Track_Modelling.ipynb
# Trains:
#  - Day model on batches 1-5
#  - Folic acid model on batches 1-4
# Saves: .pkl files to models/ folder
```

### 3. Validation & Reporting
```bash
jupyter notebook Validation_and_Reporting.ipynb
# Evaluates:
#  - Day model on batches 6-7 (unseen)
#  - Folic acid model on batch 5 (hold-out)
# Generates: plots, metrics, SHAP explanations
```

---

## Data Splits

### Storage Day Model
| Split | Batches | Samples | Purpose |
|-------|---------|---------|---------|
| Train | 1-5 | 35 | Model learning |
| Test | 6-7 | 15 | Generalization assessment |

### Folic Acid Model
| Split | Batches | Samples | Purpose |
|-------|---------|---------|---------|
| Train | 1-4 | ~28 | Model learning |
| Hold-out | 5 | ~7 | Validation |

---

## Dependencies

```
Python 3.8+
pandas
numpy
scikit-learn
matplotlib
seaborn
shap
jupyter
```

---

## Performance Analysis

### What Works Well ✅
- Proper batch-wise train/test split (no leakage)
- Clean feature extraction pipeline
- Strong day regression on unseen batches (R² 0.837)
- Excellent folic acid fit on hold-out (R² 0.9997)
- Interpretable SHAP explanations

### Current Limitations ⚠️
- Small training set (35-40 samples) limits generalization
- Folic acid validated on single batch only
- High-dimensional raw input (3700+ → 11 features)
- Batch-identity effects may confound freshness signals

---

## Recommendations for Production

### Immediate (Weeks 1-2)
1. **Data Collection**: Target 150-200 samples from 15+ batches
2. **Cross-Validation**: Implement Leave-One-Batch-Out CV
3. **Documentation**: Create model card and deployment guide

### Short-term (Months 1-3)
4. **Feature Refinement**: Validate top 5 SHAP features on larger dataset
5. **Model Optimization**: Tune Random Forest hyperparameters
6. **Uncertainty**: Add prediction confidence intervals

### Medium-term (Months 3-6)
7. **Ensemble Methods**: Benchmark against XGBoost, LightGBM
8. **API Layer**: Deploy inference service
9. **Monitoring**: Set up performance tracking & retraining triggers

---

## Key Learnings

| Issue | Fix | Impact |
|-------|-----|--------|
| Data leakage | Batch-wise split | Realistic metrics |
| Missing test data | Integrated blind set | 43% more samples |
| Ambiguous targets | Dual regression (day + folic) | Clear task definition |
| No explainability | Added SHAP plots | Feature interpretability |

---

## References & Further Reading

- **FINAL_REPORT_AND_RECOMMENDATIONS.md**: Full roadmap for scaling
- **PROJECT_FIXES_SUMMARY.md**: Technical implementation details
- **SYNTHETIC_DATA_STRATEGIES.md**: Data augmentation rationale

---

## Contact & Support

For questions or to report issues, contact the project maintainer.

**Last Updated**: December 8, 2025  
**Status**: Production-Ready Architecture (Data-Limited Performance)
