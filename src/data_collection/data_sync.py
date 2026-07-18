# # src/data_collection/data_sync.py
# from datetime import datetime, timedelta
# import time
# import threading
# from src.database.database_setup import get_session
# from src.database.models import Student, BioSignalData
# from src.data_collection.fitbit_api import FitbitAPI
# from src.data_collection.google_fit_api import GoogleFitAPI
# from src.data_collection.apple_health_api import AppleHealthAPI
# from src.bio_processing.hrv_analysis import HRVAnalyzer
# from src.bio_processing.sleep_analysis import SleepAnalyzer
# import logging

# class DataSyncManager:
#     """Manage data synchronization from multiple wearables"""
    
#     def __init__(self):
#         self.fitbit_api = FitbitAPI()
#         self.google_fit_api = GoogleFitAPI()
#         self.apple_health_api = AppleHealthAPI()
#         self.session = get_session()
#         self.logger = logging.getLogger(__name__)
#         self.is_syncing = False
        
#         # API mapping
#         self.api_map = {
#             'fitbit': self.fitbit_api,
#             'google': self.google_fit_api,
#             'apple': self.apple_health_api
#         }
    
#     def sync_all_students(self):
#         """Sync data for all active students"""
#         self.is_syncing = True
#         self.logger.info("Starting data sync for all students")
        
#         students = self.session.query(Student).all()
        
#         for student in students:
#             try:
#                 self.sync_student_data(student)
#                 time.sleep(2)  # Rate limiting
#             except Exception as e:
#                 self.logger.error(f"Error syncing student {student.student_id}: {e}")
        
#         self.is_syncing = False
#         self.logger.info("Data sync completed")
    
#     def sync_student_data(self, student):
#         """Sync data for a single student"""
#         self.logger.info(f"Syncing data for student {student.anonymous_id}")
        
#         collected_data = {}
        
#         # Try each wearable type
#         if student.wearable_type == 'fitbit' or student.wearable_type == 'all':
#             fitbit_data = self.fitbit_api.collect_all_data(student.student_id)
#             if fitbit_data:
#                 collected_data.update(fitbit_data)
        
#         if student.wearable_type == 'google' or student.wearable_type == 'all':
#             google_data = self.google_fit_api.get_heart_rate_data(student.student_id)
#             if google_data:
#                 collected_data.update(google_data)
        
#         if student.wearable_type == 'apple' or student.wearable_type == 'all':
#             apple_data = self.apple_health_api.get_heart_rate_data(student.student_id)
#             if apple_data:
#                 collected_data.update(apple_data)
        
#         # Save to database
#         if collected_data:
#             self.save_to_database(student, collected_data)
    
#     def save_to_database(self, student, data):
#         """Save collected data to database"""
        
#         # Create bio-signal record
#         bio_record = BioSignalData(
#             student_id=student.student_id,
#             timestamp=datetime.now(),
#             heart_rate=data.get('heart_rate', 70),
#             hrv_value=data.get('hrv_value', data.get('hrv_estimated', 50)),
#             sleep_hours=data.get('sleep_hours', 7),
#             sleep_quality=data.get('sleep_quality', data.get('sleep_efficiency', 0.7)),
#             step_count=data.get('step_count', 5000),
#             stress_level=self._estimate_stress(data)
#         )
        
#         self.session.add(bio_record)
#         self.session.commit()
        
#         self.logger.info(f"Data saved for student {student.anonymous_id}")
    
#     def _estimate_stress(self, data):
#         """Estimate stress level from collected data"""
#         stress_factors = []
        
#         # HRV based stress
#         hrv = data.get('hrv_value', 50)
#         if hrv < 40:
#             stress_factors.append(0.3)
#         elif hrv < 50:
#             stress_factors.append(0.2)
        
#         # Sleep based stress
#         sleep = data.get('sleep_hours', 7)
#         if sleep < 5:
#             stress_factors.append(0.4)
#         elif sleep < 6:
#             stress_factors.append(0.2)
        
#         # Activity based stress
#         steps = data.get('step_count', 5000)
#         if steps < 3000:
#             stress_factors.append(0.2)
        
#         if stress_factors:
#             return min(0.9, sum(stress_factors))
#         return 0.3
    
#     def start_auto_sync(self, interval_hours=1):
#         """Start automatic syncing at regular intervals"""
        
#         def sync_loop():
#             while True:
#                 self.sync_all_students()
#                 time.sleep(interval_hours * 3600)
        
#         thread = threading.Thread(target=sync_loop)
#         thread.daemon = True
#         thread.start()
        
#         self.logger.info(f"Auto-sync started (interval: {interval_hours} hours)")