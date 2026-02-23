import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor
from sklearn.model_selection import RandomizedSearchCV, KFold
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

    model_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', XGBRegressor(random_state=42, n_jobs=-1, objective='reg:squarederror')) # XGBoost for advanced training
    ])

    print("Setting up K-Fold CV and Hyperparameter Grid...")
    # 5-Fold Cross Validation
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    # Define hyperparameter space to search
    param_grid = {
        'regressor__n_estimators': [100, 200, 300],
        'regressor__learning_rate': [0.01, 0.05, 0.1],
        'regressor__max_depth': [3, 5, 7],
        'regressor__subsample': [0.8, 1.0],
    }

    search = RandomizedSearchCV(
        model_pipeline, 
        param_distributions=param_grid, 
        n_iter=10,        # Number of combinations to try
        cv=kf,            # 5-Fold Cross Validation
        scoring='neg_root_mean_squared_error', 
        random_state=42,
        n_jobs=-1         # Use all available CPU cores
    )

    print("Training model with RandomizedSearchCV...")
    # Train/Test Split for Final Holdout Validation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Fit the search object (this performs the CV and tuning)
    search.fit(X_train, y_train)
    
    print(f"Best Parameters found: {search.best_params_}")
    
    # Retrieve the best model pipeline
    best_model = search.best_estimator_
    y_pred = best_model.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"Holdout Validation RMSE: {rmse:.4f}")
    print(f"Holdout Validation R2 Score: {r2:.4f}")
    print("Note: A lower R2 (e.g., 0.3-0.6) is expected now because we added noise and removed the direct answer (Subtype).")
    print("This means the model is learning *patterns* rather than *memorizing*.")

    # Retrain on full data for production using the best parameters
    print("Retraining BEST model on full dataset...")
    best_model.fit(X, y)

    # Save as .pkl instead of .joblib
    output_dir = '../model'
    if not os.path.exists(output_dir):
        output_dir = 'model'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    output_path = os.path.join(output_dir, 'best_advanced_model.pkl')
    joblib.dump(best_model, output_path)
    print(f"Model saved to {output_path}")

if __name__ == "__main__":
    train_and_save()

