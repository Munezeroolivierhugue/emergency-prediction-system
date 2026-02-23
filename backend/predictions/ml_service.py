import os
import joblib
import numpy as np
import pandas as pd
from decouple import config

class MLService:
    _model = None
    _model_path = config('ML_MODEL_PATH', default='ml_models/severity_model.pkl')
    
    _kmeans = None
    _kmeans_path = config('KMEANS_MODEL_PATH', default='ml_models/kmeans.pkl')

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
    def load_kmeans(cls):
        if cls._kmeans is None:
            if not os.path.exists(cls._kmeans_path):
                raise FileNotFoundError(f"KMeans model not found at: {cls._kmeans_path}")
            cls._kmeans = joblib.load(cls._kmeans_path)
        return cls._kmeans

    @classmethod
    def predict_severity(cls, data: dict) -> dict:
        """
        Prepares features to match the trained XGBoost Pipeline and returns severity + confidence.
        Input data keys: 'type' (str), 'hour' (int 0-23), 'month' (int 1-12),
                         'day_of_week' (int 0-6), 'lat' (float), 'lng' (float)
        """
        model = cls.load_model()

        hour = data['hour']
        month = data.get('month', 1)         # default to January if not provided
        day_of_week = data.get('day_of_week', 0)  # default to Monday if not provided
        lat = data['lat']
        lng = data['lng']

        # Cyclical time encoding (must match train_model.py)
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)
        dow_sin = np.sin(2 * np.pi * day_of_week / 7)
        dow_cos = np.cos(2 * np.pi * day_of_week / 7)

        # Spatial cluster — load the KMeans object saved alongside the model
        kmeans = cls.load_kmeans()
        region_cluster = int(kmeans.predict([[lat, lng]])[0])

        processed_data = {
            'Incident_Type': data['type'],    # "EMS", "Fire", or "Traffic"
            'lat': lat,
            'lng': lng,
            'Region_Cluster': region_cluster,
            'Hour_Sin': hour_sin,
            'Hour_Cos': hour_cos,
            'Month_Sin': month_sin,
            'Month_Cos': month_cos,
            'DayOfWeek_Sin': dow_sin,
            'DayOfWeek_Cos': dow_cos,
        }

        input_df = pd.DataFrame([processed_data])

        prediction = model.predict(input_df)[0]
        severity_score = round(float(prediction))
        severity_score = max(1, min(10, severity_score))

        # Map numeric score to label
        if severity_score >= 8:
            severity = "Critical"
        elif severity_score >= 6:
            severity = "High"
        elif severity_score >= 4:
            severity = "Medium"
        else:
            severity = "Low"

        # Pseudo-confidence: based on distance from threshold boundaries
        # Higher confidence when prediction is far from boundaries (4, 6, 8)
        boundaries = [4, 6, 8]
        distances = [abs(severity_score - b) for b in boundaries]
        min_distance = min(distances)
        
        # Normalize to 0-1 range (max distance is ~3 for a 1-10 scale)
        confidence = min(1.0, 0.5 + (min_distance / 6.0))
        
        return {
            "severity": severity,
            "confidence": round(confidence, 2)
        }

# Pre-load model when the service is imported, to avoid re-loading on each request.
# This assumes MLService will be imported once during application startup.
try:
    MLService.load_model()
except FileNotFoundError as e:
    print(f"Warning: {e}. Prediction service will not be functional.")
except IOError as e:
    print(f"Warning: {e}. Prediction service might have issues.")

