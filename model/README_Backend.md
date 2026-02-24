# Emergency Severity Model – Backend Integration

## Model File
- `best_advanced_model.pkl` – Trained XGBoost/LightGBM pipeline.

## Dependencies Required
The backend environment must have the following installed:
```bash
pip install pandas numpy scikit-learn xgboost lightgbm joblib
```

---

## ⚠️ Critical Setup step: The Custom Transformer Class

Because the `.pkl` artifact uses an internal class to generate features dynamically, Python needs to know what this class is *before* it can load the file.

**The Fix:**
You **MUST** define `class EmergencyDataTransformer(BaseEstimator, TransformerMixin):` (copied exactly from `notebook/train_model.py`) inside `ml_service.py` or a related file *before* calling `joblib.load()`. If you do not include this class definition, the backend server will crash with a `ModuleNotFoundError` when loading the model.

---

## Loading and Predicting

**DO NOT** write backend code to one-hot encode variables or perform spatial math. The model handles all mathematical translations internally.

The prediction payload must be a pandas DataFrame holding exactly 5 features (`type`, `hour`, `day`, `lat`, `lng`).

```python
import joblib
import pandas as pd
# IMPORTANT: Ensure the EmergencyDataTransformer class is defined in this file!

# 1. Load the Model
model = joblib.load('best_advanced_model.pkl')

# 2. Receive JSON Data from Frontend
data = {
    'type': 'Fire',   # String
    'hour': 14,       # Int (0-23)
    'day': 'Mon',     # String 3-letters
    'lat': 34.05,     # Float
    'lng': -118.24    # Float
}

# 3. Create DataFrame EXACTLY matching the JSON dictionary
input_df = pd.DataFrame([data])

# 4. Predict
prediction = model.predict(input_df)[0]
confidence_scores = model.predict_proba(input_df)[0]

# prediction will be an index (0, 1, 2, 3) representing Severity
print(f"Predicted Class Index: {prediction}")
```