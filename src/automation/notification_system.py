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
            Hello Student {student_id}!
            
            Our system has detected changes in your heart rate variability.
            This could be a sign of stress.
            
            Please take care of your health.
            If needed, contact the university counseling service.
            
            Have a great day!
            """
        elif primary_factor == "Sleep":
            message = f"""
            Hello Student {student_id}!
            
            A decrease in your sleep pattern has been observed.
            Adequate sleep is very important for your mental health.
            
            Some simple sleep tips:
            • Reduce mobile phone usage before bedtime
            • Keep your room dark
            • Avoid coffee/tea before sleep
            """
        else:  # Activity
            message = f"""
            Hello Student {student_id}!
            
            Your physical activity level has decreased.
            A small exercise routine can help reduce mental stress.
            
            Try to walk 5000 steps daily.
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