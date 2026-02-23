"""
911 Hotspot Prediction System - Panel Construction
Creates township-month panel dataset for hotspot prediction modeling.
"""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path

# Suppress warnings
warnings.filterwarnings('ignore')

# Configuration
INPUT_PATH = 'data/processed/incidents_cleaned.csv'
OUTPUT_PATH = 'data/processed/panel.csv'
LOG_PATH = 'data/logs/02_panel_log.txt'

# Ensure directories exist
Path('data/processed').mkdir(parents=True, exist_ok=True)
Path('data/logs').mkdir(parents=True, exist_ok=True)

# Logging setup
log_lines = []

def log(msg: str = ''):
    """Log message to console and file."""
    print(msg)
    log_lines.append(str(msg))

def log_section(title: str):
    """Log a formatted section header."""
    log(f'\n{"=" * 60}')
    log(f'{title}')
    log(f'{"=" * 60}')

# Start processing
log_section('911 HOTSPOT PANEL CONSTRUCTION')
log(f'Started: {pd.Timestamp.now()}')
log(f'Input:  {INPUT_PATH}')
log(f'Output: {OUTPUT_PATH}')


#  LOAD AND PREPARE DATA

log_section('1. LOADING DATA')

try:
    df = pd.read_csv(INPUT_PATH, parse_dates=['timeStamp'])
    df['period'] = df['timeStamp'].dt.to_period('M')
    
    n_twp = df['twp'].nunique()
    n_periods = df['period'].nunique()
    
    log(f'Successfully loaded {len(df):,} incident records')
    log(f'{n_twp} unique townships')
    log(f'{n_periods} monthly periods ({df["period"].min()} → {df["period"].max()})')
except FileNotFoundError:
    log(f'ERROR: Input file not found at {INPUT_PATH}')
    raise
except Exception as e:
    log(f'ERROR: Failed to load data - {str(e)}')
    raise


#  BUILD TOWNSHIP-MONTH GRID

log_section('2. BUILDING PANEL GRID')

all_twps = sorted(df['twp'].unique())
all_periods = pd.period_range(df['period'].min(), df['period'].max(), freq='M')

# Create full grid of all township-month combinations
idx = pd.MultiIndex.from_product([all_twps, all_periods], names=['twp', 'period'])
panel = pd.DataFrame(index=idx).reset_index()

log(f'Created {n_twp} × {n_periods} = {n_twp * n_periods:,} township-month grid')

#  AGGREGATE INCIDENTS TO TOWNSHIP-MONTH LEVEL
log_section('3. AGGREGATING INCIDENTS')

agg = df.groupby(['twp', 'period']).agg(
    total_calls=('Severity', 'count'),
    critical_calls=('severity_num', lambda x: (x == 3).sum()),
    high_calls=('severity_num', lambda x: (x == 2).sum()),
    ems_calls=('Type', lambda x: (x == 'EMS').sum()),
    fire_calls=('Type', lambda x: (x == 'Fire').sum()),
    traffic_calls=('Type', lambda x: (x == 'Traffic').sum()),
    avg_severity=('severity_num', 'mean'),
    night_calls=('is_night', 'sum'),
    weekend_calls=('is_weekend', 'sum'),
    unique_subtypes=('Subtype', 'nunique'),
).reset_index()

# Merge aggregates with full grid
panel = panel.merge(agg, on=['twp', 'period'], how='left')

# Fill missing values with zeros
fill_cols = [
    'total_calls', 'critical_calls', 'high_calls', 'ems_calls',
    'fire_calls', 'traffic_calls', 'avg_severity',
    'night_calls', 'weekend_calls', 'unique_subtypes'
]
panel[fill_cols] = panel[fill_cols].fillna(0)

# Log statistics
zero_months = (panel['total_calls'] == 0).sum()
log(f'Zero-call township-months: {zero_months:,} ({zero_months / len(panel):.1%})')
log(f'Mean calls per township-month: {panel["total_calls"].mean():.1f}')
log(f'Max calls per township-month: {panel["total_calls"].max():.0f}')

# Sort for lag computation
panel['period_dt'] = panel['period'].dt.to_timestamp()
panel = panel.sort_values(['twp', 'period_dt']).reset_index(drop=True)


#  CREATE HOTSPOT TARGET VARIABLE

log_section('4. CREATING TARGET VARIABLE')

# Define hotspot as top 25% of non-zero township-months
nonzero_calls = panel[panel['total_calls'] > 0]['total_calls']
threshold = nonzero_calls.quantile(0.75)
panel['is_hotspot'] = (panel['total_calls'] >= threshold).astype(int)

log(f'Hotspot threshold: ≥ {threshold:.0f} calls per township-month')
log(f'Hotspot months: {panel["is_hotspot"].sum():,} ({panel["is_hotspot"].mean():.1%})')
log(f'Non-hotspot months: {(panel["is_hotspot"] == 0).sum():,} '
    f'({1 - panel["is_hotspot"].mean():.1%})')


#  FEATURE ENGINEERING (PAST-ONLY, NO LEAKAGE)

log_section('5. ENGINEERING FEATURES')

log('Computing lagged features (all past-only, no leakage)...')
grp = panel.groupby('twp')

# A. Direct lag features
for lag in [1, 2, 3]:
    panel[f'calls_lag{lag}'] = grp['total_calls'].shift(lag)
    panel[f'critical_lag{lag}'] = grp['critical_calls'].shift(lag)
    panel[f'hotspot_lag{lag}'] = grp['is_hotspot'].shift(lag)

# B. Rolling averages
for window in [3, 6, 12]:
    panel[f'calls_roll{window}m'] = (
        grp['total_calls'].shift(1)
        .rolling(window, min_periods=1).mean()
        .reset_index(level=0, drop=True)
    )
    panel[f'critical_roll{window}m'] = (
        grp['critical_calls'].shift(1)
        .rolling(window, min_periods=1).mean()
        .reset_index(level=0, drop=True)
    )
    panel[f'hotspot_roll{window}m'] = (
        grp['is_hotspot'].shift(1)
        .rolling(window, min_periods=1).mean()
        .reset_index(level=0, drop=True)
    )

# C. Trend features
panel['call_trend_3m'] = panel['calls_lag1'] - panel['calls_lag3']

# D. Seasonality features (same month last year)
panel['calls_same_month_ly'] = grp['total_calls'].shift(12)
panel['hotspot_same_month_ly'] = grp['is_hotspot'].shift(12)

# E. Long-run baseline features
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

# F. Hotspot streak feature
def compute_hotspot_streak(series):
    """Compute consecutive hotspot months."""
    series = series.shift(1)
    result, count = [], 0
    for value in series:
        if pd.isna(value):
            result.append(np.nan)
        elif value == 1:
            count += 1
            result.append(count)
        else:
            count = 0
            result.append(0)
    return pd.Series(result, index=series.index)

panel['hotspot_streak'] = grp['is_hotspot'].transform(compute_hotspot_streak)

# G. Temporal context features
panel['year'] = panel['period_dt'].dt.year
panel['month'] = panel['period_dt'].dt.month
panel['quarter'] = panel['period_dt'].dt.quarter
panel['month_sin'] = np.sin(2 * np.pi * panel['month'] / 12)
panel['month_cos'] = np.cos(2 * np.pi * panel['month'] / 12)
panel['is_summer'] = panel['month'].isin([6, 7, 8]).astype(int)
panel['is_winter'] = panel['month'].isin([12, 1, 2]).astype(int)

log('Feature categories created:')
log('  A) Direct lags (t-1, t-2, t-3)')
log('  B) Rolling averages (3m, 6m, 12m)')
log('  C) Trend (3-month direction)')
log('  D) Seasonality (year-over-year)')
log('  E) Long-run baselines')
log('  F) Hotspot momentum streak')
log('  G) Temporal context (month, season, cyclical)')

#  WARMUP PERIOD EXCLUSION
log_section('6. HANDLING WARMUP PERIOD')

# Drop first 3 months per township (needed for lag-3 features)
min_period = panel['period'].min()
warmup_end = min_period + 2  # Keep from month 4 onwards
panel_final = panel[panel['period'] > warmup_end].copy()

# Drop rows with missing lag features
key_lags = ['calls_lag1', 'calls_lag2', 'calls_lag3']
panel_final = panel_final.dropna(subset=key_lags)

# Fill remaining NaN values with 0
numeric_cols = panel_final.select_dtypes('number').columns
panel_final[numeric_cols] = panel_final[numeric_cols].fillna(0)

log(f'Dropped first 3 months per township (lag-3 requires 3 months history)')
log(f'Full panel: {len(panel):,} rows')
log(f'Model panel: {len(panel_final):,} rows')
log(f'Hotspot rate in model panel: {panel_final["is_hotspot"].mean():.1%}')

# Note about dataset size
log(f'\nNote: Dataset covers {n_periods} months ({df["period"].min()} → {df["period"].max()})')
log('For production use, download full 2015-2020 dataset from:')
log('https://www.kaggle.com/datasets/mchirico/montcoalert')

#  SAVE RESULTS
log_section('7. SAVING RESULTS')

# Final dataset summary
log(f'Final panel shape: {panel_final.shape[0]:,} rows × {panel_final.shape[1]} columns')
log(f'Columns: {list(panel_final.columns)}')

# Check for remaining nulls
remaining_nulls = panel_final.isnull().sum()
remaining_nulls = remaining_nulls[remaining_nulls > 0]
if len(remaining_nulls) > 0:
    log(f'\nRemaining null values:')
    for col, count in remaining_nulls.items():
        log(f'  {col}: {count:,}')
else:
    log(f'\nNo remaining null values')

# Save panel data
try:
    panel_final.to_csv(OUTPUT_PATH, index=False)
    log(f'\n✅ Panel data saved to: {OUTPUT_PATH}')
except Exception as e:
    log(f'❌ Error saving panel data: {str(e)}')
    raise

# Save log file
try:
    with open(LOG_PATH, 'w', encoding='utf-8') as log_file:
        log_file.write('\n'.join(log_lines))
    log(f'✅ Log file saved to: {LOG_PATH}')
except Exception as e:
    log(f'⚠️  Error saving log file: {str(e)}')

log_section('PANEL CONSTRUCTION COMPLETE')
log(f'Completed: {pd.Timestamp.now()}')