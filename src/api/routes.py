# # src/api/routes.py
# from fastapi import APIRouter, HTTPException, Depends, Request
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import HTMLResponse
# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime, timedelta

# from src.database.database_setup import get_session
# from src.database.models import Student, BioSignalData, BurnoutRisk
# from src.api.schemas import *
# from src.api.auth import AuthHandler
# from src.bio_processing.burnout_calculator import BurnoutCalculator
# from src.automation.notification_system import NotificationSystem
# from src.ml.predict import BurnoutPredictor
# from src.advanced_analytics.trend_analysis import TrendAnalyzer

# router = APIRouter()
# templates = Jinja2Templates(directory="src/web/templates")
# auth_handler = AuthHandler()
# notification_system = NotificationSystem()

# # ============= Web Pages =============
# @router.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# @router.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})




# @router.get("/student/{student_id}", response_class=HTMLResponse)
# async def student_dashboard_old(request: Request, student_id: str):
#     return templates.TemplateResponse("student_dashboard.html", {"request": request, "student_id": student_id})



# @router.get("/counselor", response_class=HTMLResponse)
# async def counselor_dashboard_old(request: Request):
#     return templates.TemplateResponse("counselor_dashboard.html", {"request": request, "counselor_id": "jhonwick"})

# # Initialize ML components
# predictor = BurnoutPredictor()
# trend_analyzer = TrendAnalyzer()

# # ============= API Endpoints =============
# @router.post("/api/register")
# async def register_student(student: StudentCreate):
#     session = get_session()
    
#     # Check if student exists
#     existing = session.query(Student).filter(
#         Student.student_id == student.student_id
#     ).first()
    
#     if existing:
#         raise HTTPException(status_code=400, detail="Student already exists")
    
#     # Create new student
#     new_student = Student(
#         student_id=student.student_id,
#         anonymous_id=f"ANON{hash(student.student_id) % 10000:04d}",
#         wearable_type=student.wearable_type
#     )
    
#     session.add(new_student)
#     session.commit()
    
#     return {"message": "Student registered successfully"}

# @router.get("/api/students/all")
# async def get_all_students():
#     session = get_session()
    
#     # Get latest risk for each student
#     from sqlalchemy import func
#     subquery = session.query(
#         BurnoutRisk.student_id,
#         func.max(BurnoutRisk.date).label('max_date')
#     ).group_by(BurnoutRisk.student_id).subquery()
    
#     latest_risks = session.query(BurnoutRisk).join(
#         subquery,
#         (BurnoutRisk.student_id == subquery.c.student_id) &
#         (BurnoutRisk.date == subquery.c.max_date)
#     ).all()
    
#     result = []
#     for risk in latest_risks:
#         # Get bio data
#         bio = session.query(BioSignalData).filter(
#             BioSignalData.student_id == risk.student_id
#         ).order_by(BioSignalData.timestamp.desc()).first()
        
#         # Get anonymous ID
#         student = session.query(Student).filter(Student.student_id == risk.student_id).first()
        
#         result.append({
#             'student_id': risk.student_id,
#             'anonymous_id': student.anonymous_id if student else risk.student_id,
#             'risk_level': risk.risk_level,
#             'risk_score': risk.risk_score,
#             'primary_factors': risk.primary_factors,
#             'hrv_value': bio.hrv_value if bio else 0,
#             'sleep_hours': bio.sleep_hours if bio else 0,
#             'step_count': bio.step_count if bio else 0,
#             'timestamp': risk.date.isoformat()
#         })
    
#     return result

# @router.post("/api/login")
# async def login(login_data: StudentLogin):
#     session = get_session()
    
#     student = session.query(Student).filter(
#         Student.student_id == login_data.student_id
#     ).first()
    
#     if not student:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
    
#     # Create token
#     token = auth_handler.create_access_token(
#         data={"sub": student.student_id}
#     )
    
#     return {"access_token": token, "token_type": "bearer"}

# @router.get("/api/student/{student_id}/dashboard")
# async def get_student_dashboard(student_id: str):
#     session = get_session()
    
#     # Get latest risk
#     latest_risk = session.query(BurnoutRisk).filter(
#         BurnoutRisk.student_id == student_id
#     ).order_by(BurnoutRisk.date.desc()).first()
    
#     # Get last 7 days trend
#     week_ago = datetime.now() - timedelta(days=7)
#     recent_risks = session.query(BurnoutRisk).filter(
#         BurnoutRisk.student_id == student_id,
#         BurnoutRisk.date >= week_ago
#     ).order_by(BurnoutRisk.date).all()
    
#     # Get recent bio data
#     recent_bio = session.query(BioSignalData).filter(
#         BioSignalData.student_id == student_id
#     ).order_by(BioSignalData.timestamp.desc()).limit(7).all()
    
#     # Calculate averages
#     if recent_bio:
#         avg_sleep = sum(b.sleep_hours for b in recent_bio) / len(recent_bio)
#         avg_hrv = sum(b.hrv_value for b in recent_bio) / len(recent_bio)
#     else:
#         avg_sleep = 0
#         avg_hrv = 0
    
#     # Generate recommendations
#     recommendations = []
#     if latest_risk:
#         if latest_risk.risk_level == "HIGH":
#             recommendations = [
#                 "Schedule a counseling session",
#                 "Take breaks between study sessions",
#                 "Talk to a friend or family member"
#             ]
#         elif latest_risk.risk_level == "MEDIUM":
#             recommendations = [
#                 "Practice deep breathing exercises",
#                 "Ensure 7-8 hours of sleep",
#                 "Take short walks"
#             ]
#         else:
#             recommendations = [
#                 "Maintain current healthy habits",
#                 "Stay connected with friends",
#                 "Regular exercise"
#             ]
    
#     dashboard = {
#         "student_id": student_id,
#         "current_risk": {
#             "date": latest_risk.date if latest_risk else datetime.now(),
#             "risk_score": latest_risk.risk_score if latest_risk else 0,
#             "risk_level": latest_risk.risk_level if latest_risk else "LOW",
#             "primary_factors": latest_risk.primary_factors if latest_risk else "None"
#         },
#         "recent_trend": [
#             {"date": r.date, "risk_score": r.risk_score} for r in recent_risks
#         ],
#         "weekly_summary": {
#             "avg_sleep": round(avg_sleep, 1),
#             "avg_hrv": round(avg_hrv, 1),
#             "total_days": len(recent_risks)
#         },
#         "recommendations": recommendations
#     }
    
#     return dashboard

# # Add to src/api/routes.py



# @router.get("/register", response_class=HTMLResponse)
# async def register_page(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request}) 

# @router.get("/student/dashboard", response_class=HTMLResponse)
# async def student_dashboard(request: Request):
#     # Check session (simple demo – in real app, verify token)
#     # For demo, we'll just accept any request
#     student_id = request.query_params.get("student_id", "deshan")
#     return templates.TemplateResponse("student_dashboard.html", {"request": request, "student_id": student_id})   


# @router.get("/counselor/dashboard", response_class=HTMLResponse)
# async def counselor_dashboard(request: Request):
#     return templates.TemplateResponse("counselor_dashboard.html", {"request": request, "counselor_id": "jhonwick"})


# @router.get("/api/counselor/alerts")
# async def get_counselor_alerts():
#     session = get_session()
    
#     # Get today's high risk students
#     today = datetime.now().date()
#     tomorrow = today + timedelta(days=1)
    
#     high_risks = session.query(BurnoutRisk).filter(
#         BurnoutRisk.date >= today,
#         BurnoutRisk.date < tomorrow,
#         BurnoutRisk.risk_level == "HIGH"
#     ).all()
    
#     # Get statistics
#     total_students = session.query(Student).count()
#     high_risk_count = len(high_risks)
    
#     alerts = []
#     for risk in high_risks:
#         alerts.append({
#             "student_anon_id": f"Student_{risk.student_id[-4:]}",
#             "risk_score": risk.risk_score,
#             "primary_factor": risk.primary_factors,
#             "detected_at": risk.date
#         })
    
#     return {
#         "total_students": total_students,
#         "high_risk_count": high_risk_count,
#         "high_risk_percentage": round(high_risk_count / max(total_students, 1) * 100, 1),
#         "alerts": alerts
#     }

# @router.post("/api/automation/run-daily-check")
# async def run_daily_check():
#     """Manually trigger daily automation"""
#     alerts = notification_system.check_high_risk_students()
#     scheduled = notification_system.schedule_weekly_checkins()
    
#     return {
#         "message": "Daily check completed",
#         "alerts_sent": len(alerts),
#         "checkins_scheduled": len(scheduled)
#     }

# #add to ml endpoints
# @router.get("/api/ml/predict/{student_id}")
# async def ml_predict_student(student_id: str):
#     """ML-based prediction for a student"""
#     session = get_session()
    
#     # Get latest bio-signal data
#     latest_data = session.query(BioSignalData).filter(
#         BioSignalData.student_id == student_id
#     ).order_by(BioSignalData.timestamp.desc()).first()
    
#     if not latest_data:
#         return {"error": "No data available"}
    
#     # Prepare data for prediction
#     bio_data = {
#         'hrv': latest_data.hrv_value,
#         'sleep_hours': latest_data.sleep_hours,
#         'sleep_quality': latest_data.sleep_quality,
#         'heart_rate': latest_data.heart_rate,
#         'step_count': latest_data.step_count,
#         'stress_level': latest_data.stress_level
#     }
    
#     # Get ML prediction
#     ml_prediction = predictor.predict_single(bio_data)
    
#     # Get trend analysis
#     historical = session.query(BioSignalData).filter(
#         BioSignalData.student_id == student_id
#     ).order_by(BioSignalData.timestamp).all()
    
#     if len(historical) > 5:
#         hrv_trend = trend_analyzer.analyze_trend(
#             [(d.timestamp, d.hrv_value) for d in historical[-14:]]
#         )
#     else:
#         hrv_trend = {'trend': 'insufficient_data'}
    
#     return {
#         'student_id': student_id,
#         'ml_prediction': ml_prediction,
#         'trend_analysis': hrv_trend,
#         'latest_data': {
#             'timestamp': latest_data.timestamp,
#             'hrv': latest_data.hrv_value,
#             'sleep': latest_data.sleep_hours
#         }
#     }

# @router.get("/api/ml/explain/{student_id}")
# async def explain_prediction(student_id: str):
#     """Get explanation for prediction"""
#     session = get_session()
    
#     latest_data = session.query(BioSignalData).filter(
#         BioSignalData.student_id == student_id
#     ).order_by(BioSignalData.timestamp.desc()).first()
    
#     if not latest_data:
#         return {"error": "No data available"}
    
#     bio_data = {
#         'hrv': latest_data.hrv_value,
#         'sleep_hours': latest_data.sleep_hours,
#         'sleep_quality': latest_data.sleep_quality,
#         'heart_rate': latest_data.heart_rate,
#         'step_count': latest_data.step_count,
#         'stress_level': latest_data.stress_level
#     }
    
#     explanation = predictor.explain_prediction(bio_data)
    
#     return explanation


# # Add to routes.py
# from .email_alert import check_and_alert_high_risk, send_high_risk_alert

# @router.post("/api/check-high-risk")
# async def check_high_risk_and_alert():
#     """Check for high-risk students and send email alerts"""
#     check_and_alert_high_risk()
#     return {"message": "High-risk check completed, alerts sent if any"}

# @router.get("/api/high-risk-students")
# async def get_high_risk_students():
#     """Get list of high-risk students for today"""
#     session = get_session()
#     today = datetime.now().date()
#     high_risks = session.query(BurnoutRisk).filter(
#         BurnoutRisk.date >= today,
#         BurnoutRisk.risk_level == "HIGH"
#     ).all()
    
#     result = []
#     for risk in high_risks:
#         student = session.query(Student).filter(Student.student_id == risk.student_id).first()
#         result.append({
#             'anonymous_id': student.anonymous_id if student else risk.student_id,
#             'risk_score': risk.risk_score,
#             'primary_factor': risk.primary_factors,
#             'detected_at': risk.date.isoformat()
#         })
#     session.close()
#     return result





# src/api/routes.py
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.database.database_setup import get_session
from src.database.models import Student, BioSignalData, BurnoutRisk
from datetime import datetime, timedelta
from sqlalchemy import func

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")

# Helper function to get template context with session
def get_template_context(request: Request, extra_data: dict = None):
    """Create template context with session data"""
    context = {
        "request": request,
        "session": request.session if hasattr(request, 'session') else {}
    }
    if extra_data:
        context.update(extra_data)
    return context

# Hardcoded credentials (for demo)
STUDENT_CREDENTIALS = {"deshan": "des123"}
COUNSELOR_CREDENTIALS = {"jhonwick": "jhon123"}

# ========== ROOT & BASIC ROUTES ==========
@router.get("/")
async def root(request: Request):
    """Root path - redirect to login page"""
    return RedirectResponse(url="/login", status_code=303)

@router.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/favicon.ico")

# ========== LOGIN PAGES ==========
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    context = get_template_context(request, {"error": None})
    return templates.TemplateResponse("login.html", context)

@router.post("/login/student")
async def login_student(request: Request, student_id: str = Form(...), password: str = Form(...)):
    if student_id in STUDENT_CREDENTIALS and STUDENT_CREDENTIALS[student_id] == password:
        request.session['user_type'] = 'student'
        request.session['user_id'] = student_id
        return RedirectResponse(url="/student/dashboard", status_code=303)
    context = get_template_context(request, {"error": "Invalid Student ID or Password"})
    return templates.TemplateResponse("login.html", context)

@router.post("/login/counselor")
async def login_counselor(request: Request, counselor_id: str = Form(...), password: str = Form(...)):
    if counselor_id in COUNSELOR_CREDENTIALS and COUNSELOR_CREDENTIALS[counselor_id] == password:
        request.session['user_type'] = 'counselor'
        request.session['user_id'] = counselor_id
        return RedirectResponse(url="/counselor/dashboard", status_code=303)
    context = get_template_context(request, {"error": "Invalid Counselor ID or Password"})
    return templates.TemplateResponse("login.html", context)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

# ========== REGISTER ==========
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    context = get_template_context(request)
    return templates.TemplateResponse("register.html", context)

# ========== DASHBOARDS (Protected) ==========
@router.get("/student/dashboard", response_class=HTMLResponse)
async def student_dashboard(request: Request):
    if request.session.get('user_type') != 'student':
        return RedirectResponse(url="/login", status_code=303)
    context = get_template_context(request)
    return templates.TemplateResponse("student_dashboard.html", context)

@router.get("/counselor/dashboard", response_class=HTMLResponse)
async def counselor_dashboard(request: Request):
    if request.session.get('user_type') != 'counselor':
        return RedirectResponse(url="/login", status_code=303)
    context = get_template_context(request)
    return templates.TemplateResponse("counselor_dashboard.html", context)

# Keep old endpoints for backward compatibility
@router.get("/student/{student_id}", response_class=HTMLResponse)
async def student_dashboard_old(request: Request, student_id: str):
    if request.session.get('user_type') != 'student':
        return RedirectResponse(url="/login", status_code=303)
    context = get_template_context(request)
    return templates.TemplateResponse("student_dashboard.html", context)

@router.get("/counselor", response_class=HTMLResponse)
async def counselor_dashboard_old(request: Request):
    if request.session.get('user_type') != 'counselor':
        return RedirectResponse(url="/login", status_code=303)
    context = get_template_context(request)
    return templates.TemplateResponse("counselor_dashboard.html", context)

# ========== API ENDPOINTS ==========
@router.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "System is running"}

@router.get("/api/students/all")
async def get_all_students():
    db_session = get_session()
    try:
        subquery = db_session.query(
            BurnoutRisk.student_id,
            func.max(BurnoutRisk.date).label('max_date')
        ).group_by(BurnoutRisk.student_id).subquery()
        
        latest_risks = db_session.query(BurnoutRisk).join(
            subquery,
            (BurnoutRisk.student_id == subquery.c.student_id) &
            (BurnoutRisk.date == subquery.c.max_date)
        ).all()
        
        result = []
        for risk in latest_risks:
            bio = db_session.query(BioSignalData).filter(
                BioSignalData.student_id == risk.student_id
            ).order_by(BioSignalData.timestamp.desc()).first()
            
            student = db_session.query(Student).filter(
                Student.student_id == risk.student_id
            ).first()
            
            result.append({
                'student_id': risk.student_id,
                'anonymous_id': student.anonymous_id if student else risk.student_id,
                'risk_level': risk.risk_level,
                'risk_score': risk.risk_score,
                'primary_factors': risk.primary_factors,
                'hrv_value': bio.hrv_value if bio else 0,
                'sleep_hours': bio.sleep_hours if bio else 0,
                'step_count': bio.step_count if bio else 0
            })
    except Exception as e:
        result = []
    finally:
        db_session.close()
    
    return result

@router.get("/api/high-risk-students")
async def get_high_risk_students():
    db_session = get_session()
    today = datetime.now().date()
    try:
        high_risks = db_session.query(BurnoutRisk).filter(
            BurnoutRisk.date >= today,
            BurnoutRisk.risk_level == "HIGH"
        ).all()
        
        result = []
        for risk in high_risks:
            student = db_session.query(Student).filter(
                Student.student_id == risk.student_id
            ).first()
            result.append({
                'anonymous_id': student.anonymous_id if student else risk.student_id,
                'risk_score': risk.risk_score,
                'primary_factor': risk.primary_factors,
                'detected_at': risk.date.isoformat()
            })
    except Exception as e:
        result = []
    finally:
        db_session.close()
    
    return result

@router.post("/api/check-high-risk")
async def check_high_risk_and_alert():
    """Check for high-risk students and send email alerts"""
    from src.utils.email_sender import EmailSender
    import os
    
    db_session = get_session()
    today = datetime.now().date()
    
    try:
        high_risks = db_session.query(BurnoutRisk).filter(
            BurnoutRisk.date >= today,
            BurnoutRisk.risk_level == "HIGH"
        ).all()
        
        if not high_risks:
            return {"message": "No high-risk students found", "count": 0}
        
        # Initialize email sender
        email_sender = EmailSender()
        recipient = "deshantharaka422@gmail.com"
        
        sent_count = 0
        for risk in high_risks:
            student = db_session.query(Student).filter(
                Student.student_id == risk.student_id
            ).first()
            
            anonymous_id = student.anonymous_id if student else risk.student_id
            
            success = email_sender.send_alert(
                to_email=recipient,
                student_anonymous_id=anonymous_id,
                risk_score=risk.risk_score,
                primary_factor=risk.primary_factors
            )
            
            if success:
                sent_count += 1
                print(f"📧 Alert sent for {anonymous_id}")
        
        return {"message": f"Sent {sent_count} email alerts", "count": sent_count}
        
    except Exception as e:
        print(f"Error: {e}")
        return {"message": f"Error: {e}", "count": 0}
    finally:
        db_session.close()