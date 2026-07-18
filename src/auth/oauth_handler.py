# # src/auth/oauth_handler.py
# from fastapi import HTTPException
# from authlib.integrations.starlette_client import OAuth
# from starlette.config import Config
# from src.database.database_setup import get_session
# from src.database.models import Student
# import secrets
# import json
# from datetime import datetime, timedelta

# class OAuthHandler:
#     """Handle OAuth authentication for wearable devices"""
    
#     def __init__(self):
#         self.oauth = OAuth()
#         self.sessions = {}
        
#         # Configure Fitbit OAuth
#         self.oauth.register(
#             name='fitbit',
#             client_id='YOUR_FITBIT_CLIENT_ID',
#             client_secret='YOUR_FITBIT_CLIENT_SECRET',
#             access_token_url='https://api.fitbit.com/oauth2/token',
#             authorize_url='https://www.fitbit.com/oauth2/authorize',
#             api_base_url='https://api.fitbit.com/1',
#             client_kwargs={
#                 'scope': 'heartrate sleep activity profile',
#                 'token_endpoint_auth_method': 'client_secret_post'
#             }
#         )
        
#         # Configure Google Fit OAuth
#         self.oauth.register(
#             name='google',
#             client_id='YOUR_GOOGLE_CLIENT_ID',
#             client_secret='YOUR_GOOGLE_CLIENT_SECRET',
#             access_token_url='https://oauth2.googleapis.com/token',
#             authorize_url='https://accounts.google.com/o/oauth2/auth',
#             api_base_url='https://www.googleapis.com/fitness/v1',
#             client_kwargs={
#                 'scope': 'https://www.googleapis.com/auth/fitness.activity.read https://www.googleapis.com/auth/fitness.heart_rate.read https://www.googleapis.com/auth/fitness.sleep.read'
#             }
#         )
    
#     def generate_state_token(self, student_id):
#         """Generate state token for OAuth flow"""
#         token = secrets.token_urlsafe(32)
#         self.sessions[token] = {
#             'student_id': student_id,
#             'created_at': datetime.now(),
#             'expires_at': datetime.now() + timedelta(minutes=10)
#         }
#         return token
    
#     def verify_state_token(self, token):
#         """Verify state token"""
#         if token not in self.sessions:
#             return None
        
#         session = self.sessions[token]
#         if datetime.now() > session['expires_at']:
#             del self.sessions[token]
#             return None
        
#         student_id = session['student_id']
#         del self.sessions[token]
#         return student_id
    
#     def get_authorization_url(self, provider, student_id):
#         """Get authorization URL for wearable provider"""
#         state = self.generate_state_token(student_id)
        
#         if provider == 'fitbit':
#             return self.oauth.fitbit.authorize_redirect(
#                 redirect_uri='http://localhost:8000/auth/fitbit/callback',
#                 state=state
#             )
#         elif provider == 'google':
#             return self.oauth.google.authorize_redirect(
#                 redirect_uri='http://localhost:8000/auth/google/callback',
#                 state=state
#             )
#         else:
#             raise HTTPException(status_code=400, detail="Unsupported provider")