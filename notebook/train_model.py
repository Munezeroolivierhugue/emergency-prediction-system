import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor # Added LightGBM
from sklearn.model_selection import RandomizedSearchCV, KFold
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.utils.class_weight import compute_sample_weight
import joblib
import os

# Set seeds
np.random.seed(42)
# ... [lines 19-143 truncated for brevity, assume unchanged until model_pipeline] ...
    
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

    # Output directory
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

