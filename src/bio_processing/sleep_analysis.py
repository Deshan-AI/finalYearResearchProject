# src/bio_processing/sleep_analysis.py
import numpy as np

class SleepAnalyzer:
    """Analyze sleep patterns"""
    
    @staticmethod
    def analyze_sleep_quality(sleep_hours, sleep_efficiency):
        """
        Calculate sleep quality score
        """
        # Normalize sleep hours (7-9 hours optimal)
        if sleep_hours >= 7 and sleep_hours <= 9:
            hours_score = 1.0
        elif sleep_hours >= 6 and sleep_hours < 7:
            hours_score = 0.7
        elif sleep_hours > 9 and sleep_hours <= 10:
            hours_score = 0.8
        else:
            hours_score = 0.3
        
        # Combine with sleep efficiency
        quality_score = (hours_score * 0.6) + (sleep_efficiency * 0.4)
        
        return {
            'sleep_hours': sleep_hours,
            'sleep_efficiency': sleep_efficiency,
            'quality_score': quality_score,
            'recommendation': SleepAnalyzer.get_sleep_recommendation(quality_score)
        }
    
    @staticmethod
    def get_sleep_recommendation(quality_score):
        """Get recommendation based on sleep quality"""
        if quality_score >= 0.8:
            return "Excellent sleep pattern"
        elif quality_score >= 0.6:
            return "Good sleep, maintain routine"
        elif quality_score >= 0.4:
            return "Consider improving sleep habits"
        else:
            return "Poor sleep - seek advice if persistent"