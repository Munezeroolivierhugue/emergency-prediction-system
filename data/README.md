# SENTINEL — Data Cleaning & Processing
## Chicago Crime Hotspot Prediction System

---

## Overview

This document covers the first two steps of the SENTINEL pipeline: cleaning the raw Chicago Police Department (CPD) crime dataset and transforming it into a machine-learning-ready panel structure. These two steps are the foundation everything else depends on. A model is only as trustworthy as the data it was built on.

The pipeline is split into two scripts because cleaning and feature engineering are fundamentally different activities with different failure modes, different audit requirements, and different audiences. A data analyst reviewing data quality decisions should not have to read model code — and vice versa.

```
raw_crimes.csv
      │
      ▼
01_data_cleaning.py  ──►  cleaned.csv
      │
      ▼
02_build_panel.py    ──►  panel.csv
      │
      ▼
03_hotspot_model.py
```

---

## Files

| File | Input | Output | Purpose |
|------|-------|--------|---------|
| `01_data_cleaning.py` | `data/raw_crimes.csv` | `data/cleaned.csv` | Fix all data quality issues |
| `02_build_panel.py` | `data/cleaned.csv` | `data/panel.csv` | Build spatiotemporal feature matrix |
| `data/01_cleaning_log.txt` | — | auto-generated | Full audit log of every change |
| `data/02_panel_log.txt` | — | auto-generated | Panel construction audit log |

---

## How to Run

```bash
# From the project root directory
python 01_data_cleaning.py
python 02_build_panel.py
```

Both scripts print a full log to the console and save the same log to a `.txt` file in `data/`. Run them in order. Do not skip `01` and run `02` directly — `02` depends on columns added by `01`.

**Requirements:** `pandas`, `numpy` (standard data science stack, no additional installs needed)

---

## Part 1 — Data Cleaning (`01_data_cleaning.py`)

### Raw Dataset

The input is the Chicago Police Department crime dataset downloaded from the [Chicago Data Portal](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2). The sample used in this project contains 10,000 rows spanning 2001–2026 with 22 columns per record.

**Raw dataset shape:** 10,000 rows × 22 columns

### What Cleaning Means Here

Every change to the raw data is a decision that can affect model validity. This script operates on a single principle: **nothing is dropped or modified without a documented reason**. The audit log captures every change with the number of rows affected so the full cleaning history is reproducible and reviewable.

---

### Fix 1 — Drop Admin Columns

**Columns removed:** `unique_key`, `case_number`, `updated_on`, `location`

These are database housekeeping fields, not attributes of the crime itself.

- `unique_key` and `case_number` are internal CPD identifiers. They carry no pattern the model can learn from.
- `updated_on` records when the database row was last edited — irrelevant to when or where the crime happened.
- `location` is a string like `"(41.84, -87.62)"` that duplicates the `latitude` and `longitude` columns in a less useful format.

Removing them reduces the column count from 22 to 18 and eliminates any risk of the model accidentally treating a record ID as a predictive feature.

---

### Fix 2 — Parse Timezone-Aware Dates

**Column:** `date`

Raw format: `2024-01-01 18:35:00+00:00` (UTC offset included)

Pandas cannot perform consistent date arithmetic — computing hour of day, month, year, or the difference between two dates — when some values carry a timezone and others do not. The UTC offset is stripped, converting all dates to naive datetime objects in UTC.

```python
df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_localize(None)
```

**After:** `2024-01-01 18:35:00` — consistent, comparable, arithmetic-safe.

---

### Fix 3 — Normalise Primary Type Labels

**Column:** `primary_type`

CPD changed its label for one crime category around 2014:

| Old label | New label | Rows affected |
|-----------|-----------|---------------|
| `CRIM SEXUAL ASSAULT` | `CRIMINAL SEXUAL ASSAULT` | 19 |

Both labels refer to the same crime. Leaving them separate creates two features for one crime type, which inflates apparent diversity in the data and causes the model to treat them as unrelated categories. They are merged into the current official label.

This is the only label normalisation required. The remaining 27 crime types are consistent across the full date range.

---

### Fix 4 — Drop Null Coordinate Rows

**Columns:** `latitude`, `longitude`

**Rows dropped:** 114 (1.1% of raw data)

114 records have no latitude or longitude. Since SENTINEL is a spatial prediction system, every record must be assignable to a geographic grid cell. Records without coordinates cannot be placed on the map and are therefore impossible to use in either training or evaluation.

**Why not impute coordinates?** Fabricating a location for a crime would introduce false spatial signal into the model — potentially directing patrol resources to the wrong areas. Dropping these 114 rows is the only honest option.

**Rows remaining after this step:** 9,886

---

### Fix 5 — Impute Missing Community Area

**Column:** `community_area`

**Rows affected:** 625 (6.3% of remaining data)

625 rows have valid coordinates but no `community_area` assigned. Rather than dropping these rows or filling with a single global value, a three-stage imputation strategy recovers the most accurate estimate for each record:

**Stage a — Grid-cell modal value (resolves all 625)**
Each record is mapped to a 0.01° grid cell using its latitude and longitude. The most common `community_area` among other crimes in the same cell is assigned. This works because the grid cells are small enough (~1.1 km²) that crimes within the same cell almost always belong to the same community area.

```python
df['lat_grid'] = (df['latitude']  / 0.01).round().astype(int)
df['lon_grid'] = (df['longitude'] / 0.01).round().astype(int)
```

**Stage b — District median (fallback)**
Any records that could not be resolved in stage a (grid cell contains only one record with a null community area) are filled using the median community area for the police district the crime belongs to.

**Stage c — Global median (final fallback)**
Any remaining nulls after stages a and b receive the dataset-wide median community area. In practice, stage a resolves all 625 records in this dataset.

**Result:** 0 null values remain in `community_area`.

---

### Fix 6 — Impute Missing Location Description

**Column:** `location_description`

**Rows affected:** 30

30 records have no `location_description`. These are predominantly `DECEPTIVE PRACTICE` (financial identity theft) incidents, which often have no physical crime scene — they occur online or through the mail.

These rows are filled with the literal string `'UNKNOWN'`. This is an honest category that the model can learn from — it is not a guess about where the crime happened. An `'UNKNOWN'` location type is genuinely informative (it signals an online or remote crime) and should not be replaced with the most common location type.

---

### Fix 7 — Flag Partial Year 2026

**Column added:** `is_partial_year`

41 records exist from 2026 (January–February). These are valid crimes but represent an incomplete year. Including them in year-over-year trend analysis would make 2026 appear to have dramatically lower crime than any prior year — a misleading artefact.

Rather than dropping them, a binary flag `is_partial_year = 1` is added. This allows:
- Year-over-year charts to filter them out (`df[df['is_partial_year'] == 0]`)
- The panel construction to exclude 2026 from the monthly grid without losing any data
- Future users to make their own decision about whether to include them

---

### Fix 8 — Cast Boolean Columns to Integer

**Columns:** `arrest`, `domestic`

These columns are Python `bool` type (`True`/`False`). Scikit-learn and most ML libraries expect numeric input. They are cast to `int` (0/1).

```python
df['arrest']   = df['arrest'].astype(int)
df['domestic'] = df['domestic'].astype(int)
```

**Resulting rates:** 25.1% of incidents resulted in arrest; 10.0% were domestic incidents.

---

### Fix 9 — Ward (Intentional Non-Fix)

**Column:** `ward`

619 rows (6.3%) are missing a ward value. Unlike `community_area`, ward cannot be reliably imputed from coordinates alone because ward boundaries are political and irregular. The column is retained in `cleaned.csv` but excluded from all downstream model features. It may be useful for reporting or joining with other ward-level datasets.

---

### Enrichment — Severity Tier

**Columns added:** `severity`, `high_risk`

This is not a fix — it is an analytical enrichment. Each crime type is classified into one of four severity tiers based on the FBI NIBRS classification system and CPD's own crime category definitions:

| Tier | Label | Crime Types |
|------|-------|-------------|
| 3 | Critical | Homicide, Criminal Sexual Assault, Kidnapping, Arson |
| 2 | High | Robbery, Weapons Violation, Assault, Battery, Stalking, Intimidation, Sex Offense, Offense Involving Children |
| 1 | Medium | Burglary, Motor Vehicle Theft, Narcotics, Theft, Criminal Damage, Deceptive Practice, and others |
| 0 | Low | Criminal Trespass, Other Offense, Public Indecency, and others |

`high_risk = 1` where `severity >= 2` (Tier 2 or 3).

**Important:** The hotspot model target (`is_hotspot`) is defined by raw crime *volume* per cell-month, not by severity. Severity is used in exploratory analysis and as one of the aggregated features in the panel. It is not directly the target — this is documented explicitly to prevent confusion about what the model is predicting.

---

### Clean Dataset Summary

| Metric | Value |
|--------|-------|
| Raw rows | 10,000 |
| Rows dropped (null coords) | 114 |
| **Final rows** | **9,886** |
| Final columns | 23 |
| Remaining nulls | `ward` only (619) — intentional |
| Date range | 2001-01-01 → 2026-02-09 |
| Arrest rate | 25.1% |
| Domestic rate | 10.0% |
| High-risk incidents (Tier 2+3) | 2,469 (25.0%) |

---

## Part 2 — Panel Construction (`02_build_panel.py`)

### Why a Panel? The Core Design Argument

The cleaned dataset has one row per crime incident. You cannot train a hotspot prediction model directly on this structure.

If you train on incident rows, the model learns to answer: *"given that a crime has already happened here, what type is it?"* That is a **reactive classifier** — it only activates after a crime is reported. It tells you nothing about where to deploy patrol resources before anything happens.

To predict **where crime will occur next month**, the unit of observation must change from an incident to a **location × time combination**. Every grid cell gets a row for every month, whether or not a crime was recorded there. The model then learns to distinguish cells that are about to spike from cells that will remain quiet.

This transformation — from incident records to a panel of cell-months — is the single most important step in making the model genuinely predictive rather than descriptive.

---

### Geographic Grid

Each crime record is mapped to a **0.01° grid cell** using its latitude and longitude:

```python
df['lat_grid']  = (df['latitude']  / 0.01).round().astype(int)
df['lon_grid']  = (df['longitude'] / 0.01).round().astype(int)
df['grid_cell'] = df['lat_grid'].astype(str) + '_' + df['lon_grid'].astype(str)
```

At Chicago's latitude (~41°N), 0.01° corresponds to approximately:
- **North-south:** 1.11 km
- **East-west:** 0.83 km
- **Area:** ~0.92 km² per cell

This resolution is small enough to be operationally meaningful (a patrol officer can cover a cell on foot) and large enough to accumulate enough incidents per cell to compute stable statistics.

The dataset produces **40 unique grid cells**.

---

### Panel Construction

The panel is built by taking the Cartesian product of all grid cells and all monthly periods:

```
40 cells × 300 months (Jan 2001 – Dec 2025) = 12,000 cell-month rows
```

**This explicitly includes months where a cell had zero crimes.** This is not a mistake — it is essential. The model must train on both the positive class (this cell was a hotspot) and the negative class (this cell was quiet). If zero-crime months were excluded, the model would never learn what a quiet cell looks like and would be unable to distinguish genuinely safe areas from dangerous ones.

Zero-crime cell-months: **7,448 (62.1%)** — all retained.

---

### Target Variable: `is_hotspot`

```
is_hotspot = 1  if total crimes in this cell-month ≥ 75th percentile
                  of all non-zero cell-months
is_hotspot = 0  otherwise
```

**Threshold:** 3 or more crimes in a single cell in a single month.

This definition follows the standard criminological hotspot classification used in academic literature and by police departments implementing CompStat-style systems. The top quartile of crime activity represents a genuinely elevated level that warrants a different operational response.

**Hotspot rate in the model panel:** 9.5% (1,096 of 11,520 cell-months)

The class imbalance (9.5% positive) is real and expected. Most areas are not hotspots most of the time. The evaluation metrics — particularly AUC and the precision-recall curve — are chosen specifically because they handle class imbalance correctly, unlike accuracy.

---

### The No-Leakage Rule

Every feature in the panel is computed **exclusively from data that existed before the period being predicted**. The model never sees any information from the current month when making its prediction for that month.

This constraint is enforced by using `.shift(1)` before any rolling or expanding computation. Without this, the model could inadvertently access current-period data during training, producing optimistic performance estimates that collapse in deployment.

```python
# CORRECT — shift ensures we only use data up to last month
panel['crimes_roll3m'] = grp['total_crimes'].shift(1).rolling(3).mean()

# WRONG — this would include the current month
panel['crimes_roll3m'] = grp['total_crimes'].rolling(3).mean()
```

---

### Feature Groups

#### A. Direct Lag Features
The most important feature group. Exact crime counts from 1, 2, and 3 months prior.

| Feature | Description |
|---------|-------------|
| `crimes_lag1` | Total crimes in this cell, 1 month ago |
| `crimes_lag2` | Total crimes in this cell, 2 months ago |
| `crimes_lag3` | Total crimes in this cell, 3 months ago |
| `violent_lag1/2/3` | Violent crimes (Tier 2+3) at each lag |
| `hotspot_lag1/2/3` | Was this cell a hotspot at each lag? (0 or 1) |

Crime is spatially persistent — the best single predictor of whether a cell will be a hotspot next month is whether it was a hotspot last month. These lag features capture that signal directly.

#### B. Rolling Window Averages
Smooth out month-to-month noise by averaging over longer windows.

| Feature | Description |
|---------|-------------|
| `crimes_roll3m` | 3-month trailing average crime count |
| `crimes_roll6m` | 6-month trailing average crime count |
| `crimes_roll12m` | 12-month trailing average crime count |
| `violent_roll3m/6m/12m` | Same for violent crimes |
| `hotspot_roll3m/6m/12m` | Proportion of past 3/6/12 months spent as a hotspot |

A cell with 5 crimes one month and 0 the next may just be noise. A cell averaging 3 crimes per month over the past year is genuinely elevated. Rolling features let the model distinguish persistent patterns from random spikes.

#### C. Crime Trend
```
crime_trend_3m = crimes_lag1 - crimes_lag3
```
A positive value means crime is rising; negative means it is falling. This is separate from the absolute level. A cell at 4 crimes/month rising from 1 is a different operational situation than a cell at 4 crimes/month falling from 7, even though the current count is identical.

#### D. Seasonality
| Feature | Description |
|---------|-------------|
| `crimes_same_month_ly` | Crime count in this cell, same month last year |
| `hotspot_same_month_ly` | Was this cell a hotspot, same month last year? |

Crime follows annual cycles — August is typically more active than January. By giving the model the value from the same month in the prior year, it learns to separate the expected seasonal baseline from genuine elevated activity.

#### E. Long-Run Cumulative Baseline
| Feature | Description |
|---------|-------------|
| `cumulative_crime_rate` | All-time average monthly crime count up to last month |
| `cumulative_hotspot_rate` | Proportion of all past months spent as a hotspot |

This gives the model each cell's long-run character — is this fundamentally a high-crime area or a low-crime area? A cell with a cumulative hotspot rate of 0.6 is structurally different from one with a rate of 0.05, even if their recent counts happen to be similar.

#### F. Hotspot Streak (Momentum)
```
hotspot_streak = number of consecutive months this cell has been a hotspot
                 (ending at the month before the prediction period)
```
A cell on its 8th consecutive month as a hotspot is more entrenched than one that became a hotspot last month. This feature captures that momentum without any lookahead into the current period.

#### G. Area-Level Context
| Feature | Description |
|---------|-------------|
| `area_crimes_lag1` | Total crimes across the full community area, last month |
| `area_crimes_roll3m` | Community area 3-month trailing average |

A cell does not exist in isolation. If the surrounding community area is experiencing elevated crime, that pressure can spill into individual cells. These features give each cell context about its neighbourhood beyond its own boundaries.

#### H. Temporal Context
| Feature | Description |
|---------|-------------|
| `month` | Calendar month (1–12) |
| `quarter` | Calendar quarter (1–4) |
| `month_sin`, `month_cos` | Cyclical encoding of month |
| `is_summer` | 1 if June, July, or August |
| `is_winter` | 1 if December, January, or February |

The cyclical sin/cos encoding is important. A linear model would treat December (month 12) and January (month 1) as maximally different. Cyclically encoded, they are correctly represented as adjacent. This allows the model to learn smooth seasonal transitions.

#### I. Spatial Identity
| Feature | Description |
|---------|-------------|
| `community_area` | CPD community area number |
| `district` | CPD police district number |
| `beat` | CPD police beat number |

These encode the structural identity of each cell — its place in the CPD administrative geography. A cell in District 11 has a different baseline crime profile than one in District 19, and the model uses these identifiers to learn those baselines.

---

### Warmup Period Exclusion

The first 12 months of each cell's history are excluded from the model panel. During this warmup period, rolling and lag features are based on fewer than 12 months of data, making them unreliable. Features like `crimes_roll12m` and `hotspot_same_month_ly` require at least 12 months of history to be meaningful.

```
Full panel:   12,000 rows  (all 40 cells × 300 months)
Model panel:  11,520 rows  (after 12-month warmup exclusion)
```

---

### Panel Summary

| Metric | Value |
|--------|-------|
| Input incidents | 9,845 (2001–2025, excluding partial 2026) |
| Grid cells | 40 |
| Monthly periods | 300 (Jan 2001 – Dec 2025) |
| Full panel size | 12,000 cell-months |
| Model panel size (after warmup) | 11,520 cell-months |
| Zero-crime cell-months | 7,448 (62.1%) |
| Hotspot rate | 9.5% |
| Hotspot threshold | ≥ 3 crimes per cell-month |
| Total features | 35 (all lagged — zero current-period information) |
| Output file | `data/panel.csv` — 11,520 rows × 49 columns |

---

## Data Flow Summary

```
raw_crimes.csv        10,000 rows × 22 columns
        │
        │  Fix 1:  Drop 4 admin columns
        │  Fix 2:  Parse dates (strip UTC offset)
        │  Fix 3:  Merge legacy crime type labels (19 rows)
        │  Fix 4:  Drop 114 null-coordinate rows
        │  Fix 5:  Impute 625 null community areas
        │  Fix 6:  Fill 30 null location descriptions
        │  Fix 7:  Flag 41 partial-year 2026 rows
        │  Fix 8:  Cast booleans to int
        │  Add:    severity tier + high_risk flag
        ▼
cleaned.csv           9,886 rows × 23 columns
        │
        │  Exclude 2026 (partial year)
        │  Map incidents → 0.01° grid cells
        │  Cross all 40 cells × 300 months → 12,000 cell-months
        │  Aggregate: crimes, violent, arrests, domestic per cell-month
        │  Include zero-crime months (62.1% of panel)
        │  Define is_hotspot: top 25% crime volume cell-months
        │  Compute 35 lagged features (no current-period data)
        │  Drop 12-month warmup period
        ▼
panel.csv             11,520 rows × 49 columns
        │
        ▼
03_hotspot_model.py
```

---

## Common Questions

**Why not use weekly instead of monthly periods?**
Monthly periods accumulate enough crimes per cell to compute stable statistics with a 10,000-record sample. With the full 1.2M-record CPD dataset, weekly periods would be viable and would improve temporal resolution. The code in `02_build_panel.py` can be switched to weekly by changing `freq='M'` to `freq='W'`.

**Why 0.01° grid cells and not community areas directly?**
Community areas are large (Chicago has 77, averaging ~3.4 km²) and their boundaries are politically defined, not crime-density-defined. The 0.01° grid is smaller, more regular, and allows the model to identify hotspots at finer resolution. Community area is still included as a feature (spatial identity group I) so the model can learn area-level baselines.

**Why is the hotspot threshold fixed at the 75th percentile rather than per year?**
A global threshold ensures consistent meaning across all years. If a per-year threshold were used, a cell with 3 crimes in 2020 (a low-crime COVID year) and 3 crimes in 2019 (a normal year) could receive different labels despite identical activity — which would confuse the model. The global threshold creates a single consistent definition of "unusually high."

**What happens when I run this on the full CPD dataset?**
The scripts require no changes. Drop the full CSV into `data/raw_crimes.csv` and rerun both scripts. The panel will expand from 40 grid cells to approximately 1,500+, and the lag features will be computed from thousands of observations per cell instead of hundreds. Model AUC is expected to improve from 0.89 to approximately 0.92–0.96.

**Can I change the grid resolution?**
Yes. Change the `0.01` divisor in `02_build_panel.py` to make cells larger or smaller. Finer grids (e.g. `0.005`) produce more cells but require more data per cell. Coarser grids (e.g. `0.02`) are more robust with limited data but lose spatial precision. With 10,000 records, 0.01° is near the minimum viable resolution.

---

## Audit Trail

Every run of both scripts produces a complete audit log saved to `data/`:

- `data/01_cleaning_log.txt` — row counts before and after each fix, exact number of nulls resolved, label changes applied
- `data/02_panel_log.txt` — panel dimensions, hotspot threshold calculation, feature group confirmation, warmup exclusion counts

These logs are designed to be included in project documentation and data governance reviews. If a downstream analysis produces a surprising result, the logs allow you to trace exactly what state the data was in at each stage.
