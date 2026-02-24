"""
SENTINEL — 911 Hotspot Prediction System
=========================================
Step 2: Hotspot Panel Construction
File  : pipeline/02_build_panel.py
Input : data/processed/incidents_cleaned.csv
Output: data/processed/panel.csv

Unit of prediction
------------------
Each row = one township × one calendar month.

The model answers: will this township have elevated 911
call activity next month, before those calls happen?

Why township?
-------------
The 911 dataset's primary geographic identifier is township
(twp) — 67 distinct townships in Montgomery County PA. Unlike
the Chicago dataset where lat/lng enabled precise grid cells,
the 911 data is best aggregated at the township level because:
  a) It is the native administrative unit for dispatch
  b) Each township has its own call centre and station
  c) Township-level counts are stable enough for lag features

Panel construction
------------------
All 67 townships × all months in the dataset = full grid.
Zero-call months are included as negative training examples.

Target variable
---------------
is_hotspot = 1 if township-month call volume ≥ 75th percentile
             of all non-zero township-months
is_hotspot = 0 otherwise

Feature engineering — no leakage
----------------------------------
Every feature is strictly past-only. .shift(1) is applied
before any rolling or cumulative computation.
"""

import pandas as pd
import numpy as np
import warnings, os
warnings.filterwarnings('ignore')

IN  = 'data/processed/incidents_cleaned.csv'
OUT = 'data/processed/panel.csv'
LOG = 'data/processed/02_panel_log.txt'

os.makedirs('data/processed', exist_ok=True)

lines = []
def log(msg=''):
    print(msg)
    lines.append(str(msg))

log('=' * 65)
log('SENTINEL  |  Step 2: Hotspot Panel Construction')
log('=' * 65)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(IN, parse_dates=['timeStamp'])
df['period'] = df['timeStamp'].dt.to_period('M')

n_twp     = df['twp'].nunique()
n_periods = df['period'].nunique()
log(f'\n[LOAD]   {len(df):,} incident records')
log(f'         {n_twp} unique townships')
log(f'         {n_periods} monthly periods  '
    f'({df["period"].min()} → {df["period"].max()})')

# ── Build full township × month grid ─────────────────────────────────────────
log(f'\n[PANEL]  Building {n_twp} × {n_periods} = {n_twp * n_periods:,} '
    f'township-month grid...')

all_twps    = sorted(df['twp'].unique())
all_periods = pd.period_range(df['period'].min(), df['period'].max(), freq='M')
idx   = pd.MultiIndex.from_product([all_twps, all_periods],
                                    names=['twp', 'period'])
panel = pd.DataFrame(index=idx).reset_index()

# ── Aggregate per township-month ──────────────────────────────────────────────
agg = df.groupby(['twp', 'period']).agg(
    total_calls      = ('Severity',     'count'),
    critical_calls   = ('severity_num', lambda x: (x == 3).sum()),
    high_calls       = ('severity_num', lambda x: (x == 2).sum()),
    ems_calls        = ('Type',         lambda x: (x == 'EMS').sum()),
    fire_calls       = ('Type',         lambda x: (x == 'Fire').sum()),
    traffic_calls    = ('Type',         lambda x: (x == 'Traffic').sum()),
    avg_severity     = ('severity_num', 'mean'),
    night_calls      = ('is_night',     'sum'),
    weekend_calls    = ('is_weekend',   'sum'),
    unique_subtypes  = ('Subtype',      'nunique'),
).reset_index()

panel = panel.merge(agg, on=['twp', 'period'], how='left')
fill_cols = ['total_calls', 'critical_calls', 'high_calls', 'ems_calls',
             'fire_calls', 'traffic_calls', 'avg_severity',
             'night_calls', 'weekend_calls', 'unique_subtypes']
panel[fill_cols] = panel[fill_cols].fillna(0)

zero_months = (panel['total_calls'] == 0).sum()
log(f'         {zero_months:,} zero-call township-months '
    f'({zero_months / len(panel):.1%}) — retained as negatives')
log(f'         Mean calls/township-month: {panel["total_calls"].mean():.1f}')
log(f'         Max calls/township-month:  {panel["total_calls"].max():.0f}')

# ── Sort for lag computation ──────────────────────────────────────────────────
panel['period_dt'] = panel['period'].dt.to_timestamp()
panel = panel.sort_values(['twp', 'period_dt']).reset_index(drop=True)

# ── Define hotspot target ─────────────────────────────────────────────────────
nonzero   = panel[panel['total_calls'] > 0]['total_calls']
THRESHOLD = nonzero.quantile(0.75)
panel['is_hotspot'] = (panel['total_calls'] >= THRESHOLD).astype(int)

log(f'\n[TARGET] Hotspot = top 25% of non-zero township-months')
log(f'         Threshold: ≥ {THRESHOLD:.0f} calls per township-month')
log(f'         Hotspot months:     {panel["is_hotspot"].sum():,} '
    f'({panel["is_hotspot"].mean():.1%})')
log(f'         Non-hotspot months: {(panel["is_hotspot"] == 0).sum():,} '
    f'({1 - panel["is_hotspot"].mean():.1%})')

# ── Feature engineering ───────────────────────────────────────────────────────
log(f'\n[FEATURES]  Computing lagged features (all past-only, no leakage)...')
grp = panel.groupby('twp')

# A: Direct lags — exact call counts at t-1, t-2, t-3
for lag in [1, 2, 3]:
    panel[f'calls_lag{lag}']    = grp['total_calls'].shift(lag)
    panel[f'critical_lag{lag}'] = grp['critical_calls'].shift(lag)
    panel[f'hotspot_lag{lag}']  = grp['is_hotspot'].shift(lag)

# B: Rolling averages — smooth noise, capture trend
for w in [3, 6, 12]:
    panel[f'calls_roll{w}m'] = (
        grp['total_calls'].shift(1)
        .rolling(w, min_periods=1).mean()
        .reset_index(level=0, drop=True)
    )
    panel[f'critical_roll{w}m'] = (
        grp['critical_calls'].shift(1)
        .rolling(w, min_periods=1).mean()
        .reset_index(level=0, drop=True)
    )
    panel[f'hotspot_roll{w}m'] = (
        grp['is_hotspot'].shift(1)
        .rolling(w, min_periods=1).mean()
        .reset_index(level=0, drop=True)
    )

# C: Trend — direction of call volume change
panel['call_trend_3m'] = panel['calls_lag1'] - panel['calls_lag3']

# D: Seasonality — same month last year
# Note: with only 13 months of data (Dec 2015 – Dec 2016), this feature
# is NaN for almost all rows. It is included for when the full dataset
# is used, and filled with 0 in the warmup step.
panel['calls_same_month_ly']   = grp['total_calls'].shift(12)
panel['hotspot_same_month_ly'] = grp['is_hotspot'].shift(12)

# E: Long-run baseline — cumulative average up to last month
panel['cumulative_call_rate'] = (
    grp['total_calls'].shift(1)
    .expanding().mean()
    .reset_index(level=0, drop=True)
)
panel['cumulative_hotspot_rate'] = (
    grp['is_hotspot'].shift(1)
    .expanding().mean()
    .reset_index(level=0, drop=True)
)

# F: Hotspot streak — consecutive months as hotspot
def hotspot_streak(series):
    series = series.shift(1)
    result, count = [], 0
    for v in series:
        if pd.isna(v):
            result.append(np.nan)
        elif v == 1:
            count += 1
            result.append(count)
        else:
            count = 0
            result.append(0)
    return pd.Series(result, index=series.index)

panel['hotspot_streak'] = grp['is_hotspot'].transform(hotspot_streak)

# G: Temporal context
panel['year']      = panel['period_dt'].dt.year
panel['month']     = panel['period_dt'].dt.month
panel['quarter']   = panel['period_dt'].dt.quarter
panel['month_sin'] = np.sin(2 * np.pi * panel['month'] / 12)
panel['month_cos'] = np.cos(2 * np.pi * panel['month'] / 12)
panel['is_summer'] = panel['month'].isin([6, 7, 8]).astype(int)
panel['is_winter'] = panel['month'].isin([12, 1, 2]).astype(int)

log(f'         A) Lag features:       calls, critical, hotspot at t-1/2/3')
log(f'         B) Rolling averages:   3m, 6m, 12m trailing windows')
log(f'         C) Trend:              3-month call direction')
log(f'         D) Seasonality:        same month, prior year')
log(f'         E) Long-run baseline:  cumulative call & hotspot rate')
log(f'         F) Momentum streak:    consecutive hotspot months')
log(f'         G) Temporal context:   month, quarter, sin/cos, season flags')

# ── Warmup exclusion ──────────────────────────────────────────────────────────
# Drop first 3 months — minimum needed for calls_lag3 to be valid.
# (With 13 months total, a 12-month warmup would eliminate nearly all data.
#  3-month warmup preserves enough rows for a meaningful train/test split.)
min_period  = panel['period'].min()
warmup_end  = min_period + 2          # keep from month 4 onwards
panel_final = panel[panel['period'] > warmup_end].copy()

key_lags = ['calls_lag1', 'calls_lag2', 'calls_lag3']
panel_final = panel_final.dropna(subset=key_lags)
panel_final[panel_final.select_dtypes('number').columns] = \
    panel_final.select_dtypes('number').fillna(0)

log(f'\n[WARMUP]  Dropped first 3 months per township (lag-3 requires 3 months)')
log(f'          Full panel:  {len(panel):,} rows')
log(f'          Model panel: {len(panel_final):,} rows')
log(f'          Hotspot rate in model panel: {panel_final["is_hotspot"].mean():.1%}')
log(f'\n[NOTE]    Dataset covers only 13 months (2015-12 → 2016-12).')
log(f'          Full Kaggle dataset (2015–2020) recommended for production.')
log(f'          Download: https://www.kaggle.com/datasets/mchirico/montcoalert')

panel_final.to_csv(OUT, index=False)
log(f'\n✅  Saved: {OUT}  ({panel_final.shape[0]:,} × {panel_final.shape[1]})')

with open(LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
log(f'✅  Log:   {LOG}')