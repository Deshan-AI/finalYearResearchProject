# src/ml/evaluation.py
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.metrics import precision_recall_curve, accuracy_score, f1_score
import pandas as pd
import os

class ModelEvaluator:
    """Evaluate ML model performance"""
    
    def __init__(self):
        self.risk_labels = ['LOW', 'MEDIUM', 'HIGH']
        self.results = {}
        
    def evaluate_model(self, model, X_test, y_test, feature_names=None):
        """Comprehensive model evaluation - FIXED VERSION"""
        
        # Make predictions
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)
        
        # Get unique classes in test set
        unique_classes = np.unique(y_test)
        print(f"   Classes in test set: {unique_classes}")
        
        # Calculate basic metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # For F1-score, use appropriate average
        if len(unique_classes) > 2:
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        else:
            f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)
        
        print(f"   Accuracy: {accuracy:.4f}")
        print(f"   F1-Score: {f1:.4f}")
        
        # Calculate confusion matrix
        cm = confusion_matrix(y_test, y_pred, labels=unique_classes)
        
        # Generate classification report (only for classes that exist)
        existing_labels = []
        for i in unique_classes:
            if i < len(self.risk_labels):
                existing_labels.append(self.risk_labels[i])
            else:
                existing_labels.append(f"Class {i}")
        
        report = classification_report(
            y_test, 
            y_pred,
            labels=unique_classes,
            target_names=existing_labels,
            output_dict=True,
            zero_division=0
        )
        
        # Get feature importance if available
        feature_importance = None
        if feature_names is not None:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                if len(importances) == len(feature_names):
                    feature_importance = dict(zip(feature_names, importances))
                    print(f"   ✅ Feature importance extracted")
                else:
                    print(f"   ⚠️ Feature importance length mismatch")
            elif hasattr(model, 'coef_'):
                # For linear models
                if len(model.coef_.shape) == 2:
                    coef = model.coef_[0]
                else:
                    coef = model.coef_
                
                if len(coef) == len(feature_names):
                    feature_importance = dict(zip(feature_names, np.abs(coef)))
                    print(f"   ✅ Coefficient importance extracted")
        
        return {
            'y_true': y_test,
            'y_pred': y_pred,
            'y_prob': y_prob,
            'confusion_matrix': cm,
            'classification_report': report,
            'feature_importance': feature_importance,
            'accuracy': accuracy,
            'f1_score': f1,
            'unique_classes': unique_classes
        }
    
    def plot_confusion_matrix(self, y_true, y_pred, model_name="Model", save_path=None):
        """Plot confusion matrix - SHOW ALL 3 CLASSES"""
        plt.figure(figsize=(8, 6))
        
        # ===== FIXED: Force all 3 classes to appear =====
        all_classes = [0, 1, 2]  # LOW, MEDIUM, HIGH
        cm = confusion_matrix(y_true, y_pred, labels=all_classes)
        
        # Use all risk labels
        class_labels = self.risk_labels  # ['LOW', 'MEDIUM', 'HIGH']
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=class_labels,
                    yticklabels=class_labels)
        
        plt.title(f'Confusion Matrix - {model_name} (All 3 Classes)')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        # Add text to show if any class missing
        missing_classes = []
        for i in range(3):
            if i not in y_true:
                missing_classes.append(self.risk_labels[i])
        
        if missing_classes:
            plt.figtext(0.5, 0.01, 
                    f"Note: {', '.join(missing_classes)} not in test set", 
                    ha='center', fontsize=10, style='italic')
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Confusion matrix saved to {save_path}")
        
        plt.show()
    
    def plot_feature_importance(self, feature_importance, top_n=10, save_path=None):
        """Plot feature importance"""
        if not feature_importance:
            print("⚠️ No feature importance available to plot")
            return
        
        if len(feature_importance) == 0:
            print("⚠️ Feature importance dictionary is empty")
            return
        
        print(f"📊 Plotting feature importance for {len(feature_importance)} features")
        
        # Sort features by importance
        sorted_features = sorted(feature_importance.items(), 
                                key=lambda x: x[1], reverse=True)[:top_n]
        
        if len(sorted_features) == 0:
            print("⚠️ No features to plot after sorting")
            return
        
        features, importance = zip(*sorted_features)
        
        plt.figure(figsize=(12, 8))
        plt.barh(range(len(features)), importance)
        plt.yticks(range(len(features)), features)
        plt.xlabel('Importance Score')
        plt.title(f'Top {len(features)} Feature Importance')
        plt.gca().invert_yaxis()
        
        # Add value labels on bars
        for i, v in enumerate(importance):
            plt.text(v, i, f' {v:.3f}', va='center')
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Feature importance plot saved to {save_path}")
        
        plt.show()
    
    def compare_models(self):
        """Compare all models"""
        comparison = []
        for name, metrics in self.results.items():
            comparison.append({
                'Model': name,
                'Accuracy': metrics['accuracy'],
                'F1-Score': metrics['f1_score']
            })
        
        df = pd.DataFrame(comparison)
        df = df.sort_values('F1-Score', ascending=False)
        return df
    
    def get_best_model(self, metric='f1_score'):
        """Get best model based on metric"""
        best_model = None
        best_score = -1
        
        for name, metrics in self.results.items():
            if metrics[metric] > best_score:
                best_score = metrics[metric]
                best_model = name
        
        return best_model, best_score