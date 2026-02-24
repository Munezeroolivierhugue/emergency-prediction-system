from .transformers import EmergencyDataTransformer

import os
import joblib
import numpy as np
import pandas as pd
from decouple import config

class MLService:
    _model = None
    _model_path = config('ML_MODEL_PATH', default='ml_models/best_advanced_model.pkl')
    
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
                # Add current directory to path just in case for unpickling
                import sys
                module_dir = os.path.dirname(os.path.abspath(__file__))
                if module_dir not in sys.path:
                    sys.path.append(module_dir)
                
                cls._model = joblib.load(cls._model_path)
                print(f"ML model loaded successfully from {cls._model_path}")
            except (AttributeError, ImportError, TypeError) as e:
                # This usually happens if the model was trained in a different module context
                raise IOError(f"ML Model Serialization Error: The transformer class definition doesn't match the one used during training. Error: {e}")
            except Exception as e:
                raise IOError(f"Error loading ML model from {cls._model_path}: {e}")
        return cls._model

    @classmethod
    def predict_severity(cls, data: dict) -> dict:
        """
        Passes raw data to the loaded pipeline model, which internally 
        uses EmergencyDataTransformer to engineer features.
        """
        model = cls.load_model()
        # Their previous manual encoding is removed and replaced by the Pipeline wrapper logic
        processed_data = {
            'type': data.get('type', 'Unknown'),
            'hour': data.get('hour', 0),
            'day':  data.get('day', 'Mon'), # String mapping required
            'lat':  data.get('lat', 0.0),
            'lng':  data.get('lng', 0.0),
        }
    
        input_df = pd.DataFrame([processed_data])
        
        # --- SHAP Model Pipeline Fix ---
        # The new advanced model's ColumnTransformer was trained on a DataFrame 
        # that already contained these mapped values. We must provide them here
        # or the pipeline will fail with "Feature names unseen at fit time"
        
        # 1. Aliases needed by calculate_dynamic_severity during training
        input_df['Incident_Type'] = input_df['type']
        
        # 2. Time computations needed by the preprocessor directly
        input_df['Month'] = data.get('month', 1)
        input_df['Month_Sin'] = np.sin(2 * np.pi * input_df['Month'] / 12)
        input_df['Month_Cos'] = np.cos(2 * np.pi * input_df['Month'] / 12)
        
        input_df['Hour_Sin'] = np.sin(2 * np.pi * input_df['hour'] / 24)
        input_df['Hour_Cos'] = np.cos(2 * np.pi * input_df['hour'] / 24)
        
        day_mapping = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
        day_num = day_mapping.get(input_df['day'][0], 0)
        input_df['DayOfWeek_Sin'] = np.sin(2 * np.pi * day_num / 7)
        input_df['DayOfWeek_Cos'] = np.cos(2 * np.pi * day_num / 7)
        
        # 3. Spatial computations needed by the preprocessor directly
        locations = input_df[['lat', 'lng']]
        kmeans_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ml_models', 'kmeans.pkl')
        try:
           kmeans_model = joblib.load(kmeans_path)
           input_df['Region_Cluster'] = kmeans_model.predict(locations)
        except:
           input_df['Region_Cluster'] = 0

        # The advanced model is a Regressor, returning a float 1-10
        raw_prediction = float(model.predict(input_df)[0])
        severity_score = int(max(1, min(10, round(raw_prediction))))

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
            "confidence": round(confidence, 2),
            "recommended_response": cls.RESPONSE_MAP.get(severity, "Unknown Response")
        }

# Pre-load model when the service is imported, to avoid re-loading on each request.
# This assumes MLService will be imported once during application startup.
try:
    MLService.load_model()
except FileNotFoundError as e:
    print(f"Warning: {e}. Prediction service will not be functional.")
except IOError as e:
    print(f"Warning: {e}. Prediction service might have issues.")

