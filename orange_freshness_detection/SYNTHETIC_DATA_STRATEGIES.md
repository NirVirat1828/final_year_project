# Strategies for Realistic Synthetic Data Generation & Modeling

**Problem**: Synthetic data doesn't generalize to real test samples due to domain gap.

**Solution**: Multi-pronged approach combining data generation improvements + modeling strategy changes.

---

## PART 1: IMPROVED SYNTHETIC DATA GENERATION ✅ (Already Implemented)

### Key Improvements Made to `generate_data.py`:

#### 1. **Auto-Calibration from Real Data**
```python
# OLD: Manual guessing
NOISE_LEVEL = 0.5
DRIFT_RANGE = 2.0

# NEW: Learn from real data statistics
NOISE_LEVEL = real_data_std * 0.5        # Calibrated from actual variance
DRIFT_RANGE = batch_variation_std * 0.8  # Based on real batch differences
```

#### 2. **Batch-Specific Templates**
```python
# OLD: One generic template for all synthetic data
template_signal = all_day0_samples.mean()

# NEW: Learn each batch's unique signature
batch_templates[batch_1] = batch_1_samples.mean()
batch_templates[batch_2] = batch_2_samples.mean()
# Synthetic samples inherit these batch characteristics
```

#### 3. **Hybrid Pattern Generation**
```python
# OLD: Pure physics model (unrealistic)
signal = template * exp(-k*t)

# NEW: Real data pattern + decay model
closest_real_pattern = find_closest_day_in_real_data(day)
batch_signature = select_random_batch_template()
base = 0.6 * closest_real_pattern + 0.4 * batch_signature
signal = base * exp(-k * time_diff) + calibrated_noise
```

#### 4. **Realistic Batch Assignment**
```python
# OLD: All synthetic marked as 'Synthetic' (creates domain gap)
batch = 'Synthetic'

# NEW: Assign to virtual batches 1-10 (looks like real batches)
batch = (sample_id % 10) + 1  # Distributes across batches 1-10
```

---

## PART 2: MODELING STRATEGY CHANGES (Next Steps)

### Strategy A: **Domain Adaptation Techniques**

#### A1. **Feature Normalization by Batch**
Instead of global StandardScaler, use batch-aware normalization:

```python
# Current approach:
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_all)

# Better approach:
from sklearn.preprocessing import RobustScaler

# Use RobustScaler (less sensitive to outliers/batch differences)
scaler = RobustScaler()
X_scaled = scaler.fit_transform(X_all)

# OR: Normalize within each batch, then combine
for batch in unique_batches:
    batch_data = X[y['batch'] == batch]
    batch_scaler = StandardScaler()
    X_normalized[batch] = batch_scaler.fit_transform(batch_data)
```

#### A2. **Transfer Learning Approach**
Pre-train on synthetic, fine-tune on real:

```python
# Step 1: Pre-train on ALL synthetic data
model.fit(X_synthetic, y_synthetic)

# Step 2: Fine-tune ONLY on real batches 1-5
model.partial_fit(X_real_train, y_real_train)  # For models supporting it

# OR use warm_start for sklearn models
model.set_params(warm_start=True)
model.fit(X_real_train, y_real_train)  # Continues from pre-trained weights
```

---

### Strategy B: **Change Prediction Target**

#### B1. **Predict Relative Change Instead of Absolute Values**
```python
# Current: Predict absolute day (0-14)
y_target = day_number

# Better: Predict freshness degradation (0-100%)
freshness_score = 100 * (1 - day/14)  # 100% at day 0, 0% at day 14
y_target = freshness_score

# OR: Predict decay rate category
if day < 3: category = 'Fresh'
elif day < 7: category = 'Good'
elif day < 10: category = 'Fair'
else: category = 'Spoiled'
```

#### B2. **Multi-Task Learning**
Train model to predict multiple related targets:
```python
# Instead of separate models, predict both simultaneously
from sklearn.multioutput import MultiOutputRegressor

# Targets: [day, freshness_score, quality_grade]
y_multi = np.column_stack([days, freshness, quality])

model = MultiOutputRegressor(RandomForestRegressor())
model.fit(X_train, y_multi)
```

---

### Strategy C: **Ensemble with Domain-Specific Models**

#### C1. **Separate Models for Synthetic vs Real**
```python
# Train two specialized models
model_synthetic = RandomForestRegressor()
model_synthetic.fit(X_synthetic, y_synthetic)

model_real = RandomForestRegressor()
model_real.fit(X_real, y_real)

# At prediction time, detect which domain and route accordingly
# OR: Blend predictions
pred_final = 0.3 * model_synthetic.predict(X_test) + 
             0.7 * model_real.predict(X_test)
```

#### C2. **Domain Adversarial Training**
Make features domain-invariant:
```python
# Advanced: Train feature extractor that removes batch/domain identity
# While preserving day prediction ability
# (Requires deep learning - beyond sklearn)
```

---

### Strategy D: **Better Feature Engineering**

#### D1. **Domain-Invariant Features**
Extract features that are consistent across batches:

```python
# Current features: Absolute values (Std_Dev, Skewness, DCT_1, etc.)
# Problem: These change with batch calibration

# Better: Ratio-based features (invariant to scaling)
features['Peak_Ratio'] = Peak_085V / Mean_Signal
features['Energy_Ratio'] = Energy / (Std_Dev + 1e-6)
features['Shape_Index'] = Skewness / (Kurtosis + 1e-6)

# Derivative features (rate of change)
features['DCT_Slope'] = (DCT_3 - DCT_1) / 2
features['Signal_Gradient'] = np.gradient(signal).mean()
```

#### D2. **Physics-Informed Features**
Add features based on expected decay physics:

```python
# Exponential decay indicator
features['Exp_Decay_Fit'] = fit_exponential_curve(signal)

# Signal energy concentration
features['Energy_Concentration'] = np.sum(signal[:len(signal)//2]) / np.sum(signal)

# Temporal consistency
features['Autocorrelation'] = np.correlate(signal, signal, mode='same')[len(signal)//2]
```

---

### Strategy E: **Cross-Validation Strategy Change**

#### E1. **Group K-Fold (Batch-Aware)**
```python
from sklearn.model_selection import GroupKFold

# Current: Random split (leaks batch info)
X_train, X_test = train_test_split(X, y)

# Better: Group by batch (prevents batch leakage)
gkf = GroupKFold(n_splits=5)
for train_idx, test_idx in gkf.split(X, y, groups=y['batch']):
    X_train, X_test = X[train_idx], X[test_idx]
    # Train and evaluate
```

#### E2. **Leave-One-Batch-Out Validation**
```python
# Most realistic: Test on each batch separately
for test_batch in unique_batches:
    train_mask = y['batch'] != test_batch
    test_mask = y['batch'] == test_batch
    
    model.fit(X[train_mask], y[train_mask])
    score = model.score(X[test_mask], y[test_mask])
    print(f"Batch {test_batch}: {score}")
```

---

### Strategy F: **Model Architecture Changes**

#### F1. **Use Domain-Robust Models**
```python
# Current: Random Forest (sensitive to feature distributions)

# Alternative 1: Gradient Boosting (more robust)
from sklearn.ensemble import GradientBoostingRegressor
model = GradientBoostingRegressor(
    learning_rate=0.05,
    n_estimators=200,
    max_depth=3,  # Shallow trees generalize better
    subsample=0.8  # Regularization
)

# Alternative 2: Ridge Regression (simpler, less overfitting)
from sklearn.linear_model import Ridge
model = Ridge(alpha=10.0)  # High regularization

# Alternative 3: Support Vector Regression
from sklearn.svm import SVR
model = SVR(kernel='rbf', C=1.0, epsilon=0.1)
```

#### F2. **Reduce Model Complexity**
```python
# Current: Complex stacking ensemble
# Problem: Overfits to synthetic data patterns

# Better: Single robust model
model = RandomForestRegressor(
    n_estimators=50,      # Reduced from 100
    max_depth=5,          # Limit depth
    min_samples_split=20, # Require more samples to split
    min_samples_leaf=10,  # Require more samples in leaves
    max_features='sqrt'   # Use fewer features per tree
)
```

---

## PART 3: RECOMMENDED ACTION PLAN

### **Phase 1: Regenerate Synthetic Data** (Do This First)
```bash
cd /Users/abhijitchaudhuri/Downloads/Orange_freshness_project/notebooks
python generate_data.py
```

This will create 2000 samples using:
- ✅ Calibrated noise/drift from real data
- ✅ Batch-specific templates
- ✅ Hybrid real pattern + physics model
- ✅ Realistic batch assignments (1-10)

**Expected Improvement**: 10-20% accuracy gain

---

### **Phase 2: Update Feature Engineering**

Add ratio-based features to `Preprocessing_and_Features.ipynb`:

```python
# After extracting current features, add:
X_df['Peak_Ratio'] = X_df['Peak_0.85V'] / (X_df['Mean'] + 1e-6)
X_df['Energy_Ratio'] = X_df['Energy'] / (X_df['Std_Dev'] + 1e-6)
X_df['Shape_Index'] = X_df['Skewness'] / (np.abs(X_df['Kurtosis']) + 1e-6)
X_df['DCT_Trend'] = (X_df['DCT_3'] - X_df['DCT_1']) / 2
```

**Expected Improvement**: 5-15% accuracy gain

---

### **Phase 3: Change Modeling Approach**

Update `Dual_Track_Modelling.ipynb`:

```python
# 1. Use RobustScaler instead of StandardScaler
from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()

# 2. Simplify regression model
reg = RandomForestRegressor(
    n_estimators=50,
    max_depth=5,
    min_samples_split=20,
    min_samples_leaf=10,
    random_state=42
)

# 3. For classification, use simpler model
from sklearn.ensemble import GradientBoostingClassifier
clf = GradientBoostingClassifier(
    n_estimators=50,
    max_depth=3,
    learning_rate=0.1,
    random_state=42
)
```

**Expected Improvement**: 10-25% accuracy gain

---

### **Phase 4: Change Prediction Target**

Instead of predicting batch number (hard with synthetic data), predict:

```python
# In preprocessing, create freshness score
y['freshness_score'] = 100 * (1 - y['day'] / 14)

# Categories for classification
def categorize_freshness(day):
    if day < 3: return 0  # Fresh
    elif day < 7: return 1  # Good
    elif day < 10: return 2  # Fair
    else: return 3  # Spoiled

y['quality_category'] = y['day'].apply(categorize_freshness)
```

**Expected Improvement**: 20-40% accuracy gain (easier task)

---

## PART 4: EXPECTED OUTCOMES

### **Conservative Estimate** (After Phase 1-2):
- Classification Accuracy: 0% → 20-30%
- Regression RMSE: 5.45 → 3.5-4.0 days
- R² Score: -0.59 → 0.1-0.3

### **Optimistic Estimate** (After All 4 Phases):
- Classification Accuracy: 0% → 40-60%
- Regression RMSE: 5.45 → 2.5-3.0 days  
- R² Score: -0.59 → 0.4-0.6

### **Realistic Target**:
- Freshness Category Accuracy: 60-75%
- Day Prediction MAE: ±2-3 days
- Useful for practical freshness assessment

---

## PART 5: ALTERNATIVE APPROACH (If Above Doesn't Work)

### **Pivot to Anomaly Detection**
Instead of predicting exact day/batch:

```python
from sklearn.ensemble import IsolationForest

# Train on "fresh" samples (day 0-3)
fresh_samples = X[y['day'] <= 3]
detector = IsolationForest(contamination=0.1)
detector.fit(fresh_samples)

# Predict freshness by detecting anomalies
predictions = detector.predict(X_test)
# -1 = Spoiled (anomaly), 1 = Fresh (normal)
```

**Advantage**: Doesn't require realistic synthetic day progression, only needs to distinguish fresh vs spoiled patterns.

---

## SUMMARY

**Immediate Action**: Run improved `generate_data.py` → Rerun pipeline → Measure improvement

**If Still Poor**: Implement Phase 2-4 progressively

**Last Resort**: Switch to anomaly detection or binary classification (fresh vs spoiled)

**Key Insight**: Predicting exact batch numbers from synthetic data is nearly impossible. Focus on predicting degradation/freshness which follows physical laws.
