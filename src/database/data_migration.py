# # src/database/data_migration.py
# from src.database.database_setup import get_session, setup_database
# from src.database.models import Student, BioSignalData
# from datetime import datetime
# import pandas as pd

# class DataMigration:
#     """Migrate existing mock data to real database format"""
    
#     def __init__(self):
#         self.session = get_session()
    
#     def migrate_mock_to_real(self):
#         """Convert mock data to real data format"""
        
#         # Get all existing students
#         students = self.session.query(Student).all()
        
#         for student in students:
#             # Update student format
#             if not student.anonymous_id:
#                 student.anonymous_id = f"ANON{hash(student.student_id) % 10000:04d}"
            
#             # Set default values
#             if not student.wearable_type:
#                 student.wearable_type = 'fitbit'
            
#             if not student.data_sharing_consent:
#                 student.data_sharing_consent = True
#                 student.consent_given_at = datetime.now()
        
#         self.session.commit()
#         print(f"✅ Migrated {len(students)} students")
    
#     def export_to_csv(self, filename='data/real_data/student_data.csv'):
#         """Export database to CSV for analysis"""
        
#         # Get all bio-signal data
#         data = self.session.query(BioSignalData).all()
        
#         # Convert to DataFrame
#         df = pd.DataFrame([
#             {
#                 'student_id': d.student_id,
#                 'timestamp': d.timestamp,
#                 'heart_rate': d.heart_rate,
#                 'hrv_value': d.hrv_value,
#                 'sleep_hours': d.sleep_hours,
#                 'sleep_quality': d.sleep_quality,
#                 'step_count': d.step_count,
#                 'stress_level': d.stress_level
#             }
#             for d in data
#         ])
        
#         # Save to CSV
#         df.to_csv(filename, index=False)
#         print(f"✅ Exported {len(df)} records to {filename}")
        
#         return df