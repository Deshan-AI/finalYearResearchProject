# test_email.py
from src.utils.email_sender import EmailSender

def test_email():
    print("📧 Testing email sending...")
    
    email_sender = EmailSender()
    
    success = email_sender.send_alert(
        to_email="deshantharaka422@gmail.com",
        student_anonymous_id="TEST_ANON_1234",
        risk_score="0.85",
        primary_factor="HRV (Low)"
    )
    
    if success:
        print("✅ Test email sent! Check your inbox/spam.")
    else:
        print("❌ Test failed. Check your email configuration.")

if __name__ == "__main__":
    test_email()