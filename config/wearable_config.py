# # config/wearable_config.py
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class WearableConfig:
#     """Configuration for wearable API connections"""
    
#     # Fitbit Configuration
#     FITBIT_CLIENT_ID = os.getenv('FITBIT_CLIENT_ID', '')
#     FITBIT_CLIENT_SECRET = os.getenv('FITBIT_CLIENT_SECRET', '')
#     FITBIT_REDIRECT_URI = os.getenv('FITBIT_REDIRECT_URI', 'http://localhost:8000/auth/fitbit/callback')
    
#     # Google Fit Configuration
#     GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
#     GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
#     GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')
    
#     # Apple HealthKit Configuration
#     APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID', '')
#     APPLE_KEY_ID = os.getenv('APPLE_KEY_ID', '')
#     APPLE_PRIVATE_KEY = os.getenv('APPLE_PRIVATE_KEY', '')
    
#     # Data Collection Settings
#     COLLECTION_INTERVAL = 3600  # 1 hour in seconds
#     DATA_RETENTION_DAYS = 90  # Keep data for 90 days
#     BATCH_SIZE = 100  # Number of records to process at once
    
#     # API Rate Limits
#     FITBIT_RATE_LIMIT = 150  # requests per hour
#     GOOGLE_FIT_RATE_LIMIT = 1000  # requests per day