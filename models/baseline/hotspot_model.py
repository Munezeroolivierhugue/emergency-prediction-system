"""
SENTINEL — Crime Hotspot Prediction System
==========================================
Step 3: Hotspot Prediction Model
File  : hotspot_model.py
Input : data/panel.csv
Output: output/results.json
        output/charts/*.png

Model design
------------
Unit:    grid cell × month
Target:  is_hotspot — will this cell be in the top 25% of crime activity?
Split:   temporal holdout (train 2002–2021, test 2022–2025)
         Rationale: simulates real deployment — model only knows the past
         and must predict genuinely future months it has never seen.

Four models compared on identical data:
  1. Logistic Regression  — linear baseline, interpretable
  2. Decision Tree        — non-linear, transparent (printable tree)
  3. Random Forest        — ensemble of trees, robust
  4. Gradient Boosting    — sequential ensemble, typically highest AUC

Naive persistence baseline also computed:
  "Predict that this month's hotspot status = last month's hotspot status"
  If our model cannot beat this, it adds no value.

Evaluation metrics
------------------
  Primary:   AUC-ROC  — discrimination across all thresholds (imbalance-robust)
  Secondary: Precision — when we flag a hotspot, how often are we right?
             Recall    — of actual hotspots, how many do we catch?
             F1        — harmonic mean of precision and recall
  Naive:     Persistence model AUC included for honest comparison
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
import json, os, warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model  import LogisticRegression
from sklearn.tree          import DecisionTreeClassifier
from sklearn.ensemble      import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline      import Pipeline
from sklearn.metrics       import (
    roc_auc_score, classification_report, confusion_matrix,
    roc_curve, precision_recall_curve, average_precision_score,
    f1_score, accuracy_score
)

os.makedirs('output/charts', exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────────
STYLE = {
    'figure.facecolor': '#0d1117', 'axes.facecolor':  '#161b22',
    'axes.edgecolor':   '#30363d', 'text.color':       '#e6edf3',
    'axes.labelcolor':  '#e6edf3', 'xtick.color':      '#8b949e',
    'ytick.color':      '#8b949e', 'grid.color':       '#21262d',
    'grid.linestyle':   '--',      'grid.alpha':        0.5,
    'axes.spines.top':  False,     'axes.spines.right': False,
}
plt.rcParams.update(STYLE)
BLUE   = '#58a6ff'
RED    = '#f85149'
AMBER  = '#e3b341'
GREEN  = '#3fb950'
PURPLE = '#bc8cff'

lines = []
def log(msg=''):
    print(msg)
    lines.append(str(msg))

log("=" * 65)
log("SENTINEL  |  Step 3: Hotspot Prediction Model")
log("=" * 65)

# ── Load panel ────────────────────────────────────────────────────────────────
panel = pd.read_csv('../../data/panel.csv')
log(f"\n[DATA]   {len(panel):,} cell-month observations")
log(f"         {panel['grid_cell'].nunique()} unique grid cells")
log(f"         {panel['period'].nunique()} monthly periods")
log(f"         Hotspot rate: {panel['is_hotspot'].mean():.1%}  "
    f"({panel['is_hotspot'].sum():,} hotspot / {len(panel):,} total)")

# ── Feature set ───────────────────────────────────────────────────────────────
FEATURES = [
    # Lag features — exact past counts
    'crimes_lag1',  'crimes_lag2',  'crimes_lag3',
    'violent_lag1', 'violent_lag2', 'violent_lag3',
    # Hotspot history
    'hotspot_lag1', 'hotspot_lag2', 'hotspot_lag3',
    'hotspot_streak',
    # Rolling averages (trend smoothing)
    'crimes_roll3m',  'crimes_roll6m',  'crimes_roll12m',
    'violent_roll3m', 'violent_roll6m', 'violent_roll12m',
    'hotspot_roll3m', 'hotspot_roll6m', 'hotspot_roll12m',
    # Trend & seasonality
    'crime_trend_3m', 'crimes_same_month_ly', 'hotspot_same_month_ly',
    # Long-run baseline
    'cumulative_crime_rate', 'cumulative_hotspot_rate',
    # Area context
    'area_crimes_lag1', 'area_crimes_roll3m',
    # Temporal context
    'month', 'quarter', 'month_sin', 'month_cos', 'is_summer', 'is_winter',
    # Spatial identity
    'community_area', 'district', 'beat',
]
TARGET = 'is_hotspot'
panel[FEATURES] = panel[FEATURES].fillna(0)

log(f"\n[FEATURES]  {len(FEATURES)} features, all computed from past data only")

# ── Temporal split ────────────────────────────────────────────────────────────
CUTOFF = 2022
train = panel[panel['year'] <  CUTOFF]
test  = panel[panel['year'] >= CUTOFF]

X_train, y_train = train[FEATURES], train[TARGET]
X_test,  y_test  = test[FEATURES],  test[TARGET]

log(f"\n[SPLIT]  Train: {len(train):,} cell-months  "
    f"({panel['year'].min()}–{CUTOFF-1})  hotspot rate={y_train.mean():.1%}")
log(f"         Test:  {len(test):,}  cell-months  "
    f"({CUTOFF}–{panel['year'].max()})  hotspot rate={y_test.mean():.1%}")

# ── Naive persistence baseline ────────────────────────────────────────────────
# Simplest possible model: last month's status = this month's prediction.
# Our models must beat this to demonstrate genuine learning.
naive_prob = test['hotspot_lag1'].fillna(0).values
naive_auc  = roc_auc_score(y_test, naive_prob)
log(f"\n[NAIVE]  Persistence baseline AUC: {naive_auc:.4f}")
log(f"         (Predict: hotspot this month ↔ was hotspot last month)")

# ── Model definitions ─────────────────────────────────────────────────────────
MODELS = {
    'Logistic Regression': Pipeline([
        ('scaler', StandardScaler()),
        ('clf',    LogisticRegression(max_iter=2000, class_weight='balanced',
                                      C=0.5, random_state=42)),
    ]),
    'Decision Tree': DecisionTreeClassifier(
        max_depth=6, min_samples_leaf=10,
        class_weight='balanced', random_state=42
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=300, max_depth=8, min_samples_leaf=5,
        class_weight='balanced', n_jobs=-1, random_state=42
    ),
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.8, min_samples_leaf=5, random_state=42
    ),
}
MODEL_COLORS = {
    'Logistic Regression': BLUE,
    'Decision Tree':       AMBER,
    'Random Forest':       GREEN,
    'Gradient Boosting':   RED,
}

# ── Train & evaluate ──────────────────────────────────────────────────────────
log("\n[TRAINING]")
results     = {}
probs_store = {}
preds_store = {}

for name, model in MODELS.items():
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)
    auc    = roc_auc_score(y_test, y_prob)
    cr     = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    cm     = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    results[name] = {
        'auc':       round(auc,                    4),
        'avg_prec':  round(average_precision_score(y_test, y_prob), 4),
        'accuracy':  round(cr['accuracy'],         4),
        'f1':        round(cr['1']['f1-score'],    4),
        'precision': round(cr['1']['precision'],   4),
        'recall':    round(cr['1']['recall'],      4),
        'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp),
    }
    probs_store[name] = y_prob
    preds_store[name] = y_pred
    log(f"  {name:<22}  AUC={auc:.4f}  F1={cr['1']['f1-score']:.4f}  "
        f"Prec={cr['1']['precision']:.4f}  Rec={cr['1']['recall']:.4f}")

best_name  = max(results, key=lambda k: results[k]['auc'])
best_model = MODELS[best_name]
log(f"\n  🏆  Best: {best_name}  (AUC={results[best_name]['auc']:.4f}  "
    f"vs naive={naive_auc:.4f}  Δ={results[best_name]['auc']-naive_auc:+.4f})")

# Feature importances
importances = None
if hasattr(best_model, 'feature_importances_'):
    importances = pd.Series(best_model.feature_importances_,
                            index=FEATURES).sort_values(ascending=False)

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1: ROC + PR Curves
# ─────────────────────────────────────────────────────────────────────────────
log("\n[CHARTS]")
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('SENTINEL — Hotspot Prediction: ROC & Precision-Recall Curves',
             fontsize=15, fontweight='bold', color='#e6edf3', y=1.01)

for name, y_prob in probs_store.items():
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    lw = 2.5 if name == best_name else 1.4
    axes[0].plot(fpr, tpr, lw=lw, color=MODEL_COLORS[name],
                 linestyle='-' if name == best_name else '--',
                 label=f"{name}  (AUC={results[name]['auc']:.3f})")

# Naive baseline on ROC
fpr_n, tpr_n, _ = roc_curve(y_test, naive_prob)
axes[0].plot(fpr_n, tpr_n, lw=1, color='#8b949e', linestyle=':',
             label=f'Persistence naive  (AUC={naive_auc:.3f})')
axes[0].plot([0,1],[0,1], color='#30363d', linestyle=':', lw=1, label='Random')
best_fpr, best_tpr, _ = roc_curve(y_test, probs_store[best_name])
axes[0].fill_between(best_fpr, best_tpr, alpha=0.08, color=MODEL_COLORS[best_name])
axes[0].set_title('ROC Curves', fontweight='bold', color='#e6edf3', fontsize=13)
axes[0].set_xlabel('False Positive Rate'); axes[0].set_ylabel('True Positive Rate')
axes[0].legend(fontsize=8.5, framealpha=0.3)

for name, y_prob in probs_store.items():
    prec, rec, _ = precision_recall_curve(y_test, y_prob)
    lw = 2.5 if name == best_name else 1.4
    axes[1].plot(rec, prec, lw=lw, color=MODEL_COLORS[name],
                 linestyle='-' if name == best_name else '--',
                 label=f"{name}  (AP={results[name]['avg_prec']:.3f})")
axes[1].axhline(y_test.mean(), color='#8b949e', linestyle=':', lw=1,
                label=f'No-skill ({y_test.mean():.2f})')
axes[1].set_title('Precision-Recall Curves', fontweight='bold',
                  color='#e6edf3', fontsize=13)
axes[1].set_xlabel('Recall'); axes[1].set_ylabel('Precision')
axes[1].legend(fontsize=8.5, framealpha=0.3)

plt.tight_layout()
plt.savefig('output/charts/01_roc_pr_curves.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
plt.close()
log("  01_roc_pr_curves.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 2: Model metrics comparison
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('SENTINEL — Hotspot Model Metrics Comparison',
             fontsize=15, fontweight='bold', color='#e6edf3', y=1.01)

metric_keys   = ['auc','f1','precision','recall','accuracy']
metric_labels = ['AUC','F1','Precision','Recall','Accuracy']
x = np.arange(len(metric_labels))
w = 0.18
for i, name in enumerate(MODELS):
    vals   = [results[name][m] for m in metric_keys]
    offset = (i - len(MODELS)/2) * w + w/2
    axes[0].bar(x + offset, vals, w * 0.9, label=name,
                color=MODEL_COLORS[name], edgecolor='none', alpha=0.88)
axes[0].set_xticks(x); axes[0].set_xticklabels(metric_labels, fontsize=11)
axes[0].set_ylim(0, 1.08); axes[0].set_ylabel('Score')
axes[0].set_title('All Metrics by Model', fontweight='bold', color='#e6edf3')
axes[0].legend(fontsize=9, framealpha=0.3)
axes[0].axhline(0.5, color='#30363d', linestyle='--', alpha=0.5)

# AUC ranking with naive reference
names_sorted = sorted(results, key=lambda k: results[k]['auc'])
vals_sorted  = [results[n]['auc'] for n in names_sorted]
bar_cols     = [RED if n == best_name else BLUE for n in names_sorted]
bars = axes[1].barh(names_sorted, vals_sorted, color=bar_cols,
                    edgecolor='none', height=0.45)
axes[1].axvline(naive_auc, color='#8b949e', linestyle='--', lw=1.5,
                label=f'Naive persistence ({naive_auc:.3f})')
for bar, val in zip(bars, vals_sorted):
    axes[1].text(val + 0.003, bar.get_y() + bar.get_height()/2,
                 f'{val:.4f}', va='center', fontsize=11, fontweight='bold',
                 color='#e6edf3')
axes[1].set_xlim(0, 1.05)
axes[1].set_title('AUC Ranking (vs Naive Baseline)',
                  fontweight='bold', color='#e6edf3')
axes[1].set_xlabel('AUC Score')
axes[1].legend(fontsize=9)

plt.tight_layout()
plt.savefig('output/charts/02_model_comparison.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
plt.close()
log("  02_model_comparison.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 3: Confusion matrices — all 4 models
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 4, figsize=(20, 5))
fig.suptitle('SENTINEL — Confusion Matrices: Hotspot Prediction (2022–2025 Test Set)',
             fontsize=14, fontweight='bold', color='#e6edf3')
for ax, name in zip(axes, MODELS):
    cm = confusion_matrix(y_test, preds_store[name])
    ax.imshow(cm, cmap='Blues', vmin=0)
    ax.set_xticks([0,1]); ax.set_yticks([0,1])
    ax.set_xticklabels(['Not\nHotspot','Hotspot'], fontsize=9)
    ax.set_yticklabels(['Not\nHotspot','Hotspot'], fontsize=9)
    ax.set_xlabel('Predicted', fontsize=10); ax.set_ylabel('Actual', fontsize=10)
    col = RED if name == best_name else '#e6edf3'
    ax.set_title(f'{name}\nAUC = {results[name]["auc"]:.3f}',
                 fontsize=10, fontweight='bold', color=col)
    total = cm.sum()
    labels_cm = [['TN','FP'],['FN','TP']]
    for i in range(2):
        for j in range(2):
            dark = cm[i,j] > cm.max() * 0.5
            ax.text(j, i,
                    f'{labels_cm[i][j]}\n{cm[i,j]:,}\n({cm[i,j]/total*100:.1f}%)',
                    ha='center', va='center', fontsize=8, fontweight='bold',
                    color='white' if dark else '#1a1a2e')
plt.tight_layout()
plt.savefig('output/charts/03_confusion_matrices.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
plt.close()
log("  03_confusion_matrices.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 4: Feature importances (best model)
# ─────────────────────────────────────────────────────────────────────────────
if importances is not None:
    top20 = importances.head(20)
    READABLE = {
        'crimes_lag1':            'Crimes last month (t-1)',
        'crimes_lag2':            'Crimes 2 months ago (t-2)',
        'crimes_lag3':            'Crimes 3 months ago (t-3)',
        'violent_lag1':           'Violent crimes (t-1)',
        'violent_lag2':           'Violent crimes (t-2)',
        'violent_lag3':           'Violent crimes (t-3)',
        'hotspot_lag1':           'Was hotspot last month?',
        'hotspot_lag2':           'Was hotspot 2 months ago?',
        'hotspot_lag3':           'Was hotspot 3 months ago?',
        'hotspot_streak':         'Consecutive hotspot months',
        'crimes_roll3m':          '3-month rolling avg crimes',
        'crimes_roll6m':          '6-month rolling avg crimes',
        'crimes_roll12m':         '12-month rolling avg crimes',
        'violent_roll3m':         '3-month rolling violent',
        'violent_roll6m':         '6-month rolling violent',
        'violent_roll12m':        '12-month rolling violent',
        'hotspot_roll3m':         '3-month hotspot frequency',
        'hotspot_roll6m':         '6-month hotspot frequency',
        'hotspot_roll12m':        '12-month hotspot frequency',
        'crime_trend_3m':         'Crime trend (3-month delta)',
        'crimes_same_month_ly':   'Same month last year — crimes',
        'hotspot_same_month_ly':  'Same month last year — hotspot?',
        'cumulative_crime_rate':  'All-time avg crime rate',
        'cumulative_hotspot_rate':'All-time hotspot rate',
        'area_crimes_lag1':       'Community area crimes (t-1)',
        'area_crimes_roll3m':     'Community area 3-month avg',
        'month':                  'Month of year',
        'quarter':                'Quarter',
        'month_sin':              'Month (sin — cyclical)',
        'month_cos':              'Month (cos — cyclical)',
        'is_summer':              'Summer flag (Jun–Aug)',
        'is_winter':              'Winter flag (Dec–Feb)',
        'community_area':         'Community area ID',
        'district':               'Police district',
        'beat':                   'Police beat',
    }
    labels = [READABLE.get(f, f) for f in top20.index]

    def feat_color(f):
        if 'lag' in f or 'streak' in f or 'hotspot' in f:
            return RED
        elif 'roll' in f or 'trend' in f or 'cumul' in f or 'same_month' in f or 'area' in f:
            return AMBER
        else:
            return BLUE

    bar_colors = [feat_color(f) for f in top20.index]

    fig, ax = plt.subplots(figsize=(13, 9))
    fig.suptitle(f'SENTINEL — Feature Importances: {best_name}\n'
                 f'Hotspot Prediction Model',
                 fontsize=14, fontweight='bold', color='#e6edf3')
    ax.barh(labels[::-1], top20.values[::-1],
            color=bar_colors[::-1], edgecolor='none', height=0.72)
    ax.set_xlabel('Importance Score', fontsize=11)
    for i, (val, lbl) in enumerate(zip(top20.values[::-1], labels[::-1])):
        ax.text(val + top20.max()*0.005, i, f'{val:.4f}',
                va='center', fontsize=8.5, color='#8b949e')

    legend_handles = [
        Patch(facecolor=RED,   label='Lag & hotspot history'),
        Patch(facecolor=AMBER, label='Rolling averages, trend, seasonality'),
        Patch(facecolor=BLUE,  label='Temporal & spatial context'),
    ]
    ax.legend(handles=legend_handles, fontsize=10, framealpha=0.3, loc='lower right')

    # Cumulative importance annotation
    cum = np.cumsum(top20.values)
    top5_pct = cum[4] / importances.sum() * 100
    ax.text(0.98, 0.02, f'Top 5 features explain {top5_pct:.1f}% of model',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=9,
            color='#8b949e')

    plt.tight_layout()
    plt.savefig('output/charts/04_feature_importance.png', dpi=150,
                bbox_inches='tight', facecolor='#0d1117')
    plt.close()
    log("  04_feature_importance.png")
    importances.to_csv('output/feature_importances.csv')

# ─────────────────────────────────────────────────────────────────────────────
# CHART 5: Threshold analysis (best model)
# ─────────────────────────────────────────────────────────────────────────────
best_prob = probs_store[best_name]
thresholds = np.linspace(0.05, 0.95, 100)
f1s, precs, recs, accs = [], [], [], []
for t in thresholds:
    yp = (best_prob >= t).astype(int)
    if yp.sum() == 0:
        f1s.append(0); precs.append(0); recs.append(0); accs.append(0)
    else:
        cr_t = classification_report(y_test, yp, output_dict=True, zero_division=0)
        f1s.append(cr_t['1']['f1-score'])
        precs.append(cr_t['1']['precision'])
        recs.append(cr_t['1']['recall'])
        accs.append(cr_t['accuracy'])

best_t_idx = int(np.argmax(f1s))
best_t     = thresholds[best_t_idx]

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle(f'SENTINEL — {best_name}: Threshold & Probability Analysis',
             fontsize=14, fontweight='bold', color='#e6edf3', y=1.01)

axes[0].plot(thresholds, f1s,   color=BLUE,  lw=2, label='F1')
axes[0].plot(thresholds, precs, color=AMBER, lw=2, label='Precision')
axes[0].plot(thresholds, recs,  color=GREEN, lw=2, label='Recall')
axes[0].axvline(best_t, color='white', linestyle='--', lw=1.5, alpha=0.8,
                label=f'Best F1 @ {best_t:.2f}')
axes[0].axvline(0.5, color='#30363d', linestyle=':', alpha=0.5, label='Default 0.5')
axes[0].set_title('Metrics vs Decision Threshold',
                  fontweight='bold', color='#e6edf3')
axes[0].set_xlabel('Threshold'); axes[0].set_ylabel('Score')
axes[0].legend(fontsize=9); axes[0].set_ylim(0, 1)

axes[1].hist(best_prob[y_test == 0], bins=40, alpha=0.6, color=GREEN,
             label='True Non-Hotspot', density=True)
axes[1].hist(best_prob[y_test == 1], bins=40, alpha=0.6, color=RED,
             label='True Hotspot', density=True)
axes[1].axvline(best_t, color='white', linestyle='--', lw=1.5,
                label=f'Optimal threshold ({best_t:.2f})')
axes[1].axvline(0.5, color='#8b949e', linestyle=':', alpha=0.7)
axes[1].set_title('Predicted Probability Distribution',
                  fontweight='bold', color='#e6edf3')
axes[1].set_xlabel('Predicted Hotspot Probability')
axes[1].set_ylabel('Density'); axes[1].legend(fontsize=9)

m_names  = ['AUC','Avg Precision','Accuracy','F1','Precision','Recall']
m_vals   = [results[best_name][k] for k in
            ['auc','avg_prec','accuracy','f1','precision','recall']]
m_colors = [GREEN if v >= 0.7 else AMBER if v >= 0.5 else RED for v in m_vals]
bars = axes[2].barh(m_names[::-1], m_vals[::-1],
                    color=m_colors[::-1], edgecolor='none', height=0.55)
for bar, val in zip(bars, m_vals[::-1]):
    axes[2].text(val + 0.005, bar.get_y() + bar.get_height()/2,
                 f'{val:.4f}', va='center', fontsize=11,
                 fontweight='bold', color='#e6edf3')
axes[2].set_xlim(0, 1.1)
axes[2].set_title(f'Summary Metrics: {best_name}',
                  fontweight='bold', color='#e6edf3')
axes[2].axvline(0.5, color='#30363d', linestyle='--', alpha=0.5)
axes[2].axvline(naive_auc, color='#8b949e', linestyle=':', lw=1.2,
                label=f'Naive AUC ({naive_auc:.3f})')
axes[2].legend(fontsize=9)

plt.tight_layout()
plt.savefig('output/charts/05_threshold_analysis.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
plt.close()
log("  05_threshold_analysis.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 6: Predicted hotspot map — last 6 months of test set
# ─────────────────────────────────────────────────────────────────────────────
test_copy           = test.copy()
test_copy['y_prob'] = probs_store[best_name]
test_copy['y_pred'] = preds_store[best_name]

last_6 = sorted(test['period'].unique())[-6:]
recent = test_copy[test_copy['period'].isin(last_6)].copy()

cell_map = recent.groupby('grid_cell').agg(
    avg_prob        = ('y_prob',     'mean'),
    predicted_hs    = ('y_pred',     'max'),
    actual_hs       = ('is_hotspot', 'max'),
    lat             = ('lat',        'mean'),
    lon             = ('lon',        'mean'),
).reset_index()

cell_map['outcome'] = 'True Negative'
cell_map.loc[(cell_map['predicted_hs']==1) & (cell_map['actual_hs']==1), 'outcome'] = 'True Positive'
cell_map.loc[(cell_map['predicted_hs']==1) & (cell_map['actual_hs']==0), 'outcome'] = 'False Positive'
cell_map.loc[(cell_map['predicted_hs']==0) & (cell_map['actual_hs']==1), 'outcome'] = 'False Negative'

outcome_style = {
    'True Positive':  (GREEN, 120, 'D', 'Caught correctly (TP)'),
    'False Positive': (AMBER, 80,  's', 'False alarm (FP)'),
    'False Negative': (RED,   80,  'X', 'Missed hotspot (FN)'),
    'True Negative':  (BLUE,  30,  'o', 'Correctly quiet (TN)'),
}

fig, axes = plt.subplots(1, 2, figsize=(16, 9))
fig.suptitle(f'SENTINEL — Predicted Hotspot Map  |  {best_name}\n'
             f'Last 6 months of test period ({last_6[0]} – {last_6[-1]})',
             fontsize=13, fontweight='bold', color='#e6edf3')

# Left: probability heat map
sc = axes[0].scatter(cell_map['lon'], cell_map['lat'],
                     c=cell_map['avg_prob'], cmap='YlOrRd', vmin=0, vmax=1,
                     s=cell_map['avg_prob'] * 300 + 25,
                     alpha=0.85, edgecolors='white', linewidths=0.4, zorder=3)
plt.colorbar(sc, ax=axes[0], label='Avg Hotspot Probability', shrink=0.8)
axes[0].set_title('Predicted Hotspot Probability\n(dot size ∝ probability)',
                  fontweight='bold', color='#e6edf3')
axes[0].set_xlabel('Longitude'); axes[0].set_ylabel('Latitude')
axes[0].set_facecolor('#0d1117')

# Right: TP / FP / FN / TN breakdown
for outcome, (color, size, marker, label) in outcome_style.items():
    sub = cell_map[cell_map['outcome'] == outcome]
    if len(sub):
        axes[1].scatter(sub['lon'], sub['lat'], c=color, s=size,
                        marker=marker, alpha=0.85, label=f'{label} (n={len(sub)})',
                        edgecolors='white', linewidths=0.4, zorder=3)
axes[1].set_title('Prediction Outcomes per Cell\n(last 6 test months)',
                  fontweight='bold', color='#e6edf3')
axes[1].set_xlabel('Longitude'); axes[1].set_ylabel('Latitude')
axes[1].legend(fontsize=9, framealpha=0.3)
axes[1].set_facecolor('#0d1117')

plt.tight_layout()
plt.savefig('output/charts/06_hotspot_map.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
plt.close()
log("  06_hotspot_map.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 7: Performance over time (monthly AUC in test period)
# ─────────────────────────────────────────────────────────────────────────────
test_copy['period_dt'] = pd.to_datetime(test_copy['period'])
monthly_rows = []
for period, grp in test_copy.groupby('period'):
    if grp['is_hotspot'].nunique() < 2 or grp['y_pred'].sum() == 0:
        continue
    cr_g = classification_report(grp['is_hotspot'], grp['y_pred'],
                                 output_dict=True, zero_division=0)
    monthly_rows.append({
        'period':      period,
        'period_dt':   pd.to_datetime(period),
        'auc':         roc_auc_score(grp['is_hotspot'], grp['y_prob']),
        'precision':   cr_g['1']['precision'],
        'recall':      cr_g['1']['recall'],
        'n_hotspots':  grp['is_hotspot'].sum(),
        'n_predicted': grp['y_pred'].sum(),
    })
mp = pd.DataFrame(monthly_rows)

fig, axes = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
fig.suptitle(f'SENTINEL — {best_name}: Month-by-Month Performance (2022–2025)',
             fontsize=14, fontweight='bold', color='#e6edf3')

axes[0].plot(mp['period_dt'], mp['auc'], color=BLUE, lw=2, marker='o',
             markersize=4, label='Monthly AUC')
axes[0].axhline(results[best_name]['auc'], color=RED, linestyle='--',
                lw=1.5, alpha=0.8,
                label=f'Overall AUC ({results[best_name]["auc"]:.3f})')
axes[0].axhline(naive_auc, color='#8b949e', linestyle=':', lw=1.2,
                label=f'Naive baseline ({naive_auc:.3f})')
axes[0].fill_between(mp['period_dt'], naive_auc, mp['auc'],
                     where=mp['auc'] >= naive_auc, alpha=0.12, color=GREEN,
                     label='Above naive')
axes[0].fill_between(mp['period_dt'], naive_auc, mp['auc'],
                     where=mp['auc'] < naive_auc, alpha=0.12, color=RED,
                     label='Below naive')
axes[0].set_ylabel('AUC Score'); axes[0].set_ylim(0, 1.05)
axes[0].legend(fontsize=9, framealpha=0.3)
axes[0].set_title('Monthly AUC vs Naive Baseline', fontweight='bold',
                  color='#e6edf3')

axes[1].plot(mp['period_dt'], mp['precision'], color=AMBER, lw=2,
             marker='s', markersize=4, label='Precision')
axes[1].plot(mp['period_dt'], mp['recall'],    color=GREEN, lw=2,
             marker='^', markersize=4, label='Recall')
ax1b = axes[1].twinx()
ax1b.bar(mp['period_dt'], mp['n_hotspots'], color=BLUE, alpha=0.18,
         width=20, label='Actual hotspot cells')
ax1b.set_ylabel('Hotspot count', color='#8b949e')
axes[1].set_ylabel('Score'); axes[1].set_ylim(0, 1.05)
axes[1].legend(fontsize=9, framealpha=0.3, loc='upper left')
axes[1].set_title('Monthly Precision & Recall', fontweight='bold',
                  color='#e6edf3')
axes[1].set_xlabel('Month')

plt.tight_layout()
plt.savefig('output/charts/07_performance_over_time.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
plt.close()
log("  07_performance_over_time.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 8: Crime trends — EDA on panel data
# ─────────────────────────────────────────────────────────────────────────────
panel['period_dt'] = pd.to_datetime(panel['period'])
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('SENTINEL — Crime Pattern Analysis: Panel Data (2002–2025)',
             fontsize=14, fontweight='bold', color='#e6edf3')

# Annual total crimes
annual = panel.groupby('year')['total_crimes'].sum()
bar_c  = [RED if y >= 2020 else BLUE for y in annual.index]
bars   = axes[0,0].bar(annual.index, annual.values, color=bar_c,
                       edgecolor='none', width=0.7)
for bar, val in zip(bars, annual.values):
    axes[0,0].text(bar.get_x() + bar.get_width()/2,
                   bar.get_height() + annual.max()*0.01,
                   f'{val:.0f}', ha='center', va='bottom', fontsize=7.5,
                   color='#8b949e')
axes[0,0].set_title('Annual Crime Volume (all grid cells)',
                    fontweight='bold', color='#e6edf3')
axes[0,0].set_ylabel('Total Crimes')
axes[0,0].axvline(2019.5, color=AMBER, linestyle='--', alpha=0.7, label='COVID onset')
axes[0,0].legend(fontsize=9)

# Monthly seasonal pattern
monthly_season = panel.groupby('month')['total_crimes'].mean()
month_names = ['Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']
axes[0,1].fill_between(monthly_season.index, monthly_season.values,
                       alpha=0.25, color=BLUE)
axes[0,1].plot(monthly_season.index, monthly_season.values,
               color=BLUE, lw=2.5, marker='o', markersize=5)
axes[0,1].set_xticks(range(1,13))
axes[0,1].set_xticklabels(month_names, fontsize=9)
axes[0,1].set_title('Seasonal Pattern (avg crimes per cell-month)',
                    fontweight='bold', color='#e6edf3')
axes[0,1].set_ylabel('Avg Crimes')

# Hotspot persistence: how often do cells remain hotspots?
persistence = panel.groupby('grid_cell').apply(
    lambda g: (g['hotspot_lag1'] == g['is_hotspot']).mean()
).dropna()
axes[1,0].hist(persistence.values, bins=20, color=AMBER, edgecolor='none', alpha=0.85)
axes[1,0].axvline(persistence.mean(), color='white', linestyle='--', lw=2,
                  label=f'Mean = {persistence.mean():.2f}')
axes[1,0].set_title('Hotspot Persistence per Cell\n'
                    '(P(same status as last month))',
                    fontweight='bold', color='#e6edf3')
axes[1,0].set_xlabel('Persistence Rate'); axes[1,0].set_ylabel('Grid Cells')
axes[1,0].legend(fontsize=9)

# Hotspot rate over time (test period)
hs_trend = panel[panel['year'] >= CUTOFF].groupby('period_dt')['is_hotspot'].mean()
axes[1,1].plot(hs_trend.index, hs_trend.values * 100, color=RED, lw=2,
               marker='o', markersize=3)
axes[1,1].fill_between(hs_trend.index, hs_trend.values * 100,
                       alpha=0.15, color=RED)
axes[1,1].set_title('Monthly Hotspot Rate in Test Period (2022–2025)',
                    fontweight='bold', color='#e6edf3')
axes[1,1].set_ylabel('% of Cells that are Hotspots')
axes[1,1].set_xlabel('Month')

plt.tight_layout()
plt.savefig('output/charts/08_crime_patterns.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
plt.close()
log("  08_crime_patterns.png")

# ─────────────────────────────────────────────────────────────────────────────
# FINAL TABLE & SAVE
# ─────────────────────────────────────────────────────────────────────────────
log(f"\n{'='*65}")
log("HOTSPOT PREDICTION — FINAL RESULTS TABLE")
log(f"{'='*65}")
log(f"  Naive persistence baseline AUC: {naive_auc:.4f}")
log(f"  {'Model':<22} {'AUC':>7} {'F1':>7} {'Prec':>7} {'Rec':>7} {'Acc':>7}")
log(f"  {'-'*58}")
for name in sorted(results, key=lambda k: -results[k]['auc']):
    r    = results[name]
    star = " ★" if name == best_name else ""
    beat = f"  +{r['auc']-naive_auc:.4f} vs naive" if name == best_name else ""
    log(f"  {name+star:<22} {r['auc']:>7.4f} {r['f1']:>7.4f} "
        f"{r['precision']:>7.4f} {r['recall']:>7.4f} {r['accuracy']:>7.4f}{beat}")
log(f"{'='*65}")

output = {
    'system':     'SENTINEL — Crime Hotspot Prediction',
    'problem':    'Predict which grid cells will be crime hotspots next month',
    'unit':       'grid_cell × month',
    'target':     'is_hotspot (top 25% of non-zero cell-months by crime count)',
    'split': {
        'method': 'temporal holdout',
        'train':  f"{panel['year'].min()}–{CUTOFF-1}",
        'test':   f"{CUTOFF}–{panel['year'].max()}",
        'n_train': len(train), 'n_test': len(test),
    },
    'naive_persistence_auc': round(naive_auc, 4),
    'best_model':  best_name,
    'best_thresh': round(float(best_t), 3),
    'features':   {'count': len(FEATURES), 'names': FEATURES},
    'models':     results,
}
with open('output/results.json', 'w') as f:
    json.dump(output, f, indent=2)

with open('output/model_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

log(f"\n✅  Results:  output/results.json")
log(f"✅  Charts:   output/charts/ (8 charts)")
log(f"✅  Report:   output/model_report.txt")