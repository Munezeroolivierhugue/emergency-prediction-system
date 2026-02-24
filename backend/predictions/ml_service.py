import os
import joblib
import numpy as np
import pandas as pd
from decouple import config

class MLService:
    _model = None
    _model_path = config('ML_MODEL_PATH', default='ml_models/severity_model.pkl')
    
    SEVERITY_LABELS = {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Critical'}
    
    RESPONSE_MAP = {
        'Critical': 'Dispatch 3+ Units — Immediate Response',
        'High':     'Dispatch 2 Units — Priority Response',
        'Medium':   'Dispatch 1 Unit — Standard Response',
        'Low':      'Monitor — No Dispatch Needed',
    }

    @classmethod
    def load_model(cls):
        """
        Loads the pre-trained machine learning model from the specified path.
        """
        if cls._model is None:
            if not os.path.exists(cls._model_path):
                raise FileNotFoundError(f"ML model not found at: {cls._model_path}")
            
            try:
                cls._model = joblib.load(cls._model_path)
                print(f"ML model loaded successfully from {cls._model_path}")
            except Exception as e:
                raise IOError(f"Error loading ML model from {cls._model_path}: {e}")
        return cls._model

    @classmethod
    def predict_severity(cls, data: dict) -> dict:
        """
        Build features matching the RandomForestClassifier trained in
        notebook/train_model.py → train_api_model().
        Expected feature order: hour, day_encoded, lat, lng, type_Fire, type_EMS, type_Traffic
        """
        model = cls.load_model()
    
        incident_type = data['type']  # "EMS", "Fire", or "Traffic"
    
        processed_data = {
            'hour':         data['hour'],
            'day_encoded':  data.get('day_of_week', 0),
            'lat':          data['lat'],
            'lng':          data['lng'],
            'type_Fire':    1 if incident_type == 'Fire' else 0,
            'type_EMS':     1 if incident_type == 'EMS' else 0,
            'type_Traffic': 1 if incident_type == 'Traffic' else 0,
        }
    
        input_df = pd.DataFrame([processed_data])
    
        prediction = int(model.predict(input_df)[0])
        severity = cls.SEVERITY_LABELS.get(prediction, 'Medium')
    
        # Get confidence from predict_proba (RandomForest supports this)
        try:
            proba = model.predict_proba(input_df)[0]
            confidence = round(float(max(proba)), 2)
        except AttributeError:
            confidence = None
    
        return {
            "severity": severity,
            "confidence": confidence,
            "recommended_response": cls.RESPONSE_MAP.get(severity, 'Assess on arrival'),
        }

# Pre-load model when the service is imported, to avoid re-loading on each request.
# This assumes MLService will be imported once during application startup.
try:
    MLService.load_model()
except FileNotFoundError as e:
    print(f"Warning: {e}. Prediction service will not be functional.")
except IOError as e:
    print(f"Warning: {e}. Prediction service might have issues.")

