# # src/auth/token_manager.py
# from cryptography.fernet import Fernet
# import json
# import os
# from datetime import datetime, timedelta
# from src.database.database_setup import get_session
# from src.database.models import Student
# import base64

# class TokenManager:
#     """Securely manage API tokens for wearables"""
    
#     def __init__(self):
#         # Generate or load encryption key
#         self.key_file = 'config/encryption.key'
#         self.key = self._load_or_create_key()
#         self.cipher = Fernet(self.key)
    
#     def _load_or_create_key(self):
#         """Load existing key or create new one"""
#         if os.path.exists(self.key_file):
#             with open(self.key_file, 'rb') as f:
#                 return f.read()
#         else:
#             key = Fernet.generate_key()
#             os.makedirs('config', exist_ok=True)
#             with open(self.key_file, 'wb') as f:
#                 f.write(key)
#             return key
    
#     def encrypt_token(self, token_data):
#         """Encrypt token data"""
#         token_json = json.dumps(token_data)
#         encrypted = self.cipher.encrypt(token_json.encode())
#         return base64.urlsafe_b64encode(encrypted).decode()
    
#     def decrypt_token(self, encrypted_token):
#         """Decrypt token data"""
#         try:
#             encrypted = base64.urlsafe_b64decode(encrypted_token.encode())
#             decrypted = self.cipher.decrypt(encrypted)
#             return json.loads(decrypted.decode())
#         except Exception as e:
#             print(f"Token decryption failed: {e}")
#             return None
    
#     def store_student_token(self, student_id, provider, token_data):
#         """Store encrypted token for student"""
#         session = get_session()
        
#         # Encrypt token
#         encrypted_token = self.encrypt_token({
#             'provider': provider,
#             'token': token_data,
#             'created_at': datetime.now().isoformat()
#         })
        
#         # Update student record
#         student = session.query(Student).filter(
#             Student.student_id == student_id
#         ).first()
        
#         if student:
#             if provider == 'fitbit':
#                 student.fitbit_token = encrypted_token
#             elif provider == 'google':
#                 student.google_fit_token = encrypted_token
#             elif provider == 'apple':
#                 student.apple_health_token = encrypted_token
            
#             student.token_updated_at = datetime.now()
#             session.commit()
#             return True
        
#         return False
    
#     def get_student_token(self, student_id, provider):
#         """Get decrypted token for student"""
#         session = get_session()
        
#         student = session.query(Student).filter(
#             Student.student_id == student_id
#         ).first()
        
#         if not student:
#             return None
        
#         # Get encrypted token
#         if provider == 'fitbit':
#             encrypted = student.fitbit_token
#         elif provider == 'google':
#             encrypted = student.google_fit_token
#         elif provider == 'apple':
#             encrypted = student.apple_health_token
#         else:
#             return None
        
#         if not encrypted:
#             return None
        
#         # Decrypt token
#         token_data = self.decrypt_token(encrypted)
#         if token_data:
#             return token_data['token']
        
#         return None
    
#     def refresh_token(self, student_id, provider):
#         """Refresh expired token"""
#         # This would call the provider's refresh token endpoint
#         # Implementation depends on each provider
#         pass