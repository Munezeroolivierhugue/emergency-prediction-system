"""
SENTINEL — Crime Hotspot Prediction System
==========================================
Step 2: Hotspot Panel Construction
File  : 02_build_panel.py
Input : data/cleaned.csv
Output: data/panel.csv

This is the most important transformation in the entire pipeline.

The problem with incident-level data
-------------------------------------
The raw dataset has one row per crime incident. If you train a model on
incident rows, the model answers: "given that a crime has already happened,
what kind is it?" That is reactive — it runs AFTER the crime occurs and
cannot be used to position patrol resources before anything happens.

The correct unit of prediction
-------------------------------
To predict WHERE crime will happen before it happens, the unit of observation
must be a LOCATION × TIME combination. We call this a cell-month.

  One row = one grid cell × one calendar month

This panel explicitly includes cell-months with ZERO crimes, because the
model must learn to distinguish "this area is genuinely quiet" from "this
area is about to spike." If you only include months with crimes, you never
train on the negative class and the model cannot generalize.

Panel dimensions
----------------
  40 grid cells × 300 months (2001–2025) = 12,000 cell-month observations
  62% of cell-months have zero crimes (important negative examples)

Target variable definition
---------------------------
  is_hotspot = 1  if total crimes in this cell-month ≥ 75th percentile
                   of all non-zero cell-months  (threshold = 3 crimes)
  is_hotspot = 0  otherwise

This is the standard criminological hotspot definition. The top quartile
of crime activity constitutes an operationally meaningful "hotspot."

Feature design principle — NO DATA LEAKAGE
-------------------------------------------
Every feature is computed from data that existed BEFORE the period being
predicted. The model never sees any information from the current period.

Feature groups:
  A. Lag features      — exact crime counts at t-1, t-2, t-3
  B. Rolling windows   — 3m, 6m, 12m trailing averages (trend smoothing)
  C. Hotspot history   — was this cell a hotspot in past periods?
  D. Trend             — is crime going up or down in this cell?
  E. Seasonality       — same month last year (captures annual cycles)
  F. Momentum          — consecutive hotspot streak (stickiness)
  G. Long-run baseline — all-time cumulative crime and hotspot rate
  H. Area context      — crime pressure from surrounding community area
  I. Temporal context  — month, quarter, cyclical sin/cos encoding
  J. Spatial identity  — community area, district, beat
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

IN  = './cleaned.csv'
OUT = './panel.csv'
LOG = './02_panel_log.txt'

lines = []
def log(msg=''):
    print(msg)
    lines.append(str(msg))

log("=" * 65)
log("SENTINEL  |  Step 2: Hotspot Panel Construction")
log("=" * 65)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(IN, parse_dates=['date'])

# Exclude partial 2026 — incomplete year distorts percentile thresholds
df = df[df['year'] < 2026].copy()

# Ensure grid columns exist
df['lat_grid']  = (df['latitude']  / 0.01).round().astype(int)
df['lon_grid']  = (df['longitude'] / 0.01).round().astype(int)
df['grid_cell'] = df['lat_grid'].astype(str) + '_' + df['lon_grid'].astype(str)

# Ensure night flag exists for aggregation
df['is_night'] = ((df['date'].dt.hour >= 22) | (df['date'].dt.hour < 6)).astype(int)

# Monthly period
df['period'] = df['date'].dt.to_period('M')

n_cells   = df['grid_cell'].nunique()
n_periods = df['period'].nunique()
log(f"\n[LOAD]   {len(df):,} incidents")
log(f"         {n_cells} unique grid cells  (0.01° ≈ 1.1 km²)")
log(f"         {n_periods} monthly periods  ({df['period'].min()} → {df['period'].max()})")

# ── Build full panel (every cell × every month) ───────────────────────────────
log(f"\n[PANEL]  Building {n_cells} × {n_periods} = {n_cells*n_periods:,} cell-month grid...")

all_cells   = df['grid_cell'].unique()
all_periods = pd.period_range(df['period'].min(), df['period'].max(), freq='M')
idx = pd.MultiIndex.from_product([all_cells, all_periods],
                                  names=['grid_cell', 'period'])
panel = pd.DataFrame(index=idx).reset_index()

# ── Aggregate crime statistics per cell-month ─────────────────────────────────
monthly_agg = df.groupby(['grid_cell', 'period']).agg(
    total_crimes   = ('high_risk', 'count'),
    violent_crimes = ('high_risk', 'sum'),
    arrests        = ('arrest',    'sum'),
    domestic_crimes= ('domestic',  'sum'),
    avg_severity   = ('severity',  'mean'),
    night_crimes   = ('is_night',  'sum'),
    unique_types   = ('primary_type', 'nunique'),
).reset_index()

panel = panel.merge(monthly_agg, on=['grid_cell', 'period'], how='left')
panel = panel.fillna({'total_crimes': 0, 'violent_crimes': 0, 'arrests': 0,
                      'domestic_crimes': 0, 'avg_severity': 0,
                      'night_crimes': 0, 'unique_types': 0})

zero_months = (panel['total_crimes'] == 0).sum()
log(f"         {zero_months:,} zero-crime cell-months ({zero_months/len(panel):.1%}) — kept as negatives")
log(f"         Mean crimes/cell-month: {panel['total_crimes'].mean():.2f}")
log(f"         Max crimes/cell-month:  {panel['total_crimes'].max():.0f}")

# ── Static spatial attributes per cell ───────────────────────────────────────
cell_attrs = df.groupby('grid_cell').agg(
    lat            = ('latitude',       'mean'),
    lon            = ('longitude',      'mean'),
    community_area = ('community_area', lambda x: int(x.mode()[0])),
    district       = ('district',       lambda x: int(x.mode()[0])),
    beat           = ('beat',           lambda x: int(x.mode()[0])),
).reset_index()
panel = panel.merge(cell_attrs, on='grid_cell', how='left')

# ── Sort for lag computation ──────────────────────────────────────────────────
panel['period_dt'] = panel['period'].dt.to_timestamp()
panel = panel.sort_values(['grid_cell', 'period_dt']).reset_index(drop=True)

# ── Define hotspot target variable ────────────────────────────────────────────
nonzero_counts = panel[panel['total_crimes'] > 0]['total_crimes']
HOTSPOT_THRESHOLD = nonzero_counts.quantile(0.75)
panel['is_hotspot'] = (panel['total_crimes'] >= HOTSPOT_THRESHOLD).astype(int)

log(f"\n[TARGET] Hotspot = top 25% of non-zero cell-months")
log(f"         Threshold: ≥ {HOTSPOT_THRESHOLD:.0f} crimes per cell-month")
log(f"         Hotspot cell-months:     {panel['is_hotspot'].sum():,} "
    f"({panel['is_hotspot'].mean():.1%})")
log(f"         Non-hotspot cell-months: {(panel['is_hotspot']==0).sum():,} "
    f"({1-panel['is_hotspot'].mean():.1%})")

# ── Feature Group A & B: Lag and rolling features ─────────────────────────────
log(f"\n[FEATURES]  Computing lagged features (all past-only, no leakage)...")

grp = panel.groupby('grid_cell')

# A: Direct lags — exact values 1, 2, 3 months ago
for lag in [1, 2, 3]:
    panel[f'crimes_lag{lag}']  = grp['total_crimes'].shift(lag)
    panel[f'violent_lag{lag}'] = grp['violent_crimes'].shift(lag)
    panel[f'hotspot_lag{lag}'] = grp['is_hotspot'].shift(lag)

# B: Rolling averages — smooth out noise over 3, 6, 12 month windows
# shift(1) ensures we use data up to and including last month, not current
for w in [3, 6, 12]:
    panel[f'crimes_roll{w}m']  = (grp['total_crimes'].shift(1)
                                   .rolling(w, min_periods=1).mean()
                                   .reset_index(level=0, drop=True))
    panel[f'violent_roll{w}m'] = (grp['violent_crimes'].shift(1)
                                   .rolling(w, min_periods=1).mean()
                                   .reset_index(level=0, drop=True))
    panel[f'hotspot_roll{w}m'] = (grp['is_hotspot'].shift(1)
                                   .rolling(w, min_periods=1).mean()
                                   .reset_index(level=0, drop=True))

# C: Trend — direction of crime change over last 3 months
panel['crime_trend_3m'] = panel['crimes_lag1'] - panel['crimes_lag3']

# D: Seasonality — same month last year (captures annual crime cycles)
panel['crimes_same_month_ly']  = grp['total_crimes'].shift(12)
panel['hotspot_same_month_ly'] = grp['is_hotspot'].shift(12)

# E: Long-run cumulative baseline (all history up to last month)
panel['cumulative_crime_rate']   = (grp['total_crimes'].shift(1)
                                    .expanding().mean()
                                    .reset_index(level=0, drop=True))
panel['cumulative_hotspot_rate'] = (grp['is_hotspot'].shift(1)
                                    .expanding().mean()
                                    .reset_index(level=0, drop=True))

# F: Hotspot streak — consecutive months as a hotspot (crime momentum)
def hotspot_streak(series):
    """Count consecutive hotspot months ending just before each period."""
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

# G: Area-level context — crime pressure from surrounding community
area_monthly = (panel.groupby(['community_area', 'period'])['total_crimes']
                .sum().reset_index()
                .rename(columns={'total_crimes': 'area_total'}))
area_monthly = area_monthly.sort_values(['community_area', 'period'])
ag = area_monthly.groupby('community_area')
area_monthly['area_crimes_lag1']   = ag['area_total'].shift(1)
area_monthly['area_crimes_roll3m'] = (ag['area_total'].shift(1)
                                      .rolling(3, min_periods=1).mean()
                                      .reset_index(level=0, drop=True))
panel = panel.merge(
    area_monthly[['community_area','period','area_crimes_lag1','area_crimes_roll3m']],
    on=['community_area','period'], how='left'
)

# H: Temporal context
panel['year']      = panel['period_dt'].dt.year
panel['month']     = panel['period_dt'].dt.month
panel['quarter']   = panel['period_dt'].dt.quarter
panel['month_sin'] = np.sin(2 * np.pi * panel['month'] / 12)
panel['month_cos'] = np.cos(2 * np.pi * panel['month'] / 12)
panel['is_summer'] = panel['month'].isin([6,7,8]).astype(int)
panel['is_winter'] = panel['month'].isin([12,1,2]).astype(int)

log(f"         A) Lag features:        crimes, violent, hotspot at t-1, t-2, t-3")
log(f"         B) Rolling averages:    3m, 6m, 12m trailing windows")
log(f"         C) Trend:               3-month crime direction")
log(f"         D) Seasonality:         same month, prior year")
log(f"         E) Long-run baseline:   cumulative crime & hotspot rate")
log(f"         F) Momentum streak:     consecutive hotspot months")
log(f"         G) Area context:        community-level crime pressure")
log(f"         H) Temporal context:    month, quarter, sin/cos encoding")
log(f"         I) Spatial identity:    community area, district, beat")

# ── Remove warmup period (first 12 months — insufficient lag history) ─────────
min_period   = panel['period'].min()
warmup_end   = min_period + 11
panel_final  = panel[panel['period'] > warmup_end].copy()

# Drop rows still missing key lag features after warmup
key_lags = ['crimes_lag1','crimes_lag2','crimes_lag3','crimes_roll3m','crimes_roll6m']
panel_final = panel_final.dropna(subset=key_lags)
panel_final[panel_final.select_dtypes('number').columns] = \
    panel_final.select_dtypes('number').fillna(0)

log(f"\n[WARMUP]  Dropped first 12 months per cell (insufficient history)")
log(f"          Full panel:  {len(panel):,} rows")
log(f"          Model panel: {len(panel_final):,} rows")
log(f"          Hotspot rate in model panel: {panel_final['is_hotspot'].mean():.1%}")

# ── Save ──────────────────────────────────────────────────────────────────────
panel_final.to_csv(OUT, index=False)
log(f"\n[COLUMNS]  {list(panel_final.columns)}")
log(f"\n✅  Saved: {OUT}  ({panel_final.shape[0]:,} × {panel_final.shape[1]})")

with open(LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
log(f"✅  Log:   {LOG}")