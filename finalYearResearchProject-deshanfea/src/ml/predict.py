# src/ml/predict.py
import numpy as np
import pandas as pd
import joblib
import os


class BurnoutPredictor:
    """Real-time burnout prediction using trained ML model"""

    def __init__(
        self,
        model_path='src/models/saved_models/best_burnout_model.pkl',
        scaler_path='src/models/saved_models/scaler.pkl',
        features_path='src/models/saved_models/feature_names.txt',
    ):
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.risk_labels = ['LOW', 'MEDIUM', 'HIGH']
        self.load_model(model_path, scaler_path, features_path)

    def load_model(self, model_path, scaler_path, features_path):
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            print(f"✅ Model loaded from {model_path}")
        else:
            print(f"⚠️ Model not found at {model_path}")

        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
            print(f"✅ Scaler loaded from {scaler_path}")

        if os.path.exists(features_path):
            with open(features_path, 'r') as f:
                self.feature_names = [line.strip() for line in f.readlines()]
            print(f"✅ Loaded {len(self.feature_names)} feature names")

    # ------------------------------------------------------------------
    # Feature engineering — mirrors DataPreparator.prepare_features()
    # ------------------------------------------------------------------

    def prepare_features(self, bio_data):
        """Build the same feature set that the training pipeline produces.

        bio_data keys (all optional, sensible defaults used):
            hrv, heart_rate, hrv_rmssd, step_proxy, mean_acc,
            temperature, stress_level,
            sleep_hours, sleep_quality, step_count
        """
        # Base features (same names as training)
        f = {
            'hrv':           bio_data.get('hrv', 60),
            'heart_rate':    bio_data.get('heart_rate', 72),
            'hrv_rmssd':     bio_data.get('hrv_rmssd', 0.05),
            'step_proxy':    bio_data.get('step_proxy', 100),
            'mean_acc':      bio_data.get('mean_acc', 10),
            'temperature':   bio_data.get('temperature', 36),
            'stress_level':  bio_data.get('stress_level', 20),
            'sleep_hours':   bio_data.get('sleep_hours', 7),
            'sleep_quality': bio_data.get('sleep_quality', 0.7),
            'step_count':    bio_data.get('step_count', 6000),
        }

        # Ratio features
        f['hrv_sleep_ratio']       = f['hrv'] / (f['sleep_hours'] + 1)
        f['heart_rate_variation']  = f['heart_rate'] / (f['hrv'] + 1)
        f['hrv_ratio']             = f['hrv'] / (f['hrv_rmssd'] + 1)
        f['activity_per_hour']     = f['step_count'] / (f['sleep_hours'] + 1)
        f['activity_stress_ratio'] = f['step_count'] / (f['stress_level'] * 100 + 1)
        f['movement_quality']      = f['step_proxy'] / (f['mean_acc'] + 1)
        f['temp_stress_correlation'] = f['temperature'] * f['stress_level']
        f['sleep_quality_score']   = f['sleep_hours'] * f['sleep_quality']
        f['sleep_efficiency']      = f['sleep_quality'] / (f['sleep_hours'] + 1)

        # Categorical bins
        f['hrv_category']    = 0 if f['hrv'] <= 40 else (1 if f['hrv'] <= 60 else 2)
        f['sleep_category']  = 0 if f['sleep_hours'] <= 5 else (1 if f['sleep_hours'] <= 7 else 2)
        f['hr_category']     = 0 if f['heart_rate'] <= 60 else (1 if f['heart_rate'] <= 80 else 2)
        f['stress_category'] = 0 if f['stress_level'] <= 15 else (1 if f['stress_level'] <= 25 else 2)
        f['step_category']   = 0 if f['step_count'] <= 4000 else (1 if f['step_count'] <= 8000 else 2)

        # Interaction features
        f['stress_hrv_interaction'] = f['stress_level'] * (100 - f['hrv']) / 100
        f['activity_sleep_score']   = f['step_count'] * f['sleep_hours'] / 10000
        f['temp_hrv_interaction']   = f['temperature'] * f['hrv'] / 100

        # Aggregate scores
        f['physical_stress_score'] = np.mean([
            (f['heart_rate'] - 60) / 40,
            (f['temperature'] - 35) / 5,
        ])
        f['recovery_score'] = np.mean([
            f['hrv'] / 100,
            f['sleep_quality'],
            f['sleep_hours'] / 10,
        ])

        df = pd.DataFrame([f])

        # Ensure all training features present (fill missing with 0)
        for feat in self.feature_names:
            if feat not in df.columns:
                df[feat] = 0

        return df[self.feature_names]

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict_single(self, bio_data):
        if self.model is None:
            return {
                'error': 'Model not loaded',
                'risk_level': 'UNKNOWN',
                'risk_score': 0.5,
            }

        features_df = self.prepare_features(bio_data)
        features_scaled = self.scaler.transform(features_df)

        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]

        risk_level = self.risk_labels[int(prediction)]
        confidence = float(max(probabilities))

        return {
            'risk_level': risk_level,
            'risk_score': float(probabilities[2] if len(probabilities) > 2 else probabilities[-1]),
            'prediction': int(prediction),
            'probabilities': {
                'LOW': float(probabilities[0]),
                'MEDIUM': float(probabilities[1]) if len(probabilities) > 1 else 0,
                'HIGH': float(probabilities[2]) if len(probabilities) > 2 else 0,
            },
            'confidence': confidence,
            'features_used': self.feature_names,
        }

    def predict_batch(self, bio_data_list):
        return [self.predict_single(d) for d in bio_data_list]

    def explain_prediction(self, bio_data):
        prediction = self.predict_single(bio_data)

        explanation = {
            'risk_level': prediction['risk_level'],
            'confidence': prediction['confidence'],
            'factors': [],
        }

        if bio_data.get('hrv', 60) < 45:
            explanation['factors'].append('Low HRV indicates stress')
        if bio_data.get('sleep_hours', 7) < 6:
            explanation['factors'].append('Insufficient sleep')
        if bio_data.get('sleep_quality', 0.7) < 0.5:
            explanation['factors'].append('Poor sleep quality')
        if bio_data.get('step_count', 6000) < 4000:
            explanation['factors'].append('Low physical activity')
        if bio_data.get('stress_level', 20) > 50:
            explanation['factors'].append('High stress level detected')

        if not explanation['factors']:
            explanation['factors'].append('All metrics within normal range')

        return explanation
