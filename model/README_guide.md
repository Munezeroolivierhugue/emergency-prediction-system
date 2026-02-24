# Emergency Severity Prediction Model (V3) - Integration Guide

This folder contains the trained machine learning model (`emergency_severity_v3.joblib`) used to prioritize incoming emergency incidents.

## 📁 Model Artifact
*   **Path**: `model/emergency_severity_v3.joblib`
*   **Format**: Scikit-Learn Pipeline (saved with `joblib`)
*   **Input**: JSON/DataFrame of incident details
*   **Output**: Floating point score **1.0 - 10.0** (Higher = More Critical)

---

## 🛠️ For Backend Developers (FastAPI/Python)

### 1. Load the Model
You need `joblib` and `scikit-learn` installed.
```python
import joblib
import pandas as pd

# Load the model at startup (Global scope)
model = joblib.load("model/example_model_v3.joblib")
```

### 2. Prepare the Input
The model expects a Pandas DataFrame with **exact** column names. You must transform the API request into this format.

**Required Columns:**
*   `Incident_Type`: (str) e.g., 'EMS', 'Fire', 'Traffic'
*   **`Subtype`**: (str) e.g., 'CARDIAC EMERGENCY', 'BUILDING FIRE' (**Critical Feature**)
*   `access_lat`/`lat`: (float) Latitude
*   `access_lng`/`lng`: (float) Longitude
*   `zip`: (str) Zipcode (can be '0' if unknown)
*   `twp`: (str) Township/City (can be 'Unknown')
*   `Hour`: (int) 0-23
*   `Month`: (int) 1-12
*   `DayOfWeek`: (int) 0=Mon, 6=Sun

**Example Prediction Function:**
```python
def predict_severity(data: dict):
    # 1. Create DataFrame
    df = pd.DataFrame([data])
    
    # 2. Predict (returns an array, we take the first item)
    score = model.predict(df)[0]
    
    # 3. Round and Return
    return round(float(score), 2)
```

---

## 💻 For Frontend Developers (UI Inputs)

To get accurate predictions, your "Report Incident" form must capture specific data points.

### 1. Incident Type & Subtype (The "What")
*   **Dropdown 1 (Type)**: `Fire`, `Medical` (EMS), `Traffic`, `Crime` (Future)
*   **Dropdown 2 (Subtype)**: Dependent on Type. This is the **most important** input.
    *   *If Fire*: 'Building Fire', 'Brush Fire', 'Vehicle Fire', 'Alarm'
    *   *If Medical*: 'Cardiac Arrest', 'Respiratory', 'Trauma', 'Fall', 'Overdose'
    *   *If Traffic*: 'Vehicle Accident', 'Disabled Vehicle', 'Obstruction'

### 2. Location (The "Where")
*   **Map Pin**: User clicks map -> Extract `Lat`, `Lng`.
*   **Reverse Geocode**: Use Google Maps/Mapbox API to fill `City` (mapped to `twp`) and `Zipcode`.

### 3. Time (The "When")
*   Auto-fill with current timestamp (`new Date()`).
*   Extract `Hour`, `Month`, `Day` locally or let Backend handle it.

---

## 📊 Interpreting the Score (1-10)

Display this score to the Dispatcher to help them prioritize.

| Score Range | Priority Level | Description | Example |
| :--- | :--- | :--- | :--- |
| **9.0 - 10.0** | 🔴 **CRITICAL** | Immediate Life Threat. Dispatch nearest unit. | Cardiac Arrest, Structure Fire |
| **7.0 - 8.9** | 🟠 **HIGH** | Urgent. Potential for serious harm. | Trauma, Vehicle Fire, Assault |
| **4.0 - 6.9** | 🟡 **MEDIUM** | Standard Response. Injury or Property Risk. | Car Accident, Fall, Head Injury |
| **1.0 - 3.9** | 🟢 **LOW** | Minor/Routine. No immediate danger. | Disabled Vehicle, Alarm, Nausea |
