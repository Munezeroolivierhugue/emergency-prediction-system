import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# Set seeds
np.random.seed(42)

def calculate_dynamic_severity(row):
    """
    Calculates severity based on environmental factors and incident type.
    Avoids hardcoding specific subtypes to prevent target leakage.
    Severity = Base_Score + Time_Factor + Location_Risk + Noise
    """
    type_ = str(row['Incident_Type']).upper()
    
    # 1. Base Score by broad category
    base_score = 5 
    if 'FIRE' in type_: base_score = 6
    elif 'TRAFFIC' in type_: base_score = 4
    elif 'EMS' in type_: base_score = 5
    
    # 2. Environmental Modifiers
    score_modifier = 0
    
    # Time of Day (Rush Hour: 7-9, 16-18 => High Traffic Risk)
    hour = row['Hour']
    if (7 <= hour <= 9) or (16 <= hour <= 18):
        if 'TRAFFIC' in type_:
            score_modifier += 2
        else:
            score_modifier += 0.5 
            
    # Night Time (22-5 => High Risk for EMS/Fire visibility)
    if (hour >= 22) or (hour <= 5):
        if 'EMS' in type_ or 'FIRE' in type_:
            score_modifier += 1
            
    # Seasonality (Winter: Dec-Feb => Higher risk)
    month = row['Month']
    if month in [12, 1, 2]:
        score_modifier += 1.0
        
    # Weekend (Fri-Sun => Higher alcohol-related risk?)
    day = row['DayOfWeek']
    if day >= 4: # 4=Fri, 5=Sat, 6=Sun
        score_modifier += 0.5

    # 3. Random Stochasticity (The "Unknown" factors)
    # We add significant noise so the model has to learn the *patterns* above, 
    # not just memorize a row.
    noise = np.random.normal(0, 1.5)
    
    final_score = base_score + score_modifier + noise
    return int(max(1, min(10, round(final_score))))

def train_and_save():
    print("Loading data...")
    # Load 911 Data with fallback to sample
    data_path = '../data/911.csv'
    if not os.path.exists(data_path):
        data_path = 'data/911.csv'
    
    if not os.path.exists(data_path):
        print(f"Main dataset not found at {data_path}. Checking for sample data...")
        data_path = 'data/sample_911.csv'
        if not os.path.exists(data_path):
            data_path = '../data/sample_911.csv'
            
    if not os.path.exists(data_path):
        raise FileNotFoundError("Could not find 911.csv or sample_911.csv. Please run scripts/download_data.sh or create a sample.")

    print(f"Using dataset: {data_path}")
    df = pd.read_csv(data_path, nrows=200000) # Load more for better training

    print("Preprocessing & Feature Engineering...")
    # 1. Basic Parsing
    df['Incident_Type'] = df['title'].apply(lambda x: x.split(':')[0].strip())
    df['Subtype'] = df['title'].apply(lambda x: x.split(':')[1].strip() if ':' in x else 'Unknown')
    
    df['timeStamp'] = pd.to_datetime(df['timeStamp'], errors='coerce')
    df['Hour'] = df['timeStamp'].dt.hour
    df['Month'] = df['timeStamp'].dt.month
    df['DayOfWeek'] = df['timeStamp'].dt.dayofweek
    
    # 2. Cyclical Time Encoding
    # Maps 23:00 close to 00:00
    df['Hour_Sin'] = np.sin(2 * np.pi * df['Hour'] / 24)
    df['Hour_Cos'] = np.cos(2 * np.pi * df['Hour'] / 24)
    df['Month_Sin'] = np.sin(2 * np.pi * df['Month'] / 12)
    df['Month_Cos'] = np.cos(2 * np.pi * df['Month'] / 12)
    df['DayOfWeek_Sin'] = np.sin(2 * np.pi * df['DayOfWeek'] / 7)
    df['DayOfWeek_Cos'] = np.cos(2 * np.pi * df['DayOfWeek'] / 7)

    # 3. Spatial Clustering (Risk Zones)
    # We use KMeans to cluster lat/lng into "Risk Regions"
    # This helps tree models that struggle with raw coordinates
    df['lat'] = df['lat'].fillna(df['lat'].mean())
    df['lng'] = df['lng'].fillna(df['lng'].mean())
    
    print("Generating Spatial Clusters...")
    kmeans = KMeans(n_clusters=10, random_state=42, n_init=10)
    df['Region_Cluster'] = kmeans.fit_predict(df[['lat', 'lng']])
    
    # 4. Target Generation (New Logic)
    print("Generating Severity Scores...")
    df['Severity_Score'] = df.apply(calculate_dynamic_severity, axis=1)

    # Features for Model
    # We DROP 'Subtype' to force the model to learn from Context (Time, Location, Type)
    # This prevents the "Lookup Table" problem.
    features = [
        'Incident_Type', 
        'lat', 'lng', 'Region_Cluster',
        'Hour_Sin', 'Hour_Cos', 
        'Month_Sin', 'Month_Cos', 
        'DayOfWeek_Sin', 'DayOfWeek_Cos'
    ]
    
    X = df[features]
    y = df['Severity_Score']

    # Pipeline Construction
    # Region_Cluster: KMeans IDs have no inherent order (Cluster 3 is not
    # "between" 2 and 4), so One-Hot Encoding is the correct treatment.
    categorical_features = ['Incident_Type', 'Region_Cluster']
    
    numerical_features = [
        'lat', 'lng',
        'Hour_Sin', 'Hour_Cos', 
        'Month_Sin', 'Month_Cos', 
        'DayOfWeek_Sin', 'DayOfWeek_Cos'
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', 'passthrough', numerical_features)
        ],
        verbose_feature_names_out=False
    ).set_output(transform='pandas')

    model_v3 = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', HistGradientBoostingRegressor(random_state=42, max_iter=200)) # Increased iterations
    ])

    print("Training model...")
    # Train/Test Split for Validation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model_v3.fit(X_train, y_train)
    y_pred = model_v3.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"Validation RMSE: {rmse:.4f}")
    print(f"R2 Score: {r2:.4f}")
    print("Note: A lower R2 (e.g., 0.3-0.6) is expected now because we added noise and removed the direct answer (Subtype).")
    print("This means the model is learning *patterns* rather than *memorizing*.")

    # Retrain on full data for production
    print("Retraining on full dataset...")
    model_v3.fit(X, y)

    # Save
    output_dir = '../model'
    if not os.path.exists(output_dir):
        output_dir = 'model'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    output_path = os.path.join(output_dir, 'model_v3_1.joblib')
    joblib.dump(model_v3, output_path)
    print(f"Model saved to {output_path}")

if __name__ == "__main__":
    train_and_save()

