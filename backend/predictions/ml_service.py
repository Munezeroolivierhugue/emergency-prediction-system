import os
import joblib
import numpy as np
import pandas as pd
from decouple import config

class MLService:
    _model = None
    _model_path = config('ML_MODEL_PATH', default='ml_models/severity_model.pkl')
    
    # Define a mapping for days, assuming the model expects numerical input for day
    DAY_MAPPING = {
        'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6
    }
    
    # Define severity labels based on problem description
    SEVERITY_LABELS = ['Low', 'Medium', 'High', 'Critical'] # Assuming this order for model output

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
        Takes incident data, prepares it for the ML model, and returns
        the predicted severity and confidence score.
        
        Args:
            data (dict): A dictionary containing incident features:
                         'type', 'hour', 'day', 'lat', 'lng'.
        
        Returns:
            dict: A dictionary with 'severity' and 'confidence'.
        """
        model = cls.load_model() # Ensure model is loaded

        # Prepare data for the model
        # Assuming the model expects a DataFrame with specific columns.
        # This part is highly dependent on the actual model's training features.
        
        # Example: Create a DataFrame.
        # For 'type', if it's a categorical feature, it likely needs one-hot encoding.
        # For simplicity, we'll just include it as is or use a placeholder for now.
        # The actual model integration would require understanding its feature engineering.

        # Let's assume the model was trained on features like:
        # ['hour', 'day_encoded', 'lat', 'lng', 'type_Fire', 'type_EMS', ...]
        
        # For now, we'll create a basic DataFrame that might need further processing
        # depending on the actual model.
        
        processed_data = {
            'hour': data['hour'],
            'day_encoded': cls.DAY_MAPPING.get(data['day'], -1), # -1 for unknown day
            'lat': data['lat'],
            'lng': data['lng'],
            # Placeholder for 'type' encoding. 
            # In a real scenario, you'd need the exact one-hot encoding columns
            # used during model training.
            'type_Fire': 1 if data['type'] == 'Fire' else 0,
            'type_EMS': 1 if data['type'] == 'EMS' else 0,
            'type_Traffic': 1 if data['type'] == 'Traffic' else 0,
            # Add other types as needed by the model
        }
        
        # Convert to DataFrame, ensuring column order matches model's training data
        # This is a critical step and needs to align with the actual model.
        # For a robust solution, you might store feature names during training
        # and use them here.
        feature_names = [
            'hour', 'day_encoded', 'lat', 'lng', 
            'type_Fire', 'type_EMS', 'type_Traffic'
        ] # Example feature names
        
        input_df = pd.DataFrame([processed_data], columns=feature_names)

        # Make prediction
        prediction = model.predict(input_df)[0]
        # Get confidence (probability estimates)
        confidence_scores = model.predict_proba(input_df)[0]
        
        # The 'prediction' variable holds the index of the predicted class
        # Map the prediction index to a human-readable severity label
        severity = cls.SEVERITY_LABELS[prediction]
        
        # Get the confidence for the predicted class
        confidence = confidence_scores[prediction]

        return {
            "severity": severity,
            "confidence": round(float(confidence), 2)
        }

# Pre-load model when the service is imported, to avoid re-loading on each request.
# This assumes MLService will be imported once during application startup.
try:
    MLService.load_model()
except FileNotFoundError as e:
    print(f"Warning: {e}. Prediction service will not be functional.")
except IOError as e:
    print(f"Warning: {e}. Prediction service might have issues.")

