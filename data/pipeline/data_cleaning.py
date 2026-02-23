"""
911 Data Cleaning Pipeline
Cleans raw 911 call data for hotspot prediction analysis.
Processes Montgomery County PA 911 Emergency Calls dataset.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
INPUT_PATH = 'data/raw/911.csv'
OUTPUT_PATH = 'data/processed/incidents_cleaned.csv'
LOG_PATH = 'data/logs/01_cleaning_log.txt'

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
log_section('911 DATA CLEANING PIPELINE')
log(f'Started: {pd.Timestamp.now()}')
log(f'Input:  {INPUT_PATH}')
log(f'Output: {OUTPUT_PATH}')


#  LOAD DATA
log_section('1. LOADING DATA')

try:
    df = pd.read_csv(INPUT_PATH)
    log(f'Successfully loaded {df.shape[0]:,} rows × {df.shape[1]} columns')
    log(f'Columns: {list(df.columns)}')
    
    # Initial null analysis
    log('\nInitial null counts:')
    for col in df.columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            null_pct = null_count / len(df) * 100
            log(f'  {col:<12}: {null_count:>6,} ({null_pct:.1f}%)')
except FileNotFoundError:
    log(f'ERROR: Input file not found at {INPUT_PATH}')
    raise
except Exception as e:
    log(f'ERROR: Failed to load data - {str(e)}')
    raise


#  SPLIT TITLE INTO TYPE AND SUBTYPE

log_section('2. SPLITTING TITLE COLUMN')

split_result = df['title'].str.split(':', n=1, expand=True)
df['Type'] = split_result[0].str.strip()
df['Subtype'] = split_result[1].str.strip().str.rstrip(' -').str.strip()

log('Type distribution:')
for type_name, count in df['Type'].value_counts().items():
    percentage = count / len(df) * 100
    log(f'  {type_name:<10}: {count:>7,} ({percentage:.1f}%)')

log(f'\nUnique subtypes: {df["Subtype"].nunique()}')
log('Top 10 subtypes by volume:')
for subtype, count in df['Subtype'].value_counts().head(10).items():
    log(f'  {subtype:<45}: {count:>7,}')


#  PROCESS TIMESTAMPS

log_section('3. PROCESSING TIMESTAMPS')

df['timeStamp'] = pd.to_datetime(df['timeStamp'])

# Extract temporal features
df['year'] = df['timeStamp'].dt.year
df['month'] = df['timeStamp'].dt.month
df['day'] = df['timeStamp'].dt.day
df['hour'] = df['timeStamp'].dt.hour
df['day_of_week'] = df['timeStamp'].dt.dayofweek
df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
df['is_night'] = ((df['hour'] >= 22) | (df['hour'] < 6)).astype(int)

# Log temporal statistics
date_range = f"{df['timeStamp'].min().date()} → {df['timeStamp'].max().date()}"
log(f'Date range: {date_range}')
log(f'Years covered: {sorted(df["year"].unique())}')
log(f'Night calls (22:00–06:00): {df["is_night"].sum():,} ({df["is_night"].mean():.2%})')
log(f'Weekend calls: {df["is_weekend"].sum():,} ({df["is_weekend"].mean():.2%})')


#  HANDLE MISSING VALUES

log_section('4. HANDLING MISSING VALUES')

# 4a. Handle missing zip codes (12.6% missing)
missing_zip = df['zip'].isnull().sum()
log(f'Missing zip codes: {missing_zip:,} ({missing_zip/len(df):.2%})')

# Impute using township-based modal zip
township_modal_zip = (
    df[df['zip'].notnull()]
    .groupby('twp')['zip']
    .agg(lambda x: x.mode()[0])
    .rename('zip_imputed')
)

df = df.join(township_modal_zip, on='twp')
df.loc[df['zip'].isnull(), 'zip'] = df['zip_imputed']
df.drop(columns=['zip_imputed'], inplace=True)

# Fallback to global mode for any remaining nulls
df['zip'] = df['zip'].fillna(df['zip'].mode()[0])
df['zip'] = df['zip'].astype(int).astype(str).str.zfill(5)

# 4b. Handle missing townships (0.03% missing)
missing_twp = df['twp'].isnull().sum()
log(f'Missing townships: {missing_twp:,} ({missing_twp/len(df):.4%})')

# Impute using zip-based modal township
zip_modal_twp = (
    df[df['twp'].notnull()]
    .groupby('zip')['twp']
    .agg(lambda x: x.mode()[0])
    .rename('twp_imputed')
)

df = df.join(zip_modal_twp, on='zip')
df.loc[df['twp'].isnull(), 'twp'] = df['twp_imputed']
df.drop(columns=['twp_imputed'], inplace=True)

# Fallback to global mode for any remaining nulls
df['twp'] = df['twp'].fillna(df['twp'].mode()[0])

log(f'\nRemaining nulls after imputation:')
log(f'  zip: {df["zip"].isnull().sum()}')
log(f'  twp: {df["twp"].isnull().sum()}')

#  CREATE SEVERITY CLASSIFICATION

log_section('5. CREATING SEVERITY CLASSIFICATION')

# Severity mapping based on emergency triage logic
SEVERITY_MAPPING = {
    # Critical: Immediate life threat
    'CARDIAC ARREST': 'Critical',
    'CARDIAC EMERGENCY': 'Critical',
    'RESPIRATORY EMERGENCY': 'Critical',
    'UNCONSCIOUS SUBJECT': 'Critical',
    'UNRESPONSIVE SUBJECT': 'Critical',
    'CVA/STROKE': 'Critical',
    'SEIZURES': 'Critical',
    'OVERDOSE': 'Critical',
    'CHOKING': 'Critical',
    'SHOOTING': 'Critical',
    'STABBING': 'Critical',
    'ACTIVE SHOOTER': 'Critical',
    'DROWNING': 'Critical',
    'ELECTROCUTION': 'Critical',
    'BUILDING FIRE': 'Critical',
    'VEHICLE ACCIDENT': 'Critical',
    'TRAIN CRASH': 'Critical',
    'PLANE CRASH': 'Critical',
    'INDUSTRIAL ACCIDENT': 'Critical',
    'BOMB DEVICE FOUND': 'Critical',
    'AMPUTATION': 'Critical',
    'BURN VICTIM': 'Critical',
    'HEMORRHAGING': 'Critical',
    'SUICIDE THREAT': 'Critical',
    
    # High: Serious injury/harm risk
    'HEAD INJURY': 'High',
    'ALTERED MENTAL STATUS': 'High',
    'SYNCOPAL EPISODE': 'High',
    'ALLERGIC REACTION': 'High',
    'DIABETIC EMERGENCY': 'High',
    'UNKNOWN MEDICAL EMERGENCY': 'High',
    'ASSAULT VICTIM': 'High',
    'GAS-ODOR/LEAK': 'High',
    'VEHICLE FIRE': 'High',
    'HAZARDOUS MATERIALS INCIDENT': 'High',
    'ELECTRICAL FIRE OUTSIDE': 'High',
    'ARMED SUBJECT': 'High',
    'FRACTURE': 'High',
    'POISONING': 'High',
    'RESCUE - WATER': 'High',
    'RESCUE - TECHNICAL': 'High',
    'WARRANT SERVICE': 'High',
    
    # Medium: Urgent but not life-threatening
    'FALL VICTIM': 'Medium',
    'SUBJECT IN PAIN': 'Medium',
    'ABDOMINAL PAINS': 'Medium',
    'BACK PAINS/INJURY': 'Medium',
    'GENERAL WEAKNESS': 'Medium',
    'LACERATIONS': 'Medium',
    'NAUSEA/VOMITING': 'Medium',
    'DIZZINESS': 'Medium',
    'FEVER': 'Medium',
    'DEHYDRATION': 'Medium',
    'HEAT EXHAUSTION': 'Medium',
    'MATERNITY': 'Medium',
    'ANIMAL BITE': 'Medium',
    'EYE INJURY': 'Medium',
    'FIRE ALARM': 'Medium',
    'WOODS/FIELD FIRE': 'Medium',
    'CARBON MONOXIDE DETECTOR': 'Medium',
    'ROAD OBSTRUCTION': 'Medium',
    'HAZARDOUS ROAD CONDITIONS': 'Medium',
    'VEHICLE LEAKING FUEL': 'Medium',
    'RESCUE - ELEVATOR': 'Medium',
    'RESCUE - GENERAL': 'Medium',
    'UNKNOWN TYPE FIRE': 'Medium',
    'APPLIANCE FIRE': 'Medium',
    'TRASH/DUMPSTER FIRE': 'Medium',
    'HIT + RUN': 'Medium',
    
    # Low: Minor or administrative
    'DISABLED VEHICLE': 'Low',
    'FIRE INVESTIGATION': 'Low',
    'FIRE SPECIAL SERVICE': 'Low',
    'FIRE POLICE NEEDED': 'Low',
    'MEDICAL ALERT ALARM': 'Low',
    'EMS SPECIAL SERVICE': 'Low',
    'DEBRIS/FLUIDS ON HIGHWAY': 'Low',
    'S/B AT HELICOPTER LANDING': 'Low',
    'PUMP DETAIL': 'Low',
    'TRANSFERRED CALL': 'Low',
    'POLICE INFORMATION': 'Low',
    'SUSPICIOUS': 'Low',
    'STANDBY FOR ANOTHER CO': 'Low',
}

# Apply severity mapping
df['Severity'] = df['Subtype'].map(SEVERITY_MAPPING)

# Handle unmapped subtypes
unmapped_mask = df['Severity'].isnull()
if unmapped_mask.sum() > 0:
    log(f'\nUnmapped subtypes ({unmapped_mask.sum():,} rows) → defaulting to Medium:')
    for subtype, count in df.loc[unmapped_mask, 'Subtype'].value_counts().items():
        log(f'  {subtype:<45}: {count:>7,}')
    df['Severity'] = df['Severity'].fillna('Medium')

# Convert to ordered categorical
SEVERITY_ORDER = ['Critical', 'High', 'Medium', 'Low']
df['Severity'] = pd.Categorical(df['Severity'], categories=SEVERITY_ORDER, ordered=True)

# Create numeric encoding for modeling
SEVERITY_NUMERIC = {'Critical': 3, 'High': 2, 'Medium': 1, 'Low': 0}
df['severity_num'] = df['Severity'].map(SEVERITY_NUMERIC)

# Log severity distribution
log('\nSeverity distribution:')
for level in SEVERITY_ORDER:
    count = (df['Severity'] == level).sum()
    percentage = count / len(df) * 100
    log(f'  {level:<10}: {count:>7,} ({percentage:.1f}%)')

#  FINAL CLEANUP

log_section('6. FINAL CLEANUP')

# Drop unnecessary columns
columns_to_drop = ['e', 'title']
df.drop(columns=columns_to_drop, inplace=True)
log(f'Dropped columns: {columns_to_drop}')

#  SAVE RESULTS

log_section('7. SAVING RESULTS')

# Final dataset summary
log(f'Final dataset shape: {df.shape[0]:,} rows × {df.shape[1]} columns')
log(f'Columns: {list(df.columns)}')

# Check for remaining nulls
remaining_nulls = df.isnull().sum()
remaining_nulls = remaining_nulls[remaining_nulls > 0]
if len(remaining_nulls) > 0:
    log(f'\nRemaining null values:')
    for col, count in remaining_nulls.items():
        log(f'  {col}: {count:,}')
else:
    log(f'\nNo remaining null values')

# Save cleaned data
try:
    df.to_csv(OUTPUT_PATH, index=False)
    log(f'\n✅ Cleaned data saved to: {OUTPUT_PATH}')
except Exception as e:
    log(f'❌ Error saving data: {str(e)}')
    raise

# Save log file
try:
    with open(LOG_PATH, 'w', encoding='utf-8') as log_file:
        log_file.write('\n'.join(log_lines))
    log(f'✅ Log file saved to: {LOG_PATH}')
except Exception as e:
    log(f'⚠️  Error saving log file: {str(e)}')

log_section('PROCESSING COMPLETE')
log(f'Completed: {pd.Timestamp.now()}')