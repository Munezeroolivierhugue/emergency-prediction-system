"""
SENTINEL — 911 Hotspot Prediction System
=========================================
Step 1: Data Cleaning
File  : pipeline/01_data_cleaning.py
Input : data/raw/911.csv
Output: data/processed/incidents_cleaned.csv

Source dataset:
    Montgomery County PA 911 Emergency Calls
    https://www.kaggle.com/datasets/mchirico/montcoalert
    145,518 records  |  2015-12-10 → 2016-12-19

Raw columns (9):
    lat        — WGS84 latitude (no nulls)
    lng        — WGS84 longitude (no nulls)
    desc       — full dispatch description string (no nulls)
    zip        — zip code as float, 18,346 nulls (12.6%)
    title      — "Type: Subtype" e.g. "EMS: CARDIAC ARREST" (no nulls)
    timeStamp  — datetime string "YYYY-MM-DD HH:MM:SS" (no nulls)
    twp        — township name, 47 nulls (0.03%)
    addr       — street address (no nulls)
    e          — dummy column, always 1

Card criteria implemented:
    1. Split title      → Type + Subtype columns
    2. Parse timeStamp  → datetime + temporal features
    3. Handle nulls     → zip (12.6%), twp (0.03%)
    4. Create Severity  → Critical / High / Medium / Low from Subtype
    5. Save to data/processed/incidents_cleaned.csv

Additional fixes:
    6. Clean Subtype    — strip trailing " -" (Traffic subtypes have it)
    7. Drop e column    — no analytical value
    8. Cast zip         — float → string (it is a label, not a number)
"""

import pandas as pd
import numpy as np
import os

IN  = 'data/raw/911.csv'
OUT = 'data/processed/incidents_cleaned.csv'
LOG = 'data/logs/01_cleaning_log.txt'

os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/logs', exist_ok=True)

lines = []
def log(msg=''):
    print(msg)
    lines.append(str(msg))

log('=' * 65)
log('SENTINEL  |  Step 1: Data Cleaning  |  Montgomery County 911')
log('=' * 65)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(IN)
log(f'\n[LOAD]  Raw shape: {df.shape[0]:,} rows × {df.shape[1]} columns')
log(f'        Columns: {list(df.columns)}')
log(f'\n        Null counts:')
for col in df.columns:
    n = df[col].isnull().sum()
    pct = f'  ({n/len(df):.1%})' if n > 0 else ''
    log(f'          {col:<12} {n:>6,} nulls{pct}')

# ──  Split title into Type and Subtype ──────────────────────────────────
# title is always "Type: Subtype" with exactly 3 possible Types:
#   EMS, Fire, Traffic
# Split on the first colon only (n=1) in case subtype ever contains a colon.
log(f'\n[1]  Splitting title → Type + Subtype')

split       = df['title'].str.split(':', n=1, expand=True)
df['Type']  = split[0].str.strip()

#  Traffic subtypes carry a trailing " -" artifact
# e.g. "Traffic: VEHICLE ACCIDENT -"  →  Subtype should be "VEHICLE ACCIDENT"
# Strip trailing whitespace and dash so all subtypes are clean labels.
df['Subtype'] = split[1].str.strip().str.rstrip(' -').str.strip()

log(f'     Type distribution:')
for t, cnt in df['Type'].value_counts().items():
    log(f'       {t:<10}  {cnt:,}  ({cnt/len(df):.1%})')
log(f'     Unique subtypes: {df["Subtype"].nunique()}')
log(f'     Top 10 subtypes by volume:')
for sub, cnt in df['Subtype'].value_counts().head(10).items():
    log(f'       {sub:<45} {cnt:,}')

# ──  Parse timeStamp ────────────────────────────────────────────────────
# Raw format: "2015-12-10 17:10:52" — clean, no timezone, no fractional seconds.
# Extract temporal features for modelling and EDA.
log(f'\n[2]  Parsing timeStamp → datetime + temporal features')

df['timeStamp']   = pd.to_datetime(df['timeStamp'])
df['year']        = df['timeStamp'].dt.year
df['month']       = df['timeStamp'].dt.month
df['day']         = df['timeStamp'].dt.day
df['hour']        = df['timeStamp'].dt.hour
df['day_of_week'] = df['timeStamp'].dt.dayofweek   # 0=Monday, 6=Sunday
df['is_weekend']  = (df['day_of_week'] >= 5).astype(int)
df['is_night']    = ((df['hour'] >= 22) | (df['hour'] < 6)).astype(int)

log(f'     Date range: {df["timeStamp"].min().date()}  →  {df["timeStamp"].max().date()}')
log(f'     Years covered: {sorted(df["year"].unique())}')
log(f'     Night calls (22:00–06:00): {df["is_night"].sum():,}  ({df["is_night"].mean():.1%})')
log(f'     Weekend calls:             {df["is_weekend"].sum():,}  ({df["is_weekend"].mean():.1%})')

# ── Handle null zip (18,346 nulls — 12.6%) ────────────────────────────
# zip is stored as float (e.g. 19525.0) because of nulls. Cast to string after
# imputation. Strategy: assign the most common zip for the same township.
# Any rows whose township is also null get the global modal zip.
n_null_zip = df['zip'].isnull().sum()
log(f'\n[3a] zip nulls: {n_null_zip:,}  (12.6%)')
log(f'     Strategy: modal zip per township → global modal fallback')

twp_modal_zip = (
    df[df['zip'].notnull()]
    .groupby('twp')['zip']
    .agg(lambda x: x.mode()[0])
    .rename('zip_imputed')
)
df = df.join(twp_modal_zip, on='twp')
mask_a = df['zip'].isnull() & df['zip_imputed'].notnull()
df.loc[mask_a, 'zip'] = df.loc[mask_a, 'zip_imputed']
df.drop(columns=['zip_imputed'], inplace=True)

remaining_zip = df['zip'].isnull().sum()
if remaining_zip > 0:
    global_modal_zip = df['zip'].mode()[0]
    df['zip'] = df['zip'].fillna(global_modal_zip)
    log(f'     Township modal zip: resolved {n_null_zip - remaining_zip:,}')
    log(f'     Global modal fallback: resolved {remaining_zip:,}')
else:
    log(f'     Township modal zip: resolved all {n_null_zip:,}')

# Cast to int then string — zip is a label, not a number
df['zip'] = df['zip'].astype(int).astype(str).str.zfill(5)
log(f'     Cast zip float → 5-digit string (e.g. 19401)')
log(f'     Remaining nulls: {df["zip"].isnull().sum()}')

# ── Handle null twp (47 nulls — 0.03%) ────────────────────────────────
# Only 47 rows — small enough that the exact strategy matters less than being
# explicit about it. Use modal township for the same zip code.
n_null_twp = df['twp'].isnull().sum()
log(f'\n[3b] twp nulls: {n_null_twp:,}  (0.03%)')
log(f'     Strategy: modal township per zip → global modal fallback')

zip_modal_twp = (
    df[df['twp'].notnull()]
    .groupby('zip')['twp']
    .agg(lambda x: x.mode()[0])
    .rename('twp_imputed')
)
df = df.join(zip_modal_twp, on='zip')
mask_b = df['twp'].isnull() & df['twp_imputed'].notnull()
df.loc[mask_b, 'twp'] = df.loc[mask_b, 'twp_imputed']
df.drop(columns=['twp_imputed'], inplace=True)

remaining_twp = df['twp'].isnull().sum()
if remaining_twp > 0:
    df['twp'] = df['twp'].fillna(df['twp'].mode()[0])
log(f'     Remaining nulls: {df["twp"].isnull().sum()}')

# ──  Create Severity target ────────────────────────────────────────────
# Severity is mapped from Subtype using a lookup grounded in the actual
# subtypes present in this dataset (76 unique subtypes after cleaning).
# Classification follows emergency triage logic:
#   Critical — immediate threat to life requiring fastest possible response
#   High     — serious injury or significant harm likely without rapid response
#   Medium   — urgent but not immediately life-threatening
#   Low      — minor, administrative, or informational
log(f'\n[4]  Creating Severity target from Subtype')

SEVERITY_MAP = {
    # ── CRITICAL ─────────────────────────────────────────────────────────────
    # Direct life threat — seconds matter
    'CARDIAC ARREST':             'Critical',
    'CARDIAC EMERGENCY':          'Critical',
    'RESPIRATORY EMERGENCY':      'Critical',
    'UNCONSCIOUS SUBJECT':        'Critical',
    'UNRESPONSIVE SUBJECT':       'Critical',
    'CVA/STROKE':                 'Critical',
    'SEIZURES':                   'Critical',
    'OVERDOSE':                   'Critical',
    'CHOKING':                    'Critical',
    'SHOOTING':                   'Critical',
    'STABBING':                   'Critical',
    'ACTIVE SHOOTER':             'Critical',
    'DROWNING':                   'Critical',
    'ELECTROCUTION':              'Critical',
    'BUILDING FIRE':              'Critical',
    'VEHICLE ACCIDENT':           'Critical',   # EMS + Traffic + Fire all map here
    'TRAIN CRASH':                'Critical',
    'PLANE CRASH':                'Critical',
    'INDUSTRIAL ACCIDENT':        'Critical',
    'BOMB DEVICE FOUND':          'Critical',
    'AMPUTATION':                 'Critical',
    'BURN VICTIM':                'Critical',
    'HEMORRHAGING':               'Critical',
    'SUICIDE THREAT':             'Critical',

    # ── HIGH ─────────────────────────────────────────────────────────────────
    # Serious — significant risk of harm or escalation
    'HEAD INJURY':                'High',
    'ALTERED MENTAL STATUS':      'High',
    'SYNCOPAL EPISODE':           'High',
    'ALLERGIC REACTION':          'High',
    'DIABETIC EMERGENCY':         'High',
    'UNKNOWN MEDICAL EMERGENCY':  'High',
    'ASSAULT VICTIM':             'High',
    'GAS-ODOR/LEAK':              'High',
    'VEHICLE FIRE':               'High',
    'HAZARDOUS MATERIALS INCIDENT':'High',
    'ELECTRICAL FIRE OUTSIDE':    'High',
    'ARMED SUBJECT':              'High',
    'FRACTURE':                   'High',
    'POISONING':                  'High',
    'RESCUE - WATER':             'High',
    'RESCUE - TECHNICAL':         'High',
    'WARRANT SERVICE':            'High',

    # ── MEDIUM ───────────────────────────────────────────────────────────────
    # Urgent but not immediately life-threatening
    'FALL VICTIM':                'Medium',
    'SUBJECT IN PAIN':            'Medium',
    'ABDOMINAL PAINS':            'Medium',
    'BACK PAINS/INJURY':          'Medium',
    'GENERAL WEAKNESS':           'Medium',
    'LACERATIONS':                'Medium',
    'NAUSEA/VOMITING':            'Medium',
    'DIZZINESS':                  'Medium',
    'FEVER':                      'Medium',
    'DEHYDRATION':                'Medium',
    'HEAT EXHAUSTION':            'Medium',
    'MATERNITY':                  'Medium',
    'ANIMAL BITE':                'Medium',
    'EYE INJURY':                 'Medium',
    'FIRE ALARM':                 'Medium',
    'WOODS/FIELD FIRE':           'Medium',
    'CARBON MONOXIDE DETECTOR':   'Medium',
    'ROAD OBSTRUCTION':           'Medium',
    'HAZARDOUS ROAD CONDITIONS':  'Medium',
    'VEHICLE LEAKING FUEL':       'Medium',
    'RESCUE - ELEVATOR':          'Medium',
    'RESCUE - GENERAL':           'Medium',
    'UNKNOWN TYPE FIRE':          'Medium',
    'APPLIANCE FIRE':             'Medium',
    'TRASH/DUMPSTER FIRE':        'Medium',
    'HIT + RUN':                  'Medium',

    # ── LOW ──────────────────────────────────────────────────────────────────
    # Minor, administrative, or informational
    'DISABLED VEHICLE':           'Low',
    'FIRE INVESTIGATION':         'Low',
    'FIRE SPECIAL SERVICE':       'Low',
    'FIRE POLICE NEEDED':         'Low',
    'MEDICAL ALERT ALARM':        'Low',
    'EMS SPECIAL SERVICE':        'Low',
    'DEBRIS/FLUIDS ON HIGHWAY':   'Low',
    'S/B AT HELICOPTER LANDING':  'Low',
    'PUMP DETAIL':                'Low',
    'TRANSFERRED CALL':           'Low',
    'POLICE INFORMATION':         'Low',
    'SUSPICIOUS':                 'Low',
    'STANDBY FOR ANOTHER CO':     'Low',
}

df['Severity'] = df['Subtype'].map(SEVERITY_MAP)

# Any unmapped subtypes — log them and default to Medium (conservative)
unmapped = df['Severity'].isnull()
if unmapped.sum() > 0:
    log(f'     Unmapped subtypes ({unmapped.sum():,} rows) → defaulting to Medium:')
    for sub, cnt in df.loc[unmapped, 'Subtype'].value_counts().items():
        log(f'       {sub:<45} {cnt:,}')
df['Severity'] = df['Severity'].fillna('Medium')

# Ordered categorical for correct chart sorting
SEVERITY_ORDER = ['Critical', 'High', 'Medium', 'Low']
df['Severity'] = pd.Categorical(df['Severity'],
                                categories=SEVERITY_ORDER, ordered=True)

# Numeric encoding for model features
df['severity_num'] = df['Severity'].map(
    {'Critical': 3, 'High': 2, 'Medium': 1, 'Low': 0}
)

log(f'     Severity distribution:')
for level in SEVERITY_ORDER:
    n = (df['Severity'] == level).sum()
    log(f'       {level:<10}  {n:,}  ({n/len(df):.1%})')

# ──  Drop e column ──────────────────────────────────────────────────────
# Always 1 — no analytical value whatsoever.
df.drop(columns=['e'], inplace=True)
log(f'\n[5]  Dropped dummy column "e" (always 1)')

# ── Drop original title ────────────────────────────────────────────────
# Fully replaced by Type + Subtype. Keeping it would be redundant.
df.drop(columns=['title'], inplace=True)
log(f'[6]  Dropped "title" (replaced by Type + Subtype)')

# ── Final summary ─────────────────────────────────────────────────────────────
log(f'\n{"=" * 65}')
log(f'CLEAN DATASET SUMMARY')
log(f'{"=" * 65}')
log(f'  Rows:    {len(df):,}')
log(f'  Columns: {df.shape[1]}')
remaining_nulls = df.isnull().sum()
remaining_nulls = remaining_nulls[remaining_nulls > 0]
if len(remaining_nulls):
    log(f'  Remaining nulls:\n{remaining_nulls.to_string()}')
else:
    log(f'  Remaining nulls: none')
log(f'  Columns: {list(df.columns)}')

df.to_csv(OUT, index=False)
with open(LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

log(f'\n✅  Saved: {OUT}')
log(f'✅  Log:   {LOG}')
