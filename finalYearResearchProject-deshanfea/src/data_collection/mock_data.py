# src/data_collection/mock_data.py
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class MockDataGenerator:
    """Generate mock wearable data for testing"""
    
    @staticmethod
    def generate_student_data(student_id, days=7):
        """Generate mock bio-signal data for a student"""
        data = []
        
        for day in range(days):
            date = datetime.now() - timedelta(days=day)
            
            # Generate realistic data with some stress patterns
            if day < 3:  # Normal days
                hr = np.random.normal(65, 5)
                hrv = np.random.normal(70, 10)
                sleep = np.random.normal(7.5, 0.5)
            else:  # Stress days
                hr = np.random.normal(75, 7)
                hrv = np.random.normal(50, 15)
                sleep = np.random.normal(5.5, 1.0)
            
            record = {
                'student_id': student_id,
                'timestamp': date,
                'heart_rate': max(50, min(100, hr)),
                'hrv_value': max(30, min(120, hrv)),
                'sleep_hours': max(4, min(10, sleep)),
                'sleep_quality': np.random.uniform(0.5, 0.9),
                'step_count': random.randint(3000, 10000),
                'stress_level': np.random.uniform(0.1, 0.7)
            }
            data.append(record)
        
        return pd.DataFrame(data)
    
    @staticmethod
    def create_test_students(count=5):
        """Create test student records"""
        students = []
        for i in range(count):
            students.append({
                'student_id': f'STU{i+1:03d}',
                'anonymous_id': f'ANON{random.randint(1000, 9999)}',
                'wearable_type': random.choice(['Fitbit', 'Apple Watch', 'Samsung']),
                'api_token': f'token_{random.randint(10000, 99999)}'
            })
        return students