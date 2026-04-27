# tests/test_basic.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.bio_processing.hrv_analysis import HRVAnalyzer
from src.bio_processing.sleep_analysis import SleepAnalyzer
from src.bio_processing.burnout_calculator import BurnoutCalculator
import numpy as np

def test_hrv_analysis():
    print("Testing HRV Analysis...")
    hr_data = np.random.normal(70, 5, 100)
    features = HRVAnalyzer.calculate_hrv_features(hr_data)
    print(f"  HRV Features: {features}")
    assert 'hr_mean' in features
    print("  ✓ HRV Analysis passed")

def test_sleep_analysis():
    print("Testing Sleep Analysis...")
    analysis = SleepAnalyzer.analyze_sleep_quality(2.5, 0.85)
    print(f"  Sleep Analysis: {analysis}")
    assert 'quality_score' in analysis
    print("  ✓ Sleep Analysis passed")

def test_burnout_calculator():
    print("Testing Burnout Calculator...")
    hrv_data = {'hrv_rmssd': 45}
    sleep_data = {'quality_score': 0.6}
    result = BurnoutCalculator.calculate_burnout_risk(hrv_data, sleep_data, 6000)
    print(f"  Burnout Risk: {result}")
    assert 'risk_level' in result
    print("  ✓ Burnout Calculator passed")

if __name__ == "__main__":
    print("Running tests...\n")
    test_hrv_analysis()
    print()
    test_sleep_analysis()
    print()
    test_burnout_calculator()
    print("\nAll tests passed! ✅")