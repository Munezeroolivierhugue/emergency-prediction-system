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

### Districts (Rwanda)

All 30 districts: "Gasabo", "Nyarugenge", "Kicukiro", "Muhanga", "Rubavu", "Musanze", "Kayonza", "Ngoma", "Nyagatare", "Rusizi", "Huye", "Karongi", "Gicumbi", "Rulindo", "Nyamagabe", "Ngororero", "Bugesera", "Gatsibo", "Kamonyi", "Ruhango", "Nyamasheke", "Rutsiro", "Burera", "Gakenke", "Rwamagana", "Nyabihu", "Nyaruguru", "Kirehe", "Muhororo", "Gisagara".

### Caller Severity (optional)

"Minor"
"Serious"
"Critical"

## 5. Prediction Function

We recommend creating a simple Python service (e.g., Flask) that loads the pipeline once and exposes an endpoint. Below is a complete reference implementation.

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
