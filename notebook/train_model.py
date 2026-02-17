import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import TargetEncoder
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# Set seeds
np.random.seed(42)

def assign_severity(row):
    """
    Rule-based severity labeling for training.
    """
    subtype = str(row['Subtype']).upper()
    type_ = str(row['Incident_Type']).upper()
    
    # --- FIRE ---
    if 'FIRE' in type_:
        if 'BUILDING' in subtype or 'STRUCTURE' in subtype: return 10
        if 'APPLIANCE' in subtype: return 6
        if 'ALARM' in subtype: return 3
        return 8 # Default high for fire
        
    # --- EMS ---
    if 'EMS' in type_:
        if 'CARDIAC' in subtype or 'ARREST' in subtype or 'UNCONSCIOUS' in subtype: return 10
        if 'STROKE' in subtype or 'CHOKING' in subtype: return 9
        if 'TRAUMA' in subtype or 'OVERDOSE' in subtype: return 8
        if 'FALL' in subtype or 'HEAD INJURY' in subtype: return 6
        if 'DIZZINESS' in subtype or 'NAUSEA' in subtype: return 3
        return 5 # Default medium for EMS

    # --- TRAFFIC ---
    if 'TRAFFIC' in type_:
        if 'ACCIDENT' in subtype:
            if 'INJURY' in subtype: return 7
            return 5
        if 'DISABLED' in subtype: return 2
        return 4
        
    return 1

def train_and_save():
    print("Loading data...")
    # Load 911 Data
    # Adjust path if running from a different directory
    data_path = '../data/911.csv'
    if not os.path.exists(data_path):
        data_path = 'data/911.csv'
    
    df = pd.read_csv(data_path, nrows=200000)

    print("Preprocessing...")
    # Parse Title
    df['Incident_Type'] = df['title'].apply(lambda x: x.split(':')[0])
    df['Subtype'] = df['title'].apply(lambda x: x.split(':')[1].strip() if ':' in x else 'Unknown')

    # Parse Time
    df['timeStamp'] = pd.to_datetime(df['timeStamp'], errors='coerce')
    df['Hour'] = df['timeStamp'].dt.hour
    df['Month'] = df['timeStamp'].dt.month
    df['DayOfWeek'] = df['timeStamp'].dt.dayofweek

    # Apply Labels
    df['Severity_Score'] = df.apply(assign_severity, axis=1)
    
    # Add noise
    perturbation = np.random.normal(0, 0.5, size=len(df))
    df['Severity_Score'] = (df['Severity_Score'] + perturbation).clip(1, 10).round().astype(int)

    # Features
    df['zip'] = df['zip'].fillna(0).astype(str)
    df['twp'] = df['twp'].fillna('Unknown')
    df['lat'] = df['lat'].fillna(0)
    df['lng'] = df['lng'].fillna(0)

    features = ['Incident_Type', 'Subtype', 'zip', 'twp', 'lat', 'lng', 'Hour', 'Month', 'DayOfWeek']
    X = df[features]
    y = df['Severity_Score']

    # Pipeline
    categorical_features = ['Incident_Type', 'Subtype', 'zip', 'twp']
    numerical_features = ['lat', 'lng', 'Hour', 'Month', 'DayOfWeek']

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', TargetEncoder(target_type='continuous'), categorical_features),
            ('num', 'passthrough', numerical_features)
        ],
        verbose_feature_names_out=False
    ).set_output(transform='pandas')

    model_v3 = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', HistGradientBoostingRegressor(random_state=42))
    ])

    print("Training model...")
    model_v3.fit(X, y) # Training on full dataset for production/saving
    print("Training complete.")

    # Validate on a small split just to print metrics
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model_for_metrics = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', HistGradientBoostingRegressor(random_state=42))
    ])
    model_for_metrics.fit(X_train, y_train)
    y_pred = model_for_metrics.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"Validation RMSE: {rmse:.2f}")

    # Save
    output_dir = '../model'
    if not os.path.exists(output_dir):
        output_dir = 'model'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    output_path = os.path.join(output_dir, 'model_v3.joblib')
    joblib.dump(model_v3, output_path)
    print(f"Model saved to {output_path}")

if __name__ == "__main__":
    train_and_save()
