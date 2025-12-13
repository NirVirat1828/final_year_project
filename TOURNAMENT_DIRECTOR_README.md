# Tournament Director - ML Algorithm Benchmarking System

## 🏆 Overview

A comprehensive benchmarking system designed by a Senior ML Engineer to rigorously compare multiple machine learning algorithms across two preprocessing strategies and two prediction tracks.

### Key Features

- **Dual Preprocessing Methods:**
  - **Method A (Raw)**: StandardScaler only
  - **Method B (Advanced)**: Savitzky-Golay Filter → DCT → RFE

- **Dual Prediction Tracks:**
  - **Track A (Classification)**: Freshness Grade A/B/C/D prediction
  - **Track B (Regression)**: Shelf-life days prediction

- **9 Algorithms Tested:**
  - Classification: LDA, SVM, Random Forest, XGBoost, 1D-CNN
  - Regression: PLS, SVR, Random Forest, XGBoost

- **Comprehensive Visualizations:**
  - PCA scatter plots (Raw vs Processed)
  - Confusion matrices
  - Signal comparison plots
  - Regression parity plots
  - Performance comparison bar charts

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# If using a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r tournament_requirements.txt
```

### 2. Run the Tournament

```bash
python3 tournament_director.py
```

### 3. View Results

Results are automatically saved to:
- **CSV Report**: `results_comparison.csv`
- **Visualizations**: `tournament_figures/`

---

## 📊 Output Structure

### Results CSV Format

| Preprocessing | Track | Algorithm | Accuracy | F1_Weighted | RMSE | R2 |
|--------------|-------|-----------|----------|-------------|------|-----|
| Raw_StandardScaler | Classification | 1_LDA_Baseline | 0.7245 | 0.7189 | - | - |
| Advanced_SavGol_DCT_RFE | Classification | 3_RandomForest | 0.7890 | 0.7823 | - | - |
| Raw_StandardScaler | Regression | 1_PLS_Industry_Standard | - | - | 2.34 | 0.82 |

### Generated Figures

1. **pca_scatter_comparison.png** - 2D PCA projections comparing raw vs processed data
2. **confusion_matrix_*.png** - Heatmaps for best classifiers
3. **signal_comparison.png** - Raw signal vs Savitzky-Golay smoothed signal
4. **parity_plot_*.png** - Predicted vs Actual for regression models
5. **classification_performance.png** - Bar charts comparing all classification algorithms
6. **regression_performance.png** - Bar charts comparing all regression algorithms

---

## 🔧 Architecture Details

### Preprocessing Pipeline

#### Method A: Raw Data
```
Raw Features → StandardScaler → Model
```

#### Method B: Advanced
```
Raw Features → Savitzky-Golay Filter (window=11, poly=3)
             → DCT Transform (keep top 5 coefficients)
             → StandardScaler
             → RFE Selection (select top 5 features)
             → Model
```

### Algorithm Specifications

#### Track A: Classification

1. **LDA (Baseline)**
   - Linear Discriminant Analysis
   - Industry standard for multiclass problems

2. **SVM (RBF Kernel)**
   - C=1.0
   - Kernel='rbf'
   - Probability estimates enabled

3. **Random Forest**
   - n_estimators=100
   - Current best performer

4. **XGBoost**
   - Default gradient boosting settings
   - Automatic handling of multiclass

5. **1D-CNN (Deep Learning)**
   - Architecture: Conv1D → MaxPool → Conv1D → MaxPool → Flatten → Dense
   - 32 and 64 filters
   - Dropout (0.3) for regularization

#### Track B: Regression

1. **PLS Regression**
   - n_components=5
   - Industry standard for spectroscopy data

2. **SVR (RBF Kernel)**
   - Support Vector Regression
   - Non-linear relationships

3. **Random Forest**
   - n_estimators=100
   - Ensemble tree-based method

4. **XGBoost**
   - Gradient boosting regressor
   - State-of-the-art performance

---

## 📈 Metrics Explained

### Classification Metrics

- **Accuracy**: Overall correct prediction rate
  - Range: [0, 1], higher is better
  - Formula: (TP + TN) / Total

- **F1-Score (Weighted)**: Harmonic mean of precision and recall, weighted by class support
  - Range: [0, 1], higher is better
  - Accounts for class imbalance

### Regression Metrics

- **RMSE (Root Mean Squared Error)**: Average prediction error magnitude
  - Range: [0, ∞], lower is better
  - Same units as target variable (days)

- **R² (R-squared)**: Proportion of variance explained
  - Range: (-∞, 1], higher is better
  - 1.0 = perfect prediction, 0.0 = as good as mean baseline

---

## 💡 Usage Tips

### Customizing the Tournament

Edit the following sections in `tournament_director.py`:

#### 1. Change Preprocessing Parameters

```python
# In PreprocessorAdvanced class
def __init__(self):
    self.savgol_window = 11     # Adjust smoothing window
    self.savgol_poly = 3        # Polynomial order
    self.dct_keep = 5           # DCT coefficients to keep
    self.rfe_features = 5       # Final feature count
```

#### 2. Add New Algorithms

```python
# In AlgorithmRegistry class
@staticmethod
def get_classification_models():
    models = {
        # Add your custom model here
        '6_YourModel': YourModelClass(param1=value1),
    }
    return models
```

#### 3. Modify Train-Test Split

```python
# In main() function
X_train, X_test, ... = create_train_test_split(
    X, y_grade, y_days,
    test_size=0.3,        # Change split ratio
    random_state=123      # Change random seed
)
```

---

## 🔍 Interpreting Results

### What to Look For

1. **Preprocessing Impact**
   - Compare same algorithm across Raw vs Advanced preprocessing
   - Look for consistent improvement patterns

2. **Algorithm Ranking**
   - Identify top 2-3 performers per track
   - Check if rankings hold across both preprocessing methods

3. **Overfitting Indicators**
   - Large gap between train and test metrics
   - Very high R² (>0.99) may indicate data leakage

4. **Visual Insights**
   - PCA plots show if preprocessing improves class separation
   - Confusion matrices reveal which grades are hardest to classify
   - Parity plots show if regression predictions are biased

### Best Practices

- **Classification**: Prioritize F1-Score over Accuracy if classes are imbalanced
- **Regression**: Both RMSE and R² are important; low RMSE with low R² means predictions are close to mean
- **Model Selection**: Consider computational cost vs performance gain
- **Production Deployment**: Test top 3 models on completely held-out data before finalizing

---

## 🐛 Troubleshooting

### Common Issues

**1. ModuleNotFoundError**
```bash
# Solution: Install missing packages
pip install -r tournament_requirements.txt
```

**2. Memory Error with 1D-CNN**
```python
# Solution: Reduce batch size or epochs
history = cnn_model.fit(..., batch_size=16, epochs=20)
```

**3. RFE Taking Too Long**
```python
# Solution: Reduce RFE estimator complexity
base_estimator = RandomForestClassifier(n_estimators=20)
```

**4. Data Shape Mismatch**
```
# Ensure X_train and X_test have same number of features
print(f"Train: {X_train.shape}, Test: {X_test.shape}")
```

---

## 📚 References

### Algorithms
- [Linear Discriminant Analysis (LDA)](https://scikit-learn.org/stable/modules/lda_qda.html)
- [Support Vector Machines](https://scikit-learn.org/stable/modules/svm.html)
- [Random Forests](https://scikit-learn.org/stable/modules/ensemble.html#forest)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [TensorFlow/Keras](https://www.tensorflow.org/)

### Signal Processing
- [Savitzky-Golay Filter](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html)
- [Discrete Cosine Transform](https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.dct.html)

### Feature Selection
- [Recursive Feature Elimination (RFE)](https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.RFE.html)
- [PLS Regression](https://scikit-learn.org/stable/modules/cross_decomposition.html)

---

## 🤝 Contributing

To extend the Tournament Director:

1. **Add New Preprocessing Method**
   - Create new class inheriting preprocessing interface
   - Implement `fit_transform()` and `transform()` methods
   - Add to `preprocessors` list in `run_tournament()`

2. **Add New Algorithm**
   - Add to `AlgorithmRegistry.get_*_models()` methods
   - Follow naming convention: `N_ModelName`
   - Handle exceptions gracefully

3. **Add New Visualization**
   - Create method in `TournamentVisualizer` class
   - Follow save path convention
   - Add call in `main()` function

---

## 📝 License & Citation

This tournament system was designed for the Orange Freshness Detection project.

If you use this system in your research, please cite:
```
Tournament Director: A Comprehensive ML Benchmarking System
Orange Freshness Detection Project, 2025
```

---

## 🎯 Next Steps After Tournament

1. **Model Selection**
   - Choose top performer from each track
   - Consider computational cost vs accuracy trade-off

2. **Hyperparameter Tuning**
   - Use GridSearchCV or RandomizedSearchCV on winners
   - Focus on top 2-3 models only

3. **Cross-Validation**
   - Implement k-fold CV for more robust estimates
   - Check for overfitting

4. **Ensemble Methods**
   - Combine top models via voting/stacking
   - Often yields best results

5. **Production Deployment**
   - Serialize best models with joblib
   - Create inference API
   - Set up monitoring pipeline

---

## 📧 Contact

For questions or issues, refer to the main project README or open an issue in the repository.

---

**Happy Benchmarking! 🚀**
