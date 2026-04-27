# src/utils/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///student_burnout.db"

    # JWT Authentication
    JWT_SECRET_KEY: str = "CHANGE_ME_TO_A_RANDOM_SECRET_KEY"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Fitbit API
    FITBIT_CLIENT_ID: str = ""
    FITBIT_CLIENT_SECRET: str = ""
    FITBIT_REDIRECT_URI: str = "http://localhost:8000/auth/fitbit/callback"

    # Google Fit API
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # Apple HealthKit
    APPLE_TEAM_ID: str = ""
    APPLE_KEY_ID: str = ""
    APPLE_PRIVATE_KEY: str = ""

    # Data Collection Settings
    COLLECTION_INTERVAL: int = 3600
    DATA_RETENTION_DAYS: int = 90
    BATCH_SIZE: int = 100

    # API Rate Limits
    FITBIT_RATE_LIMIT: int = 150
    GOOGLE_FIT_RATE_LIMIT: int = 1000

    # Analysis Thresholds
    HRV_THRESHOLD_LOW: int = 50
    SLEEP_THRESHOLD_MIN: int = 6
    ACTIVITY_THRESHOLD: int = 5000

    # Burnout Risk Level Thresholds
    RISK_LEVEL_LOW: float = 0.3
    RISK_LEVEL_MEDIUM: float = 0.6
    RISK_LEVEL_HIGH: float = 0.8

    @property
    def RISK_LEVELS(self) -> dict:
        return {
            'LOW': self.RISK_LEVEL_LOW,
            'MEDIUM': self.RISK_LEVEL_MEDIUM,
            'HIGH': self.RISK_LEVEL_HIGH,
        }

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Backward-compatible alias so existing `from src.utils.config import Config` still works
Config = get_settings()
