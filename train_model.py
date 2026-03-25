# train_model.py
from src.ml.train import ModelTrainingPipeline
from src.ml.predict import BurnoutPredictor
import numpy as np

def main():
    print("="*60)
    print("🧠 BURNOUT DETECTION ML TRAINING - REAL WESAD DATA")
    print("="*60)
    
    # Step 1: Train models using REAL data only
    print("\n📚 Phase 1: Model Training (Real WESAD Data)")
    pipeline = ModelTrainingPipeline()
    
    # No synthetic option anymore - always use real data
    results = pipeline.run_pipeline()  # use_synthetic parameter ඉවත් කළා
    
    # Step 2: Test prediction with sample student data
    print("\n🎯 Phase 2: Testing Predictions")
    predictor = BurnoutPredictor()
    
    # Test with sample data (same as before)
    test_student = {
        'hrv': 42,              # Low HRV (stress indicator)
        'sleep_hours': 4.5,     # Poor sleep
        'sleep_quality': 0.4,
        'heart_rate': 82,
        'step_count': 2000,     # Low activity
        'stress_level': 0.8     # High stress
    }
    
    prediction = predictor.predict_single(test_student)
    
    print("\n📊 Sample Prediction:")
    print(f"   Risk Level: {prediction['risk_level']}")
    print(f"   Risk Score: {prediction['risk_score']:.3f}")
    print(f"   Confidence: {prediction['confidence']:.3f}")
    print("\n   Probabilities:")
    for level, prob in prediction['probabilities'].items():
        print(f"      {level}: {prob:.3f}")
    
    # Explain prediction
    explanation = predictor.explain_prediction(test_student)
    print("\n💡 Explanation:")
    for factor in explanation['factors']:
        print(f"   • {factor}")
    
    print("\n" + "="*60)
    print("✅ ML TRAINING COMPLETED SUCCESSFULLY (Real Data Used)")
    print("="*60)

if __name__ == "__main__":
    main()