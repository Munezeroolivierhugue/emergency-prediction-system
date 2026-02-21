# Emergency Severity Model – Backend Integration

## Model File
- `emergency_model_v1.joblib` – trained RandomForest pipeline.

## Dependencies
Install the packages in `requirements.txt`.

## Loading the Model
```python
import joblib
model = joblib.load('emergency_model_rf_v1.joblib')