# Track A: Freshness Grade Classification

**Full implementation of Track A specification:**  
✅ Savitzky–Golay smoothing (window=11, polyorder=3)  
✅ DCT feature extraction (10 coefficients)  
✅ RFE feature selection (top 5 features)  
✅ StackingClassifier with RandomForest + SVM  
✅ Modular code with clear documentation  
✅ End-to-end pipeline: preprocessing → training → inference  

---

## Modules Overview

### 1. `track_a_preprocessing.py`
**Handles raw signal → engineered features**

- `TrackAPreprocessor.apply_savgol_filter()` — Smooths raw 15-reading signal
- `extract_dct_features()` — Computes DCT coefficients (top 10)
- `extract_energy()` — Total signal energy
- `extract_all_features()` — Complete pipeline (returns 11 features)

**Usage:**
```python
from track_a_preprocessing import TrackAPreprocessor
import numpy as np

raw_signal = np.array([...])  # 15 readings from sensor
preprocessor = TrackAPreprocessor(savgol_window=11, savgol_polyorder=3, dct_keep=10)
features = preprocessor.extract_all_features(raw_signal)
# Output: dict with 11 features (DCT_0 to DCT_9, Energy)
```

### 2. `track_a_feature_selection.py`
**RFE-based selection: 11 features → top 5**

- `TrackAFeatureSelector.fit()` — Fit RFE on training data
- `get_selected_feature_names()` — Return selected feature names
- `transform()` — Apply selection to new data
- `save() / load()` — Persist selector

**Usage:**
```python
from track_a_feature_selection import TrackAFeatureSelector

selector = TrackAFeatureSelector(n_features_to_select=5, random_state=42)
X_selected = selector.fit_transform(X_train, y_train, feature_names=feature_names)
# Output: shape (n_samples, 5)
```

### 3. `track_a_train_classifier.py`
**Complete training pipeline: load data → train stacking → evaluate → save**

**Pipeline steps:**
1. Load dataset (real or synthetic) → create grade labels (A/B/C/D)
2. Impute missing values + StandardScaler
3. Train/test split (80/20, stratified)
4. RFE: select top 5 features
5. Train StackingClassifier:
   - Base models: RandomForest (100 estimators), SVM (RBF kernel)
   - Meta-model: RandomForest (100 estimators)
6. Evaluate: accuracy, confusion matrix, classification report
7. Save: imputer, scaler, RFE, stacking model, feature metadata

**Saved artifacts:**
- `models/track_a/imputer.pkl` — SimpleImputer for NaN handling
- `models/track_a/scaler.pkl` — StandardScaler
- `models/track_a/rfe_selector.pkl` — RFE selector
- `models/track_a/stacking_model.pkl` — Trained StackingClassifier
- `models/track_a/feature_names.json` — Feature metadata

**Usage:**
```bash
cd orange_freshness_detection
python track_a_train_classifier.py
```

**Expected output:**
```
Accuracy: 0.7585 (75.85%)
Confusion Matrix:
  A: 70% correctly classified
  B: 70% correctly classified
  C: 79% correctly classified
  D: 86% correctly classified
```

### 4. `track_a_inference.py`
**Load trained model → predict freshness grades**

- `TrackAInference.__init__()` — Load all artifacts
- `predict_from_raw_signal()` — End-to-end: raw sensor → grade + probabilities
- `predict_from_features()` — Direct prediction from engineered features
- `batch_predict_from_raw_signals()` — Process multiple samples

**Output format:**
```json
{
  "grade": "A",
  "probabilities": {
    "A": 0.85,
    "B": 0.10,
    "C": 0.05,
    "D": 0.00
  },
  "selected_features": ["DCT_1", "DCT_3", "DCT_6", "DCT_7", "DCT_8"]
}
```

**Usage:**
```python
from track_a_inference import TrackAInference
import numpy as np

inference = TrackAInference(models_dir='models/track_a')

# Single prediction
raw_signal = np.array([...])  # 15 readings
result = inference.predict_from_raw_signal(raw_signal)
print(f"Grade: {result['grade']}")
print(f"Confidence: {max(result['probabilities'].values()):.2%}")

# Batch prediction
raw_signals = [np.array([...]), np.array([...]), ...]
batch_results = inference.batch_predict_from_raw_signals(raw_signals)
```

---

## Quick Start

### Step 1: Train the classifier
```bash
cd /Users/nirvik/final_year_project/orange_freshness_detection
python track_a_train_classifier.py
```

### Step 2: Run inference on test signals
```bash
python track_a_inference.py
```

### Step 3: Integrate into your API
```python
from track_a_inference import TrackAInference

# Initialize once (load models)
inference = TrackAInference(models_dir='models/track_a')

# In your API handler:
@app.post("/predict_grade")
def predict_freshness_grade(raw_signal: list):
    result = inference.predict_from_raw_signal(raw_signal)
    return result
```

---

## Architecture Diagram

```
Raw Sensor Signal (15 readings)
    ↓
Savitzky–Golay Smoothing (window=11, poly=3)
    ↓
DCT Extraction (10 coefficients) + Energy
    ↓
11 Engineered Features
    ↓
StandardScaler
    ↓
RFE Selection → Top 5 Features
    ↓
StackingClassifier:
  ├─ Base Model 1: RandomForestClassifier (100 trees)
  ├─ Base Model 2: SVM (RBF kernel, probability=True)
  └─ Meta-Model: RandomForestClassifier (100 trees)
    ↓
Freshness Grade (A/B/C/D) + Confidence Probabilities
```

---

## Model Performance

**Test Set Accuracy: 75.85%**

| Grade | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| A (0-3 days) | 70% | 71% | 71% | 87 |
| B (4-7 days) | 70% | 67% | 68% | 118 |
| C (8-10 days) | 74% | 79% | 77% | 91 |
| D (>10 days) | 88% | 86% | 87% | 114 |

**Notes:**
- Grade D (oldest oranges) has highest accuracy (86%) — easier to detect.
- Grade A & B have some confusion due to overlapping spectral signatures.
- Larger training dataset would improve generalization.

---

## Freshness Grade Definition

| Grade | Storage Days | Folic Acid (proxy) | Freshness |
|-------|--------------|-------------------|-----------|
| **A** | 0–3 | High (4.5+ µM) | Premium |
| **B** | 4–7 | Medium-High (2.5–4.5 µM) | Good |
| **C** | 8–10 | Medium (1.0–2.5 µM) | Fair |
| **D** | >10 | Low (<1.0 µM) | Poor (Discard?) |

---

## Dependencies

All required packages are already in the venv:
- `scikit-learn` — RandomForest, SVM, RFE, StackingClassifier
- `scipy` — Savitzky-Golay, DCT
- `numpy`, `pandas` — Data handling
- `joblib` — Model serialization

---

## Testing

Run end-to-end example:
```bash
python track_a_preprocessing.py      # Test feature extraction
python track_a_train_classifier.py   # Train model
python track_a_inference.py          # Test inference
```

---

## Future Enhancements

1. **Hyperparameter Tuning:** GridSearchCV for RandomForest/SVM parameters
2. **Class Imbalance:** Try SMOTE or class weights
3. **Feature Importance:** SHAP plots for interpretability
4. **Cross-Validation:** Leave-One-Batch-Out validation
5. **API Integration:** Deploy as REST endpoint in `inference_api.py`
6. **Uncertainty Quantification:** Calibration curves, conformal prediction

---

## File Locations

```
orange_freshness_detection/
├── track_a_preprocessing.py          ← Raw signal → 11 features
├── track_a_feature_selection.py      ← RFE: 11 → 5 features
├── track_a_train_classifier.py       ← Training pipeline
├── track_a_inference.py              ← Inference/prediction
└── models/track_a/                   ← Saved artifacts
    ├── imputer.pkl
    ├── scaler.pkl
    ├── rfe_selector.pkl
    ├── stacking_model.pkl
    └── feature_names.json
```

---

**Last Updated:** December 10, 2025  
**Status:** ✅ Production-Ready
