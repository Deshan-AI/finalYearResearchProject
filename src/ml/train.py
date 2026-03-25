# src/ml/train.py
import numpy as np
import pandas as pd
from src.ml.data_preparation import DataPreparator
from src.ml.models import BurnoutMLModels
from src.ml.evaluation import ModelEvaluator
import joblib
import os

class ModelTrainingPipeline:
    """Complete ML training pipeline"""
    
    def __init__(self):
        self.preparator = DataPreparator()
        self.models = BurnoutMLModels()
        self.evaluator = ModelEvaluator()
        self.training_history = []
        
    def run_pipeline(self, n_samples=1000):
        """Run complete training pipeline"""
        
        print("="*60)
        print("🤖 ML TRAINING PIPELINE STARTED")
        print("="*60)
        
        # Step 1: Load REAL Data
        print("\n📊 Step 1: Loading Real WESAD Data")
        df = self.preparator.prepare_wesad_data()
        
        if len(df) == 0:
            raise ValueError("No data loaded from WESAD! Check prepare_wesad_data() function.")
        
        print(f"   Loaded {len(df)} samples")
        print(f"   Features: {df.columns.tolist()}")
        
        # Step 2: Feature Engineering
        print("\n🔧 Step 2: Feature Engineering")
        df = self.preparator.prepare_features(df)
        print(f"   Features after engineering: {len(df.columns)}")
        
        # Step 3: Check class distribution
        print("\n📈 Step 3: Class Distribution")
        class_dist = df['burnout_level'].value_counts().sort_index()
        for i, count in class_dist.items():
            risk = ['LOW', 'MEDIUM', 'HIGH'][i]
            print(f"   {risk} Risk (Class {i}): {count} samples ({count/len(df)*100:.1f}%)")
        
        # Step 4: Split and Scale
        print("\n✂️ Step 4: Train-Test Split")
        data_dict = self.preparator.split_and_scale(df)
        print(f"   Training samples: {len(data_dict['X_train'])}")
        print(f"   Testing samples: {len(data_dict['X_test'])}")
        
        # Step 5: Initialize Models
        print("\n🤖 Step 5: Initializing Models")
        self.models.initialize_models()
        
        # Step 6: Train Models
        print("\n🎯 Step 6: Training Models")
        scores = self.models.train_all_models(
            data_dict['X_train'],
            data_dict['y_train'],
            data_dict['X_test'],
            data_dict['y_test']
        )
        
        # Step 7: Detailed Evaluation
        print("\n📊 Step 7: Detailed Model Evaluation")
        if self.models.best_model:
            print(f"\n   🏆 Best Model: {self.models.best_model_name}")
            
            # Get evaluation
            evaluation = self.evaluator.evaluate_model(
                self.models.best_model,
                data_dict['X_test'],
                data_dict['y_test'],
                data_dict['feature_names']
            )
            
            # ===== FIX: Check if we have multiple classes in test set =====
            unique_test_classes = evaluation.get('unique_classes', np.unique(data_dict['y_test']))
            print(f"   Test set contains classes: {unique_test_classes}")
            
            # Plot confusion matrix (this will work with any number of classes)
            print("\n   📈 Plotting Confusion Matrix...")
            self.evaluator.plot_confusion_matrix(
                evaluation['y_true'],
                evaluation['y_pred'],
                model_name=self.models.best_model_name,
                save_path='reports/confusion_matrix.png'
            )
            
            # Plot feature importance
            print("\n   📊 Plotting Feature Importance...")
            if evaluation.get('feature_importance'):
                self.evaluator.plot_feature_importance(
                    evaluation['feature_importance'],
                    top_n=min(10, len(evaluation['feature_importance'])),
                    save_path='reports/feature_importance.png'
                )
            else:
                print("   ⚠️ No feature importance available")
                
                # Try to get feature importance directly
                if hasattr(self.models.best_model, 'feature_importances_'):
                    try:
                        feat_imp = dict(zip(data_dict['feature_names'], 
                                        self.models.best_model.feature_importances_))
                        self.evaluator.plot_feature_importance(
                            feat_imp,
                            save_path='reports/feature_importance.png'
                        )
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
        
        
        # Step 8: Save Best Model
        print("\n💾 Step 8: Saving Best Model")
        model_path = self.models.save_best_model()
        
        # Save scaler and feature names
        joblib.dump(data_dict['scaler'], 'src/models/saved_models/scaler.pkl')
        with open('src/models/saved_models/feature_names.txt', 'w') as f:
            f.write('\n'.join(data_dict['feature_names']))
        
        # Step 9: Save Training History
        training_record = {
            'timestamp': pd.Timestamp.now(),
            'n_samples': len(df),
            'best_model': self.models.best_model_name,
            'best_f1_score': self.models.model_scores[self.models.best_model_name]['f1_score'],
            'class_distribution': class_dist.to_dict(),
            'model_scores': self.models.model_scores
        }
        self.training_history.append(training_record)
        
        # Save history
        import json
        with open('reports/training_history.json', 'w') as f:
            json.dump(self.training_history, f, indent=2, default=str)
        
        print("\n" + "="*60)
        print("✅ TRAINING PIPELINE COMPLETED")
        print("="*60)
        
        return {
            'best_model': self.models.best_model,
            'best_model_name': self.models.best_model_name,
            'scaler': data_dict['scaler'],
            'feature_names': data_dict['feature_names'],
            'scores': self.models.model_scores
        }