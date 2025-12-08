# Orange Freshness Project - Comprehensive Fixes Applied

## Summary of Changes (December 8, 2025)

All critical issues are resolved, and the pipeline now supports **dual regression tasks** (storage day + folic acid µM) with batch-aware validation.

---

## 🔴 Critical Issues Fixed

### 1. **Data Leakage Eliminated**
- **Problem**: Random 80/20 split caused data leakage - test samples from same batches as training
- **Fix**: Implemented proper **batch-wise split**
  - **Training**: Batches 1-5 (35 samples)
  - **Testing**: Batches 6-7 (15 samples - completely unseen)
- **Impact**: Now testing on truly unseen data, realistic performance metrics

### 2. **Dataset Expanded (35 → 50 samples)**
- **Problem**: Only using 35 samples from `master_all_batches.csv`, ignoring 15 test files
- **Fix**: Integrated `test_dataset_blind/` folder containing batches 6-7
  - Processed 15 CSV files (batch6_day1.csv through batch7_day14.csv)
  - Aggregated raw sensor data (voltage × current readings)
  - Combined with existing training data
- **Impact**: 43% increase in dataset size

### 3. **Proper Target Variables**
- **Problem**: Targets were ambiguous; folic acid labels were missing from the pipeline
- **Fix**: Targets now explicitly include:
   - **day**: Storage days (0-14 days post-harvest)
   - **folic acid (true_conc_uM)**: Integrated from `key.csv` for batches 1-5
- **Impact**: Dual regression heads (day + folic acid) trained with correct labels

### 4. **Batch-Aware Splits for Each Task**
- **Problem**: Single split pattern did not account for different label availability per task
- **Fix**:
   - **Day model**: Train on batches 1-5, test on batches 6-7
   - **Folic model**: Train on batches 1-4, hold-out batch 5
- **Impact**: No leakage; evaluations aligned with label availability

---

## 📊 Current Model Performance (Batch-Aware)

### Storage Day Regression (Test: batches 6-7)
- **RMSE / MAE / R²**: 1.65 days / 1.14 days / 0.837
- **Interpretation**: Good fit on unseen batches with small-n variance risk

### Folic Acid Regression (Hold-out: batch 5)
- **RMSE / MAE / R²**: 0.79 µM / 0.73 µM / 0.9997
- **Interpretation**: Excellent fit on single hold-out batch; needs more labeled batches to confirm

### Feature Selection
- **Top 5 Features (day model)**: DCT_3, DCT_2, Mean, Energy, DCT_1
- **Method**: Recursive Feature Elimination (RFE) with Random Forest + SHAP validation

---

## 📂 Files Modified

### 1. **Preprocessing_and_Features.ipynb**
**Changes:**
- Ingests `master_all_batches.csv` and all blind test CSVs
- Integrates folic acid labels (`true_conc_uM`) from `key.csv`
- Parses filenames to extract batch/day and keeps batch-wise provenance
- Outputs `X_features.csv` (11 engineered features) and `y_targets.csv` (day + folic acid)

**Results:**
- Total samples: 50 across batches 1-7
- Labels available: day for all, folic acid for batches 1-5
- Clean batch-aware dataset for downstream splits

### 2. **Dual_Track_Modelling.ipynb**
**Changes:**
- Builds two RandomForestRegressor models:
   - **Day model**: train batches 1-5; test batches 6-7
   - **Folic model**: train batches 1-4; hold-out batch 5
- Saves artifacts: `model_day_rf.pkl`, `model_folic_rf.pkl`, `scaler.pkl`, `selected_features.pkl`
- Logs per-task metrics (RMSE/MAE/R²) with batch-wise splits

**Results:**
- Day model generalizes to unseen batches 6-7 with RMSE 1.65 days, R² 0.837
- Folic model fits hold-out batch 5 with RMSE 0.79 µM, R² 0.9997
- Both tasks remain data-limited; structure ready for more data

### 3. **Validation_and_Reporting.ipynb**
**Changes:**
- Adds batch-aware evaluation for both tasks (day, folic)
- Reports RMSE/MAE/R² for day on batches 6-7 and folic on batch 5
- Plots refreshed (scatter/regression diagnostics) and SHAP for day model

**Results:**
- Day model: RMSE 1.65 days, MAE 1.14 days, R² 0.837 on batches 6-7
- Folic model: RMSE 0.79 µM, MAE 0.73 µM, R² 0.9997 on batch 5
- SHAP confirms top features (DCT_3, DCT_2, Mean, Energy, DCT_1)

---

## 🎯 Realistic Performance Benchmarks

### What's Normal for This Dataset Size?
With **only 35 training samples across 5 batches** for day prediction and even fewer for folic acid:
- ✅ **Expected**: High variance across batches; results swing with each split
- ✅ **Expected**: Strong metrics on a single hold-out can be optimistic (small-n)
- ❌ **NOT Expected**: Stable generalization claims without more batches

### For Good Performance, You Would Need:
- **Minimum**: 100-150 samples from 10+ batches
- **Better**: 300-500 samples from 15-20 batches
- **Best**: 1000+ samples with varied storage conditions

---

## 🚀 Next Steps (Prioritized)

### Immediate (High Priority)
1. **Collect More Data**
   - Aim for 200+ samples
   - Include more batches with varied conditions
   - Record environmental factors (temperature, humidity)

2. **Define Better Targets**
   - Add actual folic acid concentration measurements
   - Create freshness labels (Fresh/Medium/Spoiled) based on objective criteria
   - Include other quality indicators (pH, sugar content, etc.)

3. **Feature Engineering**
   - Add derivative features (rate of change over days)
   - Include batch-agnostic features
   - Experiment with wavelets, Fourier transforms

### Short-term (Medium Priority)
4. **Cross-Validation**
   - Implement Leave-One-Batch-Out cross-validation
   - Report confidence intervals

5. **Model Improvements**
   - Try deep learning on raw sensor data
   - Implement ensemble methods
   - Add uncertainty quantification

6. **Data Augmentation**
   - Synthetic data generation (with caution)
   - Transfer learning from related datasets

### Long-term (Research Direction)
7. **Multi-modal Learning**
   - Combine sensor data with images
   - Add temporal sequence modeling

8. **Deployment Considerations**
   - Build calibration protocol
   - Account for sensor drift
   - Create real-time prediction API

---

## 📈 Key Learnings

### What Was Wrong
1. ❌ Random split violated temporal/batch structure
2. ❌ Unused test data sitting in folder
3. ❌ Misleading performance metrics (due to data leakage)
4. ❌ Target variable confusion (day vs. chemical concentration)

### What's Now Correct
1. ✅ Proper batch-wise train/test split
2. ✅ All available data utilized (50 samples)
3. ✅ Realistic performance evaluation
4. ✅ Clear documentation of limitations
5. ✅ Complete end-to-end pipeline working

---

## 📝 How to Use Fixed Pipeline

```bash
# Step 1: Run preprocessing (processes all 50 samples)
# Execute all cells in: Preprocessing_and_Features.ipynb
# Output: X_features.csv (50×11), y_targets.csv (day + folic acid)

# Step 2: Train models (batch-aware)
# Execute all cells in: Dual_Track_Modelling.ipynb
# Output: model_day_rf.pkl, model_folic_rf.pkl, scaler.pkl, selected_features.pkl

# Step 3: Validate on held-out batches
# Execute all cells in: Validation_and_Reporting.ipynb
# Output: Day metrics on batches 6-7, folic metrics on batch 5, regression plots, SHAP plot (day)
```

---

## 💡 Final Thoughts

The **current results are directionally strong but data-limited**:
- Day model shows good fit on batches 6-7 (RMSE 1.65d) but needs more batches to confirm
- Folic model is excellent on batch 5 hold-out (RMSE 0.79 µM) yet optimism risk remains with n=1 batch
- High-dimensional raw input (3700+ → 11 engineered) still benefits most from more labeled data

**This is the realistic baseline** to iterate from; earlier inflated metrics were leakage-driven and are superseded by the batch-aware results above.

---

## ✅ All Systems Operational

- ✅ Data pipeline: Working
- ✅ Feature extraction: Working  
- ✅ Model training: Working
- ✅ Validation: Working
- ✅ Proper evaluation: Working

**The project is now scientifically sound and ready for iterative improvement.**
