import pandas as pd
import numpy as np
import os
import joblib

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split, RandomizedSearchCV, KFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestClassifier

# Set seeds
np.random.seed(42)

def calculate_dynamic_severity(row):
    """
    Calculates severity based on environmental factors and incident type.
    """
    type_ = str(row.get('Incident_Type', row.get('type', ''))).upper()
    
    # 1. Base Score by broad category
    base_score = 5 
    if 'FIRE' in type_: base_score = 6
    elif 'TRAFFIC' in type_: base_score = 4
    elif 'EMS' in type_: base_score = 5
    
    # 2. Environmental Modifiers
    score_modifier = 0
    
    # Time of Day (Rush Hour: 7-9, 16-18 => High Traffic Risk)
    hour = row.get('Hour', row.get('hour', 0))
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
    month = row.get('Month', 1)
    if month in [12, 1, 2]:
        score_modifier += 1.0
        
    # Weekend (Fri-Sun => Higher alcohol-related risk?)
    day = row.get('DayOfWeek', row.get('day_encoded', row.get('day_num', 0)))
    if day >= 4: # 4=Fri, 5=Sat, 6=Sun
        score_modifier += 0.5

    # 3. Random Stochasticity (The "Unknown" factors)
    noise = np.random.normal(0, 1.5)
    
    final_score = base_score + score_modifier + noise
    return int(max(1, min(10, round(final_score))))


class EmergencyDataTransformer(BaseEstimator, TransformerMixin):
    """
    Custom transformer to align the backend's raw input schema:
    ['type', 'hour', 'day', 'lat', 'lng']
    into the engineered features expected by the model.
    """
    def __init__(self, n_clusters=10):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        self.day_mapping = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
        self.mean_lat = 0.0
        self.mean_lng = 0.0

    def fit(self, X, y=None):
        X_copy = X.copy()
        self.mean_lat = X_copy['lat'].mean()
        self.mean_lng = X_copy['lng'].mean()
        
        locations = X_copy[['lat', 'lng']].fillna(value={'lat': self.mean_lat, 'lng': self.mean_lng})
        self.kmeans.fit(locations)
        return self

    def transform(self, X):
        X_out = X.copy()
        
        # 1. Fill NAs for coordinates
        locations = X_out[['lat', 'lng']].fillna(value={'lat': self.mean_lat, 'lng': self.mean_lng})
        X_out['lat'] = locations['lat']
        X_out['lng'] = locations['lng']
        
        # 2. Region Cluster
        X_out['Region_Cluster'] = self.kmeans.predict(locations)
        
        # 3. Time Encoding (hour)
        X_out['Hour_Sin'] = np.sin(2 * np.pi * X_out['hour'] / 24)
        X_out['Hour_Cos'] = np.cos(2 * np.pi * X_out['hour'] / 24)
        
        # 4. Day Encoding
        X_out['day_num'] = X_out['day'].map(self.day_mapping).fillna(0)
        X_out['DayOfWeek_Sin'] = np.sin(2 * np.pi * X_out['day_num'] / 7)
        X_out['DayOfWeek_Cos'] = np.cos(2 * np.pi * X_out['day_num'] / 7)
        
        # Select final engineered features
        features = [
            'type', 
            'lat', 'lng', 'Region_Cluster',
            'Hour_Sin', 'Hour_Cos', 
            'DayOfWeek_Sin', 'DayOfWeek_Cos'
        ]
        return X_out[features]

def train_and_save():
    print("Loading data...")
    data_path = '../data/911.csv'
    if not os.path.exists(data_path):
        data_path = 'data/911.csv'
    
    if not os.path.exists(data_path):
        print(f"Main dataset not found at {data_path}. Checking for sample data...")
        data_path = 'data/sample_911.csv'
        if not os.path.exists(data_path):
            data_path = '../data/sample_911.csv'
            
    if not os.path.exists(data_path):
        raise FileNotFoundError("Could not find 911.csv or sample_911.csv")

    print(f"Using dataset: {data_path}")
    df = pd.read_csv(data_path, nrows=200000) 

    print("Mapping to Backend Schema & Generating Targets...")
    # Exact variables backend will send
    df['type'] = df['title'].apply(lambda x: x.split(':')[0].strip() if pd.notnull(x) else 'Unknown')
    df['Incident_Type'] = df['type'] # Aliased for calculate_dynamic_severity
    df['timeStamp'] = pd.to_datetime(df['timeStamp'], errors='coerce')
    df['hour'] = df['timeStamp'].dt.hour.fillna(0).astype(int)
    # Get 3-letter day string to match backend 'Mon', 'Tue'
    df['day'] = df['timeStamp'].dt.day_name().str[:3].fillna('Mon')
    
    # Internal variables for dynamic severity calculation only
    df['Month'] = df['timeStamp'].dt.month.fillna(1).astype(int)
    df['day_num'] = df['timeStamp'].dt.dayofweek.fillna(0).astype(int)
    df['DayOfWeek'] = df['day_num']
    df['Hour'] = df['hour']
    
    # Generate labels
    df['Severity_Score'] = df.apply(calculate_dynamic_severity, axis=1)

    # Class Weights for imbalance
    sample_weights_all = compute_sample_weight(class_weight='balanced', y=df['Severity_Score'])

    # Input Schema exactly matching Backend expected JSON
    input_features = ['type', 'hour', 'day', 'lat', 'lng']
    
    X = df[input_features]
    y = df['Severity_Score']

    print("Pipeline Construction...")
    
    categorical_features = ['type', 'Region_Cluster']
    numerical_features = ['lat', 'lng', 'Hour_Sin', 'Hour_Cos', 'DayOfWeek_Sin', 'DayOfWeek_Cos']

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', 'passthrough', numerical_features)
        ],
        verbose_feature_names_out=False
    ).set_output(transform='pandas')

    # We use a placeholder regressor here because RandomizedSearchCV will swap it
    model_pipeline = Pipeline([
        ('feature_engineer', EmergencyDataTransformer(n_clusters=10)),
        ('preprocessor', preprocessor),
        ('regressor', XGBRegressor(random_state=42)) # Placeholder
    ])

    print("Setting up K-Fold CV and Hyperparameter Grid for XGBoost and LightGBM...")
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    # Define a combined grid that searches across BOTH model types
    param_grid = [
        # XGBoost Parameter Space
        {
            'regressor': [XGBRegressor(random_state=42, n_jobs=-1, objective='reg:squarederror')],
            'regressor__n_estimators': [100, 200, 300],
            'regressor__learning_rate': [0.01, 0.05, 0.1],
            'regressor__max_depth': [3, 5, 7],
            'regressor__subsample': [0.8, 1.0],
        },
        # LightGBM Parameter Space
        {
            'regressor': [LGBMRegressor(random_state=42, n_jobs=-1)],
            'regressor__n_estimators': [100, 200, 300],
            'regressor__learning_rate': [0.01, 0.05, 0.1],
            'regressor__max_depth': [3, 5, 7, -1], # LightGBM supports -1 for no depth limit
            'regressor__num_leaves': [31, 50, 100], 
            'regressor__subsample': [0.8, 1.0],
        }
    ]

    # Increase n_iter because we have a much larger search space now across two models
    search = RandomizedSearchCV(
        model_pipeline, 
        param_distributions=param_grid, 
        n_iter=15, # Increased iterations to explore both models well
        cv=kf,            
        scoring='neg_root_mean_squared_error', 
        random_state=42,
        n_jobs=-1         
    )

    print("Training models (XGBoost vs LightGBM) with RandomizedSearchCV...")
    X_train, X_test, y_train, y_test, sw_train, sw_test = train_test_split(
        X, y, sample_weights_all, test_size=0.2, random_state=42
    )
    
    # Note: Using sample_weight in fit might require specific handling depending on the estimator selected.
    # To keep it generic across pipelines with different final estimators, it is often easier to pass 
    # fit_params but scikit-learn handles it okay if the estimator accepts sample_weight.
    search.fit(X_train, y_train, regressor__sample_weight=sw_train)
    
    print(f"Best Model Type selected: {search.best_estimator_.named_steps['regressor'].__class__.__name__}")
    print(f"Best Parameters found: {search.best_params_}")
    
    best_model = search.best_estimator_
    y_pred = best_model.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"Holdout Validation RMSE: {rmse:.4f}")
    print(f"Holdout Validation R2 Score: {r2:.4f}")

    print("Retraining BEST model on full dataset...")
    best_model.fit(X, y, regressor__sample_weight=sample_weights_all)

    # Save directly to backend/ml_models/ — this is where ml_service.py loads from.
    # Try relative paths from notebook/ or project root.
    output_dir = '../backend/ml_models'
    if not os.path.exists(output_dir):
        output_dir = 'backend/ml_models'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, 'best_advanced_model.pkl')
    joblib.dump(best_model, output_path)
    print(f"Advanced model saved to {output_path}")

def train_api_model():
    print("Training simpler model for API...")
    data_path = '../data/911.csv'
    if not os.path.exists(data_path):
        data_path = 'data/911.csv'
    if not os.path.exists(data_path):
        data_path = 'data/sample_911.csv'
    if not os.path.exists(data_path):
        data_path = '../data/sample_911.csv'
        
    if not os.path.exists(data_path):
        print(f"Skipping API model training. Dataset not found: {data_path}")
        return

    df = pd.read_csv(data_path, nrows=50000)
    df['type'] = df['title'].apply(lambda x: x.split(':')[0].strip() if pd.notnull(x) else 'Unknown')
    df['Incident_Type'] = df['type'] 
    df['timeStamp'] = pd.to_datetime(df['timeStamp'], errors='coerce')
    df['hour'] = df['timeStamp'].dt.hour
    df['day_encoded'] = df['timeStamp'].dt.dayofweek
    df['lat'] = df['lat'].fillna(df['lat'].mean())
    df['lng'] = df['lng'].fillna(df['lng'].mean())
    df['type_Fire'] = (df['Incident_Type'] == 'Fire').astype(int)
    df['type_EMS'] = (df['Incident_Type'] == 'EMS').astype(int)
    df['type_Traffic'] = (df['Incident_Type'] == 'Traffic').astype(int)
    
    df['Hour'] = df['hour']
    
    df['Month'] = df['timeStamp'].dt.month
    df['DayOfWeek'] = df['day_encoded']
    
    severity_scores = df.apply(calculate_dynamic_severity, axis=1)
    
    def map_severity(score):
        if score <= 3: return 0
        elif score <= 6: return 1
        elif score <= 8: return 2
        else: return 3
        
    y = severity_scores.apply(map_severity)
    X = df[['hour', 'day_encoded', 'lat', 'lng', 'type_Fire', 'type_EMS', 'type_Traffic']]
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    out_dir = '../backend/ml_models'
    if not os.path.exists(out_dir):
        out_dir = 'backend/ml_models'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
            
    out_path = os.path.join(out_dir, 'severity_model.pkl')
    joblib.dump(model, out_path)
    print(f"API Model saved to {out_path}")

if __name__ == "__main__":
    train_and_save()
    train_api_model()
