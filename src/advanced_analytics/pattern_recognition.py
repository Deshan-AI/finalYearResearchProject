# src/advanced_analytics/pattern_recognition.py
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

class PatternRecognizer:
    """Recognize patterns in student behavior"""
    
    def __init__(self):
        self.patterns = {}
        self.cluster_model = None
    
    def identify_stress_patterns(self, student_data):
        """
        Identify common stress patterns
        student_data: DataFrame with student bio-signals
        """
        patterns = []
        
        # Pattern 1: Late night + low HRV next day
        late_nights = student_data[student_data['sleep_hours'] < 5]
        if len(late_nights) > 0:
            for idx in late_nights.index:
                if idx + 1 < len(student_data):
                    next_day_hrv = student_data.iloc[idx + 1]['hrv_value']
                    if next_day_hrv < 45:
                        patterns.append({
                            'pattern': 'late_night_stress',
                            'frequency': len(late_nights),
                            'impact': 'high_hrv_reduction'
                        })
        
        # Pattern 2: Weekend recovery
        # (Implementation depends on data structure)
        
        # Pattern 3: Exam week stress
        # (Implementation depends on data structure)
        
        return patterns
    
    def cluster_students(self, student_features, n_clusters=3):
        """
        Cluster students based on behavior patterns
        """
        # Scale features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(student_features)
        
        # Perform clustering
        self.cluster_model = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = self.cluster_model.fit_predict(features_scaled)
        
        # Analyze clusters
        cluster_profiles = []
        for i in range(n_clusters):
            cluster_data = student_features[clusters == i]
            profile = {
                'cluster_id': i,
                'size': len(cluster_data),
                'centroid': self.cluster_model.cluster_centers_[i].tolist(),
                'avg_hrv': cluster_data['hrv_value'].mean() if 'hrv_value' in cluster_data.columns else None,
                'avg_sleep': cluster_data['sleep_hours'].mean() if 'sleep_hours' in cluster_data.columns else None
            }
            cluster_profiles.append(profile)
        
        return {
            'clusters': clusters.tolist(),
            'profiles': cluster_profiles,
            'model': self.cluster_model
        }