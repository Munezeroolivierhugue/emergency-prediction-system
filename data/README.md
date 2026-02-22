# SENTINEL — Data Cleaning & Processing Guide

**Montgomery County PA 911 Hotspot Prediction System**

---

## Overview

SENTINEL transforms raw Montgomery County 911 emergency call logs into a clean, model-ready dataset. The pipeline runs in three sequential steps: data cleaning, panel construction, and model training. This document covers the first two — everything that happens before a model sees a single row.

---

## Project Structure

```
sentinel_911/
├── data/
│   ├── raw/
│   │   └── 911.csv                     ← Place raw Kaggle file here
│   └── processed/
│       ├── incidents_cleaned.csv        ← Output of Step 1
│       ├── panel.csv                    ← Output of Step 2
│       ├── 01_cleaning_log.txt          ← Detailed cleaning audit trail
│       └── 02_panel_log.txt             ← Panel construction audit trail
|       │
|       pipeline/
|           ├── 01_data_cleaning.py              ← Step 1
|           └── 02_build_panel.py                ← Step 2


```

---

## Source Data

| Property | Value |
|---|---|
| Dataset | Montgomery County PA 911 Emergency Calls |
| Source | [Kaggle — mchirico/montcoalert](https://www.kaggle.com/datasets/mchirico/montcoalert) |
| Full date range | December 2015 – December 2020 |
| Uploaded subset | December 2015 – December 2016 (145,518 records) |
| Raw columns | 9 |

### Raw Columns

| Column | Type | Nulls | Description |
|---|---|---|---|
| `lat` | float | 0 | WGS84 latitude |
| `lng` | float | 0 | WGS84 longitude |
| `desc` | string | 0 | Full dispatch description text |
| `zip` | float | 18,346 (12.6%) | ZIP code, stored as float due to nulls |
| `title` | string | 0 | Call type in `"Type: Subtype"` format |
| `timeStamp` | string | 0 | Datetime of the call |
| `twp` | string | 47 (0.03%) | Township name |
| `addr` | string | 0 | Street address |
| `e` | int | 0 | Dummy column, always 1 |

---

## Step 1 — Data Cleaning

**Script:** `pipeline/01_data_cleaning.py`  
**Input:** `data/raw/911.csv`  
**Output:** `data/processed/incidents_cleaned.csv`  
**Log:** `data/processed/01_cleaning_log.txt`

### What it does

#### 1. Split `title` into `Type` and `Subtype`

The raw `title` field uses a `"Type: Subtype"` format, for example `"EMS: CARDIAC ARREST"` or `"Traffic: VEHICLE ACCIDENT -"`. The script splits on the first colon to produce two clean columns.

Traffic subtypes carry a trailing ` -` artifact in the raw data (e.g. `"VEHICLE ACCIDENT -"`). This is stripped so all subtypes are consistent labels regardless of call type.

**Type distribution after splitting:**

| Type | Count | Share |
|---|---|---|
| EMS | ~71,600 | 49.2% |
| Traffic | ~51,900 | 35.7% |
| Fire | ~22,000 | 15.1% |

There are 80 unique subtypes across all three types.

#### 2. Parse `timeStamp` and extract temporal features

The raw timestamp string is parsed into a proper datetime and the following features are extracted for use in modelling and EDA:

| Feature | Description |
|---|---|
| `year` | Calendar year |
| `month` | Calendar month (1–12) |
| `day` | Day of month |
| `hour` | Hour of day (0–23) |
| `day_of_week` | 0 = Monday, 6 = Sunday |
| `is_weekend` | 1 if Saturday or Sunday |
| `is_night` | 1 if hour is 22:00–05:59 |

#### 3. Impute missing `zip` values (12.6% null)

18,346 rows have no ZIP code. The imputation strategy is:

1. For each null-zip row, find the most common ZIP used by other calls from the same township. This handles the vast majority of cases.
2. Any rows whose township is also null fall back to the single most common ZIP in the entire dataset.

After imputation, ZIP is cast from float to a zero-padded 5-digit string (e.g. `19401`), since it is a geographic label, not a number.

#### 4. Impute missing `twp` values (0.03% null)

Only 47 rows are affected. The same modal-lookup strategy is applied in reverse: for each null-township row, the most common township associated with that row's ZIP code is used. A global modal fallback handles any remaining edge cases.

#### 5. Create the `Severity` target column

A `Severity` label is assigned to every call based on its `Subtype`, using a lookup table grounded in emergency triage logic.

| Level | Definition | Example subtypes |
|---|---|---|
| **Critical** | Immediate threat to life | `CARDIAC ARREST`, `CVA/STROKE`, `BUILDING FIRE`, `VEHICLE ACCIDENT`, `OVERDOSE` |
| **High** | Serious risk of harm or escalation | `HEAD INJURY`, `ALTERED MENTAL STATUS`, `GAS-ODOR/LEAK`, `ASSAULT VICTIM` |
| **Medium** | Urgent but not immediately life-threatening | `FALL VICTIM`, `FIRE ALARM`, `NAUSEA/VOMITING`, `CARBON MONOXIDE DETECTOR` |
| **Low** | Minor, administrative, or informational | `DISABLED VEHICLE`, `MEDICAL ALERT ALARM`, `TRANSFERRED CALL` |

Any subtype not in the lookup table defaults to `Medium` (conservative). The severity is also encoded as a numeric column (`severity_num`) for model features: Critical=3, High=2, Medium=1, Low=0.

**Severity distribution in this dataset:**

| Level | Count | Share |
|---|---|---|
| Critical | ~70,700 | 48.6% |
| High | ~19,200 | 13.2% |
| Medium | ~39,000 | 26.8% |
| Low | ~16,600 | 11.4% |

#### 6. Drop redundant columns

`title` is dropped because it is fully replaced by `Type` and `Subtype`. The dummy column `e` (always 1) is dropped because it carries no information.

### Clean dataset summary

| Property | Value |
|---|---|
| Rows | 145,518 |
| Columns | 18 |
| Null values | 0 |

**Output columns:** `lat`, `lng`, `desc`, `zip`, `timeStamp`, `twp`, `addr`, `Type`, `Subtype`, `year`, `month`, `day`, `hour`, `day_of_week`, `is_weekend`, `is_night`, `Severity`, `severity_num`

---

## Step 2 — Hotspot Panel Construction

**Script:** `pipeline/02_build_panel.py`  
**Input:** `data/processed/incidents_cleaned.csv`  
**Output:** `data/processed/panel.csv`  
**Log:** `data/processed/02_panel_log.txt`

### What it does

#### The prediction unit

Each row in the panel represents one township in one calendar month. The model's job is to predict, before the month begins, whether that township will have elevated call activity during that month.

This township × month structure was chosen because township is the native administrative unit in the 911 dataset — each has its own dispatch station and geographic boundary. The 67 townships in the county provide enough variation to make the classification problem meaningful.

#### Building the full grid

A complete grid of all 67 townships × all 13 months is constructed. Months where a township received zero calls are retained as negative training examples (non-hotspots), not dropped. Dropping them would bias the model by removing easy negatives.

#### Defining a hotspot

A township-month is labelled a **hotspot** (`is_hotspot = 1`) if its total call count is at or above the **75th percentile** of all non-zero township-months. In this dataset that threshold is **224 calls per month**. Approximately 25.3% of observations are hotspots.

The consistent top-volume townships are Lower Merion, Norristown, Pottstown, Abington, and Upper Merion.

#### Feature engineering — no data leakage

Every feature is strictly past-only. All raw aggregations are shifted by one period (`.shift(1)`) before any rolling or cumulative calculation, ensuring the model never sees information from the period it is predicting.

30 lag features are created per township:

| Feature group | Features |
|---|---|
| **Direct lags** | `lag_1`, `lag_2`, `lag_3` — call volumes from the previous 1, 2, and 3 months |
| **Rolling averages** | `roll_3m_mean`, `roll_6m_mean`, `roll_12m_mean` — average call volume over windows of 3, 6, and 12 past months |
| **Trend** | `trend_3m` — linear slope of call volume over the past 3 months |
| **Seasonality** | `same_month_last_year` — call volume in the same calendar month one year prior |
| **Cumulative rates** | `cum_hotspot_rate` — running fraction of past months this township was a hotspot |
| **Streak** | `hotspot_streak` — number of consecutive past months this township was a hotspot |
| **Severity lags** | `lag_1_critical`, `lag_1_high` — previous month's critical and high-severity call counts |
| **Type lags** | `lag_1_ems`, `lag_1_fire`, `lag_1_traffic` — previous month's call counts by call type |
| **Temporal context** | `month_sin`, `month_cos` — cyclical encoding of calendar month |

#### Warmup period

The first 3 months of data are used only to build initial lag features and are excluded from the modelled panel. On a 13-month dataset this is the minimum viable warmup. On the full 2015–2020 dataset, the warmup would extend to 12 months for more stable lag features.

### Panel summary

| Property | Value |
|---|---|
| Observations | 680 township-month rows |
| Townships | 68 |
| Modelled periods | 10 months (after 3-month warmup) |
| Features | 30 (all lagged, no leakage) |
| Hotspot rate | 25.3% (172 / 680) |
| Hotspot threshold | ≥ 224 calls/month (75th percentile) |

---

## Running the Pipeline

### Requirements

```
pandas
numpy
scikit-learn
matplotlib
seaborn
```

### Execution

Run the scripts in order from the project root:

```bash
python pipeline/01_data_cleaning.py
python pipeline/02_build_panel.py
python models/baseline/03_hotspot_model.py
```

Each script writes a detailed log file alongside its output. Check the logs first if anything looks unexpected.

### Upgrading to the full dataset

The pipeline is designed to run unchanged on the full 2015–2020 Kaggle file. Simply replace `data/raw/911.csv` with the complete download and rerun all three scripts. On the full dataset:

- The warmup period will extend to 12 months for more stable rolling features
- The train/test split will use 2019 as the validation year and 2020 as holdout
- The naive persistence baseline will drop, making the model's genuine predictive lift more visible
- Seasonal patterns will become meaningful across multiple years

---

## Key Design Decisions

**Why impute rather than drop nulls?** Dropping the 18,346 null-zip rows would remove 12.6% of the dataset and could introduce geographic bias if certain townships have systematically missing ZIP codes. Modal imputation by township is conservative and preserves all call records.

**Why township rather than grid cells?** The 911 dataset does not have precise enough coordinates for grid-cell aggregation to be meaningful. Township is the operationally relevant unit — dispatchers and stations are organised by township.

**Why 75th percentile as the hotspot threshold?** It produces a roughly 25/75 class split that is imbalanced enough to reflect real operational conditions (most townships in most months are not hotspots) while keeping enough positive examples for the model to learn from.

**Why include zero-call months?** Quiet townships in quiet months are legitimate negative examples. Excluding them would inflate model performance and produce a biased picture of what the model has actually learned.

---

*SENTINEL — Montgomery County PA 911 Hotspot Prediction*
