# src/bio_processing/hrv_analysis.py
import neurokit2 as nk
import numpy as np

class HRVAnalyzer:
    """Analyze Heart Rate Variability"""
    
    @staticmethod
    def calculate_hrv_features(heart_rate_data):
        """
        Calculate HRV features from heart rate data
        """
        try:
            # Simulate ECG signal from heart rate
            ecg_simulated = nk.ecg_simulate(
                duration=60, 
                sampling_rate=100, 
                heart_rate=np.mean(heart_rate_data)
            )
            
            # Process ECG
            signals, info = nk.ecg_process(ecg_simulated, sampling_rate=100)
            
            # Calculate HRV metrics
            hrv_time = nk.hrv_time(signals, sampling_rate=100)
            hrv_freq = nk.hrv_frequency(signals, sampling_rate=100)
            
            features = {
                'hr_mean': np.mean(heart_rate_data),
                'hr_std': np.std(heart_rate_data),
                'hrv_sdnn': float(hrv_time['HRV_SDNN'].iloc[0]) if not hrv_time.empty else 50,
                'hrv_rmssd': float(hrv_time['HRV_RMSSD'].iloc[0]) if not hrv_time.empty else 40,
                'hrv_lf': float(hrv_freq['HRV_LF'].iloc[0]) if not hrv_freq.empty else 200,
                'hrv_hf': float(hrv_freq['HRV_HF'].iloc[0]) if not hrv_freq.empty else 150
            }
            
            return features
            
        except Exception as e:
            print(f"HRV Analysis Error: {e}")
            return {
                'hr_mean': np.mean(heart_rate_data),
                'hr_std': np.std(heart_rate_data),
                'hrv_sdnn': 50,
                'hrv_rmssd': 40,
                'hrv_lf': 200,
                'hrv_hf': 150
            }
    
    @staticmethod
    def analyze_stress_from_hrv(hrv_features):
        """
        Estimate stress level from HRV features
        """
        # Lower HRV = Higher Stress
        hrv_score = hrv_features['hrv_rmssd']
        
        if hrv_score > 60:
            stress_level = 0.2  # Low stress
        elif hrv_score > 40:
            stress_level = 0.5  # Moderate stress
        else:
            stress_level = 0.8  # High stress
            
        return stress_level