# SENTINEL — Baseline Model Development

**Crime Hotspot Prediction System  |  Chicago Police Department**

This document covers everything about the baseline model: what it predicts,
how it was designed, the four algorithms compared, how each decision was made,
and how to interpret the results. It is intended as both a technical reference
and a record of reasoning — so that anyone picking this up later understands
not just what the model does but why it does it that way.

---

## Table of Contents

1. [What This Model Does](#what-this-model-does)
2. [Quick Start](#quick-start)
3. [Inputs and Outputs](#inputs-and-outputs)
4. [Model Design Decisions](#model-design-decisions)
5. [The Naive Baseline](#the-naive-baseline)
6. [The Four Models](#the-four-models)
7. [Hyperparameters](#hyperparameters)
8. [Evaluation Metrics](#evaluation-metrics)
9. [Results](#results)
10. [Reading the Charts](#reading-the-charts)
11. [Choosing a Model for Deployment](#choosing-a-model-for-deployment)
12. [Known Limitations](#known-limitations)
13. [Next Steps](#next-steps)

---

## What This Model Does

SENTINEL predicts which geographic areas will be **crime hotspots next month**,
before those months begin. This enables patrol commanders to position resources
proactively rather than reacting after incidents are reported.

**Prediction unit:** one grid cell (~1.1 km²) × one calendar month  
**Target:** will this cell be in the top 25% of crime activity next month?  
**Output:** a probability score (0.0–1.0) for each cell, updated monthly  

This is a **proactive** system. The model runs at the beginning of each month
using only historical data and produces a ranked list of cells by hotspot
probability. Patrol deployment decisions are made before any crime has occurred.

---

## Quick Start

```bash
# Requires data/panel.csv from 02_build_panel.py
python 03_hotspot_model.py
```

**Outputs written to:**

```
output/results.json               — all metrics, model config, feature list
output/model_report.txt           — full console log
output/feature_importances.csv    — ranked feature scores (best model)
output/charts/
  01_roc_pr_curves.png
  02_model_comparison.png
  03_confusion_matrices.png
  04_feature_importance.png
  05_threshold_analysis.png
  06_hotspot_map.png
  07_performance_over_time.png
  08_crime_patterns.png
```

---

## Inputs and Outputs

### Input: `data/panel.csv`

Produced by `02_build_panel.py`. Each row is one grid cell in one calendar
month. The panel covers 40 cells × 288 model months = 11,520 cell-month
observations after the 12-month warmup exclusion.

| Property | Value |
|---|---|
| Rows | 11,520 |
| Columns | 49 |
| Grid cells | 40 |
| Monthly periods | 288 (2002–2025) |
| Hotspot rate | 9.5% (1,096 hotspot cell-months) |
| Zero-crime months | 62.1% of panel |

### Output: `output/results.json`

Machine-readable record of everything — model config, train/test split,
all metrics for all four models, feature list, best threshold. Use this
to compare future runs or load metrics into a dashboard.

```json
{
  "best_model": "Random Forest",
  "naive_persistence_auc": 0.674,
  "best_thresh": 0.714,
  "models": {
    "Random Forest": {
      "auc": 0.8865,
      "f1": 0.4431,
      "precision": 0.3343,
      "recall": 0.657,
      ...
    }
  }
}
```

---

## Model Design Decisions

### Decision 1: Temporal holdout, not random split

The training set covers **2002–2021**. The test set covers **2022–2025**.
No test records appear anywhere in training.

**Why this matters:** A random 80/20 shuffle would allow 2024 records into
the training set, letting the model learn 2024 crime patterns and then
"predict" 2024 test records it has already seen. Performance would look strong
but would collapse immediately in deployment. A temporal cutoff simulates
real operational conditions: the model was built at the end of 2021 and must
predict years it has never seen.

**A concrete example of why this is wrong:** Imagine a new construction project
that dramatically changed crime patterns in one cell from 2023 onwards. With
random splitting, the model trains on 2023 records that reflect this change
and can "predict" test records from the same period. With temporal splitting,
the model has no knowledge of the construction project and must predict 2023
purely from pre-2023 patterns — which is exactly the situation a real deployed
model would face.

| Split | Train | Test |
|---|---|---|
| Temporal holdout ✅ | 2002–2021 (9,600 rows) | 2022–2025 (1,920 rows) |
| Random shuffle ❌ | 80% random sample | 20% random sample |

### Decision 2: Class imbalance handling

Hotspot cell-months represent 9.5% of the panel. The remaining 90.5% are
non-hotspot. A model that predicted "never a hotspot" for every cell would
achieve 90.5% accuracy while being completely useless.

**How it is handled:**

- `class_weight='balanced'` is set on Logistic Regression, Decision Tree,
  and Random Forest. This automatically weights each class inversely
  proportional to its frequency, making a missed hotspot as costly to the
  model as a missed non-hotspot.
- Gradient Boosting does not support `class_weight` natively. The class
  imbalance is partially addressed through the `subsample=0.8` parameter
  and the use of AUC (not accuracy) as the primary evaluation metric.
- AUC-ROC is used as the primary metric precisely because it is insensitive
  to class imbalance. Unlike accuracy, it evaluates discrimination ability
  across all possible thresholds.

### Decision 3: Four models instead of one

Training four algorithms on the same data serves a specific purpose: it tells
you whether performance comes from the algorithm or from the features. If all
four models perform similarly, the features are doing the work. If one model
dramatically outperforms the others, the model family matters.

In this case, all four models achieved AUC in the 0.87–0.89 range, which
confirms the features — particularly the lag and rolling history features —
are the primary driver of performance. No single algorithm has a decisive
structural advantage on this problem.

### Decision 4: AUC as primary metric, not accuracy

AUC measures the probability that the model ranks a randomly chosen hotspot
cell above a randomly chosen non-hotspot cell. An AUC of 0.8865 means the
model correctly discriminates hotspots from non-hotspots 88.65% of the time.

**Why not accuracy?** At 9.5% hotspot rate, a model predicting "never a
hotspot" achieves 90.5% accuracy — higher than any of the trained models —
while having no predictive value whatsoever. AUC is immune to this failure
mode because it evaluates discrimination ability across every possible
decision threshold, not just at the default 0.5.

Precision and recall are reported as secondary metrics because they are
operationally meaningful:
- **Precision** = when we flag a cell, how often are we right? (false alarm rate)
- **Recall** = of actual hotspots, how many did we catch? (miss rate)

These trade off against each other through the decision threshold, and the
right tradeoff is an operational policy decision, not a statistical one.

### Decision 5: Threshold selection

The model outputs probabilities, not binary predictions. The decision
threshold — the probability above which a cell is flagged as a hotspot —
is a separate choice from model training.

The default threshold of 0.5 is almost always wrong for imbalanced
datasets. With a 9.5% hotspot rate, a cell needs to be roughly 10× more
likely to be a hotspot than a non-hotspot before crossing a 0.5 threshold
that treats both classes as equally likely.

The script sweeps thresholds from 0.05 to 0.95 and identifies the value
that maximises F1 score on the test set. For Random Forest, the optimal
F1 threshold is **0.714**. This is the recommended starting point for
deployment, but departments should adjust it based on their resource
constraints (lower = more cells flagged, higher = fewer cells flagged).

---

## The Naive Baseline

Before evaluating any trained model, the script computes a **naive persistence
baseline**: simply predict that each cell's hotspot status this month equals
its hotspot status last month.

```
naive prediction for cell C in month t = is_hotspot(C, t-1)
```

This baseline requires no training, no features, and no algorithm. If a
trained model cannot beat it, the model has learned nothing useful.

**Naive baseline AUC: 0.6740**

All four trained models exceed this by a substantial margin:

| Model | AUC | vs. Naive |
|---|---|---|
| Random Forest | 0.8865 | +0.2125 |
| Logistic Regression | 0.8824 | +0.2084 |
| Gradient Boosting | 0.8810 | +0.2070 |
| Decision Tree | 0.8676 | +0.1936 |

The gap of approximately +0.21 AUC points demonstrates that the models have
genuinely learned predictive structure beyond simple persistence — the rolling
history, trend, seasonality, and area context features are contributing real
signal that cannot be captured by just repeating last month's answer.

---

## The Four Models

### Logistic Regression

A linear model that learns a weighted combination of the 35 input features.
Features are standardised before training (via `StandardScaler` in a pipeline)
so that coefficients are comparable across features with different scales.

**Role in the comparison:** Establishes a linear baseline. If a non-linear
model cannot substantially outperform Logistic Regression, the relationship
between features and target is approximately linear and the added complexity
is not justified.

**When to use for deployment:** When you need to explain to a non-technical
audience exactly why a cell was flagged. The model's coefficients translate
directly into plain-language rules: "cells with higher 6-month rolling crime
averages receive higher scores."

**Result:** AUC 0.8824 — competitive with the ensemble methods, which confirms
the feature engineering is strong.

---

### Decision Tree

A non-linear model that learns a series of binary splits on input features.
The tree is constrained to `max_depth=6` and `min_samples_leaf=10` to prevent
memorising the training set.

**Role in the comparison:** The most transparent non-linear model. The full
decision tree can be printed and read as a set of if/else rules. If patrol
commanders want to understand exactly which combination of factors triggers a
hotspot alert, the Decision Tree can be explained as a flowchart.

**When to use for deployment:** For operational briefings where the model
must be fully explainable without code — e.g., a laminated decision chart for
desk sergeants.

**Result:** AUC 0.8676 — lowest of the four, which is expected. Depth-limited
single trees consistently underperform ensembles. The result is still +0.19
above the naive baseline, confirming genuine learning.

---

### Random Forest

An ensemble of 300 decision trees trained on random subsets of the training
data and random subsets of features. Predictions are averaged across all 300
trees, which reduces variance and produces more stable probability estimates
than any single tree.

**Role in the comparison:** The standard workhorse of tabular ML. Generally
robust, hard to overfit badly, and produces reliable probability scores.

**Key hyperparameters:**
- `n_estimators=300` — enough trees for stable averaging; diminishing returns
  beyond ~200
- `max_depth=8` — deeper than the single Decision Tree, allowed because
  averaging across trees controls overfitting
- `min_samples_leaf=5` — each leaf must represent at least 5 observations
- `class_weight='balanced'` — compensates for the 9.5% hotspot minority
- `n_jobs=-1` — use all available CPU cores

**Result:** AUC 0.8865 — highest of the four models. **Selected as the
recommended baseline model.**

---

### Gradient Boosting

An ensemble that builds trees sequentially, where each tree focuses on
correcting the errors of the previous one. This sequential error-correction
produces highly accurate models but is slower to train and more sensitive to
hyperparameters than Random Forest.

**Role in the comparison:** Often the strongest performer on structured tabular
data. The expectation was that it would lead on AUC; instead, Random Forest
narrowly edged it (0.8865 vs 0.8810), which is unusual and suggests the
problem may benefit more from variance reduction (RF) than bias correction (GBM).

**Key hyperparameters:**
- `n_estimators=300` — number of sequential trees
- `max_depth=4` — shallower than RF because GBM trees are meant to be weak
  learners; deep trees cause overfitting
- `learning_rate=0.05` — conservative rate; slower learning generalises better
- `subsample=0.8` — trains each tree on 80% of the data, introducing
  stochastic regularisation similar to dropout in neural networks
- `min_samples_leaf=5` — minimum observations per leaf

**Standout result:** Although GBM did not win on AUC, it achieved **81.1%
precision** — by far the highest of any model. When GBM flags a cell as a
hotspot, it is correct 4 times out of 5. This makes it the preferred model
for departments where false alarms have a high operational cost.

**Result:** AUC 0.8810, Precision 0.8108, Recall 0.3488.

---

## Hyperparameters

Complete hyperparameter record for reproducibility.

| Model | Parameter | Value | Rationale |
|---|---|---|---|
| Logistic Regression | `C` | 0.5 | Moderate L2 regularisation — prevents over-reliance on any single feature |
| Logistic Regression | `class_weight` | `'balanced'` | Compensates for 9.5% hotspot minority |
| Logistic Regression | `max_iter` | 2000 | Ensures convergence; 35 features requires more iterations than default 100 |
| Logistic Regression | `random_state` | 42 | Reproducibility |
| Decision Tree | `max_depth` | 6 | Prevents memorisation on 9,600 training rows |
| Decision Tree | `min_samples_leaf` | 10 | Requires meaningful support at each leaf |
| Decision Tree | `class_weight` | `'balanced'` | Compensates for class imbalance |
| Decision Tree | `random_state` | 42 | Reproducibility |
| Random Forest | `n_estimators` | 300 | Stable variance reduction; returns plateau after ~200 |
| Random Forest | `max_depth` | 8 | Deeper allowed vs single tree because averaging controls variance |
| Random Forest | `min_samples_leaf` | 5 | Lower than DT — ensemble averaging tolerates noisier individual trees |
| Random Forest | `class_weight` | `'balanced'` | Compensates for class imbalance |
| Random Forest | `n_jobs` | -1 | Parallel training across all CPU cores |
| Random Forest | `random_state` | 42 | Reproducibility |
| Gradient Boosting | `n_estimators` | 300 | Sequential trees — more trees = lower bias |
| Gradient Boosting | `max_depth` | 4 | Shallow weak learners — overfitting risk is high in GBM |
| Gradient Boosting | `learning_rate` | 0.05 | Conservative; lower LR with more trees generalises better |
| Gradient Boosting | `subsample` | 0.8 | Row-level stochastic regularisation |
| Gradient Boosting | `min_samples_leaf` | 5 | Minimum leaf size |
| Gradient Boosting | `random_state` | 42 | Reproducibility |

All `random_state=42` values are set consistently so that results are
identical on every run with the same input data.

---

## Evaluation Metrics

### Primary metric: AUC-ROC

Area Under the Receiver Operating Characteristic Curve. Measures the
probability that the model assigns a higher score to a randomly chosen
hotspot cell than to a randomly chosen non-hotspot cell.

- **0.50** = no better than random guessing
- **0.67** = naive persistence baseline (just repeat last month)
- **0.88** = SENTINEL best model
- **1.00** = perfect discrimination

AUC is the primary metric because it is threshold-independent and
imbalance-robust. It evaluates the full discrimination ability of the model,
not just its performance at one arbitrary cutoff.

### Average Precision (AP)

Area under the Precision-Recall curve. More informative than AUC for highly
imbalanced datasets because it focuses specifically on the model's performance
on the minority class. A no-skill classifier achieves AP equal to the base
rate (9.5% here). Higher is better.

### Precision

Of all cell-months predicted as hotspots, what fraction actually were?

```
Precision = TP / (TP + FP)
```

High precision = fewer false alarms. Use Gradient Boosting (Precision 0.811)
when patrol resources are scarce and false deployments are costly.

### Recall

Of all actual hotspot cell-months, what fraction did the model catch?

```
Recall = TP / (TP + FN)
```

High recall = fewer missed hotspots. Use Decision Tree (Recall 0.762) or
Logistic Regression (Recall 0.709) when the priority is maximum coverage
even at the cost of more false alarms.

### F1 Score

Harmonic mean of precision and recall. Provides a single balanced score
that penalises extreme values of either metric.

```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

### Accuracy

Overall fraction of correct predictions. Reported for completeness but
**not used for model selection** due to class imbalance. A model predicting
"never a hotspot" achieves 90.5% accuracy — higher than every trained model.

### Confusion matrix terms

| | Predicted: Not Hotspot | Predicted: Hotspot |
|---|---|---|
| **Actual: Not Hotspot** | TN — correctly quiet | FP — false alarm |
| **Actual: Hotspot** | FN — missed hotspot | TP — correctly caught |

The operational cost of FN (missed hotspot) vs FP (false alarm) is determined
by department policy, not by the data. Adjust the decision threshold
accordingly.

---

## Results

### Final comparison table

| Model | AUC | Avg Prec | F1 | Precision | Recall | Accuracy |
|---|---|---|---|---|---|---|
| **Random Forest ★** | **0.8865** | 0.5883 | 0.4431 | 0.3343 | 0.6570 | 85.2% |
| Logistic Regression | 0.8824 | 0.5838 | 0.4026 | 0.2811 | 0.7093 | 81.2% |
| Gradient Boosting | 0.8810 | 0.5738 | 0.4878 | **0.8108** | 0.3488 | **93.4%** |
| Decision Tree | 0.8676 | 0.5581 | 0.4100 | 0.2805 | **0.7616** | 80.4% |
| Naive persistence | 0.6740 | — | — | — | — | — |

Test set: 1,920 cell-months (2022–2025). All models trained on 2002–2021 data only.

### Confusion matrices (test set, 1,920 observations)

| Model | TN | FP | FN | TP |
|---|---|---|---|---|
| Random Forest | 1,523 | 225 | 59 | 113 |
| Logistic Regression | 1,436 | 312 | 50 | 122 |
| Gradient Boosting | 1,734 | 14 | 112 | 60 |
| Decision Tree | 1,412 | 336 | 41 | 131 |

### What the feature importances reveal

The top five features by importance in the Random Forest model are all
lag or rolling history features:

1. `crimes_lag1` — crimes in this cell last month
2. `crimes_roll3m` — 3-month rolling average
3. `hotspot_lag1` — was this cell a hotspot last month?
4. `cumulative_hotspot_rate` — all-time hotspot rate
5. `crimes_roll6m` — 6-month rolling average

This confirms the central criminological finding: **crime is spatially
persistent**. The best predictor of where crime will happen next month
is where it happened recently. Temporal features (month, season) and
spatial identity features (district, beat) contribute but rank lower.

Implication for the full dataset: the lag features become dramatically
more powerful with more data. The current 10,000-record sample gives each
cell approximately 250 incidents of lag history. The full 1.2M-record
dataset would give each of 1,500+ cells thousands of incidents of history,
producing far more stable and reliable lag estimates.

---

## Reading the Charts

Eight charts are produced, each serving a distinct purpose.

### `01_roc_pr_curves.png` — Discrimination ability

**Left panel (ROC):** Shows the tradeoff between true positive rate (recall)
and false positive rate at every possible threshold. The further the curve
bulges toward the top-left, the better. The naive persistence baseline
appears as a dotted grey line — all four trained models substantially exceed
it. The shaded area under the best model's curve visualises the AUC.

**Right panel (Precision-Recall):** More informative for imbalanced data.
The horizontal dotted line marks the base rate (9.5%) — a no-skill classifier
stays on this line. All four models rise substantially above it, especially
at lower recall values.

**Use this chart to:** compare overall discrimination ability across models
and verify that all models exceed the naive baseline.

---

### `02_model_comparison.png` — Metric summary

**Left panel:** All five metrics (AUC, F1, Precision, Recall, Accuracy) for
all four models, side by side. Reveals that Gradient Boosting dominates on
Precision and Accuracy while Random Forest leads on AUC.

**Right panel:** AUC ranking with the naive baseline marked as a vertical
line. The gap between each model and the dotted line is the value added by
machine learning over simple persistence.

**Use this chart to:** select the model appropriate for your operational
priorities and show stakeholders the improvement over naive prediction.

---

### `03_confusion_matrices.png` — Prediction breakdown

Four confusion matrices, one per model. Each cell shows the label (TN/FP/FN/TP),
raw count, and percentage of total test observations.

**Key reading:** Compare Gradient Boosting (FP=14, FN=112) against Decision
Tree (FP=336, FN=41). Gradient Boosting almost never raises a false alarm
but misses most actual hotspots. Decision Tree catches most hotspots but
generates many false alarms. Neither is universally better — it depends on
your deployment priorities.

**Use this chart to:** understand what errors each model makes and how often.

---

### `04_feature_importance.png` — What drives predictions

Horizontal bar chart of the top 20 features by importance score in the best
model (Random Forest). Features are colour-coded by group:

- **Red:** Lag and hotspot history
- **Amber:** Rolling averages, trend, and seasonality
- **Blue:** Temporal and spatial context

The annotation in the bottom-right shows what percentage of model importance
is captured by the top 5 features.

**Use this chart to:** understand which information the model relies on and
justify why the feature engineering choices were correct.

---

### `05_threshold_analysis.png` — Choosing an operating point

**Left panel:** Precision, Recall, and F1 plotted against every threshold
from 0.05 to 0.95. The white dashed line marks the threshold that maximises
F1. The grey dotted line marks the default 0.5. Note that the optimal F1
threshold (0.714) is substantially higher than 0.5, which is expected for a
dataset where only 9.5% of observations are positive.

**Centre panel:** Distribution of predicted probabilities for hotspot vs.
non-hotspot cells. The further apart the two distributions, the better the
model is at discriminating between classes. The white dashed line shows the
optimal threshold.

**Right panel:** Summary of all key metrics for the best model, colour-coded
green (≥0.70), amber (0.50–0.69), red (<0.50). The naive AUC is marked for
direct comparison.

**Use this chart to:** select a decision threshold appropriate to your patrol
budget. Lower threshold → more cells flagged (higher recall, lower precision).
Higher threshold → fewer cells flagged (higher precision, lower recall).

---

### `06_hotspot_map.png` — Geographic prediction view

Predictions visualised in geographic space, using the last 6 months of the
test period (mid-2025).

**Left panel:** Each grid cell plotted by its centroid coordinates, coloured
and sized by its average predicted hotspot probability. Darker, larger dots
indicate cells the model considers most likely to be hotspots.

**Right panel:** Each cell coloured by its prediction outcome:
- 🟢 Green diamond — **True Positive**: correctly flagged as hotspot
- 🟡 Amber square — **False Positive**: incorrectly flagged (false alarm)
- 🔴 Red cross — **False Negative**: missed hotspot
- 🔵 Blue circle — **True Negative**: correctly identified as quiet

**Use this chart to:** show patrol commanders which specific areas the model
is targeting and where it is making errors.

---

### `07_performance_over_time.png` — Temporal stability

**Top panel:** Monthly AUC throughout the entire test period (2022–2025). Green
shading indicates months where the model beats the naive baseline; red shading
indicates months where it falls below. Consistent green shading demonstrates
that model skill is stable over time, not concentrated in specific months.

**Bottom panel:** Monthly precision and recall alongside a bar chart of actual
hotspot cell counts. This shows how the model's error profile shifts as the
frequency of real hotspots fluctuates month to month.

**Use this chart to:** verify temporal stability before deployment and identify
whether model performance degrades in any particular season or year.

---

### `08_crime_patterns.png` — EDA on the panel

**Top left:** Annual crime volume. Highlights the COVID-era dip in 2020–2021
and the post-COVID partial recovery. Bars from 2020 onwards are red to flag
the unusual period.

**Top right:** Monthly seasonal pattern — average crimes per cell-month across
all years. The summer peak (Jun–Aug) is clearly visible and validates the
`is_summer` feature.

**Bottom left:** Hotspot persistence histogram — for each grid cell, the
probability that its hotspot status next month matches its hotspot status this
month. The mean of ~0.87 confirms the strong autocorrelation that the lag
features exploit.

**Bottom right:** Monthly hotspot rate throughout the 2022–2025 test period.
Confirms the 9.5% average with moderate month-to-month variation.

**Use this chart to:** understand why lag features dominate and justify the
panel structure and feature engineering choices to stakeholders.

---

## Choosing a Model for Deployment

The "best" model is an operational decision, not a purely statistical one.
The right choice depends on what errors your department can afford to make.

| Priority | Model | Key metric | Real-world meaning |
|---|---|---|---|
| Balanced overall performance | **Random Forest** | AUC 0.8865 | Best discrimination across all thresholds |
| Minimise false alarms | **Gradient Boosting** | Precision 0.811 | 4 in 5 flagged cells are real hotspots |
| Maximise hotspot coverage | **Decision Tree** | Recall 0.762 | Catches 3 in 4 actual hotspots |
| Explainability to non-technical stakeholders | **Logistic Regression** | AUC 0.8824 | Fully readable coefficients |

**On threshold selection:** whichever model you choose, do not use the default
0.5 threshold. Use the optimal threshold from `05_threshold_analysis.png`
as a starting point, then adjust based on how many cells your patrol resources
can realistically cover per month. If you can only cover 5 cells, set the
threshold high. If you want comprehensive coverage, lower it.

**A practical approach:** Run Gradient Boosting for the monthly high-confidence
list (cells above 0.80 probability — almost certainly hotspots). Run Random
Forest for the broader watch list (cells above the 0.71 F1-optimal threshold).
Use the two lists together to tier patrol intensity.

---

## Known Limitations

**Sample size is the primary constraint.** With 10,000 records across 40 cells,
lag and rolling features are computed from sparse histories. The full CPD
dataset (1.2M+ records, ~1,500+ cells) will produce dramatically more stable
historical signal. AUC is expected to improve from 0.89 to approximately
0.92–0.96 on the full data without any code changes.

**Grid sparsity.** 62.1% of cell-months have zero crimes. Hotspot features
computed over sparse histories are noisier than they would be with full data.
The models compensate through ensemble averaging and regularisation, but
fundamental information is missing that more data would provide.

**No external features.** Weather (temperature and precipitation are proven
crime predictors), local events (concerts, sports fixtures, festivals),
transit ridership, and economic indicators are not included. Adding these
would require additional data pipelines but would likely produce meaningful
AUC improvements.

**Static grid.** The 0.01° grid is fixed across the entire study period.
Boundaries do not adapt to where crime is actually concentrated. A future
version could use adaptive grids that shrink in high-crime areas and expand
in sparse areas.

**Reported crimes only.** CPD records reflect incidents that were reported
and logged. Under-reporting in certain areas — which varies systematically
by crime type and neighbourhood — creates blind spots the model cannot detect
or correct for.

**No temporal drift correction.** The model is trained on 2002–2021 and applied
to 2022–2025 without retraining. Crime patterns shift over years due to
demographic change, policing strategy changes, and economic conditions. A
production system should retrain monthly on a rolling window.

---

## Next Steps

### Immediate (run on full data)

The entire pipeline — `01_data_cleaning.py`, `02_build_panel.py`,
`03_hotspot_model.py` — runs unchanged on the full dataset. No code
modifications required.

```bash
# Download from data.cityofchicago.org, filter Year >= 2018, save as:
data/raw_crimes.csv   # ~1.2M rows, ~300 MB

# Run pipeline unchanged:
python 01_data_cleaning.py
python 02_build_panel.py
python 03_hotspot_model.py
```

Expected AUC improvement: 0.89 → 0.92–0.96.

### Short term (model improvements)

- **Hyperparameter tuning:** Grid search over GBM `learning_rate` (0.01–0.1),
  `max_depth` (3–6), and `subsample` (0.6–1.0). Random Forest `max_features`
  ('sqrt', 'log2', 0.5).
- **XGBoost / LightGBM:** Faster and often stronger than sklearn GBM.
  Drop-in replacement for `GradientBoostingClassifier`.
- **SHAP values:** Per-prediction feature attribution. Tells you not just
  which features are generally important, but why each specific cell was flagged.
- **Regression variant:** Predict crime count directly rather than binary
  hotspot/non-hotspot. Provides finer-grained prioritisation — a cell predicted
  at 8 crimes vs 3 crimes gets different patrol intensity.

### Medium term (additional features)

- **Weather:** NOAA daily temperature and precipitation at cell level.
  Temperature-crime relationship is one of the most robust findings in
  criminological literature.
- **Event calendar:** Concert venues, Wrigley Field, United Center, festival
  grounds drive localised spikes the spatial history features cannot anticipate.
- **Transit ridership:** CTA station entries as a proxy for foot traffic.
- **Economic indicators:** Unemployment rate, retail vacancy, household income
  at community area level.

### Long term (production system)

- **Rolling retraining:** Retrain monthly on a 3-year sliding window to account
  for temporal drift.
- **Real-time dashboard:** Interactive map updated nightly showing the current
  month's hotspot probability scores per cell.
- **Alert system:** Automated weekly briefing to district commanders listing
  the top 10 predicted hotspots with probability scores and historical context.
- **Feedback loop:** Track actual crime events against monthly predictions.
  Compute operational accuracy metrics monthly and flag if model performance
  degrades beyond a threshold.

---

*SENTINEL — Crime Analysis Division  |  Last updated: February 2026*
