# src/bio_processing/burnout_calculator.py
import numpy as np
from src.utils.config import Config

class BurnoutCalculator:
    """Calculate burnout risk from multiple factors"""
    
    @staticmethod
    def calculate_burnout_risk(hrv_data, sleep_data, activity_level):
        """
        Calculate overall burnout risk score (0-1)
        """
        # HRV Component (40% weight)
        hrv_score = max(0, min(1, hrv_data['hrv_rmssd'] / 100))
        hrv_component = (1 - hrv_score) * 0.4  # Lower HRV = higher risk
        
        # Sleep Component (35% weight)
        sleep_score = sleep_data['quality_score']
        sleep_component = (1 - sleep_score) * 0.35
        
        # Activity Component (25% weight)
        activity_score = min(1, activity_level / 10000)
        activity_component = (1 - activity_score) * 0.25
        
        # Total Risk Score
        total_risk = hrv_component + sleep_component + activity_component
        
        # Determine Risk Level
        risk_level = BurnoutCalculator.get_risk_level(total_risk)
        
        return {
            'risk_score': round(total_risk, 3),
            'risk_level': risk_level,
            'components': {
                'hrv': round(hrv_component, 3),
                'sleep': round(sleep_component, 3),
                'activity': round(activity_component, 3)
            },
            'primary_factor': BurnoutCalculator.get_primary_factor(
                hrv_component, sleep_component, activity_component
            )
        }
    
    @staticmethod
    def get_risk_level(score):
        """Convert score to risk level"""
        if score < Config.RISK_LEVELS['LOW']:
            return "LOW"
        elif score < Config.RISK_LEVELS['MEDIUM']:
            return "MEDIUM"
        else:
            return "HIGH"
    
    @staticmethod
    def get_primary_factor(hrv, sleep, activity):
        """Identify primary contributing factor"""
        factors = {'HRV': hrv, 'Sleep': sleep, 'Activity': activity}
        return max(factors, key=factors.get)