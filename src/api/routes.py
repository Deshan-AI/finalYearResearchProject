# src/api/routes.py
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from src.database.database_setup import get_session
from src.database.models import Student, BioSignalData, BurnoutRisk
from src.api.schemas import *
from src.api.auth import AuthHandler
from src.bio_processing.burnout_calculator import BurnoutCalculator
from src.automation.notification_system import NotificationSystem
from src.ml.predict import BurnoutPredictor
from src.advanced_analytics.trend_analysis import TrendAnalyzer

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")
auth_handler = AuthHandler()
notification_system = NotificationSystem()

# ============= Web Pages =============
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/student/{student_id}", response_class=HTMLResponse)
async def student_portal(request: Request, student_id: str):
    return templates.TemplateResponse(
        "student_portal.html", 
        {"request": request, "student_id": student_id}
    )

@router.get("/counselor", response_class=HTMLResponse)
async def counselor_dashboard(request: Request):
    return templates.TemplateResponse(
        "counselor_dashboard.html", 
        {"request": request}
    )

# Initialize ML components
predictor = BurnoutPredictor()
trend_analyzer = TrendAnalyzer()

# ============= API Endpoints =============
@router.post("/api/register")
async def register_student(student: StudentCreate):
    session = get_session()
    
    # Check if student exists
    existing = session.query(Student).filter(
        Student.student_id == student.student_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Student already exists")
    
    # Create new student
    new_student = Student(
        student_id=student.student_id,
        anonymous_id=f"ANON{hash(student.student_id) % 10000:04d}",
        wearable_type=student.wearable_type
    )
    
    session.add(new_student)
    session.commit()
    
    return {"message": "Student registered successfully"}

@router.post("/api/login")
async def login(login_data: StudentLogin):
    session = get_session()
    
    student = session.query(Student).filter(
        Student.student_id == login_data.student_id
    ).first()
    
    if not student:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = auth_handler.create_access_token(
        data={"sub": student.student_id}
    )
    
    return {"access_token": token, "token_type": "bearer"}

@router.get("/api/student/{student_id}/dashboard")
async def get_student_dashboard(student_id: str):
    session = get_session()
    
    # Get latest risk
    latest_risk = session.query(BurnoutRisk).filter(
        BurnoutRisk.student_id == student_id
    ).order_by(BurnoutRisk.date.desc()).first()
    
    # Get last 7 days trend
    week_ago = datetime.now() - timedelta(days=7)
    recent_risks = session.query(BurnoutRisk).filter(
        BurnoutRisk.student_id == student_id,
        BurnoutRisk.date >= week_ago
    ).order_by(BurnoutRisk.date).all()
    
    # Get recent bio data
    recent_bio = session.query(BioSignalData).filter(
        BioSignalData.student_id == student_id
    ).order_by(BioSignalData.timestamp.desc()).limit(7).all()
    
    # Calculate averages
    if recent_bio:
        avg_sleep = sum(b.sleep_hours for b in recent_bio) / len(recent_bio)
        avg_hrv = sum(b.hrv_value for b in recent_bio) / len(recent_bio)
    else:
        avg_sleep = 0
        avg_hrv = 0
    
    # Generate recommendations
    recommendations = []
    if latest_risk:
        if latest_risk.risk_level == "HIGH":
            recommendations = [
                "Schedule a counseling session",
                "Take breaks between study sessions",
                "Talk to a friend or family member"
            ]
        elif latest_risk.risk_level == "MEDIUM":
            recommendations = [
                "Practice deep breathing exercises",
                "Ensure 7-8 hours of sleep",
                "Take short walks"
            ]
        else:
            recommendations = [
                "Maintain current healthy habits",
                "Stay connected with friends",
                "Regular exercise"
            ]
    
    dashboard = {
        "student_id": student_id,
        "current_risk": {
            "date": latest_risk.date if latest_risk else datetime.now(),
            "risk_score": latest_risk.risk_score if latest_risk else 0,
            "risk_level": latest_risk.risk_level if latest_risk else "LOW",
            "primary_factors": latest_risk.primary_factors if latest_risk else "None"
        },
        "recent_trend": [
            {"date": r.date, "risk_score": r.risk_score} for r in recent_risks
        ],
        "weekly_summary": {
            "avg_sleep": round(avg_sleep, 1),
            "avg_hrv": round(avg_hrv, 1),
            "total_days": len(recent_risks)
        },
        "recommendations": recommendations
    }
    
    return dashboard

# Add to src/api/routes.py

@router.get("/student/{student_id}", response_class=HTMLResponse)
async def student_dashboard(request: Request, student_id: str):
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "student_id": student_id}
    )

@router.get("/counselor", response_class=HTMLResponse)
async def counselor_dashboard(request: Request):
    return templates.TemplateResponse(
        "counselor_dashboard.html", 
        {"request": request}
    )

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})    

@router.get("/api/counselor/alerts")
async def get_counselor_alerts():
    session = get_session()
    
    # Get today's high risk students
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    high_risks = session.query(BurnoutRisk).filter(
        BurnoutRisk.date >= today,
        BurnoutRisk.date < tomorrow,
        BurnoutRisk.risk_level == "HIGH"
    ).all()
    
    # Get statistics
    total_students = session.query(Student).count()
    high_risk_count = len(high_risks)
    
    alerts = []
    for risk in high_risks:
        alerts.append({
            "student_anon_id": f"Student_{risk.student_id[-4:]}",
            "risk_score": risk.risk_score,
            "primary_factor": risk.primary_factors,
            "detected_at": risk.date
        })
    
    return {
        "total_students": total_students,
        "high_risk_count": high_risk_count,
        "high_risk_percentage": round(high_risk_count / max(total_students, 1) * 100, 1),
        "alerts": alerts
    }

@router.post("/api/automation/run-daily-check")
async def run_daily_check():
    """Manually trigger daily automation"""
    alerts = notification_system.check_high_risk_students()
    scheduled = notification_system.schedule_weekly_checkins()
    
    return {
        "message": "Daily check completed",
        "alerts_sent": len(alerts),
        "checkins_scheduled": len(scheduled)
    }

#add to ml endpoints
@router.get("/api/ml/predict/{student_id}")
async def ml_predict_student(student_id: str):
    """ML-based prediction for a student"""
    session = get_session()
    
    # Get latest bio-signal data
    latest_data = session.query(BioSignalData).filter(
        BioSignalData.student_id == student_id
    ).order_by(BioSignalData.timestamp.desc()).first()
    
    if not latest_data:
        return {"error": "No data available"}
    
    # Prepare data for prediction
    bio_data = {
        'hrv': latest_data.hrv_value,
        'sleep_hours': latest_data.sleep_hours,
        'sleep_quality': latest_data.sleep_quality,
        'heart_rate': latest_data.heart_rate,
        'step_count': latest_data.step_count,
        'stress_level': latest_data.stress_level
    }
    
    # Get ML prediction
    ml_prediction = predictor.predict_single(bio_data)
    
    # Get trend analysis
    historical = session.query(BioSignalData).filter(
        BioSignalData.student_id == student_id
    ).order_by(BioSignalData.timestamp).all()
    
    if len(historical) > 5:
        hrv_trend = trend_analyzer.analyze_trend(
            [(d.timestamp, d.hrv_value) for d in historical[-14:]]
        )
    else:
        hrv_trend = {'trend': 'insufficient_data'}
    
    return {
        'student_id': student_id,
        'ml_prediction': ml_prediction,
        'trend_analysis': hrv_trend,
        'latest_data': {
            'timestamp': latest_data.timestamp,
            'hrv': latest_data.hrv_value,
            'sleep': latest_data.sleep_hours
        }
    }

@router.get("/api/ml/explain/{student_id}")
async def explain_prediction(student_id: str):
    """Get explanation for prediction"""
    session = get_session()
    
    latest_data = session.query(BioSignalData).filter(
        BioSignalData.student_id == student_id
    ).order_by(BioSignalData.timestamp.desc()).first()
    
    if not latest_data:
        return {"error": "No data available"}
    
    bio_data = {
        'hrv': latest_data.hrv_value,
        'sleep_hours': latest_data.sleep_hours,
        'sleep_quality': latest_data.sleep_quality,
        'heart_rate': latest_data.heart_rate,
        'step_count': latest_data.step_count,
        'stress_level': latest_data.stress_level
    }
    
    explanation = predictor.explain_prediction(bio_data)
    
    return explanation