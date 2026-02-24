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

*(Instructions: After running `model_analysis.py`, analyze the generated plots and fill out the following insights to complete the documentation requirement for sprint ticket.)*

### A. The Most Critical Predicting Factors
1. **[Top Feature Name]**: Based on the SHAP Bar Plot, [____] is the strongest predictor of emergency severity. 
2. **[Second Feature Name]**: [____] is the second strongest.

### B. Understanding Time of Day (Hour/Day features)
*Review the Beeswarm plot for `Hour_Sin`/`Hour_Cos`.*
- How does the time of day influence severity? Do late nights (high values) push the SHAP value right (higher severity) or left (lower)?
- **Insight:** *[Insert observation here. E.g., The model learned that incidents occurring at [Time] tend to have an inherently higher severity score, likely due to visibility or traffic factors.]*

### C. Understanding Location (Region Clusters & Lat/Lng)
*Review the Beeswarm plot.*
- Are certain geographic clusters strongly pushing the severity up?
- **Insight:** *[Insert observation here. E.g., The system heavily weighs location `Region_Cluster_[X]`, indicating historical data shows that specific geographic zone produces more critical emergencies.]*

### D. Incident Types
*Review the categorical one-hot encoded features (e.g., `type_Fire` vs `type_Traffic`).*
- Does the presence of a "Fire" independently raise or lower the SHAP value compared to "Traffic"?
- **Insight:** *[Insert observation here]*
