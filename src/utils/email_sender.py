# # src/utils/email_sender.py
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import logging

# logger = logging.getLogger(__name__)

# class EmailSender:
#     """Send email alerts for high-risk students"""
    
#     def __init__(self, sender_email="deshantharaka422@gmail.com", sender_password="opec kwsd rfso ecdt"):
#         # For Gmail, use App Password (not normal password)
#         self.sender_email = sender_email
#         self.sender_password = sender_password
#         self.smtp_server = "smtp.gmail.com"
#         self.smtp_port = 587
        
#     def send_alert(self, to_email, student_anonymous_id, risk_score, primary_factor):
#         """Send high-risk alert email"""
#         subject = f"🚨 HIGH RISK ALERT - Student {student_anonymous_id}"
        
#         body = f"""
#         Student Burnout Detection System - Alert
        
#         Student: {student_anonymous_id}
#         Risk Level: HIGH
#         Risk Score: {risk_score}
#         Primary Factor: {primary_factor}
        
#         Recommended Actions:
#         1. Schedule a counseling session
#         2. Send wellness tips
#         3. Follow up in 2 days
        
#         This is an automated alert from the system.
#         """
        
#         msg = MIMEMultipart()
#         msg['From'] = self.sender_email
#         msg['To'] = to_email
#         msg['Subject'] = subject
#         msg.attach(MIMEText(body, 'plain'))
        
#         try:
#             server = smtplib.SMTP(self.smtp_server, self.smtp_port)
#             server.starttls()
#             server.login(self.sender_email, self.sender_password)
#             server.send_message(msg)
#             server.quit()
#             logger.info(f"Email sent to {to_email}")
#             return True
#         except Exception as e:
#             logger.error(f"Failed to send email: {e}")
#             return False



# src/utils/email_sender.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

class EmailSender:
    """Send email alerts for high-risk students"""
    
    def __init__(self, sender_email="deshantharaka422@gmail.com", sender_password="opec kwsd rfso ecdt"):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
    def send_alert(self, to_email, student_anonymous_id, risk_score, primary_factor):
        """Send high-risk alert email"""
        subject = f"🚨 HIGH RISK ALERT - Student {student_anonymous_id}"
        
        body = f"""
        Student Burnout Detection System - Alert
        
        Student: {student_anonymous_id}
        Risk Level: HIGH
        Risk Score: {risk_score}
        Primary Factor: {primary_factor}
        
        Recommended Actions:
        1. Schedule a counseling session
        2. Send wellness tips
        3. Follow up in 2 days
        
        This is an automated alert from the system.
        """
        
        return self._send_email(to_email, subject, body)
    
    def send_wellness_tips(self, to_email, wellness_content, total_students, high_risk_count, medium_risk_count, low_risk_count):
        """Send mass wellness tips to all students"""
        subject = f"🌿 STUDENT WELLNESS REPORT - {total_students} Students"
        
        body = f"""
        Student Wellness Tips - Daily Report
        ========================================
        Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Summary:
        • Total Students: {total_students}
        • High Risk: {high_risk_count}
        • Medium Risk: {medium_risk_count}
        • Low Risk: {low_risk_count}
        
        ========================================
        
        {wellness_content}
        
        ========================================
        This is an automated wellness message.
        For immediate support, contact the counseling center.
        """
        
        return self._send_email(to_email, subject, body)
    
    def _send_email(self, to_email, subject, body):
        """Internal method to send email"""
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False