# Emergency Severity Prediction Model – Backend Integration Guide

This README provides backend developers with all necessary information to integrate the machine learning model for predicting emergency incident severity. The model is trained on the US Accidents dataset (Kaggle) as a proxy for Rwanda emergency data. It predicts severity levels (Low, Medium, High, Critical) based on minimal dispatcher inputs and automatically enriched data (weather, location, time).

## 1. Model Overview

The model is a Random Forest classifier trained on historical incident data. It expects a fixed set of features derived from:

Dispatcher inputs (incident type, district, timestamp, optional caller severity)
Enrichment data (weather, population density, road type, etc.)
Temporal features (hour, day of week, month, weekend flag)
The output includes predicted severity, confidence score, recommended response, and estimated response time.

## 2. Delivered Artifacts

The ML team provides the following files:

### File	Description
pipeline.joblib	Full sklearn pipeline (preprocessing + model). Load with joblib.load().
feature_names.pkl	List of all feature names in the exact order expected by the pipeline.
severity_mapping.json	Mapping from class integers to labels (e.g., {0: "Low", 1: "Medium", 2: "High", 3: "Critical"}).
example_enrichment.json	Sample enrichment data structure (for testing).
requirements.txt	Python dependencies.
Note: The pipeline includes:

One‑hot encoding for categorical variables
Standard scaling for numerical variables
Missing value imputation (median for numbers, "Unknown" for categories)
The trained Random Forest model

## 3. Input Data Format

The backend must provide two dictionaries to the prediction function:

### 3.1 Raw Dispatcher Input (from frontend)

Field	Type	Required	Description
incident_type	string	yes	Type of emergency. See list of expected values below.
district	string	yes	District name (Rwanda). Expected values: all 30 districts.
sector	string	no	Sector within district (optional).
caller_severity	string	no	Caller’s description: "Minor", "Serious", "Critical".
timestamp	string	yes	ISO 8601 format, e.g., "2025-03-15T18:30:00Z".
### 3.2 Enrichment Data (fetched by backend)

Field	Type	Required	Source	Notes
weather_condition	string	yes	Weather API	See expected categories below.
temperature	float	yes	Weather API	In Celsius.
humidity	float	yes	Weather API	Percentage (0–100).
wind_speed	float	yes	Weather API	km/h.
population_density	float	yes	Geo DB / Census	People per km².
road_type	string	yes	Map DB	e.g., "Highway", "Residential", "Urban".
is_holiday	boolean	yes	Calendar	true if day is a public holiday in Rwanda.
historical_incident_density	float	yes	Historical DB	Incidents per km² in that district/sector.
If any enrichment field is unavailable, pass null; the pipeline will handle imputation.

## 4. Expected Categorical Values

The pipeline was trained on the following categories (based on US data, adapted for Rwanda). For values not seen during training, the pipeline will map them to "Unknown" (or the most frequent category). Backend should log such cases.

### Incident Type

"Traffic Accident"
"Fire"
"Medical Emergency"
"Crime"
"Natural Disaster"
"Other"

### Weather Condition

"Clear"
"Cloudy"
"Rain"
"Light Rain"
"Heavy Rain"
"Snow"
"Fog"
"Thunderstorm"
"Unknown"

### Road Type

"Highway"
"Primary Road"
"Secondary Road"
"Residential"
"Urban"
"Rural"
"Unknown"

###Districts (Rwanda)

All 30 districts: "Gasabo", "Nyarugenge", "Kicukiro", "Muhanga", "Rubavu", "Musanze", "Kayonza", "Ngoma", "Nyagatare", "Rusizi", "Huye", "Karongi", "Gicumbi", "Rulindo", "Nyamagabe", "Ngororero", "Bugesera", "Gatsibo", "Kamonyi", "Ruhango", "Nyamasheke", "Rutsiro", "Burera", "Gakenke", "Rwamagana", "Nyabihu", "Nyaruguru", "Kirehe", "Muhororo", "Gisagara".

### Caller Severity (optional)

"Minor"
"Serious"
"Critical"

## 5. Prediction Function

We recommend creating a simple Python service (e.g., Flask) that loads the pipeline once and exposes an endpoint. Below is a complete reference implementation.

### 5.1 Setup

python
import joblib
import pandas as pd
import numpy as np
import json
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load model artifacts at startup
pipeline = joblib.load('models/pipeline.joblib')
with open('models/severity_mapping.json') as f:
    severity_mapping = json.load(f)
# severity_mapping: {"0": "Low", "1": "Medium", "2": "High", "3": "Critical"}
5.2 Prediction Endpoint

python
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        dispatcher_input = data['dispatcher']
        enrichment = data['enrichment']
        
        # Combine into one dictionary
        combined = {**dispatcher_input, **enrichment}
        
        # The pipeline expects a DataFrame with columns exactly as during training.
        # It includes a transformer that extracts hour, day_of_week, etc. from 'timestamp'.
        # So we can simply pass the raw timestamp.
        
        # Create a single-row DataFrame
        df = pd.DataFrame([combined])
        
        # Predict
        pred_class = pipeline.predict(df)[0]
        proba = pipeline.predict_proba(df)[0]
        
        # Prepare response
        response = {
            'predicted_severity': severity_mapping[str(pred_class)],
            'confidence': float(np.max(proba)),
            'probabilities': {
                severity_mapping[str(i)]: float(proba[i])
                for i in range(len(proba))
            },
            'recommended_response': get_recommendation(pred_class),
            'estimated_response_time': estimate_time(combined['district'], pred_class)
        }
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_recommendation(severity_class):
    recs = {
        0: 'Routine response – single unit',
        1: 'Priority response – multiple units',
        2: 'Urgent response – full team',
        3: 'Critical – all available resources, notify authorities'
    }
    return recs[severity_class]

def estimate_time(district, severity_class):
    # Simplified logic; replace with actual model or lookup table
    base_times = {
        'Gasabo': 10, 'Nyarugenge': 12, 'Kicukiro': 11,
        # ... defaults for other districts
    }
    base = base_times.get(district, 20)
    multiplier = {0: 1.2, 1: 1.0, 2: 0.8, 3: 0.6}
    return f"{round(base * multiplier[severity_class])} minutes"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
5.3 Example Request

json
POST /predict
Content-Type: application/json

{
  "dispatcher": {
    "incident_type": "Traffic Accident",
    "district": "Gasabo",
    "sector": "Kimironko",
    "caller_severity": "Serious",
    "timestamp": "2025-03-15T18:30:00Z"
  },
  "enrichment": {
    "weather_condition": "Light Rain",
    "temperature": 22.5,
    "humidity": 78,
    "wind_speed": 5.2,
    "population_density": 4500,
    "road_type": "Highway",
    "is_holiday": false,
    "historical_incident_density": 12.3
  }
}
5.4 Example Response

json
{
  "predicted_severity": "High",
  "confidence": 0.89,
  "probabilities": {
    "Low": 0.02,
    "Medium": 0.09,
    "High": 0.89,
    "Critical": 0.00
  },
  "recommended_response": "Urgent response – full team",
  "estimated_response_time": "12 minutes"
}
## 6. Error Handling

Missing enrichment fields: The pipeline will impute missing values (e.g., median temperature, "Unknown" for categories). However, the backend should log these cases for monitoring.
Unknown categorical values: If a value not seen during training is provided (e.g., a new district), the pipeline will map it to "Unknown". Consider adding a monitoring alert.
Model loading failure: The service should not start if pipeline fails to load.
Prediction errors: Return HTTP 400 with error details.

## 7. Performance Considerations

Model size: ~100–200 MB (depending on number of trees). Ensure sufficient memory.
Prediction time: < 50 ms after pipeline is loaded.
Caching:

Weather data: Cache per location for 30 minutes (weather changes slowly).
Population density, road type, historical density: Cache indefinitely (update weekly).
Concurrency: Use a thread‑safe prediction (sklearn estimators are thread‑safe for inference). Consider using gunicorn with multiple workers.
## 8. Dependencies

### Create a requirements.txt file with:

text
scikit-learn>=1.0.0
pandas>=1.3.0
numpy>=1.21.0
joblib>=1.1.0
flask>=2.0.0
Install with pip install -r requirements.txt.

## 9. Testing the Model Locally

The ML team will provide a sample script test_predictor.py that demonstrates loading the pipeline and making a prediction with dummy data. Use this to verify your integration.

## 10. Contact

For questions or issues, contact the ML team
