# src/utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DATABASE_URL = "sqlite:///student_burnout.db"
    
    # Wearable API (Mock for now)
    FITBIT_CLIENT_ID = os.getenv("FITBIT_CLIENT_ID", "mock_id")
    FITBIT_CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET", "mock_secret")
    
    # Analysis Thresholds
    HRV_THRESHOLD_LOW = 50  # ms
    SLEEP_THRESHOLD_MIN = 6  # hours
    ACTIVITY_THRESHOLD = 5000  # steps
    
    # Burnout Risk Levels
    RISK_LEVELS = {
        'LOW': 0.3,
        'MEDIUM': 0.6,
        'HIGH': 0.8
    }