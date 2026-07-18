# # src/data_collection/google_fit_api.py
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# from datetime import datetime, timedelta
# import pandas as pd
# from src.auth.token_manager import TokenManager
# import logging

# class GoogleFitAPI:
#     """Google Fit wearable API integration"""
    
#     def __init__(self):
#         self.token_manager = TokenManager()
#         self.logger = logging.getLogger(__name__)
#         self.service = None
    
#     def _build_service(self, student_id):
#         """Build Google Fit service"""
#         token_data = self.token_manager.get_student_token(student_id, 'google')
#         if not token_data:
#             return None
        
#         credentials = Credentials(
#             token=token_data.get('access_token'),
#             refresh_token=token_data.get('refresh_token'),
#             token_uri='https://oauth2.googleapis.com/token',
#             client_id='YOUR_CLIENT_ID',
#             client_secret='YOUR_CLIENT_SECRET'
#         )
        
#         self.service = build('fitness', 'v1', credentials=credentials)
#         return self.service
    
#     def get_heart_rate_data(self, student_id, date=None):
#         """Get heart rate data from Google Fit"""
#         service = self._build_service(student_id)
#         if not service:
#             return None
        
#         if date is None:
#             date = datetime.now()
#         else:
#             date = datetime.strptime(date, '%Y-%m-%d')
        
#         # Set time range for the day
#         start_time = int(date.replace(hour=0, minute=0, second=0).timestamp() * 1000)
#         end_time = int(date.replace(hour=23, minute=59, second=59).timestamp() * 1000)
        
#         try:
#             # Query heart rate data
#             dataset = service.users().dataSources().datasets().get(
#                 userId='me',
#                 dataSourceId='derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm',
#                 datasetId=f'{start_time}-{end_time}'
#             ).execute()
            
#             return self._process_heart_rate(dataset)
            
#         except Exception as e:
#             self.logger.error(f"Google Fit API error: {e}")
#             return None
    
#     def get_sleep_data(self, student_id, date=None):
#         """Get sleep data from Google Fit"""
#         service = self._build_service(student_id)
#         if not service:
#             return None
        
#         if date is None:
#             date = datetime.now()
        
#         # Sleep data typically from previous night
#         start_time = int((date - timedelta(days=1)).replace(hour=20, minute=0).timestamp() * 1000)
#         end_time = int(date.replace(hour=10, minute=0).timestamp() * 1000)
        
#         try:
#             # Query sleep data
#             dataset = service.users().dataSources().datasets().get(
#                 userId='me',
#                 dataSourceId='derived:com.google.sleep.segment:com.google.android.gms:merged',
#                 datasetId=f'{start_time}-{end_time}'
#             ).execute()
            
#             return self._process_sleep(dataset)
            
#         except Exception as e:
#             self.logger.error(f"Google Fit sleep API error: {e}")
#             return None
    
#     def _process_heart_rate(self, dataset):
#         """Process Google Fit heart rate data"""
#         points = dataset.get('point', [])
        
#         if not points:
#             return {}
        
#         # Calculate average HR
#         heart_rates = []
#         for point in points:
#             for value in point.get('value', []):
#                 if 'fpVal' in value:
#                     heart_rates.append(value['fpVal'])
        
#         if heart_rates:
#             avg_hr = sum(heart_rates) / len(heart_rates)
#             return {
#                 'heart_rate': avg_hr,
#                 'hrv_estimated': self._estimate_hrv(heart_rates)
#             }
        
#         return {}
    
#     def _process_sleep(self, dataset):
#         """Process Google Fit sleep data"""
#         points = dataset.get('point', [])
        
#         if not points:
#             return {}
        
#         total_sleep = 0
#         for point in points:
#             start = int(point.get('startTimeNanos', 0)) / 1e9
#             end = int(point.get('endTimeNanos', 0)) / 1e9
#             duration = (end - start) / 3600  # hours
#             total_sleep += duration
        
#         return {
#             'sleep_hours': total_sleep,
#             'sleep_quality': min(total_sleep / 8, 1.0)
#         }
    
#     def _estimate_hrv(self, heart_rates):
#         """Estimate HRV from heart rate data"""
#         # Simple estimation - lower HRV when HR is variable
#         hr_std = pd.Series(heart_rates).std()
#         # Rough HRV estimation
#         return max(30, 60 - hr_std * 2)