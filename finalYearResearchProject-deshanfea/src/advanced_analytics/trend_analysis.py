# src/advanced_analytics/trend_analysis.py
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression

class TrendAnalyzer:
    """Analyze trends in student bio-signals"""
    
    def __init__(self):
        self.trends = {}
    
    def analyze_trend(self, data_series, window=7):
        """
        Analyze trend in time series data
        data_series: list of (timestamp, value)
        """
        if len(data_series) < 3:
            return {'trend': 'insufficient_data', 'slope': 0}
        
        # Convert to numpy array
        timestamps = np.array([(t - data_series[0][0]).total_seconds() 
                               for t, _ in data_series]).reshape(-1, 1)
        values = np.array([v for _, v in data_series])
        
        # Fit linear regression
        model = LinearRegression()
        model.fit(timestamps, values)
        
        slope = model.coef_[0]
        
        # Determine trend direction
        if slope > 0.1:
            trend = 'increasing'
        elif slope < -0.1:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        # Calculate moving average
        if len(values) >= window:
            ma = pd.Series(values).rolling(window=window).mean().iloc[-1]
        else:
            ma = values[-1]
        
        # Detect anomalies (simple Z-score)
        z_scores = np.abs(stats.zscore(values))
        anomalies = np.where(z_scores > 2)[0].tolist()
        
        return {
            'trend': trend,
            'slope': slope,
            'moving_average': ma,
            'current_value': values[-1],
            'anomalies': anomalies,
            'volatility': np.std(values)
        }
    
    def predict_next_value(self, data_series, days_ahead=3):
        """Predict future values based on trend"""
        if len(data_series) < 5:
            return None
        
        timestamps = np.array([i for i in range(len(data_series))]).reshape(-1, 1)
        values = np.array([v for _, v in data_series])
        
        model = LinearRegression()
        model.fit(timestamps, values)
        
        next_timestamps = np.array([[len(data_series) + i] 
                                     for i in range(days_ahead)])
        predictions = model.predict(next_timestamps)
        
        return predictions.tolist()