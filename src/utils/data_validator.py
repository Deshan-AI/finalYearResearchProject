# # src/utils/data_validator.py
# import pandas as pd
# import numpy as np
# from datetime import datetime

# class DataValidator:
#     """Validate incoming wearable data"""
    
#     def __init__(self):
#         self.validation_rules = {
#             'heart_rate': (40, 200),  # min, max
#             'hrv_value': (20, 150),
#             'sleep_hours': (0, 24),
#             'sleep_quality': (0, 1),
#             'step_count': (0, 50000),
#             'stress_level': (0, 1)
#         }
    
#     def validate_record(self, record):
#         """Validate a single data record"""
#         errors = []
#         warnings = []
        
#         for field, (min_val, max_val) in self.validation_rules.items():
#             if field in record:
#                 value = record[field]
#                 if value < min_val or value > max_val:
#                     errors.append(f"{field} out of range: {value}")
        
#         # Check for missing required fields
#         required_fields = ['student_id', 'timestamp']
#         for field in required_fields:
#             if field not in record:
#                 errors.append(f"Missing required field: {field}")
        
#         # Check timestamp
#         if 'timestamp' in record:
#             if isinstance(record['timestamp'], datetime):
#                 age = (datetime.now() - record['timestamp']).days
#                 if age > 7:
#                     warnings.append(f"Data is {age} days old")
        
#         return {
#             'valid': len(errors) == 0,
#             'errors': errors,
#             'warnings': warnings
#         }
    
#     def clean_data(self, df):
#         """Clean and normalize dataframe"""
#         df_clean = df.copy()
        
#         # Remove duplicates
#         df_clean = df_clean.drop_duplicates()
        
#         # Handle missing values
#         for col in df_clean.columns:
#             if col in self.validation_rules:
#                 median_val = df_clean[col].median()
#                 df_clean[col] = df_clean[col].fillna(median_val)
        
#         # Remove outliers
#         for col in df_clean.columns:
#             if col in self.validation_rules:
#                 min_val, max_val = self.validation_rules[col]
#                 df_clean = df_clean[
#                     (df_clean[col] >= min_val) & 
#                     (df_clean[col] <= max_val)
#                 ]
        
#         return df_clean