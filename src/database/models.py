# src/database/models.py
from sqlalchemy import Boolean, create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.utils.config import Config

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(50), unique=True, nullable=False)
    anonymous_id = Column(String(50), unique=True, nullable=False)
    wearable_type = Column(String(50))
    api_token = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)


    # Wearable tokens (encrypted)
    fitbit_token = Column(String(500), nullable=True)
    google_fit_token = Column(String(500), nullable=True)
    apple_health_token = Column(String(500), nullable=True)
    
    # Wearable settings
    wearable_type = Column(String(50), default='fitbit')  # fitbit, google, apple, all
    data_sharing_consent = Column(Boolean, default=False)
    consent_given_at = Column(DateTime, nullable=True)
    
    # Sync settings
    last_sync_time = Column(DateTime, nullable=True)
    sync_frequency = Column(Integer, default=3600)  # seconds
    token_updated_at = Column(DateTime, nullable=True)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    notification_frequency = Column(String(20), default='daily')  # immediate, daily, weekly
    
    def __repr__(self):
        return f"<Student {self.student_id}>"
    
    

class BioSignalData(Base):
    __tablename__ = 'biosignal_data'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    heart_rate = Column(Float)
    hrv_value = Column(Float)
    sleep_hours = Column(Float)
    sleep_quality = Column(Float)  # 0-1 scale
    step_count = Column(Integer)
    stress_level = Column(Float)  # 0-1 scale
    
    def __repr__(self):
        return f"<BioSignalData {self.student_id} at {self.timestamp}>"

class BurnoutRisk(Base):
    __tablename__ = 'burnout_risk'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(50), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float)  # 0-1
    risk_level = Column(String(20))  # LOW, MEDIUM, HIGH
    primary_factors = Column(String(200))  # e.g., "HRV, Sleep"
    
    def __repr__(self):
        return f"<BurnoutRisk {self.student_id}: {self.risk_level}>"
    


# Add to src/database/models.py
class FitProDevice(Base):
    __tablename__ = 'fitpro_devices'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(50))
    watch_address = Column(String(20))
    last_connected = Column(DateTime)
    battery_level = Column(Integer)
