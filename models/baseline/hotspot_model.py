"""
SENTINEL — 911 Hotspot Prediction System
=========================================
Step 3: Baseline Hotspot Prediction Model
File  : models/baseline/03_hotspot_model.py
Input : data/processed/panel.csv
Output: models/baseline/output/results.json
        models/baseline/output/charts/*.png

Model design
------------
Unit:    township × month
Target:  is_hotspot — will this township be in the top 25%
         of 911 call volume next month?
Split:   temporal holdout — train on earlier months,
         test on the final 3 months of the dataset.

Four models + naive persistence baseline.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
    roc_curve, precision_recall_curve, average_precision_score
)

os.makedirs('models/baseline/output/charts', exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0d1117', 'axes.facecolor': '#161b22',
    'axes.edgecolor':   '#30363d', 'text.color':     '#e6edf3',
    'axes.labelcolor':  '#e6edf3', 'xtick.color':    '#8b949e',
    'ytick.color':      '#8b949e', 'grid.color':     '#21262d',
    'grid.linestyle':   '--',      'grid.alpha':      0.5,
    'axes.spines.top':  False,     'axes.spines.right': False,
})
BLUE = '#58a6ff'; RED = '#f85149'; AMBER = '#e3b341'
GREEN = '#3fb950'; PURPLE = '#bc8cff'

lines = []
def log(msg=''):
    print(msg)
    lines.append(str(msg))

log('=' * 65)
log('SENTINEL  |  Step 3: Baseline Hotspot Prediction Model')
log('=' * 65)

# ── Load ──────────────────────────────────────────────────────────────────────
panel = pd.read_csv('data/processed/panel.csv')
log(f'\n[DATA]   {len(panel):,} township-month observations')
log(f'         {panel["twp"].nunique()} townships')
log(f'         {panel["period"].nunique()} monthly periods  '
    f'({panel["period"].min()} → {panel["period"].max()})')
log(f'         Hotspot rate: {panel["is_hotspot"].mean():.1%}  '
    f'({panel["is_hotspot"].sum():,} / {len(panel):,})')

# ── Features ──────────────────────────────────────────────────────────────────
FEATURES = [
    # Lag features
    'calls_lag1',    'calls_lag2',    'calls_lag3',
    'critical_lag1', 'critical_lag2', 'critical_lag3',
    'hotspot_lag1',  'hotspot_lag2',  'hotspot_lag3',
    'hotspot_streak',
    # Rolling averages
    'calls_roll3m',    'calls_roll6m',    'calls_roll12m',
    'critical_roll3m', 'critical_roll6m', 'critical_roll12m',
    'hotspot_roll3m',  'hotspot_roll6m',  'hotspot_roll12m',
    # Trend & seasonality
    'call_trend_3m',
    'calls_same_month_ly', 'hotspot_same_month_ly',
    # Long-run baseline
    'cumulative_call_rate', 'cumulative_hotspot_rate',
    # Temporal context
    'month', 'quarter', 'month_sin', 'month_cos',
    'is_summer', 'is_winter',
]
TARGET = 'is_hotspot'
panel[FEATURES] = panel[FEATURES].fillna(0)
log(f'\n[FEATURES]  {len(FEATURES)} features, all lagged — no current-period leakage')

# ── Temporal split ────────────────────────────────────────────────────────────
# Dataset: 13 months (2015-12 → 2016-12), after 3-month warmup = 10 months.
# Train on first 7 months, test on last 3.
sorted_periods = sorted(panel['period'].unique())
n_test    = 3
cutoff    = sorted_periods[-n_test]
train     = panel[panel['period'] <  cutoff]
test      = panel[panel['period'] >= cutoff]

X_train, y_train = train[FEATURES], train[TARGET]
X_test,  y_test  = test[FEATURES],  test[TARGET]

log(f'\n[SPLIT]  Train: {len(train):,}  '
    f'({sorted_periods[0]} → {sorted_periods[-n_test-1]})  '
    f'hotspot rate={y_train.mean():.1%}')
log(f'         Test:  {len(test):,}   '
    f'({cutoff} → {sorted_periods[-1]})  '
    f'hotspot rate={y_test.mean():.1%}')
log(f'         (Note: small dataset — 13 months. Full dataset will give')
log(f'          stable train/test split with multiple years of holdout.)')

# ── Naive persistence baseline ────────────────────────────────────────────────
naive_prob = test['hotspot_lag1'].fillna(0).values
naive_auc  = roc_auc_score(y_test, naive_prob)
log(f'\n[NAIVE]  Persistence baseline AUC: {naive_auc:.4f}')
log(f'         (Predict: hotspot this month = hotspot last month)')

# ── Models ────────────────────────────────────────────────────────────────────
MODELS = {
    'Logistic Regression': Pipeline([
        ('scaler', StandardScaler()),
        ('clf',    LogisticRegression(max_iter=2000, class_weight='balanced',
                                      C=0.5, random_state=42)),
    ]),
    'Decision Tree': DecisionTreeClassifier(
        max_depth=4, min_samples_leaf=5,
        class_weight='balanced', random_state=42
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=300, max_depth=6, min_samples_leaf=3,
        class_weight='balanced', n_jobs=-1, random_state=42
    ),
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=200, max_depth=3, learning_rate=0.05,
        subsample=0.8, min_samples_leaf=3, random_state=42
    ),
}
MODEL_COLORS = {
    'Logistic Regression': BLUE, 'Decision Tree': AMBER,
    'Random Forest': GREEN,      'Gradient Boosting': RED,
}

# ── Train & evaluate ──────────────────────────────────────────────────────────
log('\n[TRAINING]')
results, probs_store, preds_store = {}, {}, {}

for name, model in MODELS.items():
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)
    auc    = roc_auc_score(y_test, y_prob)
    cr     = classification_report(y_test, y_pred,
                                   output_dict=True, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    results[name] = {
        'auc':       round(auc, 4),
        'avg_prec':  round(average_precision_score(y_test, y_prob), 4),
        'accuracy':  round(cr['accuracy'], 4),
        'f1':        round(cr['1']['f1-score'], 4),
        'precision': round(cr['1']['precision'], 4),
        'recall':    round(cr['1']['recall'], 4),
        'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp),
    }
    probs_store[name] = y_prob
    preds_store[name] = y_pred
    log(f'  {name:<22}  AUC={auc:.4f}  F1={cr["1"]["f1-score"]:.4f}  '
        f'Prec={cr["1"]["precision"]:.4f}  Rec={cr["1"]["recall"]:.4f}')

best_name  = max(results, key=lambda k: results[k]['auc'])
best_model = MODELS[best_name]
log(f'\n  🏆  Best: {best_name}  (AUC={results[best_name]["auc"]:.4f}  '
    f'vs naive={naive_auc:.4f}  '
    f'Δ={results[best_name]["auc"] - naive_auc:+.4f})')

importances = None
if hasattr(best_model, 'feature_importances_'):
    importances = pd.Series(best_model.feature_importances_,
                            index=FEATURES).sort_values(ascending=False)
elif hasattr(best_model, 'named_steps'):
    clf = best_model.named_steps.get('clf')
    if hasattr(clf, 'coef_'):
        importances = pd.Series(np.abs(clf.coef_[0]),
                                index=FEATURES).sort_values(ascending=False)

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1: ROC & PR Curves
# ─────────────────────────────────────────────────────────────────────────────
log('\n[CHARTS]')
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('SENTINEL — 911 Hotspot Prediction: ROC & Precision-Recall Curves',
             fontsize=15, fontweight='bold', color='#e6edf3', y=1.01)

for name, y_prob in probs_store.items():
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    lw = 2.5 if name == best_name else 1.4
    axes[0].plot(fpr, tpr, lw=lw, color=MODEL_COLORS[name],
                 linestyle='-' if name == best_name else '--',
                 label=f'{name}  (AUC={results[name]["auc"]:.3f})')

fpr_n, tpr_n, _ = roc_curve(y_test, naive_prob)
axes[0].plot(fpr_n, tpr_n, lw=1, color='#8b949e', linestyle=':',
             label=f'Persistence naive  (AUC={naive_auc:.3f})')
axes[0].plot([0, 1], [0, 1], color='#30363d', linestyle=':', lw=1)
best_fpr, best_tpr, _ = roc_curve(y_test, probs_store[best_name])
axes[0].fill_between(best_fpr, best_tpr, alpha=0.08,
                     color=MODEL_COLORS[best_name])
axes[0].set_title('ROC Curves', fontweight='bold', color='#e6edf3', fontsize=13)
axes[0].set_xlabel('False Positive Rate')
axes[0].set_ylabel('True Positive Rate')
axes[0].legend(fontsize=8.5, framealpha=0.3)

for name, y_prob in probs_store.items():
    prec, rec, _ = precision_recall_curve(y_test, y_prob)
    lw = 2.5 if name == best_name else 1.4
    axes[1].plot(rec, prec, lw=lw, color=MODEL_COLORS[name],
                 linestyle='-' if name == best_name else '--',
                 label=f'{name}  (AP={results[name]["avg_prec"]:.3f})')
axes[1].axhline(y_test.mean(), color='#8b949e', linestyle=':', lw=1,
                label=f'No-skill ({y_test.mean():.2f})')
axes[1].set_title('Precision-Recall Curves', fontweight='bold',
                  color='#e6edf3', fontsize=13)
axes[1].set_xlabel('Recall')
axes[1].set_ylabel('Precision')
axes[1].legend(fontsize=8.5, framealpha=0.3)

plt.tight_layout()
plt.savefig('models/baseline/output/charts/01_roc_pr_curves.png',
            dpi=150, bbox_inches='tight', facecolor='#0d1117')
plt.close()
log('  01_roc_pr_curves.png')

# ─────────────────────────────────────────────────────────────────────────────
# CHART 2: Model metrics comparison
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('SENTINEL — Model Metrics Comparison',
             fontsize=15, fontweight='bold', color='#e6edf3', y=1.01)

metric_keys   = ['auc', 'f1', 'precision', 'recall', 'accuracy']
metric_labels = ['AUC', 'F1', 'Precision', 'Recall', 'Accuracy']
x = np.arange(len(metric_labels))
w = 0.18
for i, name in enumerate(MODELS):
    vals   = [results[name][m] for m in metric_keys]
    offset = (i - len(MODELS) / 2) * w + w / 2
    axes[0].bar(x + offset, vals, w * 0.9, label=name,
                color=MODEL_COLORS[name], edgecolor='none', alpha=0.88)
axes[0].set_xticks(x)
axes[0].set_xticklabels(metric_labels, fontsize=11)
axes[0].set_ylim(0, 1.08)
axes[0].set_ylabel('Score')
axes[0].set_title('All Metrics by Model', fontweight='bold', color='#e6edf3')
axes[0].legend(fontsize=9, framealpha=0.3)
axes[0].axhline(0.5, color='#30363d', linestyle='--', alpha=0.5)

names_sorted = sorted(results, key=lambda k: results[k]['auc'])
vals_sorted  = [results[n]['auc'] for n in names_sorted]
bar_cols     = [RED if n == best_name else BLUE for n in names_sorted]
bars = axes[1].barh(names_sorted, vals_sorted, color=bar_cols,
                    edgecolor='none', height=0.45)
axes[1].axvline(naive_auc, color='#8b949e', linestyle='--', lw=1.5,
                label=f'Naive persistence ({naive_auc:.3f})')
for bar, val in zip(bars, vals_sorted):
    axes[1].text(val + 0.003, bar.get_y() + bar.get_height() / 2,
                 f'{val:.4f}', va='center', fontsize=11,
                 fontweight='bold', color='#e6edf3')
axes[1].set_xlim(0, 1.05)
axes[1].set_title('AUC Ranking (vs Naive Baseline)',
                  fontweight='bold', color='#e6edf3')
axes[1].set_xlabel('AUC Score')
axes[1].legend(fontsize=9)

plt.tight_layout()
plt.savefig('models/baseline/output/charts/02_model_comparison.png',
            dpi=150, bbox_inches='tight', facecolor='#0d1117')
plt.close()
log('  02_model_comparison.png')

# ─────────────────────────────────────────────────────────────────────────────
# CHART 3: Confusion matrices
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 4, figsize=(20, 5))
fig.suptitle('SENTINEL — Confusion Matrices (Test Set)',
             fontsize=14, fontweight='bold', color='#e6edf3')
for ax, name in zip(axes, MODELS):
    cm = confusion_matrix(y_test, preds_store[name])
    ax.imshow(cm, cmap='Blues', vmin=0)
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(['Not\nHotspot', 'Hotspot'], fontsize=9)
    ax.set_yticklabels(['Not\nHotspot', 'Hotspot'], fontsize=9)
    ax.set_xlabel('Predicted', fontsize=10)
    ax.set_ylabel('Actual', fontsize=10)
    col = RED if name == best_name else '#e6edf3'
    ax.set_title(f'{name}\nAUC = {results[name]["auc"]:.3f}',
                 fontsize=10, fontweight='bold', color=col)
    total     = cm.sum()
    labels_cm = [['TN', 'FP'], ['FN', 'TP']]
    for i in range(2):
        for j in range(2):
            dark = cm[i, j] > cm.max() * 0.5
            ax.text(j, i,
                    f'{labels_cm[i][j]}\n{cm[i, j]:,}\n'
                    f'({cm[i, j] / total * 100:.1f}%)',
                    ha='center', va='center', fontsize=8,
                    fontweight='bold',
                    color='white' if dark else '#1a1a2e')
plt.tight_layout()
plt.savefig('models/baseline/output/charts/03_confusion_matrices.png',
            dpi=150, bbox_inches='tight', facecolor='#0d1117')
plt.close()
log('  03_confusion_matrices.png')

# ─────────────────────────────────────────────────────────────────────────────
# CHART 4: Feature importances
# ─────────────────────────────────────────────────────────────────────────────
if importances is not None:
    top20 = importances.head(20)
    READABLE = {
        'calls_lag1':            'Total calls last month (t-1)',
        'calls_lag2':            'Total calls 2 months ago (t-2)',
        'calls_lag3':            'Total calls 3 months ago (t-3)',
        'critical_lag1':         'Critical calls (t-1)',
        'critical_lag2':         'Critical calls (t-2)',
        'critical_lag3':         'Critical calls (t-3)',
        'hotspot_lag1':          'Was hotspot last month?',
        'hotspot_lag2':          'Was hotspot 2 months ago?',
        'hotspot_lag3':          'Was hotspot 3 months ago?',
        'hotspot_streak':        'Consecutive hotspot months',
        'calls_roll3m':          '3-month rolling avg calls',
        'calls_roll6m':          '6-month rolling avg calls',
        'calls_roll12m':         '12-month rolling avg calls',
        'critical_roll3m':       '3-month rolling critical calls',
        'critical_roll6m':       '6-month rolling critical calls',
        'critical_roll12m':      '12-month rolling critical calls',
        'hotspot_roll3m':        '3-month hotspot frequency',
        'hotspot_roll6m':        '6-month hotspot frequency',
        'hotspot_roll12m':       '12-month hotspot frequency',
        'call_trend_3m':         'Call trend (3-month delta)',
        'calls_same_month_ly':   'Same month last year — calls',
        'hotspot_same_month_ly': 'Same month last year — hotspot?',
        'cumulative_call_rate':  'All-time avg call rate',
        'cumulative_hotspot_rate':'All-time hotspot rate',
        'month':                 'Month of year',
        'quarter':               'Quarter',
        'month_sin':             'Month (sin — cyclical)',
        'month_cos':             'Month (cos — cyclical)',
        'is_summer':             'Summer flag (Jun–Aug)',
        'is_winter':             'Winter flag (Dec–Feb)',
    }
    labels = [READABLE.get(f, f) for f in top20.index]

    def feat_color(f):
        if 'lag' in f or 'streak' in f: return RED
        elif 'roll' in f or 'trend' in f or 'cumul' in f or 'same' in f: return AMBER
        else: return BLUE

    fig, ax = plt.subplots(figsize=(13, 9))
    fig.suptitle(f'SENTINEL — Feature Importances: {best_name}',
                 fontsize=14, fontweight='bold', color='#e6edf3')
    bar_colors = [feat_color(f) for f in top20.index]
    ax.barh(labels[::-1], top20.values[::-1],
            color=bar_colors[::-1], edgecolor='none', height=0.72)
    ax.set_xlabel('Importance Score', fontsize=11)
    for i, val in enumerate(top20.values[::-1]):
        ax.text(val + top20.max() * 0.005, i, f'{val:.4f}',
                va='center', fontsize=8.5, color='#8b949e')
    ax.legend(handles=[
        Patch(facecolor=RED,   label='Lag & hotspot history'),
        Patch(facecolor=AMBER, label='Rolling, trend, seasonality'),
        Patch(facecolor=BLUE,  label='Temporal context'),
    ], fontsize=10, framealpha=0.3, loc='lower right')
    cum = np.cumsum(top20.values)
    ax.text(0.98, 0.02,
            f'Top 5 features explain {cum[4]/importances.sum()*100:.1f}% of model',
            transform=ax.transAxes, ha='right', va='bottom',
            fontsize=9, color='#8b949e')
    plt.tight_layout()
    plt.savefig('models/baseline/output/charts/04_feature_importance.png',
                dpi=150, bbox_inches='tight', facecolor='#0d1117')
    plt.close()
    log('  04_feature_importance.png')
    importances.to_csv('models/baseline/output/feature_importances.csv')

# ─────────────────────────────────────────────────────────────────────────────
# CHART 5: Threshold analysis
# ─────────────────────────────────────────────────────────────────────────────
best_prob  = probs_store[best_name]
thresholds = np.linspace(0.05, 0.95, 100)
f1s, precs, recs = [], [], []
for t in thresholds:
    yp = (best_prob >= t).astype(int)
    if yp.sum() == 0:
        f1s.append(0); precs.append(0); recs.append(0)
    else:
        cr_t = classification_report(y_test, yp,
                                     output_dict=True, zero_division=0)
        f1s.append(cr_t['1']['f1-score'])
        precs.append(cr_t['1']['precision'])
        recs.append(cr_t['1']['recall'])

best_t = float(thresholds[int(np.argmax(f1s))])

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle(f'SENTINEL — {best_name}: Threshold & Probability Analysis',
             fontsize=14, fontweight='bold', color='#e6edf3', y=1.01)

axes[0].plot(thresholds, f1s,   color=BLUE,  lw=2, label='F1')
axes[0].plot(thresholds, precs, color=AMBER, lw=2, label='Precision')
axes[0].plot(thresholds, recs,  color=GREEN, lw=2, label='Recall')
axes[0].axvline(best_t, color='white', linestyle='--', lw=1.5,
                label=f'Best F1 @ {best_t:.2f}')
axes[0].axvline(0.5, color='#30363d', linestyle=':', alpha=0.5)
axes[0].set_title('Metrics vs Decision Threshold',
                  fontweight='bold', color='#e6edf3')
axes[0].set_xlabel('Threshold'); axes[0].set_ylabel('Score')
axes[0].legend(fontsize=9); axes[0].set_ylim(0, 1)

axes[1].hist(best_prob[y_test == 0], bins=20, alpha=0.6, color=GREEN,
             label='True Non-Hotspot', density=True)
axes[1].hist(best_prob[y_test == 1], bins=20, alpha=0.6, color=RED,
             label='True Hotspot', density=True)
axes[1].axvline(best_t, color='white', linestyle='--', lw=1.5,
                label=f'Optimal threshold ({best_t:.2f})')
axes[1].set_title('Predicted Probability Distribution',
                  fontweight='bold', color='#e6edf3')
axes[1].set_xlabel('Predicted Hotspot Probability')
axes[1].set_ylabel('Density'); axes[1].legend(fontsize=9)

m_names = ['AUC', 'Avg Precision', 'Accuracy', 'F1', 'Precision', 'Recall']
m_vals  = [results[best_name][k] for k in
           ['auc', 'avg_prec', 'accuracy', 'f1', 'precision', 'recall']]
m_colors = [GREEN if v >= 0.7 else AMBER if v >= 0.5 else RED for v in m_vals]
bars = axes[2].barh(m_names[::-1], m_vals[::-1],
                    color=m_colors[::-1], edgecolor='none', height=0.55)
for bar, val in zip(bars, m_vals[::-1]):
    axes[2].text(val + 0.005, bar.get_y() + bar.get_height() / 2,
                 f'{val:.4f}', va='center', fontsize=11,
                 fontweight='bold', color='#e6edf3')
axes[2].set_xlim(0, 1.1)
axes[2].set_title(f'Summary Metrics: {best_name}',
                  fontweight='bold', color='#e6edf3')
axes[2].axvline(naive_auc, color='#8b949e', linestyle=':', lw=1.2,
                label=f'Naive AUC ({naive_auc:.3f})')
axes[2].legend(fontsize=9)

plt.tight_layout()
plt.savefig('models/baseline/output/charts/05_threshold_analysis.png',
            dpi=150, bbox_inches='tight', facecolor='#0d1117')
plt.close()
log('  05_threshold_analysis.png')

# ─────────────────────────────────────────────────────────────────────────────
# CHART 6: Severity & type distribution (from cleaned data)
# ─────────────────────────────────────────────────────────────────────────────
cleaned = pd.read_csv('data/processed/incidents_cleaned.csv')
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('SENTINEL — 911 Call Severity & Type Distribution',
             fontsize=14, fontweight='bold', color='#e6edf3')

sev_counts = (cleaned['Severity']
              .value_counts()
              .reindex(['Critical', 'High', 'Medium', 'Low']))
sev_colors = [RED, AMBER, BLUE, GREEN]
axes[0].bar(sev_counts.index, sev_counts.values,
            color=sev_colors, edgecolor='none', width=0.6)
for i, (idx, val) in enumerate(sev_counts.items()):
    axes[0].text(i, val + sev_counts.max() * 0.01,
                 f'{val:,}\n({val/len(cleaned):.1%})',
                 ha='center', va='bottom', fontsize=10, color='#e6edf3')
axes[0].set_title('Severity Distribution', fontweight='bold', color='#e6edf3')
axes[0].set_ylabel('Call Count')

type_counts = cleaned['Type'].value_counts()
type_colors = [RED, BLUE, AMBER]
axes[1].bar(type_counts.index, type_counts.values,
            color=type_colors[:len(type_counts)],
            edgecolor='none', width=0.5)
for i, (idx, val) in enumerate(type_counts.items()):
    axes[1].text(i, val + type_counts.max() * 0.01,
                 f'{val:,}\n({val/len(cleaned):.1%})',
                 ha='center', va='bottom', fontsize=10, color='#e6edf3')
axes[1].set_title('Call Type Distribution (EMS / Traffic / Fire)',
                  fontweight='bold', color='#e6edf3')
axes[1].set_ylabel('Call Count')

plt.tight_layout()
plt.savefig('models/baseline/output/charts/06_severity_distribution.png',
            dpi=150, bbox_inches='tight', facecolor='#0d1117')
plt.close()
log('  06_severity_distribution.png')

# ─────────────────────────────────────────────────────────────────────────────
# CHART 7: Top townships by call volume
# ─────────────────────────────────────────────────────────────────────────────
twp_vol = (cleaned.groupby('twp').size()
           .sort_values(ascending=False).head(15))
fig, ax = plt.subplots(figsize=(14, 7))
fig.suptitle('SENTINEL — Top 15 Townships by 911 Call Volume',
             fontsize=14, fontweight='bold', color='#e6edf3')
bars = ax.barh(twp_vol.index[::-1], twp_vol.values[::-1],
               color=BLUE, edgecolor='none', height=0.7)
for bar, val in zip(bars, twp_vol.values[::-1]):
    ax.text(val + twp_vol.max() * 0.005,
            bar.get_y() + bar.get_height() / 2,
            f'{val:,}', va='center', fontsize=9, color='#8b949e')
ax.set_xlabel('Total 911 Calls')
ax.set_title('Dec 2015 – Dec 2016', color='#8b949e', fontsize=11)
plt.tight_layout()
plt.savefig('models/baseline/output/charts/07_township_volumes.png',
            dpi=150, bbox_inches='tight', facecolor='#0d1117')
plt.close()
log('  07_township_volumes.png')

# ─────────────────────────────────────────────────────────────────────────────
# CHART 8: Hourly and monthly call patterns
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('SENTINEL — 911 Call Temporal Patterns',
             fontsize=14, fontweight='bold', color='#e6edf3')

hourly = cleaned.groupby('hour').size()
axes[0].fill_between(hourly.index, hourly.values, alpha=0.3, color=BLUE)
axes[0].plot(hourly.index, hourly.values, color=BLUE, lw=2.5,
             marker='o', markersize=4)
axes[0].axvspan(22, 24, alpha=0.08, color=RED, label='Night (22–00)')
axes[0].axvspan(0,  6,  alpha=0.08, color=RED)
axes[0].set_title('Calls by Hour of Day', fontweight='bold', color='#e6edf3')
axes[0].set_xlabel('Hour'); axes[0].set_ylabel('Total Calls')
axes[0].set_xticks(range(0, 24, 2))
axes[0].legend(fontsize=9)

monthly = cleaned.groupby('month').size()
month_names = ['Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']
axes[1].bar([month_names[m-1] for m in monthly.index],
            monthly.values, color=AMBER, edgecolor='none', width=0.7)
axes[1].set_title('Calls by Month', fontweight='bold', color='#e6edf3')
axes[1].set_xlabel('Month'); axes[1].set_ylabel('Total Calls')

plt.tight_layout()
plt.savefig('models/baseline/output/charts/08_temporal_patterns.png',
            dpi=150, bbox_inches='tight', facecolor='#0d1117')
plt.close()
log('  08_temporal_patterns.png')

# ─────────────────────────────────────────────────────────────────────────────
# Final results & save
# ─────────────────────────────────────────────────────────────────────────────
log(f'\n{"=" * 65}')
log('HOTSPOT PREDICTION — FINAL RESULTS')
log(f'{"=" * 65}')
log(f'  Naive persistence baseline AUC: {naive_auc:.4f}')
log(f'  {"Model":<22} {"AUC":>7} {"F1":>7} {"Prec":>7} {"Rec":>7} {"Acc":>7}')
log(f'  {"-" * 58}')
for name in sorted(results, key=lambda k: -results[k]['auc']):
    r    = results[name]
    star = ' ★' if name == best_name else ''
    beat = (f'  +{r["auc"] - naive_auc:.4f} vs naive'
            if name == best_name else '')
    log(f'  {name + star:<22} {r["auc"]:>7.4f} {r["f1"]:>7.4f} '
        f'{r["precision"]:>7.4f} {r["recall"]:>7.4f} '
        f'{r["accuracy"]:>7.4f}{beat}')
log(f'{"=" * 65}')

output = {
    'system':  'SENTINEL — Montgomery County 911 Hotspot Prediction',
    'dataset': 'Montgomery County PA 911 Emergency Calls (Kaggle)',
    'problem': 'Predict which townships will have elevated 911 call '
               'activity next month',
    'unit':    'township × month',
    'target':  'is_hotspot (top 25% by call volume)',
    'split': {
        'method':  'temporal holdout',
        'train':   f'{sorted_periods[0]} → {sorted_periods[-n_test - 1]}',
        'test':    f'{cutoff} → {sorted_periods[-1]}',
        'n_train': len(train),
        'n_test':  len(test),
    },
    'naive_persistence_auc': round(naive_auc, 4),
    'best_model':  best_name,
    'best_thresh': round(best_t, 3),
    'features':   {'count': len(FEATURES), 'names': FEATURES},
    'models':     results,
}
with open('models/baseline/output/results.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)
with open('models/baseline/output/model_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

# ── Save models to disk ───────────────────────────────────────────────────────
import pickle, datetime

os.makedirs('models/baseline/output/saved_models', exist_ok=True)

# Save all trained models
for name, model in MODELS.items():
    safe_name = name.lower().replace(' ', '_')
    pkl_path  = f'models/baseline/output/saved_models/{safe_name}.pkl'
    with open(pkl_path, 'wb') as f:
        pickle.dump(model, f)
    log(f'✅  Saved:    {pkl_path}')

# Save best model separately for easy loading
best_safe = best_name.lower().replace(' ', '_')
best_pkl  = 'models/baseline/output/saved_models/best_model.pkl'
with open(best_pkl, 'wb') as f:
    pickle.dump(MODELS[best_name], f)
log(f'✅  Best model saved separately: {best_pkl}')

# Save model metadata alongside the pkl files
metadata = {
    'saved_at':        datetime.datetime.now().isoformat(),
    'best_model':      best_name,
    'best_model_file': f'{best_safe}.pkl',
    'best_thresh':     round(best_t, 3),
    'features':        FEATURES,
    'feature_count':   len(FEATURES),
    'hotspot_threshold_calls': 224,
    'hotspot_percentile':      75,
    'trained_on': {
        'periods': f'{sorted_periods[0]} → {sorted_periods[-n_test - 1]}',
        'n_rows':  len(train),
    },
    'evaluated_on': {
        'periods': f'{cutoff} → {sorted_periods[-1]}',
        'n_rows':  len(test),
    },
    'model_files': {
        name.lower().replace(' ', '_') + '.pkl': results[name]
        for name in MODELS
    },
}
with open('models/baseline/output/saved_models/metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
log('✅  Metadata: models/baseline/output/saved_models/metadata.json')

log('\n✅  Results:  models/baseline/output/results.json')
log('✅  Charts:   models/baseline/output/charts/ (8 charts)')
log('✅  Report:   models/baseline/output/model_report.txt')