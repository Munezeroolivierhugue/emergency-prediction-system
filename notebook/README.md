# Emergency Severity Prediction Model

This directory contains the machine learning pipelines and training scripts used to build the core predictive engine for the Emergency Prediction System.

## Overview
The primary model is an advanced gradient boosting regressor (capable of training both `XGBoost` and `LightGBM`) that predicts the required severity tracking score (1-10) of an incoming emergency dispatch. 

Crucially, **the model is built to perfectly mirror the Backend API**. It acts as an intelligent "black box" that accepts raw, non-mathematical JSON from the frontend, dynamically converts it into complex data features in memory, and returns the severity and confidence score.

---

## The Input Schema (API Compatibility)
To maintain pure alignment with the backend, the final `best_advanced_model.pkl` natively expects a pandas DataFrame with exactly these 5 columns:

- `type` (String, e.g., "Fire", "EMS", "Traffic")
- `hour` (Integer, 0-23)
- `day` (String, e.g., "Mon", "Tue")
- `lat` (Float, Latitude)
- `lng` (Float, Longitude)

**The backend developers DO NOT need to perform One-Hot Encoding or spatial calculations.** The trained `.pkl` artifact contains an internal Scikit-Learn `Pipeline` customized to take these raw data points.

---

## Feature Engineering pipeline

Under the hood, the training script uses a custom `EmergencyDataTransformer` class to generate advanced mathematical features required for the XGBoost/LightGBM engines:

1. **Cyclical Time Encoding**: Translates `hour` and `day` into `Sin` and `Cos` waves. This ensures the model knows that 23:00 (11 PM) is chronologically directly adjacent to 00:00 (Midnight).
2. **Spatial Risk Clusters**: Uses a pre-fitted `KMeans` algorithm to place the incoming `lat`/`lng` coordinates into specific geographic "Risk Regions", helping the decision trees understand invisible spatial boundaries better than raw numbers alone.
3. **One-Hot Encoding**: Handled internally by a Scikit-Learn `ColumnTransformer` to convert categorical text (like `Incident_Type`) into binary matrices.

---

## Training Structure & Workflow

The main training script is `train_model.py`. 

### 1. Prerequisites
To train the model, ensure you are in a Python environment with the required data science packages:
```bash
pip install pandas numpy scikit-learn xgboost lightgbm joblib
```

### 2. Data Requirements
The script expects a historical dataset file named `911.csv` inside a root `data/` directory. If it is missing, it will attempt to fall back to `sample_911.csv`. **For production, the full `911.csv` dataset must be present.**

### 3. Execution
To run the full pipeline, generate features, tune hyperparameters, and save the final module:
```bash
cd notebook
python train_model.py
```

### 4. What Happens During Execution?
1. **Dynamic Target Generation**: The script processes historical records to learn hidden patterns (Weekend risk, Night-time multipliers, Location variance) and establishes baseline labels.
2. **Class Balancing**: Applies rigorous `sample_weights` to ensure rare critical emergencies are treated with as much weight as common traffic accidents.
3. **RandomizedSearchCV**: The core algorithmic tournament. The script sets up an intense grid-search combining hundreds of hyperparameters across **both XGBoost and LightGBM**. It utilizes 5-Fold Cross Validation.
4. **Export**: The ultimate winning algorithm (either the best XGBoost or LightGBM model) and all parameter settings are seamlessly compressed inside the `EmergencyDataTransformer` pipeline, serialized, and saved to the project's root `model/` directory.

### 5. Final Artifact
- `../model/best_advanced_model.pkl`

---

## Instructions for Backend Integration

When the backend pipeline loads `best_advanced_model.pkl`, it must adhere to the following rules to prevent crashes:

### 1. The Custom Transformer Class
The `.pkl` file expects a custom Python class. You **MUST** define `class EmergencyDataTransformer(BaseEstimator, TransformerMixin):` (copied exactly from `notebook/train_model.py`) inside `ml_service.py` or a related file *before* calling `joblib.load()`. 

If you do not do this, Python will not know how to rebuild the model and will throw a `ModuleNotFoundError`.

### 2. No Manual Feature Engineering
**DO NOT** manually one-hot encode text or perform math (like Sin/Cos or spatial clustering) on the input variables in the backend! 

Simply pass a pandas DataFrame matching the exact validated dictionary directly to the model's `.predict()` function:
```python
input_df = pd.DataFrame([{
    'type': data['type'],
    'hour': data['hour'],
    'day': data['day'],
    'lat': data['lat'],
    'lng': data['lng']
}])
prediction = model.predict(input_df)[0]
```
The `.pkl` handles all internal preprocessing automatically.
