# src/ml/models.py
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os

class BurnoutMLModels:
    """Collection of ML models for burnout detection"""
    
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.model_scores = {}
        
    def initialize_models(self):
        """Initialize all ML models"""
        
        # Model 1: Random Forest
        self.models['RandomForest'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        # Model 2: XGBoost
        self.models['XGBoost'] = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='mlogloss'
        )
        
        # Model 3: Gradient Boosting
        self.models['GradientBoosting'] = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        # Model 4: Logistic Regression (baseline)
        self.models['LogisticRegression'] = LogisticRegression(
            max_iter=1000,
            random_state=42
        )
        
        # Model 5: SVM
        self.models['SVM'] = SVC(
            kernel='rbf',
            probability=True,
            random_state=42
        )
        
        print(f"✅ Initialized {len(self.models)} models")
        return self.models
    
    def train_all_models(self, X_train, y_train, X_test, y_test):
        """Train all models and evaluate"""
        
        for name, model in self.models.items():
            print(f"\n🔄 Training {name}...")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Store scores
            self.model_scores[name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'model': model
            }
            
            print(f"   Accuracy: {accuracy:.4f}")
            print(f"   F1-Score: {f1:.4f}")
        
        # Find best model
        self.best_model_name = max(
            self.model_scores,
            key=lambda x: self.model_scores[x]['f1_score']
        )
        self.best_model = self.model_scores[self.best_model_name]['model']
        
        print(f"\n🏆 Best Model: {self.best_model_name}")
        print(f"   F1-Score: {self.model_scores[self.best_model_name]['f1_score']:.4f}")
        
        return self.model_scores
    
    def save_best_model(self, path='src/models/saved_models/'):
        """Save the best model"""
        os.makedirs(path, exist_ok=True)
        
        if self.best_model:
            model_path = f'{path}best_burnout_model.pkl'
            joblib.dump(self.best_model, model_path)
            
            # Save model info
            info = {
                'model_name': self.best_model_name,
                'scores': self.model_scores[self.best_model_name],
                'all_scores': self.model_scores
            }
            
            import json
            with open(f'{path}model_info.json', 'w') as f:
                json.dump(info, f, indent=2, default=str)
            
            print(f"✅ Best model saved to {model_path}")
            return model_path
        else:
            print("❌ No model to save")
            return None
    
    def load_model(self, path='src/models/saved_models/best_burnout_model.pkl'):
        """Load a saved model"""
        if os.path.exists(path):
            self.best_model = joblib.load(path)
            print(f"✅ Model loaded from {path}")
            return self.best_model
        else:
            print(f"❌ Model not found at {path}")
            return None