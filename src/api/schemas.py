# src/api/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class StudentBase(BaseModel):
    student_id: str
    wearable_type: str

class StudentCreate(StudentBase):
    email: EmailStr
    password: str

class StudentLogin(BaseModel):
    student_id: str
    password: str

class StudentResponse(BaseModel):
    student_id: str
    anonymous_id: str
    wearable_type: str
    created_at: datetime

class BioSignalResponse(BaseModel):
    date: datetime
    heart_rate: float
    hrv_value: float
    sleep_hours: float
    sleep_quality: float
    step_count: int
    stress_level: float

class BurnoutRiskResponse(BaseModel):
    date: datetime
    risk_score: float
    risk_level: str
    primary_factors: str

class DashboardData(BaseModel):
    student_id: str
    current_risk: BurnoutRiskResponse
    recent_trend: List[BurnoutRiskResponse]
    weekly_summary: dict
    recommendations: List[str]