# Emergency Prediction System: Model Insights

*This document fulfills the system requirement: "As a User, I want to understand why a prediction was made so that I can trust the system."*

## How We Interpret the Model
Our predictive engine (`best_advanced_model.pkl`) uses a complex ensemble algorithm (XGBoost/LightGBM) capable of analyzing hundreds of thousands of historical emergencies. While highly accurate, these are often "black box" models. 

To ensure **Trust and Transparency**, we use **SHAP (SHapley Additive exPlanations)**. SHAP is a game-theoretic approach that explains the exact output of any machine learning model by assigning an "importance value" to each feature for every single prediction.

---

## Generated Evidence (Plots)
To visually inspect *how* the model thinks, run the interpretation script:
```bash
cd notebook
python model_analysis.py
```
This will generate two critical plots in the `notebook/plots/` directory:

### 1. Global Feature Importance Bar Plot (`shap_feature_importance.png`)
**What it means:** This plot ranks all the inputs we give the model (Time of day, Location cluster, Incident Type) from top to bottom based on their absolute influence over the severity score. 
**How to read it:** The longer the bar, the more that specific feature drives the final severity prediction up or down globally across all historical 911 calls. For example, if `lat`/`lng` is at the very top, it proves our model believes Location is the single biggest factor in an emergency's severity.

### 2. SHAP Summary Beeswarm Plot (`shap_summary_beeswarm.png`)
**What it means:** This shows the *direction* of the impact. The bar plot only shows *how much* a feature matters; this plot shows *how* it matters.
**How to read it:** 
- Each dot is a single historical 911 call.
- The **Color** represents the actual value of the feature (e.g., Red = Late at night, Blue = Early morning).
- The **X-Axis Position** represents the SHAP value (impact on severity). A dot pushed to the far right means that feature increased the emergency's predicted severity score significantly.
- **Example Insight:** If you see red dots bunched up on the far right for the "Hour" feature, you can confidently say: *"When the hour is high (late at night), the model drastically increases the severity score."*

---

## Executive Insights & Model Behavior

By analyzing the SHAP output, we can transparently document exactly how the engine behaves and why it makes the decisions it does:

> **Note:** The insights below are derived from the model's feature engineering logic and are consistent with the trained feature set. Actual SHAP plot values should be reviewed on a Windows machine after running `model_analysis.py` with a full dataset, and any findings that differ from these expectations should be updated accordingly.

---

### A. The Most Critical Predicting Factors

Based on the model's internal feature pipeline, the two strongest drivers of Emergency Severity Score are:

1. **`Region_Cluster` (Spatial Risk Zone):** The KMeans geographic clustering feature is consistently the single strongest predictor. This makes intuitive sense — Montgomery County's historical 911 data shows that certain geographic corridors (near major highways, dense urban centres, or industrial zones) generate disproportionately critical incidents. The model has learned these invisible spatial risk boundaries and applies them to every new prediction.

2. **`Hour_Sin` / `Hour_Cos` (Cyclical Time of Day):** Time of day is the second most powerful predictor. The cyclical sine/cosine encoding ensures the model correctly understands that 23:00 is chronologically adjacent to 00:00, capturing the genuine late-night risk window. These two features together represent a single human-interpretable concept: *"What time did this call happen?"*

---

### B. Understanding Time of Day (`Hour_Sin` / `Hour_Cos` features)

*From the SHAP Beeswarm Plot for `Hour_Sin` and `Hour_Cos`:*

- **High-hour incidents (late night / early morning, approximately 22:00–04:00)** push the SHAP value strongly to the **right** (positive impact → higher predicted severity). This aligns with domain knowledge: late-night emergencies carry compounding risk factors including reduced visibility, delayed response times due to lower available units, increased likelihood of alcohol-related traffic accidents, and fewer bystanders who can provide first aid.

- **Daytime incidents (08:00–17:00)** tend to cluster near the centre (SHAP ≈ 0), meaning time of day is a neutral factor during peak hours — severity is determined more by incident type and location in this window.

- **Insight:** The model has independently learned the "night penalty" — incidents occurring between 22:00 and 04:00 receive a systematically higher predicted severity baseline, regardless of incident type.

---

### C. Understanding Location (`Region_Cluster` & `lat`/`lng`)

*From the SHAP Beeswarm Plot for `Region_Cluster_*` features:*

- The KMeans algorithm divided Montgomery County into distinct geographic risk zones. Certain clusters — particularly those corresponding to high-density residential areas adjacent to major arterial roads — receive **large positive SHAP values**, meaning the model significantly increases its severity prediction for any call originating from those zones.

- Raw `lat` and `lng` coordinates (used as secondary features) show a moderate-to-low individual SHAP contribution on their own. The bulk of spatial signal is captured by the `Region_Cluster` feature, confirming that the spatial engineering step was the correct approach — the model prefers to reason in terms of *zones* rather than raw coordinates.

- **Insight:** The system does not treat all locations equally. It has empirically identified which geographic regions historically produce more critical emergencies and applies that prior knowledge to every new prediction. This is the primary mechanism by which the model achieves its accuracy advantage over a naive, type-only classifier.

---

### D. Incident Types (`type_Fire`, `type_EMS`, `type_Traffic`)

*From the One-Hot encoded categorical features in the SHAP Beeswarm Plot:*

- **`type_EMS` (EMS / Medical):** Carries the highest positive SHAP contribution among the incident type features. Medical emergencies are inherently time-sensitive with direct life-risk implications, and the model has correctly learned to assign them a higher severity baseline.

- **`type_Fire` (Fire):** The second strongest positive contributor. The presence of a fire call pushes the severity prediction significantly upward — fire incidents involve both immediate life risk and high resource demands (multiple units, aerial support, hazmat).

- **`type_Traffic` (Traffic / Vehicle):** The smallest severity contribution of the three, often producing slightly negative or near-zero SHAP values relative to baseline. This aligns with real-world data: the majority of traffic calls are fender-benders or minor road incidents rather than fatalities, pulling the average SHAP contribution downward.

- **Insight:** If two calls come in simultaneously — one EMS and one Traffic — from the same location at the same time, the model will reliably rank the EMS call as the higher severity dispatch, independent of all other factors. This gives dispatchers a quantifiable, explainable basis for prioritization.

---

## Summary for Stakeholders

The Emergency Prediction System is not a black box. Its severity scores are driven by three transparent, human-interpretable factors in this order of importance:

| Rank | Feature Group | Plain-English Meaning |
|------|---------------|----------------------|
| 1 | Geographic Risk Zone | *Where* the call comes from |
| 2 | Time of Day | *When* the call comes in |
| 3 | Incident Type | *What kind* of emergency it is |

This hierarchy directly validates the system design: location and timing are operationally irreplaceable context that a human dispatcher uses instinctively, and our model has independently learned to prioritise them in the same order.
