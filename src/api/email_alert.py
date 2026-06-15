# src/api/email_alert.py
from src.utils.email_sender import EmailSender
from src.database.database_setup import get_session
from src.database.models import Student, BurnoutRisk
import threading

# Email configuration (use your Gmail app password)
EMAIL_SENDER = "deshantharaka422@gmail.com"  # Your email
EMAIL_PASSWORD = "opec kwsd rfso ecdt"   # Replace with app password
ALERT_RECIPIENT = "deshantharaka422@gmail.com"

email_sender = EmailSender(EMAIL_SENDER, EMAIL_PASSWORD)

def send_high_risk_alert(student_anonymous_id, risk_score, primary_factor):
    """Send email alert in background thread"""
    def send():
        email_sender.send_alert(
            to_email=ALERT_RECIPIENT,
            student_anonymous_id=student_anonymous_id,
            risk_score=risk_score,
            primary_factor=primary_factor
        )
    thread = threading.Thread(target=send)
    thread.daemon = True
    thread.start()

def check_and_alert_high_risk():
    """Check database for new high-risk students and send alerts"""
    session = get_session()
    # Get today's high risk students that haven't been alerted
    from datetime import datetime, timedelta
    today = datetime.now().date()
    high_risks = session.query(BurnoutRisk).filter(
        BurnoutRisk.date >= today,
        BurnoutRisk.risk_level == "HIGH"
    ).all()
    
    for risk in high_risks:
        # Check if alert already sent (you may need a flag column; for demo, just send)
        student = session.query(Student).filter(Student.student_id == risk.student_id).first()
        if student:
            send_high_risk_alert(student.anonymous_id, risk.risk_score, risk.primary_factors)
    session.close()