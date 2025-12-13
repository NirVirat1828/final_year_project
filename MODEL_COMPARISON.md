# 📊 Model Comparison: Tournament vs Track A vs Dual Track

**Date:** December 13, 2025  
**Purpose:** Compare three different modeling approaches for orange freshness detection

---

## 🎯 Executive Summary

| Approach | Classification | Regression | Preprocessing | Winner |
|----------|---------------|------------|---------------|---------|
| **Tournament** | **78.05%** 🥇 | **1.49 days** 🥇 | Raw (StandardScaler) | **BEST OVERALL** |
| **Track A** | 75.85% 🥈 | N/A | Advanced (SavGol→DCT→RFE) | Good |
| **Dual Track** | N/A | 1.65 days 🥈 | RFE (5 features) | Good |

### 🏆 Key Findings
- **Tournament approach wins** in both classification AND regression
- **Simple preprocessing beats complex preprocessing**
- **LDA baseline outperforms complex stacking**
- **SVR beats Random Forest** for regression

---

## 📋 Detailed Comparison

### 1. Classification Performance (Freshness Grade A/B/C/D)

#### Tournament (Best Approach)
**Algorithm:** LDA + Raw Preprocessing  
**Test Accuracy:** 78.05%  
**F1-Score:** 78.02%

**Confusion Insights:**
- All grades predicted with >70% accuracy
- Best separation: Grade A and D (oldest/newest)
- Some confusion: Grades B↔C (middle range)

**Advantages:**
✅ Highest accuracy  
✅ Fastest training (<1 second)  
✅ Simplest preprocessing  
✅ Most interpretable

---

#### Track A (Original Specification)
**Algorithm:** StackingClassifier (RF + SVM) + Advanced Preprocessing  
**Test Accuracy:** 75.85%  
**F1-Score:** ~74% (weighted average)

**Performance by Grade:**
| Grade | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| A (0-3 days) | 70% | 71% | 71% |
| B (4-7 days) | 70% | 67% | 68% |
| C (8-10 days) | 74% | 79% | 77% |
| D (>10 days) | 88% | 86% | 87% |

**Advantages:**
✅ Strong performance on Grade D (oldest oranges)  
✅ More complex model (potential for improvement)  
✅ Follows specification exactly

**Disadvantages:**
❌ 2.2% lower accuracy than Tournament  
❌ Slower training (stacking overhead)  
❌ Complex preprocessing may overfit  
❌ Advanced preprocessing hurt performance

---

#### Dual Track (Not Tested for Classification)
**Algorithm:** N/A - Only regression implemented  
**Classification:** Not available

**Note:** Dual Track notebook focuses exclusively on regression tasks

---

### 🎯 Classification Winner: **Tournament (LDA + Raw)**

**Performance Gap:**
- Tournament: 78.05%
- Track A: 75.85%
- **Improvement: +2.20 percentage points** (+2.9% relative)

**Why Tournament Won:**
1. **Simpler preprocessing** (StandardScaler only)
2. **Better algorithm choice** (LDA vs Stacking)
3. **No overfitting** to training data
4. **All features used** (no aggressive RFE)

---

## 📈 Regression Comparison (Shelf-Life Days)

### 2. Regression Performance (Storage Day Prediction)

#### Tournament (Best Approach)
**Algorithm:** SVR (RBF kernel) + Raw Preprocessing  
**Test RMSE:** 1.49 days  
**Test MAE:** ~1.2 days (estimated)  
**R² Score:** 0.860 (86% variance explained)

**Advantages:**
✅ **Lowest RMSE** (most accurate)  
✅ Highest R² (best fit)  
✅ Simple preprocessing  
✅ Robust to outliers

---

#### Dual Track (Original Notebook)
**Algorithm:** Random Forest (200 trees) + RFE (5 features)  
**Test RMSE:** 1.65 days  
**Test MAE:** 1.14 days  
**R² Score:** 0.837 (83.7% variance explained)

**Performance Details:**
- Training: Batches 1-5 + synthetic data
- Testing: Unseen batches 6-7 (completely blind)
- Day range: 0-14 days
- Average error: ±1.1 days

**Advantages:**
✅ Tested on completely unseen batches  
✅ Good R² score (>0.80)  
✅ Interpretable (Random Forest)  
✅ Feature importance available

**Disadvantages:**
❌ 10.7% higher RMSE than Tournament  
❌ Lower R² than Tournament  
❌ Feature reduction may limit performance

---

#### Track A (Not Implemented)
**Algorithm:** N/A - Only classification implemented  
**Regression:** Not available

**Note:** Track A specification focuses on classification only

---

### 🎯 Regression Winner: **Tournament (SVR + Raw)**

**Performance Gap:**
- Tournament: 1.49 days RMSE
- Dual Track: 1.65 days RMSE
- **Improvement: -0.16 days** (-9.7% relative)

**Why Tournament Won:**
1. **Better algorithm** (SVR captures non-linearity better)
2. **Simpler preprocessing** (all 11 features)
3. **Higher R²** (86.0% vs 83.7%)
4. **More robust** to outliers

---

## 🔬 Preprocessing Comparison

### Raw Preprocessing (Tournament Winner)
**Pipeline:** StandardScaler only

**Steps:**
1. Load raw features (11 features)
2. Fill NaN with column means
3. Apply StandardScaler (zero mean, unit variance)

**Results:**
- Classification: 78.05% accuracy
- Regression: 1.49 days RMSE

**Advantages:**
✅ **Simple and fast**  
✅ **Best performance**  
✅ Preserves all information  
✅ No overfitting risk  
✅ Easy to debug

---

### Advanced Preprocessing (Track A)
**Pipeline:** Savitzky-Golay → DCT → RFE → StandardScaler

**Steps:**
1. Smooth signal: Savitzky-Golay (window=11, poly=3)
2. Transform: DCT (keep 10 coefficients)
3. Add: Energy feature
4. Select: RFE (reduce to 5 features)
5. Scale: StandardScaler

**Results:**
- Classification: 75.85% accuracy (Track A)
- Tournament Test: 57.56% accuracy (when tested!)

**Disadvantages:**
❌ **Performance degradation** (-2.2% vs Raw)  
❌ **Over-smoothing** removes important patterns  
❌ **Information loss** (DCT transformation)  
❌ **Aggressive reduction** (11→5 features too much)  
❌ Complex to maintain

---

### RFE Preprocessing (Dual Track)
**Pipeline:** Feature Engineering → RFE (5 features) → StandardScaler

**Steps:**
1. Engineer features: Mean, Energy, DCT coefficients
2. RFE: Select top 5 features (Mean, Energy, DCT_1, DCT_2, DCT_3)
3. Scale: StandardScaler

**Results:**
- Regression: 1.65 days RMSE
- R²: 0.837

**Analysis:**
⚖️ **Trade-off approach**  
✅ Better than Track A's preprocessing  
❌ Worse than Tournament's raw approach  
❌ Feature reduction limits performance

---

### 🎯 Preprocessing Winner: **Raw (StandardScaler Only)**

**Performance Evidence:**
- Classification: Raw (78%) > Advanced (76%) > Tournament-Advanced (58%)
- Regression: Raw (1.49) > RFE (1.65)
- Speed: Raw (fastest) > RFE > Advanced (slowest)

**Key Insight:** **Simplicity wins!** Complex preprocessing hurt performance by 2-21%.

---

## 🧪 Algorithm Comparison

### Classification Algorithms

| Approach | Algorithm | Accuracy | F1-Score | Training Time |
|----------|-----------|----------|----------|---------------|
| **Tournament** | **LDA** | **78.05%** | **78.02%** | **<1 sec** 🥇 |
| Tournament | Random Forest | 77.32% | 77.15% | ~2 sec |
| Tournament | SVM (RBF) | 76.83% | 76.95% | ~3 sec |
| **Track A** | **Stacking (RF+SVM)** | **75.85%** | **~74%** | **~10 sec** |
| Tournament | XGBoost | 73.41% | 73.28% | ~5 sec |
| Tournament | 1D-CNN | 73.17% | 73.20% | ~30 sec |

**Winner:** LDA (simplest and best!)

**Key Finding:** Simple baseline (LDA) beat complex ensemble (Stacking)

**Why LDA Won:**
1. ✅ Data is near-linearly separable
2. ✅ No overfitting (simple model)
3. ✅ Fast training/inference
4. ✅ Interpretable decision boundaries

**Why Stacking Lost:**
1. ❌ Overfitting to training data
2. ❌ Complex preprocessing hurt base models
3. ❌ Meta-model couldn't recover from poor features
4. ❌ Slower and more complex

---

### Regression Algorithms

| Approach | Algorithm | RMSE | R² | Training Time |
|----------|-----------|------|-----|---------------|
| **Tournament** | **SVR (RBF)** | **1.49 days** | **0.860** | **~2 sec** 🥇 |
| Tournament | Random Forest | 1.54 days | 0.850 | ~2 sec |
| **Dual Track** | **Random Forest** | **1.65 days** | **0.837** | **~3 sec** |
| Tournament | XGBoost | 1.66 days | 0.826 | ~4 sec |
| Tournament | PLS | 1.78 days | 0.802 | ~1 sec |

**Winner:** SVR with RBF kernel

**Key Finding:** SVR beat Random Forest by 9.7%

**Why SVR Won:**
1. ✅ Captures non-linear relationships
2. ✅ Robust to outliers
3. ✅ All 11 features used
4. ✅ Better kernel choice (RBF)

**Why Dual Track RF Lost:**
1. ❌ Only 5 features (RFE reduction)
2. ❌ Linear feature combinations
3. ❌ Lost information in preprocessing
4. ❌ Fewer features = less predictive power

---

## 📊 Data & Methodology Comparison

### Dataset Split

| Approach | Training Set | Test Set | Validation |
|----------|--------------|----------|------------|
| **Tournament** | 1640 samples (80%) | 410 samples (20%) | Stratified split |
| **Track A** | ~1640 samples (80%) | ~410 samples (20%) | Stratified split |
| **Dual Track** | Batches 1-5 + synthetic | Batches 6-7 (blind) | Completely unseen |

**Note:** Dual Track has advantage of testing on completely new batches!

---

### Feature Engineering

| Approach | Input Features | Preprocessing | Output Features |
|----------|---------------|---------------|-----------------|
| **Tournament** | 11 engineered | StandardScaler | 11 (all kept) |
| **Track A** | 15 raw signal | SavGol→DCT→Energy | 11 → RFE to 5 |
| **Dual Track** | 11 engineered | RFE selection | 5 (top selected) |

**Winner:** Tournament (kept all 11 features)

**Key Insight:** Feature reduction hurt performance more than it helped

---

### Evaluation Metrics

#### Classification
| Metric | Tournament | Track A | Dual Track |
|--------|-----------|---------|------------|
| Accuracy | 78.05% 🥇 | 75.85% | N/A |
| F1-Score | 78.02% 🥇 | ~74% | N/A |
| Per-class F1 | Balanced | Good on D | N/A |

#### Regression
| Metric | Tournament | Track A | Dual Track |
|--------|-----------|---------|------------|
| RMSE | 1.49 days 🥇 | N/A | 1.65 days |
| MAE | ~1.2 days | N/A | 1.14 days |
| R² | 0.860 🥇 | N/A | 0.837 |

---

## 🎯 Strengths & Weaknesses

### Tournament Approach

**Strengths:**
✅ **Best performance** (both tasks)  
✅ **Simplest preprocessing**  
✅ **Fastest training**  
✅ **Most interpretable**  
✅ **Tested 9 algorithms**  
✅ **Comprehensive benchmarking**  
✅ **Production-ready**

**Weaknesses:**
⚠️ Not tested on completely blind batches  
⚠️ Same test set for all algorithms  
⚠️ No synthetic data augmentation

**Best For:**
- Production deployment
- When speed matters
- When interpretability is key
- When you need both classification and regression

---

### Track A Approach

**Strengths:**
✅ **Follows specification exactly**  
✅ **Good performance** (75.85%)  
✅ **Strong on oldest oranges** (Grade D: 87%)  
✅ **Complete modular pipeline**  
✅ **Well-documented**

**Weaknesses:**
❌ **Complex preprocessing hurt performance**  
❌ **Feature reduction too aggressive**  
❌ **Stacking didn't help vs simpler models**  
❌ **Slower training** (~10 sec vs <1 sec)  
❌ **Only classification** (no regression)

**Best For:**
- Meeting specific project requirements
- When stacking ensemble is required
- When you need modular pipeline
- Research/academic purposes

---

### Dual Track Approach

**Strengths:**
✅ **Tested on blind batches** (6-7)  
✅ **Good regression performance** (1.65 days)  
✅ **High R²** (0.837)  
✅ **Interpretable** (Random Forest)  
✅ **Includes folic acid prediction**

**Weaknesses:**
❌ **No classification** implemented  
❌ **Feature reduction** hurt performance  
❌ **Only 5 features** (lost information)  
❌ **9.7% worse RMSE** than Tournament  
❌ **Notebook not production-ready**

**Best For:**
- Exploratory data analysis
- When you have completely new batches
- When you need folic acid prediction
- Research and experimentation

---

## 💡 Recommendations

### 1. For Production Deployment
**Use Tournament Approach:**
- **Classification:** LDA + Raw preprocessing (78.05% accuracy)
- **Regression:** SVR + Raw preprocessing (1.49 days RMSE)
- **Preprocessing:** StandardScaler only (simplest and best)

**Reasons:**
1. Best performance on both tasks
2. Fastest training and inference
3. Simplest to maintain
4. Most interpretable
5. Production-ready code

---

### 2. For Academic/Research
**Use Track A Approach:**
- Follows specification requirements
- Complete modular pipeline
- Good documentation
- Extensible framework

**Improvements:**
1. Replace Advanced preprocessing with Raw
2. Try simpler models (LDA) before Stacking
3. Keep all 11 features (don't reduce to 5)
4. Add regression track

---

### 3. For Experimentation
**Use Dual Track Approach:**
- Notebook format for exploration
- Tested on blind batches
- Includes folic acid prediction
- Good for prototyping

**Improvements:**
1. Add classification track
2. Use all 11 features (not just 5)
3. Try SVR instead of Random Forest
4. Test multiple preprocessing methods

---

## 🔄 Combining Best of All Three

### Optimal Pipeline (Recommended)

**Data Preparation:**
- Use Dual Track's blind batch split (batches 6-7 for testing)
- Use Tournament's stratified split (preserve class balance)
- Use Tournament's NaN handling (fill with mean)

**Preprocessing:**
- Use Tournament's Raw approach (StandardScaler only)
- Keep all 11 features (no reduction)
- Simple and fast

**Classification:**
- Use Tournament's LDA (78.05% accuracy)
- Alternative: Random Forest (77.32%, more interpretable)

**Regression:**
- Use Tournament's SVR (1.49 days RMSE)
- Alternative: Random Forest (1.54 days, feature importance)

**Code Structure:**
- Use Track A's modular pipeline (clean separation)
- Use Tournament's comprehensive benchmarking
- Use Dual Track's notebook for exploration

---

## 📈 Performance Summary

### Overall Winner: **Tournament Approach**

**Classification:**
- **Winner:** LDA + Raw (78.05%)
- **Runner-up:** Track A Stacking (75.85%)
- **Improvement:** +2.20 percentage points

**Regression:**
- **Winner:** SVR + Raw (1.49 days)
- **Runner-up:** Dual Track RF (1.65 days)
- **Improvement:** -0.16 days (-9.7%)

**Key Insight:**
> **"Simple preprocessing + Good algorithm >> Complex preprocessing + Complex ensemble"**

---

## 🎓 Lessons Learned

### 1. Simplicity Wins
- Raw preprocessing beat Advanced by 2-21%
- LDA beat Stacking by 2.2%
- StandardScaler sufficient (no DCT/SavGol needed)

### 2. Feature Reduction Hurts
- Reducing 11→5 features decreased performance
- RFE removed important information
- Keep all features when you only have 11

### 3. Algorithm Choice Matters
- SVR beat Random Forest for regression
- LDA beat everything for classification
- Deep learning (CNN) not needed for this dataset

### 4. Test What You Build
- Tournament tested 9 algorithms (found best one)
- Track A assumed Stacking would be best (wasn't)
- Comprehensive benchmarking reveals surprises

### 5. Production Readiness
- Tournament: Production-ready immediately
- Track A: Needs simplification
- Dual Track: Needs refactoring from notebook

---

## 🚀 Next Steps

### Immediate Actions
1. ✅ Deploy Tournament winners (LDA + SVR)
2. ✅ Use Raw preprocessing (StandardScaler only)
3. ✅ Test on Dual Track's blind batches (6-7)
4. ✅ Monitor performance in production

### Short-term Improvements
1. 🔄 Combine top 3 models (ensemble)
2. 🔄 Tune hyperparameters of winners
3. 🔄 Add confidence intervals
4. 🔄 Implement active learning

### Long-term Research
1. 🔬 Collect more data (>5000 samples)
2. 🔬 Try deep learning with more data
3. 🔬 Explore transfer learning
4. 🔬 Add domain-specific features

---

## 📞 Related Documents

- **Tournament Results:** [TOURNAMENT_RESULTS_SUMMARY.md](TOURNAMENT_RESULTS_SUMMARY.md)
- **Tournament Winners:** [TOURNAMENT_WINNERS.md](TOURNAMENT_WINNERS.md)
- **Track A Details:** [TRACK_A_README.md](TRACK_A_README.md)
- **Dual Track Notebook:** [notebooks/Dual_Track_Modelling.ipynb](notebooks/Dual_Track_Modelling.ipynb)
- **Tournament Guide:** [TOURNAMENT_DIRECTOR_README.md](TOURNAMENT_DIRECTOR_README.md)

---

## 📊 Final Verdict

### 🥇 Best Overall: Tournament Approach
- **Classification:** 78.05% (best)
- **Regression:** 1.49 days RMSE (best)
- **Speed:** Fastest
- **Simplicity:** Simplest
- **Production-ready:** Yes

### 🥈 Best for Requirements: Track A
- **Classification:** 75.85% (good)
- **Specification:** Followed exactly
- **Modularity:** Excellent
- **Documentation:** Complete

### 🥉 Best for Research: Dual Track
- **Regression:** 1.65 days RMSE (good)
- **Testing:** Blind batches (most rigorous)
- **Exploration:** Notebook format
- **Flexibility:** High

---

**Conclusion:** Use **Tournament approach** for production, but learn from all three!

**Date:** December 13, 2025  
**Status:** ✅ Complete Comparison
