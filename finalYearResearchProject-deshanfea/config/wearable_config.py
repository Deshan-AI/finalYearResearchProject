# config/wearable_config.py
from src.utils.config import Config


class WearableConfig:
    """Configuration for wearable API connections — delegates to central Config."""

    # Fitbit
    FITBIT_CLIENT_ID = Config.FITBIT_CLIENT_ID
    FITBIT_CLIENT_SECRET = Config.FITBIT_CLIENT_SECRET
    FITBIT_REDIRECT_URI = Config.FITBIT_REDIRECT_URI

    # Google Fit
    GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET
    GOOGLE_REDIRECT_URI = Config.GOOGLE_REDIRECT_URI

    # Apple HealthKit
    APPLE_TEAM_ID = Config.APPLE_TEAM_ID
    APPLE_KEY_ID = Config.APPLE_KEY_ID
    APPLE_PRIVATE_KEY = Config.APPLE_PRIVATE_KEY

    # Data Collection Settings
    COLLECTION_INTERVAL = Config.COLLECTION_INTERVAL
    DATA_RETENTION_DAYS = Config.DATA_RETENTION_DAYS
    BATCH_SIZE = Config.BATCH_SIZE

    # API Rate Limits
    FITBIT_RATE_LIMIT = Config.FITBIT_RATE_LIMIT
    GOOGLE_FIT_RATE_LIMIT = Config.GOOGLE_FIT_RATE_LIMIT
