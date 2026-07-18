# # src/data_collection/fitbit_api.py
# import requests
# from datetime import datetime, timedelta
# import time
# from src.auth.token_manager import TokenManager
# from src.database.database_setup import get_session
# from src.database.models import BioSignalData, Student
# import logging

# class FitbitAPI:
#     """Fitbit wearable API integration"""
    
#     def __init__(self):
#         self.base_url = "https://api.fitbit.com/1/user/-"
#         self.token_manager = TokenManager()
#         self.session = get_session()
#         self.logger = logging.getLogger(__name__)
    
#     def get_heart_rate_data(self, student_id, date=None):
#         """Get heart rate data from Fitbit"""
#         if date is None:
#             date = datetime.now().strftime('%Y-%m-%d')
        
#         token = self.token_manager.get_student_token(student_id, 'fitbit')
#         if not token:
#             self.logger.error(f"No Fitbit token for student {student_id}")
#             return None
        
#         headers = {
#             'Authorization': f'Bearer {token}',
#             'Accept-Language': 'en_US'
#         }
        
#         # Get heart rate data
#         url = f"{self.base_url}/activities/heart/date/{date}/1d.json"
        
#         try:
#             response = requests.get(url, headers=headers)
            
#             if response.status_code == 200:
#                 data = response.json()
#                 return self._process_heart_rate(data)
#             elif response.status_code == 429:
#                 # Rate limited
#                 time.sleep(60)
#                 return self.get_heart_rate_data(student_id, date)
#             else:
#                 self.logger.error(f"Fitbit API error: {response.status_code}")
#                 return None
                
#         except Exception as e:
#             self.logger.error(f"Fitbit API exception: {e}")
#             return None
    
#     def get_sleep_data(self, student_id, date=None):
#         """Get sleep data from Fitbit"""
#         if date is None:
#             date = datetime.now().strftime('%Y-%m-%d')
        
#         token = self.token_manager.get_student_token(student_id, 'fitbit')
#         if not token:
#             return None
        
#         headers = {'Authorization': f'Bearer {token}'}
        
#         # Get sleep data
#         url = f"{self.base_url}/sleep/date/{date}.json"
        
#         try:
#             response = requests.get(url, headers=headers)
            
#             if response.status_code == 200:
#                 data = response.json()
#                 return self._process_sleep(data)
#             else:
#                 return None
                
#         except Exception as e:
#             self.logger.error(f"Fitbit sleep API error: {e}")
#             return None
    
#     def get_activity_data(self, student_id, date=None):
#         """Get activity data from Fitbit"""
#         if date is None:
#             date = datetime.now().strftime('%Y-%m-%d')
        
#         token = self.token_manager.get_student_token(student_id, 'fitbit')
#         if not token:
#             return None
        
#         headers = {'Authorization': f'Bearer {token}'}
        
#         # Get activity data
#         url = f"{self.base_url}/activities/date/{date}.json"
        
#         try:
#             response = requests.get(url, headers=headers)
            
#             if response.status_code == 200:
#                 data = response.json()
#                 return self._process_activity(data)
#             else:
#                 return None
                
#         except Exception as e:
#             self.logger.error(f"Fitbit activity API error: {e}")
#             return None
    
#     def collect_all_data(self, student_id, date=None):
#         """Collect all data types for a student"""
#         heart_data = self.get_heart_rate_data(student_id, date)
#         sleep_data = self.get_sleep_data(student_id, date)
#         activity_data = self.get_activity_data(student_id, date)
        
#         # Combine data
#         combined = {
#             'student_id': student_id,
#             'timestamp': datetime.now(),
#             'date': date or datetime.now().strftime('%Y-%m-%d')
#         }
        
#         if heart_data:
#             combined.update(heart_data)
#         if sleep_data:
#             combined.update(sleep_data)
#         if activity_data:
#             combined.update(activity_data)
        
#         return combined
    
#     def _process_heart_rate(self, data):
#         """Process heart rate data"""
#         try:
#             heart_data = data.get('activities-heart', [{}])[0]
#             heart_rate_zones = heart_data.get('value', {}).get('heartRateZones', [])
            
#             # Calculate average HRV (simplified)
#             # Real HRV would require intraday data
#             result = {
#                 'heart_rate': heart_data.get('value', {}).get('restingHeartRate', 70),
#                 'heart_rate_zones': heart_rate_zones
#             }
            
#             return result
#         except:
#             return {}
    
#     def _process_sleep(self, data):
#         """Process sleep data"""
#         try:
#             sleep_data = data.get('sleep', [{}])[0]
            
#             result = {
#                 'sleep_hours': sleep_data.get('minutesAsleep', 0) / 60,
#                 'sleep_efficiency': sleep_data.get('efficiency', 0) / 100,
#                 'sleep_start': sleep_data.get('startTime'),
#                 'sleep_end': sleep_data.get('endTime')
#             }
            
#             return result
#         except:
#             return {}
    
#     def _process_activity(self, data):
#         """Process activity data"""
#         try:
#             summary = data.get('summary', {})
            
#             result = {
#                 'step_count': summary.get('steps', 0),
#                 'active_minutes': summary.get('fairlyActiveMinutes', 0) + summary.get('veryActiveMinutes', 0),
#                 'calories': summary.get('caloriesOut', 0),
#                 'distance': summary.get('distances', [{}])[0].get('distance', 0)
#             }
            
#             return result
#         except:
#             return {}