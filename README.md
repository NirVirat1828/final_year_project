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
        # Orange Freshness Detection System

        Dual-track ML system for non-destructive orange freshness assessment, now upgraded with a richer feature set (11 → 26) for stronger grade classification confidence.

        ---
        ## Highlights (Current State)
        - **Feature uplift:** Added 15 new amplitude/temporal/complexity/interaction features; enhanced dataset saved as `datasets/X_features_enhanced.csv`.
        - **Tracks:**
          - **Track A (Classification):** Freshness grade A/B/C/D (stacking ensemble). Expected confidence after retrain: **65–75%+**.
          - **Track B (Regression):** Storage day + folic acid µM (RandomForest regressors; legacy performance retained).
        - **Artifacts:** Inference scripts, API, dashboard, presentation assets, and enhanced preprocessing (`track_a_preprocessing_v2.py`).

        ---
        ## Quickstart
        1) **Environment**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        pip install -U numpy pandas scikit-learn joblib matplotlib seaborn shap jupyter
        ```

        2) **Use enhanced features (already generated)**
        ```bash
        ls datasets/X_features_enhanced.csv  # 2050 × 26 features
        # If needed, regenerate (run from project root):
        python -m src.preprocessing.generate_enhanced_features
        ```

        3) **Retrain Track A (classification)**
        - Load `datasets/X_features_enhanced.csv` + `datasets/y_targets.csv`.
        - Scale → RFE (select ~5 of 26) → train stacking ensemble (RF + GB + SVM, meta RF).
        - Save to `models/track_a_v2/`: `scaler.pkl`, `rfe_selector.pkl`, `stacking_model.pkl`, `metadata.json`.

        4) **Run inference demo**
        ```bash
        source venv/bin/activate
        python -m src.inference.track_a_inference
        ```

        5) **Serve / visualize**
        ```bash
        python -m src.inference.inference_api           # REST API
        python -m src.visualization.presentation_dashboard  # Streamlit dashboard
        ```

        ---
        ## Data & Splits (legacy baseline)
        - **Features (legacy):** `datasets/X_features.csv` — 11 engineered features
        - **Features (enhanced):** `datasets/X_features_enhanced.csv` — 26 engineered features
        - **Targets:** `datasets/y_targets.csv` (batch, day, true_conc_uM)
        - **Blind test CSVs:** `datasets/test_dataset_blind/` (batches 6–7)

        **Baseline splits (regression):**
        - Train: batches 1–5 (35 samples) | Test: batches 6–7 (15 samples)
        - Folic acid: train batches 1–4, hold-out batch 5 (~7 samples)

        **Classification:** stratified 80/20 split over 2050 samples (legacy); retrain recommended with enhanced features.

        ---
        ## Repository Map
        ```
        notebooks/                # Preprocessing, modelling, validation notebooks
        models/                   # Saved models (legacy Track A/B)
        datasets/                 # Features/targets + blind test CSVs + enhanced features
        src/preprocessing/track_a_preprocessing_v2.py  # Enhanced feature extractor (26 features)
        src/inference/track_a_inference.py            # Inference demo for Track A
        src/training/track_a_train_classifier.py      # Training pipeline (legacy)
        src/preprocessing/generate_enhanced_features.py # Builds enhanced feature CSV
        src/inference/inference_api.py, src/visualization/presentation_dashboard.py  # Serving & dashboard
        docs/reports/              # Project reports and writeups (moved from root)
        ```

        ---
        ## Current Performance (legacy baseline)
        - **Track B (regression):** R² day = 0.837, MAE 1.14 days; folic acid R² = 0.9997 (hold-out batch 5).
        - **Track A (classification):** Legacy accuracy ~75.85% on stratified split; confidence low (~44% on sample). Expected uplift after retraining with enhanced features.

        **Next measurement needed:** Re-evaluate after retraining with `X_features_enhanced.csv` and record updated metrics (update presentation assets accordingly).

        ---
        ## Testing & Validation Checklist
        - [ ] Retrain Track A using enhanced features
        - [ ] Evaluate on held-out batches (6–7) and record accuracy/F1/confusion matrix
        - [ ] Calibrate probabilities (Platt / isotonic) for production confidence
        - [ ] Refresh presentation asset captions once new metrics are available

        ---
        ## Notes
        - Clean-up performed: removed `.DS_Store`, `__pycache__/`.
        - Keep `venv/` local-only (do not commit); already ignored by `.gitignore`.

        ---
        ## Support
| Train | 1-5 | 35 | Model learning |
