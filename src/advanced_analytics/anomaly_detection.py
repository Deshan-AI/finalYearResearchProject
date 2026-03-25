# src/advanced_analytics/anomaly_detection.py
import numpy as np
from sklearn.ensemble import IsolationForest
from scipy import stats

class AnomalyDetector:
    """Detect anomalies in student data"""
    
    def __init__(self, contamination=0.1):
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42
        )
    
    def detect_anomalies_isolation_forest(self, data):
        """
        Detect anomalies using Isolation Forest
        """
        predictions = self.isolation_forest.fit_predict(data)
        # -1 for anomalies, 1 for normal
        anomalies = np.where(predictions == -1)[0].tolist()
        
        return {
            'anomaly_indices': anomalies,
            'anomaly_count': len(anomalies),
            'scores': self.isolation_forest.score_samples(data).tolist()
        }
    
    def detect_anomalies_zscore(self, data, threshold=3):
        """
        Detect anomalies using Z-score method
        """
        z_scores = np.abs(stats.zscore(data))
        anomalies = np.where(z_scores > threshold)[0].tolist()
        
        return {
            'anomaly_indices': anomalies,
            'anomaly_count': len(anomalies),
            'z_scores': z_scores.tolist()
        }
    
    def detect_sudden_changes(self, time_series, window=3, threshold=2):
        """
        Detect sudden changes in time series
        """
        changes = []
        
        for i in range(window, len(time_series)):
            recent_avg = np.mean(time_series[i-window:i])
            current = time_series[i]
            
            if current > recent_avg * threshold:
                changes.append({
                    'index': i,
                    'type': 'spike',
                    'value': current,
                    'baseline': recent_avg
                })
            elif current < recent_avg / threshold:
                changes.append({
                    'index': i,
                    'type': 'drop',
                    'value': current,
                    'baseline': recent_avg
                })
        
        return changes