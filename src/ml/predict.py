# src/ml/predict.py
import numpy as np
import pandas as pd
import joblib
import os

class BurnoutPredictor:
    """Real-time burnout prediction using trained ML model"""
    
    def __init__(self, model_path='src/models/saved_models/best_burnout_model.pkl',
                 scaler_path='src/models/saved_models/scaler.pkl',
                 features_path='src/models/saved_models/feature_names.txt'):
        
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.risk_labels = ['LOW', 'MEDIUM', 'HIGH']
        
        # Load model and artifacts
        self.load_model(model_path, scaler_path, features_path)
    
    def load_model(self, model_path, scaler_path, features_path):
        """Load trained model and artifacts"""
        
        # Load model
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            print(f"✅ Model loaded from {model_path}")
        else:
            print(f"⚠️ Model not found at {model_path}")
            self.model = None
        
        # Load scaler
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
            print(f"✅ Scaler loaded from {scaler_path}")
        
        # Load feature names
        if os.path.exists(features_path):
            with open(features_path, 'r') as f:
                self.feature_names = [line.strip() for line in f.readlines()]
            print(f"✅ Loaded {len(self.feature_names)} feature names")
    
    def prepare_features(self, bio_data):
        """
        Prepare features for prediction
        bio_data: dict with raw bio-signals
        """
        
        # Create base features
        features = {
            'hrv': bio_data.get('hrv', 60),
            'sleep_hours': bio_data.get('sleep_hours', 7),
            'sleep_quality': bio_data.get('sleep_quality', 0.7),
            'heart_rate': bio_data.get('heart_rate', 72),
            'step_count': bio_data.get('step_count', 6000),
            'stress_level': bio_data.get('stress_level', 0.3)
        }
        
        # Engineer additional features
        features['hrv_sleep_ratio'] = features['hrv'] / (features['sleep_hours'] + 1)
        features['heart_rate_variation'] = features['heart_rate'] / (features['hrv'] + 1)
        features['sleep_quality_score'] = features['sleep_hours'] * features['sleep_quality']
        features['activity_stress_ratio'] = features['step_count'] / (features['stress_level'] * 10000 + 1)
        
        # Create DataFrame
        df = pd.DataFrame([features])
        
        # Ensure all required features are present
        for feat in self.feature_names:
            if feat not in df.columns:
                df[feat] = 0
        
        # Select only required features in correct order
        df = df[self.feature_names]
        
        return df
    
    def predict_single(self, bio_data):
        """
        Predict burnout risk for a single student
        """
        if self.model is None:
            return {
                'error': 'Model not loaded',
                'risk_level': 'UNKNOWN',
                'risk_score': 0.5
            }
        
        # Prepare features
        features_df = self.prepare_features(bio_data)
        
        # Scale features
        features_scaled = self.scaler.transform(features_df)
        
        # Make prediction
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        # Get risk level
        risk_level = self.risk_labels[int(prediction)]
        
        # Calculate confidence (max probability)
        confidence = max(probabilities)
        
        return {
            'risk_level': risk_level,
            'risk_score': float(probabilities[2] if len(probabilities) > 2 else probabilities[1]),
            'prediction': int(prediction),
            'probabilities': {
                'LOW': float(probabilities[0]),
                'MEDIUM': float(probabilities[1]) if len(probabilities) > 1 else 0,
                'HIGH': float(probabilities[2]) if len(probabilities) > 2 else 0
            },
            'confidence': float(confidence),
            'features_used': self.feature_names
        }
    
    def predict_batch(self, bio_data_list):
        """
        Predict for multiple students
        """
        results = []
        for bio_data in bio_data_list:
            results.append(self.predict_single(bio_data))
        return results
    
    def explain_prediction(self, bio_data):
        """
        Explain why a prediction was made
        (Simplified version - for SHAP values, need shap library)
        """
        prediction = self.predict_single(bio_data)
        
        explanation = {
            'risk_level': prediction['risk_level'],
            'confidence': prediction['confidence'],
            'factors': []
        }
        
        # Simple rule-based explanation
        if bio_data.get('hrv', 60) < 45:
            explanation['factors'].append('Low HRV indicates stress')
        if bio_data.get('sleep_hours', 7) < 6:
            explanation['factors'].append('Insufficient sleep')
        if bio_data.get('sleep_quality', 0.7) < 0.5:
            explanation['factors'].append('Poor sleep quality')
        if bio_data.get('step_count', 6000) < 4000:
            explanation['factors'].append('Low physical activity')
        if bio_data.get('stress_level', 0.3) > 0.7:
            explanation['factors'].append('High self-reported stress')
        
        if not explanation['factors']:
            explanation['factors'].append('All metrics within normal range')
        
        return explanation