# src/api/routes.py
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.database.database_setup import get_db
from src.database.models import Student, BioSignalData, BurnoutRisk
from src.api.schemas import (
    StudentCreate, StudentLogin, StudentResponse,
    BioSignalResponse, BurnoutRiskResponse, DashboardData,
)
from src.api.auth import AuthHandler
from src.automation.notification_system import NotificationSystem
from src.ml.predict import BurnoutPredictor
from src.advanced_analytics.trend_analysis import TrendAnalyzer

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")
auth_handler = AuthHandler()
notification_system = NotificationSystem()

# Initialize ML components
predictor = BurnoutPredictor()
trend_analyzer = TrendAnalyzer()

# ============= Web Pages =============

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/student/{student_id}", response_class=HTMLResponse)
async def student_portal(request: Request, student_id: str):
    return templates.TemplateResponse(
        "student_portal.html",
        {"request": request, "student_id": student_id},
    )

@router.get("/counselor", response_class=HTMLResponse)
async def counselor_dashboard(request: Request):
    return templates.TemplateResponse(
        "counselor_dashboard.html",
        {"request": request},
    )

# ============= API Endpoints =============

@router.post("/api/register")
async def register_student(student: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(
        Student.student_id == student.student_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Student already exists")

    new_student = Student(
        student_id=student.student_id,
        anonymous_id=f"ANON{hash(student.student_id) % 10000:04d}",
        wearable_type=student.wearable_type,
    )
    db.add(new_student)
    db.commit()
    return {"message": "Student registered successfully"}


@router.post("/api/login")
async def login(login_data: StudentLogin, db: Session = Depends(get_db)):
    student = db.query(Student).filter(
        Student.student_id == login_data.student_id
    ).first()

    if not student:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth_handler.create_access_token(
        data={"sub": student.student_id}
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/api/student/{student_id}/dashboard")
async def get_student_dashboard(student_id: str, db: Session = Depends(get_db)):
    latest_risk = db.query(BurnoutRisk).filter(
        BurnoutRisk.student_id == student_id
    ).order_by(BurnoutRisk.date.desc()).first()

    week_ago = datetime.now() - timedelta(days=7)
    recent_risks = db.query(BurnoutRisk).filter(
        BurnoutRisk.student_id == student_id,
        BurnoutRisk.date >= week_ago,
    ).order_by(BurnoutRisk.date).all()

    recent_bio = db.query(BioSignalData).filter(
        BioSignalData.student_id == student_id
    ).order_by(BioSignalData.timestamp.desc()).limit(7).all()

    if recent_bio:
        avg_sleep = sum(b.sleep_hours for b in recent_bio) / len(recent_bio)
        avg_hrv = sum(b.hrv_value for b in recent_bio) / len(recent_bio)
    else:
        avg_sleep = 0
        avg_hrv = 0

    if latest_risk and latest_risk.risk_level == "HIGH":
        recommendations = [
            "Schedule a counseling session",
            "Take breaks between study sessions",
            "Talk to a friend or family member",
        ]
    elif latest_risk and latest_risk.risk_level == "MEDIUM":
        recommendations = [
            "Practice deep breathing exercises",
            "Ensure 7-8 hours of sleep",
            "Take short walks",
        ]
    else:
        recommendations = [
            "Maintain current healthy habits",
            "Stay connected with friends",
            "Regular exercise",
        ]

    return {
        "student_id": student_id,
        "current_risk": {
            "date": latest_risk.date if latest_risk else datetime.now(),
            "risk_score": latest_risk.risk_score if latest_risk else 0,
            "risk_level": latest_risk.risk_level if latest_risk else "LOW",
            "primary_factors": latest_risk.primary_factors if latest_risk else "None",
        },
        "recent_trend": [
            {"date": r.date, "risk_score": r.risk_score} for r in recent_risks
        ],
        "weekly_summary": {
            "avg_sleep": round(avg_sleep, 1),
            "avg_hrv": round(avg_hrv, 1),
            "total_days": len(recent_risks),
        },
        "recommendations": recommendations,
    }


@router.get("/api/counselor/alerts")
async def get_counselor_alerts(db: Session = Depends(get_db)):
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    high_risks = db.query(BurnoutRisk).filter(
        BurnoutRisk.date >= today,
        BurnoutRisk.date < tomorrow,
        BurnoutRisk.risk_level == "HIGH",
    ).all()

    total_students = db.query(Student).count()
    high_risk_count = len(high_risks)

    alerts = [
        {
            "student_anon_id": f"Student_{risk.student_id[-4:]}",
            "risk_score": risk.risk_score,
            "primary_factor": risk.primary_factors,
            "detected_at": risk.date,
        }
        for risk in high_risks
    ]

    return {
        "total_students": total_students,
        "high_risk_count": high_risk_count,
        "high_risk_percentage": round(high_risk_count / max(total_students, 1) * 100, 1),
        "alerts": alerts,
    }


@router.post("/api/automation/run-daily-check")
async def run_daily_check():
    alerts = notification_system.check_high_risk_students()
    scheduled = notification_system.schedule_weekly_checkins()
    return {
        "message": "Daily check completed",
        "alerts_sent": len(alerts),
        "checkins_scheduled": len(scheduled),
    }


# ============= ML Endpoints =============

@router.get("/api/ml/predict/{student_id}")
async def ml_predict_student(student_id: str, db: Session = Depends(get_db)):
    latest_data = db.query(BioSignalData).filter(
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
        'stress_level': latest_data.stress_level,
    }

    ml_prediction = predictor.predict_single(bio_data)

    historical = db.query(BioSignalData).filter(
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
            'sleep': latest_data.sleep_hours,
        },
    }


@router.get("/api/ml/explain/{student_id}")
async def explain_prediction(student_id: str, db: Session = Depends(get_db)):
    latest_data = db.query(BioSignalData).filter(
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
        'stress_level': latest_data.stress_level,
    }

    return predictor.explain_prediction(bio_data)
