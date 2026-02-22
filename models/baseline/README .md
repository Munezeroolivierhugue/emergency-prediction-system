# SENTINEL — Baseline Model Development

**Montgomery County PA 911 Hotspot Prediction System**

---

## Overview

This document covers the baseline modelling stage of SENTINEL — the design choices, training setup, evaluation methodology, and results for the first generation of hotspot prediction models. Four classifiers are trained and evaluated against a naive persistence baseline. The best-performing model is Logistic Regression with an AUC of 0.9793.

---

## Problem Definition

The model answers a single operational question: **will this township be in the top 25% of 911 call volume next month, before that month begins?**

This is framed as binary classification. Each observation is one township in one calendar month. The label `is_hotspot = 1` if that township-month falls at or above the 75th percentile of call volume across all non-zero township-months (≥ 224 calls/month). Everything the model sees at prediction time must come from prior months — there is no access to current-period data.

---

## Files

```
models/baseline/
├── hotspot_model.py             ← Training script
└── output/
    ├── results.json             ← All metrics, split details, feature list
    ├── model_report.txt         ← Full training log
    ├── feature_importances.csv  ← Ranked feature coefficients
    └── charts/
        ├── 01_roc_pr_curves.png
        ├── 02_model_comparison.png
        ├── 03_confusion_matrices.png
        ├── 04_feature_importance.png
        ├── 05_threshold_analysis.png
        ├── 06_severity_distribution.png
        ├── 07_township_volumes.png
        └── 08_temporal_patterns.png
```

---

## Dataset

| Property | Value |
|---|---|
| Input | `data/processed/panel.csv` |
| Observations | 680 township-month rows |
| Townships | 68 |
| Modelled periods | 10 months (March 2016 – December 2016) |
| Hotspot rate | 25.3% (172 / 680) |
| Hotspot threshold | ≥ 224 calls/month (75th percentile) |

The first 3 months of data are used only as warmup for lag feature construction and are excluded from training and evaluation.

---

## Features

30 features are used, all strictly past-only. No feature contains any information from the period being predicted.

### Direct lags

| Feature | Description |
|---|---|
| `calls_lag1` | Total calls, 1 month prior |
| `calls_lag2` | Total calls, 2 months prior |
| `calls_lag3` | Total calls, 3 months prior |
| `critical_lag1` | Critical-severity calls, 1 month prior |
| `critical_lag2` | Critical-severity calls, 2 months prior |
| `critical_lag3` | Critical-severity calls, 3 months prior |
| `hotspot_lag1` | Was this township a hotspot 1 month ago? (0/1) |
| `hotspot_lag2` | Was this township a hotspot 2 months ago? (0/1) |
| `hotspot_lag3` | Was this township a hotspot 3 months ago? (0/1) |
| `hotspot_streak` | Consecutive months this township has been a hotspot |

### Rolling averages

| Feature | Description |
|---|---|
| `calls_roll3m` | Mean call volume over the past 3 months |
| `calls_roll6m` | Mean call volume over the past 6 months |
| `calls_roll12m` | Mean call volume over the past 12 months |
| `critical_roll3m` | Mean critical calls over the past 3 months |
| `critical_roll6m` | Mean critical calls over the past 6 months |
| `critical_roll12m` | Mean critical calls over the past 12 months |
| `hotspot_roll3m` | Fraction of past 3 months this township was a hotspot |
| `hotspot_roll6m` | Fraction of past 6 months this township was a hotspot |
| `hotspot_roll12m` | Fraction of past 12 months this township was a hotspot |

### Trend and seasonality

| Feature | Description |
|---|---|
| `call_trend_3m` | Linear slope of call volume over the past 3 months |
| `calls_same_month_ly` | Call volume in the same calendar month, one year prior |
| `hotspot_same_month_ly` | Hotspot status in the same calendar month, one year prior |

### Long-run baselines

| Feature | Description |
|---|---|
| `cumulative_call_rate` | Running average call rate for this township across all past months |
| `cumulative_hotspot_rate` | Running fraction of past months this township was a hotspot |

### Temporal context

| Feature | Description |
|---|---|
| `month` | Calendar month (1–12) |
| `quarter` | Calendar quarter (1–4) |
| `month_sin` | Sine encoding of month (cyclical) |
| `month_cos` | Cosine encoding of month (cyclical) |
| `is_summer` | 1 if June, July, or August |
| `is_winter` | 1 if December, January, or February |

---

## Naive Persistence Baseline

Before training any model, a naive baseline is established. The persistence baseline predicts that a township's hotspot status this month will be the same as last month. This is the simplest possible predictor and sets a floor that any trained model must beat to be considered useful.

**Naive persistence AUC: 0.9543**

The high naive baseline reflects the short dataset (13 months). With only one year of data, the same townships are consistently busy month after month, making persistence a strong predictor. On the full 2015–2020 dataset, townships shift in and out of hotspot status across seasons and years, and the naive baseline is expected to fall significantly.

---

## Train / Test Split

A strict temporal holdout is used. Models are never evaluated on periods they trained on.

| Set | Periods | Observations | Hotspot rate |
|---|---|---|---|
| Train | March 2016 – September 2016 | 476 | 26.7% |
| Test | October 2016 – December 2016 | 204 | 22.1% |

The split is purely time-based — no shuffling. Earlier months train the model; the final three months of the dataset are held out entirely for evaluation. This mirrors the real operational setting where a model trained on historical data is used to predict future months.

---

## Models

Four classifiers are trained. Each is configured to handle the class imbalance (25% positive rate) via `class_weight='balanced'`.

### Logistic Regression

A linear model with L2 regularisation (`C=0.5`). Features are standardised via `StandardScaler` before fitting. Logistic Regression is the most interpretable option and provides well-calibrated probabilities, which matters for threshold analysis. `max_iter=2000` ensures convergence on the full feature set.

### Decision Tree

A shallow tree with `max_depth=4` and `min_samples_leaf=5`. The depth limit prevents overfitting on the small dataset. Decision Trees are included because they produce fully human-readable rules — a practical advantage for dispatchers who need to understand why a prediction was made.

### Random Forest

An ensemble of 300 trees, each with `max_depth=6` and `min_samples_leaf=3`. Random Forest reduces the variance of the single Decision Tree through bagging and random feature subsampling. `n_jobs=-1` uses all available CPU cores.

### Gradient Boosting

A boosted ensemble of 200 shallow trees (`max_depth=3`), trained sequentially with a learning rate of 0.05 and subsampling of 80% per tree. The conservative learning rate and subsampling reduce overfitting risk on the small dataset.

---

## Results

### Model comparison

| Model | AUC | F1 | Precision | Recall | Accuracy |
|---|---|---|---|---|---|
| **Logistic Regression ★** | **0.9793** | **0.8889** | **0.8148** | **0.9778** | **0.9461** |
| Decision Tree | 0.9678 | 0.8654 | 0.7627 | 1.0000 | 0.9314 |
| Random Forest | 0.9646 | 0.8713 | 0.7857 | 0.9778 | 0.9363 |
| Gradient Boosting | 0.9563 | 0.8800 | 0.8000 | 0.9778 | 0.9412 |
| Naive persistence | 0.9543 | — | — | — | — |

★ Best model. AUC improvement over naive: **+0.0250**

### Confusion matrix — Logistic Regression (test set, 204 observations)

| | Predicted non-hotspot | Predicted hotspot |
|---|---|---|
| **Actual non-hotspot** | 149 (TN) | 10 (FP) |
| **Actual hotspot** | 1 (FN) | 44 (TP) |

The model misses only 1 true hotspot (false negative) at the default threshold. The 10 false positives represent townships incorrectly flagged as high-risk — a conservative error that over-allocates resources rather than under-allocating them, which is the safer failure mode for emergency services.

### Optimal decision threshold

The default classification threshold of 0.5 is not always optimal for imbalanced problems. Threshold analysis finds that **0.241** maximises F1 on the test set for the Logistic Regression model. At this threshold:

- The model is more willing to predict a hotspot (higher recall)
- This reduces false negatives at the cost of some additional false positives
- For emergency resource pre-positioning, high recall is more operationally valuable than high precision

---

## Feature Importance

Feature importances are derived from the absolute values of the Logistic Regression coefficients after standardisation. The top features by importance:

| Rank | Feature | Importance |
|---|---|---|
| 1 | `hotspot_lag2` | 0.801 |
| 2 | `calls_lag2` | 0.629 |
| 3 | `critical_lag3` | 0.597 |
| 4 | `critical_lag1` | 0.584 |
| 5 | `hotspot_streak` | 0.565 |
| 6 | `critical_roll3m` | 0.542 |
| 7 | `calls_roll3m` | 0.517 |
| 8 | `calls_lag1` | 0.482 |
| 9 | `cumulative_hotspot_rate` | 0.459 |
| 10 | `hotspot_roll6m` | 0.448 |

The most predictive features are all persistence-based — recent hotspot status, recent call volumes, and critical-call counts. Temporal features (month, season) contribute less on a 13-month dataset because there is not enough data to learn robust seasonal patterns. On the full 5-year dataset, seasonal features are expected to gain importance.

Notably, `calls_same_month_ly`, `hotspot_same_month_ly`, and `is_winter` have zero importance in this run. This is expected — with only 13 months of data, same-month-last-year features have only one data point per township and carry no generalizable signal.

---

## Charts

| Chart | Contents |
|---|---|
| `01_roc_pr_curves.png` | ROC curves and Precision-Recall curves for all four models plus the naive baseline |
| `02_model_comparison.png` | Side-by-side bar chart of AUC, F1, Precision, and Recall across all models |
| `03_confusion_matrices.png` | Confusion matrices for all four models on the test set |
| `04_feature_importance.png` | Top 20 features by Logistic Regression coefficient magnitude |
| `05_threshold_analysis.png` | Precision/Recall/F1 vs threshold curve, probability distribution, and summary metrics for the best model |
| `06_severity_distribution.png` | Call counts by Severity level and by call Type (EMS / Traffic / Fire) |
| `07_township_volumes.png` | Top 15 townships by total 911 call volume |
| `08_temporal_patterns.png` | Call volume by hour of day and by calendar month |

---

## Limitations and Next Steps

**Dataset size.** The current results are based on 13 months of data. The high naive baseline (0.9543) and the zero importance of same-month-last-year features both reflect this constraint. The pipeline is designed to run unchanged on the full 2015–2020 Kaggle dataset, which will provide a more honest evaluation.

**Temporal leakage check.** All features use `.shift(1)` before any rolling computation. This has been verified in `02_build_panel.py`. The temporal holdout split provides a further structural guarantee that no test-period information enters training.

**Class imbalance.** The 25% hotspot rate is handled via `class_weight='balanced'` in all models. For the full dataset, SMOTE or threshold tuning may provide additional improvement.

**No spatial features.** Township geographic relationships (adjacency, shared infrastructure) are not currently encoded. Spatial lag features — e.g. whether a neighbouring township was a hotspot last month — could improve prediction for smaller townships with sparse individual histories.

**Recommended next model.** Once the full dataset is in place, the next development step is a township fixed-effects model or a gradient-boosted model with longer rolling windows (24-month and 36-month averages), proper hyperparameter search via time-series cross-validation, and spatial adjacency features.

---

## Running the Model

From the project root, after completing Steps 1 and 2:

```bash
python models/baseline/03_hotspot_model.py
```

Outputs are written to `models/baseline/output/`. The script requires `pandas`, `numpy`, `scikit-learn`, and `matplotlib`.

---

*SENTINEL — Montgomery County PA 911 Hotspot Prediction*
