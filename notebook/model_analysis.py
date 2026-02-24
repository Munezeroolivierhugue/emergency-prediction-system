import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt

# We must import the custom transformer class exactly as it was defined during training
# so that joblib can successfully un-pickle the `best_advanced_model.pkl`
from train_model import EmergencyDataTransformer

try:
    import shap
except ImportError:
    print("SHAP library is missing. Please install it using: pip install shap matplotlib")
    exit(1)

def analyze_model():
    print("Model Interpretability Analysis (SHAP)")
    print("---------------------------------------")
    
    # 1. Load the Model
    model_path = '../model/best_advanced_model.pkl'
    if not os.path.exists(model_path):
        model_path = 'model/best_advanced_model.pkl'
        
    if not os.path.exists(model_path):
        print(f"Error: Could not find model at {model_path}. You must train the model first.")
        return
        
    print("Loading model pipeline...")
    pipeline = joblib.load(model_path)
    
    # Extract the actual ML model from the end of the pipeline
    # The pipeline structure is: [('feature_engineer', ...), ('preprocessor', ...), ('regressor', Model)]
    regressor = pipeline.named_steps['regressor']
    preprocessor = pipeline.named_steps['preprocessor']
    feature_engineer = pipeline.named_steps['feature_engineer']

    # 2. Load Sample Data
    data_path = '../data/911.csv'
    if not os.path.exists(data_path):
        data_path = 'data/sample_911.csv'
    if not os.path.exists(data_path):
        data_path = '../data/sample_911.csv'
        
    if not os.path.exists(data_path):
        print(f"Error: Could not find dataset at {data_path}")
        return
        
    print(f"Loading background dataset from {data_path}...")
    df = pd.read_csv(data_path, nrows=5000) # Load a subset for performance
    
    # Format the data exactly as the backend would send it to the pipeline
    df['type'] = df['title'].apply(lambda x: x.split(':')[0].strip() if pd.notnull(x) else 'Unknown')
    df['timeStamp'] = pd.to_datetime(df['timeStamp'], errors='coerce')
    df['hour'] = df['timeStamp'].dt.hour.fillna(0).astype(int)
    df['day'] = df['timeStamp'].dt.day_name().str[:3].fillna('Mon')
    
    input_features = ['type', 'hour', 'day', 'lat', 'lng']
    X_raw = df[input_features]
    
    # 3. Transform data up to the Regressor step
    # We must pass the raw data through our custom transformers to get the numeric matrix
    # that the Regressor (XGBoost/LightGBM) actually sees and understands.
    print("Transforming features for SHAP...")
    X_engineered = feature_engineer.transform(X_raw)
    X_processed = preprocessor.transform(X_engineered)
    
    # Extract final feature names from the preprocessor to label the plots
    feature_names = preprocessor.get_feature_names_out()

    # 4. SHAP Analysis
    print("Calculating SHAP values... (This might take a minute)")
    # TreeExplainer is computationally exact and fast for XGBoost/LightGBM
    explainer = shap.TreeExplainer(regressor)
    shap_values = explainer.shap_values(X_processed)

    # 5. Generate and Save Plots
    os.makedirs('plots', exist_ok=True)
    
    print("Generating Feature Importance Bar Plot...")
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_processed, feature_names=feature_names, plot_type="bar", show=False)
    plt.title("Global Feature Importance (SHAP)")
    plt.tight_layout()
    plt.savefig('plots/shap_feature_importance.png')
    plt.close()
    
    print("Generating SHAP Summary Beeswarm Plot...")
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_processed, feature_names=feature_names, show=False)
    plt.title("SHAP Summary Plot")
    plt.tight_layout()
    plt.savefig('plots/shap_summary_beeswarm.png')
    plt.close()

    print("\nSuccess! Interpretability plots saved to 'notebook/plots/'")
    print("Please review notebook/MODEL_INSIGHTS.md for instructions on interpreting these results.")

if __name__ == "__main__":
    analyze_model()
