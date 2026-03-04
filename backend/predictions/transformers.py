import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cluster import KMeans
import os
import joblib

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
