# main.py
from src.database.database_setup import setup_database, get_session
from src.database.models import Student, BioSignalData, BurnoutRisk
from src.data_collection.mock_data import MockDataGenerator
from src.bio_processing.hrv_analysis import HRVAnalyzer
from src.bio_processing.sleep_analysis import SleepAnalyzer
from src.bio_processing.burnout_calculator import BurnoutCalculator
import pandas as pd
from datetime import datetime

def main():
    print("=== Student Burnout Detection System ===")
    
    # 1. Setup Database
    print("\n1. Setting up database...")
    engine = setup_database()
    session = get_session()
    
    # 2. Create Test Students
    print("\n2. Creating test students...")
    test_students = MockDataGenerator.create_test_students(3)
    
    for student_data in test_students:
        student = Student(**student_data)
        session.add(student)
        print(f"   Created: {student.student_id} ({student.anonymous_id})")
    
    session.commit()
    
    # 3. Generate and Analyze Sample Data
    print("\n3. Generating and analyzing sample data...")
    
    for student in test_students:
        student_id = student['student_id']
        
        # Generate mock data
        mock_df = MockDataGenerator.generate_student_data(student_id, days=5)
        
        # Process each day's data
        for _, row in mock_df.iterrows():
            # Analyze HRV
            heart_rate_samples = [row['heart_rate']] * 100  # Simulate samples
            hrv_features = HRVAnalyzer.calculate_hrv_features(heart_rate_samples)
            
            # Analyze Sleep
            sleep_analysis = SleepAnalyzer.analyze_sleep_quality(
                row['sleep_hours'], 
                row['sleep_quality']
            )
            
            # Calculate Burnout Risk
            burnout_risk = BurnoutCalculator.calculate_burnout_risk(
                hrv_features, 
                sleep_analysis, 
                row['step_count']
            )
            
            # Save to database
            bio_data = BioSignalData(
                student_id=student_id,
                timestamp=row['timestamp'],
                heart_rate=row['heart_rate'],
                hrv_value=hrv_features['hrv_rmssd'],
                sleep_hours=row['sleep_hours'],
                sleep_quality=row['sleep_quality'],
                step_count=row['step_count'],
                stress_level=row['stress_level']
            )
            
            risk_record = BurnoutRisk(
                student_id=student_id,
                date=row['timestamp'],
                risk_score=burnout_risk['risk_score'],
                risk_level=burnout_risk['risk_level'],
                primary_factors=burnout_risk['primary_factor']
            )
            
            session.add(bio_data)
            session.add(risk_record)
            
            print(f"   {student_id}: {burnout_risk['risk_level']} risk "
                  f"({burnout_risk['risk_score']:.2f})")
    
    session.commit()
    
    # 4. Display Results
    print("\n4. Summary of Burnout Risk Analysis:")
    print("=" * 50)
    
    risks = session.query(BurnoutRisk).all()
    for risk in risks:
        print(f"Student: {risk.student_id:<8} "
              f"Risk: {risk.risk_level:<8} "
              f"Score: {risk.risk_score:.2f} "
              f"Factors: {risk.primary_factors}")
    
    print("\n" + "=" * 50)
    print("First week implementation completed successfully!")
    print(f"Total records created: {len(risks)}")
    
    session.close()

if __name__ == "__main__":
    main()