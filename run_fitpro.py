# run_fitpro.py
"""
FitPro Real-Time Data Collection - Main Runner
start this file to collect data from FitPro watch and save to database
"""

import sys
import os
import time

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_collection.fitpro_collector import FitProCollector
from src.database.database_setup import setup_database
from src.database.models import Student
from src.database.database_setup import get_session

def register_fitpro_student(student_id, watch_address, student_name="Test Student"):
    """
    Register a new FitPro student
    """
    session = get_session()
    
    # Check if student exists
    existing = session.query(Student).filter(Student.student_id == student_id).first()
    
    if existing:
        print(f"✅ Student {student_id} already exists")
        print(f"   Updating with FitPro watch: {watch_address}")
        existing.fitpro_watch_address = watch_address
        existing.wearable_type = 'fitpro'
    else:
        # Create new student
        new_student = Student(
            student_id=student_id,
            anonymous_id=f"ANON{hash(student_id) % 10000:04d}",
            wearable_type='fitpro',
            fitpro_watch_address=watch_address,
            data_sharing_consent=True,
            consent_given_at=datetime.now()
        )
        session.add(new_student)
        print(f"✅ New student registered: {student_id}")
    
    session.commit()
    session.close()

def main():
    print("="*60)
    print("🎓 FITPRO REAL-TIME DATA COLLECTION - WEEK 4")
    print("="*60)
    
    # ============================================
    # ⚠️ IMPORTANT: CONFIGURE YOUR FITPRO MAC ADDRESS BELOW!
    # ============================================
    
    FITPRO_MAC_ADDRESS = "XX:XX:XX:XX:XX:XX"  # ← Replace with your MAC!
    STUDENT_ID = "STU_FITPRO_001"
    
    print(f"\n📋 Configuration:")
    print(f"   Student ID: {STUDENT_ID}")
    print(f"   Watch MAC: {FITPRO_MAC_ADDRESS}")
    print(f"   Collection Interval: 60 seconds")
    
    # Check if MAC address is set
    if FITPRO_MAC_ADDRESS == "XX:XX:XX:XX:XX:XX":
        print("\n❌ ERROR: Please set your FitPro MAC address!")
        print("\n   How to find MAC address:")
        print("   1. Run: python find_fitpro.py")
        print("   2. Copy the MAC address")
        print("   3. Update FITPRO_MAC_ADDRESS in this file")
        return
    
    # Setup database
    print("\n📁 Setting up database...")
    setup_database()
    
    # Register student
    print("\n📝 Registering student...")
    register_fitpro_student(STUDENT_ID, FITPRO_MAC_ADDRESS)
    
    # Start data collection
    print("\n🔵 Starting data collection...")
    print("   Press Ctrl+C to stop\n")
    
    collector = FitProCollector(STUDENT_ID, FITPRO_MAC_ADDRESS)
    collector.start_collecting(interval_seconds=60)  # Data every 60 seconds
    
    try:
        # Keep running
        while True:
            time.sleep(1)
            
            # Print stats every 30 seconds
            if int(time.time()) % 30 == 0:
                stats = collector.get_statistics()
                print(f"\n📈 Stats: {stats['data_points']} records collected")
                
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping data collection...")
        collector.stop_collecting()
        print("✅ Done!")
        print(f"\n📊 Total data points collected: {collector.data_points_collected}")

if __name__ == "__main__":
    from datetime import datetime
    main()