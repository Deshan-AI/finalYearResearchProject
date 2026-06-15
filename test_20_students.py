# test_20_students.py
"""
Generate test data for 20 students with different health metrics.
4 students will be HIGH risk and trigger email alerts.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import random
import pandas as pd
from datetime import datetime, timedelta
from src.database.database_setup import get_session, setup_database
from src.database.models import Student, BioSignalData, BurnoutRisk
from src.utils.email_sender import EmailSender

# Target email for alerts
ALERT_EMAIL = "deshantharaka422@gmail.com"

def generate_student_data():
    """Generate 20 students with varying health profiles"""
    
    session = get_session()
    
    # Clear existing test data (optional - be careful!)
    # Uncomment if you want clean test:
    # session.query(BurnoutRisk).delete()
    # session.query(BioSignalData).delete()
    # session.query(Student).delete()
    # session.commit()
    
    students = []
    
    # Predefine 4 high-risk students (indices 0, 5, 10, 15)
    high_risk_indices = [0, 5, 10, 15]
    
    for i in range(20):
        student_id = f"TEST_STU_{i+1:03d}"
        anonymous_id = f"ANON_{random.randint(1000,9999)}"
        
        # Determine risk level
        if i in high_risk_indices:
            risk_level = "HIGH"
        else:
            # Random low/medium for others
            risk_level = random.choice(["LOW", "MEDIUM"])
        
        # Set health parameters based on risk level
        if risk_level == "HIGH":
            hrv = random.randint(30, 45)           # Low HRV = high stress
            sleep_hours = random.uniform(3.5, 5.5)
            sleep_quality = random.uniform(0.2, 0.4)
            heart_rate = random.randint(85, 105)
            step_count = random.randint(1000, 3000)
            stress_level = random.uniform(0.7, 0.95)
            primary_factor = random.choice(["HRV", "Sleep", "Activity"])
        elif risk_level == "MEDIUM":
            hrv = random.randint(46, 60)
            sleep_hours = random.uniform(5.5, 7.0)
            sleep_quality = random.uniform(0.4, 0.7)
            heart_rate = random.randint(75, 90)
            step_count = random.randint(3000, 6000)
            stress_level = random.uniform(0.4, 0.7)
            primary_factor = "Mixed"
        else:  # LOW
            hrv = random.randint(61, 85)
            sleep_hours = random.uniform(7.0, 9.0)
            sleep_quality = random.uniform(0.7, 1.0)
            heart_rate = random.randint(60, 75)
            step_count = random.randint(6000, 12000)
            stress_level = random.uniform(0.1, 0.4)
            primary_factor = "None"
        
        # Create student record
        student = Student(
            student_id=student_id,
            anonymous_id=anonymous_id,
            wearable_type="test_mock",
            data_sharing_consent=True,
            consent_given_at=datetime.now()
        )
        session.add(student)
        students.append(student)
        
        # Create bio-signal record for today
        bio = BioSignalData(
            student_id=student_id,
            timestamp=datetime.now(),
            heart_rate=heart_rate,
            hrv_value=hrv,
            sleep_hours=sleep_hours,
            sleep_quality=sleep_quality,
            step_count=step_count,
            stress_level=stress_level
        )
        session.add(bio)
        
        # Create burnout risk record
        risk = BurnoutRisk(
            student_id=student_id,
            date=datetime.now(),
            risk_score=round(1 - (hrv / 100), 2) if risk_level == "HIGH" else round(random.uniform(0.2, 0.6), 2),
            risk_level=risk_level,
            primary_factors=primary_factor
        )
        session.add(risk)
        
        print(f"✅ Created {student_id}: {risk_level} risk | HRV={hrv}, Sleep={sleep_hours:.1f}h")
    
    session.commit()
    print(f"\n📊 Total students created: {len(students)}")
    return students

def send_high_risk_alerts():
    """Send email alerts for all HIGH risk students"""
    
    session = get_session()
    
    # Find all high risk students from today
    today = datetime.now().date()
    high_risks = session.query(BurnoutRisk).filter(
        BurnoutRisk.date >= today,
        BurnoutRisk.risk_level == "HIGH"
    ).all()
    
    if not high_risks:
        print("⚠️ No high risk students found today.")
        return
    
    # Initialize email sender (You need to set your credentials)
    # For Gmail, use App Password: https://myaccount.google.com/apppasswords
    email_sender = EmailSender(
        sender_email="deshantharaka422@gmail.com",  # Replace with your email
        sender_password="opec kwsd rfso ecdt"    # Replace with App Password
    )
    
    print(f"\n📧 Sending alerts for {len(high_risks)} high-risk students...")
    
    for risk in high_risks:
        # Get student info
        student = session.query(Student).filter(Student.student_id == risk.student_id).first()
        if student:
            success = email_sender.send_alert(
                to_email=ALERT_EMAIL,
                student_anonymous_id=student.anonymous_id,
                risk_score=risk.risk_score,
                primary_factor=risk.primary_factors
            )
            if success:
                print(f"   ✅ Alert sent for {student.anonymous_id}")
            else:
                print(f"   ❌ Failed to send for {student.anonymous_id}")
    
    session.close()

def run_test():
    
    print("="*60)
    print("🧪 TESTING 20 STUDENTS WITH EMAIL ALERTS")
    print("="*60)
    
    # Setup database
    print("\n📁 Setting up database...")
    setup_database()   # This comes from the import at the top
    
    # === SCHEMA FIX BLOCK ===
    try:
        from src.database.models import Base
        from src.database.database_setup import get_session
        
        # Get engine safely
        session = get_session()
        engine = session.get_bind()
        
        print("🔄 Updating database schema (dropping & recreating tables)...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema updated successfully!")
        
    except Exception as e:
        print(f"❌ Schema update failed: {e}")
        print("Trying to add columns manually...")
        
        try:
            from sqlalchemy import text
            from src.database.database_setup import get_session
            
            session = get_session()
            engine = session.get_bind()
            
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE students ADD COLUMN fitbit_token TEXT"))
                conn.execute(text("ALTER TABLE students ADD COLUMN google_fit_token TEXT"))
                conn.execute(text("ALTER TABLE students ADD COLUMN apple_health_token TEXT"))
                conn.execute(text("ALTER TABLE students ADD COLUMN token_updated_at DATETIME"))
                conn.execute(text("ALTER TABLE students ADD COLUMN last_sync_time DATETIME"))
                conn.execute(text("ALTER TABLE students ADD COLUMN sync_frequency INTEGER DEFAULT 3600"))
                conn.execute(text("ALTER TABLE students ADD COLUMN email_notifications BOOLEAN DEFAULT true"))
                conn.execute(text("ALTER TABLE students ADD COLUMN sms_notifications BOOLEAN DEFAULT false"))
                conn.execute(text("ALTER TABLE students ADD COLUMN notification_frequency TEXT DEFAULT 'daily'"))
                conn.commit()
            print("✅ Missing columns added using ALTER TABLE!")
            
        except Exception as e2:
            print(f"❌ Could not add columns: {e2}")
            print("💡 Recommendation: Delete the 'students.db' file and run again.")
    # ======================================
    
    # Generate 20 students
    print("\n👥 Generating 20 students with mock data...")
    students = generate_student_data()
    
    # Send email alerts
    print("\n📧 Sending email alerts...")
    send_high_risk_alerts()
    
    print("\n✅ Test complete!")
    print("\n📋 Next steps:")
    print("   1. Run your web app: python run.py")
    print("   2. Open browser: http://localhost:8000")


# After generating students, trigger email alerts
import requests
try:
    requests.post('http://localhost:8000/api/check-high-risk')
    print("📧 High-risk email alerts triggered.")
except:
    print("⚠️ Could not trigger email alerts (server not running?)")    

if __name__ == "__main__":
    run_test()