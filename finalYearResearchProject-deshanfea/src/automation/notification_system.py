# src/automation/notification_system.py
from datetime import datetime, timedelta
from src.database.database_setup import get_session
from src.database.models import BurnoutRisk, Student
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationSystem:
    """Automated notification system (RPA alternative)"""
    
    def __init__(self):
        self.session = get_session()
    
    def check_high_risk_students(self):
        """Daily check for high-risk students"""
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        high_risks = self.session.query(BurnoutRisk).filter(
            BurnoutRisk.date >= today,
            BurnoutRisk.date < tomorrow,
            BurnoutRisk.risk_level == "HIGH"
        ).all()
        
        alerts = []
        for risk in high_risks:
            alert = self.generate_alert(risk)
            self.send_alert(alert)
            alerts.append(alert)
        
        return alerts
    
    def generate_alert(self, risk_record):
        """Generate personalized alert message"""
        student_id = risk_record.student_id
        risk_score = risk_record.risk_score
        primary_factor = risk_record.primary_factors
        
        # Personalized messages based on primary factor
        if primary_factor == "HRV":
            message = f"""
            හෙලෝ Student {student_id}!
            
            අපගේ පද්ධතියට අනුව ඔබගේ හෘද ස්පන්දන රටාවේ වෙනස්කම් දක්නට ලැබේ.
            මෙය ආතතියේ ලකුණක් විය හැකියි.
            
            කරුණාකර ඔබේ සෞඛ්‍යය ගැන සැලකිලිමත් වන්න.
            අවශ්‍ය නම් විශ්වවිද්‍යාලයේ කාවන්සලින්ග් සේවාව අමතන්න.
            
            සුබ දවසක්!
            """
        elif primary_factor == "Sleep":
            message = f"""
            හෙලෝ Student {student_id}!
            
            ඔබගේ නින්දේ රටාවේ අඩුවක් පෙනෙනවා.
            ප්‍රමාණවත් නින්ද ඔබේ මානසික සෞඛ්‍යට ඉතා වැදගත්.
            
            සරල නින්ද උපදෙස් කිහිපයක්:
            • නින්දට යාමට පෙර ජංගම දුරකථන භාවිතය අඩු කරන්න
            • කාමරය අඳුරු කර තබා ගන්න
            • නින්දට පෙර කෝපි/තේ පානයෙන් වළකින්න
            """
        else:  # Activity
            message = f"""
            හෙලෝ Student {student_id}!
            
            ඔබගේ ශාරීරික ක්‍රියාකලාපය අඩු වී ඇත.
            කුඩා ව්‍යායාම පුරුද්දක් මානසික ආතතිය අඩු කරන්න උපකාරී වේ.
            
            දිනපතා පියවර 5000ක් ඇවිදින්න උත්සාහ කරන්න.
            """
        
        return {
            'student_id': student_id,
            'risk_score': risk_score,
            'primary_factor': primary_factor,
            'message': message,
            'timestamp': datetime.now()
        }
    
    def send_alert(self, alert):
        """Send alert (simulate for now)"""
        print("\n" + "="*50)
        print(f"📱 ALERT FOR STUDENT: {alert['student_id']}")
        print(f"Risk Score: {alert['risk_score']}")
        print(f"Primary Factor: {alert['primary_factor']}")
        print(f"Message: {alert['message']}")
        print("="*50 + "\n")
        
        # In real implementation, this would:
        # 1. Send email
        # 2. Send SMS
        # 3. Push notification
        # 4. Log to database
        
        return True
    
    def schedule_weekly_checkins(self):
        """Schedule automatic check-ins for medium risk students"""
        medium_risks = self.session.query(BurnoutRisk).filter(
            BurnoutRisk.risk_level == "MEDIUM"
        ).all()
        
        for risk in medium_risks:
            # Schedule reminder for next week
            reminder = {
                'student_id': risk.student_id,
                'scheduled_date': datetime.now() + timedelta(days=7),
                'type': 'weekly_checkin',
                'message': 'Weekly wellness check-in reminder'
            }
            print(f"📅 Scheduled check-in for {risk.student_id}")
        
        return medium_risks