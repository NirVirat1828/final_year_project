# Tournament Director - Quick Reference Guide

## 🎯 One-Liner Commands

### Installation
```bash
bash install_tournament.sh
```

### Run Demo (No dependencies needed)
```bash
python3 tournament_director_demo.py
```

### Run Full Tournament
```bash
source venv/bin/activate
python3 tournament_director.py
```

---

## 📊 Output Files

| File | Description | Location |
|------|-------------|----------|
| **results_comparison.csv** | Full results table with all metrics | Root directory |
| **pca_scatter_comparison.png** | 2D PCA visualization | tournament_figures/ |
| **confusion_matrix_*.png** | Classification confusion matrices | tournament_figures/ |
| **signal_comparison.png** | Raw vs smoothed signal | tournament_figures/ |
| **parity_plot_*.png** | Regression predictions | tournament_figures/ |
| **classification_performance.png** | Bar chart comparison | tournament_figures/ |
| **regression_performance.png** | Bar chart comparison | tournament_figures/ |

---

## 🏆 Algorithms Tested

### Track A: Classification (9 Models)
1. **LDA** - Linear Discriminant Analysis (Baseline)
2. **SVM** - Support Vector Machine (RBF kernel)
3. **Random Forest** - Ensemble trees
4. **XGBoost** - Gradient boosting
5. **1D-CNN** - Deep learning

### Track B: Regression (4 Models)
1. **PLS** - Partial Least Squares (Industry standard)
2. **SVR** - Support Vector Regressor
3. **Random Forest** - Ensemble trees
4. **XGBoost** - Gradient boosting

---

## 🔧 Preprocessing Methods

### Method A: Raw
```
Raw Features → StandardScaler → Model
```

### Method B: Advanced
```
Raw Features → Savitzky-Golay Filter → DCT → StandardScaler → RFE → Model
```

**Parameters:**
- SavGol window: 11
- SavGol polynomial: 3
- DCT coefficients: 5
- RFE features: 5

---

## 📈 Metrics Cheatsheet

### Classification
- **Accuracy**: % of correct predictions (0-1, higher better)
- **F1-Score**: Balance of precision & recall (0-1, higher better)

### Regression
- **RMSE**: Average prediction error in days (0-∞, lower better)
- **R²**: Variance explained (0-1, higher better)

---

## 🔍 How to Interpret Results

### 1. Preprocessing Comparison
Look at the same algorithm with both preprocessing methods:
```
RandomForest + Raw         → Accuracy: 0.72
RandomForest + Advanced    → Accuracy: 0.79
```
**Conclusion:** Advanced preprocessing adds +7% accuracy

### 2. Algorithm Ranking
Sort by metric within each preprocessing method:
```
Classification (Advanced preprocessing):
1. RandomForest: 0.79
2. XGBoost: 0.76
3. SVM: 0.74
...
```

### 3. Overfitting Check
- Large gap between train/test → overfitting
- R² > 0.99 → possible data leakage

---

## 🛠️ Customization Quick Guide

### Change Train-Test Split
```python
# In tournament_director.py, line ~450
X_train, X_test = create_train_test_split(
    X, y, 
    test_size=0.3,     # Change from 0.2 to 0.3
    random_state=42
)
```

### Add New Algorithm
```python
# In AlgorithmRegistry.get_classification_models()
models = {
    '6_MyModel': MyModelClass(param1=value1),
}
```

### Modify Preprocessing
```python
# In PreprocessorAdvanced.__init__()
self.savgol_window = 15     # Change from 11
self.dct_keep = 10          # Change from 5
```

---

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError
**Solution:**
```bash
source venv/bin/activate
pip install -r tournament_requirements.txt
```

### Issue: Memory error with CNN
**Solution:** Reduce batch size in code:
```python
# Line ~250 in tournament_director.py
cnn_model.fit(..., batch_size=16, epochs=20)
```

### Issue: RFE takes too long
**Solution:** Use fewer trees:
```python
# Line ~80 in tournament_director.py
base_estimator = RandomForestClassifier(n_estimators=20)
```

### Issue: TensorFlow warnings
**Solution:** Add at top of file:
```python
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
```

---

## 📚 Key Files Reference

| File | Purpose |
|------|---------|
| `tournament_director.py` | Main tournament script (800+ lines) |
| `tournament_director_demo.py` | Quick demo (no dependencies) |
| `TOURNAMENT_DIRECTOR_README.md` | Full documentation |
| `TOURNAMENT_QUICK_REFERENCE.md` | This file |
| `tournament_requirements.txt` | Package dependencies |
| `install_tournament.sh` | Automated setup script |

---

## 🎨 Visualization Guide

### PCA Scatter Plot
**Purpose:** See if preprocessing improves class separation
**What to look for:** 
- More distinct clusters = better
- Colors (grades) should group together

### Confusion Matrix
**Purpose:** See which grades are confused
**What to look for:**
- Dark diagonal = good (correct predictions)
- Off-diagonal values = confusion between grades

### Signal Comparison
**Purpose:** Visualize smoothing effect
**What to look for:**
- Smoothed line should follow raw signal trend
- Reduced noise in smoothed version

### Parity Plot
**Purpose:** Check regression prediction quality
**What to look for:**
- Points near red line (y=x) = accurate predictions
- Spread around line = prediction variance

---

## 💾 Data Requirements

**Input Format:**
- `datasets/X_features.csv` - Feature matrix (N samples × M features)
- `datasets/y_targets.csv` - Must have columns: `batch`, `day`, `true_conc_uM`

**Automatic Grade Creation:**
- Days 0-3 → Grade A (0)
- Days 4-7 → Grade B (1)
- Days 8-10 → Grade C (2)
- Days 11+ → Grade D (3)

---

## 🚀 Typical Workflow

1. **Setup** (one-time)
   ```bash
   bash install_tournament.sh
   ```

2. **Run Tournament**
   ```bash
   source venv/bin/activate
   python3 tournament_director.py
   ```
   ⏱️ Expected time: 5-15 minutes

3. **Analyze Results**
   ```bash
   open results_comparison.csv
   open tournament_figures/
   ```

4. **Select Best Models**
   - Top 2-3 from classification
   - Top 2-3 from regression
   - Consider preprocessing method

5. **Deploy** (separate workflow)
   - Save best models with joblib
   - Create inference API
   - Set up monitoring

---

## 🎓 Best Practices

### ✅ Do
- Run tournament multiple times with different random seeds
- Check both preprocessing methods
- Consider computational cost vs accuracy
- Validate on truly held-out data before production
- Document why you chose final models

### ❌ Don't
- Trust single run results
- Ignore overfitting indicators
- Deploy without validation on new data
- Forget about inference time in production
- Skip visualization review

---

## 📞 Support Resources

1. **Full Documentation:** `TOURNAMENT_DIRECTOR_README.md`
2. **Source Code:** `tournament_director.py` (heavily commented)
3. **Demo:** `tournament_director_demo.py`
4. **Project README:** `README.md`
5. **Track A Details:** `TRACK_A_README.md`

---

## 🔄 Version Control

**Created:** December 2025  
**Last Updated:** December 2025  
**Compatible with:** Python 3.8+, scikit-learn 1.0+, TensorFlow 2.8+

---

## ⚡ Performance Tips

1. **Speed up RFE:** Reduce base estimator trees
2. **Speed up CNN:** Reduce epochs or batch size
3. **Parallelize:** Some algorithms support `n_jobs=-1`
4. **Sample data:** Test on subset first
5. **Cache transforms:** Save preprocessed data

---

**Need help?** Check `TOURNAMENT_DIRECTOR_README.md` for detailed explanations!
