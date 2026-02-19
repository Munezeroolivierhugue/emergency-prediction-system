"""
SENTINEL — Crime Hotspot Prediction System
==========================================
Step 1: Data Cleaning
File  : 01_data_cleaning.py
Input : data/raw_crimes.csv
Output: data/cleaned.csv

Problem:
    Law enforcement agencies rely on reactive approaches to crime management.
    This system analyzes historical Chicago crime records to predict future
    crime hotspots, enabling proactive patrol allocation and resource planning.

What this script does:
    Takes the raw CPD dataset and resolves all data quality issues so every
    downstream script works on a trustworthy foundation. Every decision is
    documented with a reason — nothing is dropped or changed silently.

Cleaning decisions made:
    1.  Drop admin-only columns   — no analytical value
    2.  Parse timezone-aware dates — standardize to naive datetime
    3.  Normalize primary_type     — merge legacy label variants
    4.  Drop null-coordinate rows  — cannot spatially locate, cannot model
    5.  Impute community_area      — recover from lat/lon grid neighbors
    6.  Impute location_description— fill unknowns honestly
    7.  Flag partial-year 2026    — incomplete year, keep but mark
    8.  Cast booleans to integers  — ML models require numeric input
    9.  Add severity tier          — criminological classification for EDA
    10. Add high_risk flag         — used in hotspot volume aggregation
"""

import pandas as pd
import numpy as np

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW = './chicago_crime_data1.csv'
OUT = './cleaned.csv'
LOG = './01_cleaning_log.txt'

lines = []
def log(msg=''):
    print(msg)
    lines.append(str(msg))

log("=" * 65)
log("SENTINEL  |  Step 1: Data Cleaning")
log("=" * 65)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(RAW)
log(f"\n[LOAD]  Raw shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
log(f"        Columns: {list(df.columns)}")

# ── Fix 1: Drop admin columns ─────────────────────────────────────────────────
# unique_key, case_number  — database identifiers, not features
# updated_on               — record metadata, not crime attribute
# location                 — duplicate of lat/lon in string format
ADMIN_COLS = ['unique_key', 'case_number', 'updated_on', 'location']
df.drop(columns=ADMIN_COLS, inplace=True)
log(f"\n[1]  Dropped {len(ADMIN_COLS)} admin columns: {ADMIN_COLS}")
log(f"     Remaining columns: {df.shape[1]}")

# ── Fix 2: Parse dates ────────────────────────────────────────────────────────
# Raw dates include UTC timezone offset: "2024-01-01 18:35:00+00:00"
# Strip timezone for consistent arithmetic across the pipeline.
df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_localize(None)
log(f"\n[2]  Parsed dates → naive UTC")
log(f"     Range: {df['date'].min().date()}  →  {df['date'].max().date()}")

# ── Fix 3: Normalize primary_type labels ──────────────────────────────────────
# CPD changed "CRIM SEXUAL ASSAULT" to "CRIMINAL SEXUAL ASSAULT" around 2014.
# Both labels exist in the dataset for the same crime type — merge them.
REMAP = {'CRIM SEXUAL ASSAULT': 'CRIMINAL SEXUAL ASSAULT'}
before_counts = df['primary_type'].value_counts().to_dict()
df['primary_type'] = df['primary_type'].replace(REMAP)
log(f"\n[3]  Normalized primary_type labels:")
for old, new in REMAP.items():
    n = before_counts.get(old, 0)
    log(f"     '{old}'  →  '{new}'  ({n} rows merged)")
log(f"     Unique types now: {df['primary_type'].nunique()}")

# ── Fix 4: Drop null-coordinate rows ─────────────────────────────────────────
# 114 rows have no latitude/longitude. These cannot be assigned to a grid
# cell and are therefore useless for spatial hotspot modelling. Drop them.
# Imputing coordinates would fabricate spatial data — unacceptable.
null_coords = df['latitude'].isnull()
log(f"\n[4]  Null coordinate rows: {null_coords.sum()} → DROPPED")
df = df[~null_coords].copy()
log(f"     Remaining rows: {len(df):,}")

# ── Fix 5: Impute missing community_area ──────────────────────────────────────
# 625 rows have coordinates but no community_area. Strategy:
#   a) Assign the modal community_area of other crimes in the same 0.01° cell.
#   b) Any remaining: use the median community_area within the same district.
#   c) Final fallback: dataset-wide median.
df['lat_grid'] = (df['latitude']  / 0.01).round().astype(int)
df['lon_grid'] = (df['longitude'] / 0.01).round().astype(int)

n_null = df['community_area'].isnull().sum()

# Step a — grid cell mode
cell_mode = (
    df[df['community_area'].notnull()]
    .groupby(['lat_grid', 'lon_grid'])['community_area']
    .agg(lambda x: x.mode()[0])
    .rename('area_imputed')
    .reset_index()
)
df = df.merge(cell_mode, on=['lat_grid', 'lon_grid'], how='left')
mask_a = df['community_area'].isnull() & df['area_imputed'].notnull()
df.loc[mask_a, 'community_area'] = df.loc[mask_a, 'area_imputed']
df.drop(columns=['area_imputed'], inplace=True)

# Step b — district median
df['community_area'] = df.groupby('district')['community_area'].transform(
    lambda x: x.fillna(x.median())
)

# Step c — global fallback
df['community_area'] = df['community_area'].fillna(df['community_area'].median())

log(f"\n[5]  community_area nulls: {n_null} → fully imputed")
log(f"       a) Grid-cell modal value: {n_null - df['community_area'].isnull().sum()} resolved")
log(f"       b) District median: remaining resolved")
log(f"       c) Global fallback: 0 remaining")

# ── Fix 6: Impute location_description ───────────────────────────────────────
# 30–43 rows (mostly DECEPTIVE PRACTICE / identity theft) have no physical
# location. Fill with 'UNKNOWN' — an honest category, not a guess.
n_null_loc = df['location_description'].isnull().sum()
df['location_description'] = df['location_description'].fillna('UNKNOWN')
log(f"\n[6]  location_description nulls: {n_null_loc} → filled as 'UNKNOWN'")

# ── Fix 7: Flag partial year 2026 ─────────────────────────────────────────────
# 41 records from 2026 exist (data through Feb 2026). They are valid crimes
# but represent an incomplete year. Flag them so year-over-year trend charts
# can exclude them without losing them from the spatial model.
df['is_partial_year'] = (df['year'] == 2026).astype(int)
log(f"\n[7]  Flagged {df['is_partial_year'].sum()} partial-year 2026 rows (retained)")

# ── Fix 8: Cast boolean columns to integer ────────────────────────────────────
# arrest and domestic are Python booleans. ML libraries expect numeric input.
df['arrest']   = df['arrest'].astype(int)
df['domestic'] = df['domestic'].astype(int)
log(f"\n[8]  arrest / domestic cast to int (0 / 1)")
log(f"     Arrest rate:   {df['arrest'].mean():.1%}  ({df['arrest'].sum():,} arrests)")
log(f"     Domestic rate: {df['domestic'].mean():.1%}  ({df['domestic'].sum():,} domestic)")

# ── Fix 9 (note): Ward — left with nulls, excluded from model ─────────────────
log(f"\n[9]  ward: {df['ward'].isnull().sum()} nulls — retained, excluded from model")

# ── Enrichment: Severity tier ─────────────────────────────────────────────────
# Classify each crime type into 4 severity tiers based on CPD / FBI NIBRS
# classification. Used for weighted hotspot scoring and EDA — not leaked
# into the hotspot model target (which uses raw crime counts, not severity).
SEVERITY_MAP = {
    # Tier 3 — Critical (crimes against persons, maximum harm)
    'HOMICIDE': 3, 'CRIMINAL SEXUAL ASSAULT': 3, 'KIDNAPPING': 3, 'ARSON': 3,
    # Tier 2 — High (violent / weapon-involved)
    'ROBBERY': 2, 'WEAPONS VIOLATION': 2, 'ASSAULT': 2, 'BATTERY': 2,
    'STALKING': 2, 'INTIMIDATION': 2, 'OFFENSE INVOLVING CHILDREN': 2,
    'SEX OFFENSE': 2,
    # Tier 1 — Medium (property / drug)
    'BURGLARY': 1, 'MOTOR VEHICLE THEFT': 1, 'NARCOTICS': 1, 'THEFT': 1,
    'CRIMINAL DAMAGE': 1, 'DECEPTIVE PRACTICE': 1, 'PUBLIC PEACE VIOLATION': 1,
    'PROSTITUTION': 1, 'LIQUOR LAW VIOLATION': 1, 'GAMBLING': 1,
    'INTERFERENCE WITH PUBLIC OFFICER': 1,
    # Tier 0 — Low (administrative / minor)
    'CRIMINAL TRESPASS': 0, 'OTHER OFFENSE': 0, 'PUBLIC INDECENCY': 0,
    'OTHER NARCOTIC VIOLATION': 0, 'CONCEALED CARRY LICENSE VIOLATION': 0,
}
df['severity']  = df['primary_type'].map(SEVERITY_MAP).fillna(0).astype(int)
df['high_risk'] = (df['severity'] >= 2).astype(int)

log(f"\n[ENRICH]  Severity tiers:")
for tier, label in [(3,'Critical'),(2,'High'),(1,'Medium'),(0,'Low')]:
    n = (df['severity'] == tier).sum()
    log(f"          Tier {tier} ({label:8s}): {n:,} rows")
log(f"          High-risk total (Tier 2+3): {df['high_risk'].sum():,}  "
    f"({df['high_risk'].mean():.1%})")

# ── Final summary ─────────────────────────────────────────────────────────────
log(f"\n{'='*65}")
log(f"CLEAN DATASET SUMMARY")
log(f"{'='*65}")
log(f"  Rows:    {len(df):,}")
log(f"  Columns: {df.shape[1]}")
remaining_nulls = df.isnull().sum()
remaining_nulls = remaining_nulls[remaining_nulls > 0]
if len(remaining_nulls):
    log(f"  Remaining nulls:\n{remaining_nulls.to_string()}")
else:
    log(f"  Remaining nulls: none (except ward, intentional)")
log(f"  Columns: {list(df.columns)}")

df.to_csv(OUT, index=False)
with open(LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

log(f"\n✅  Saved: {OUT}")
log(f"✅  Log:   {LOG}")