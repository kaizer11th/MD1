import pandas as pd
import numpy as np
from datetime import datetime

class AdvancedWeatherAnalysis:
    """Advanced weather pattern analysis"""
    
    def __init__(self, historical_data_path):
        self.historical_data = pd.read_csv(historical_data_path)
    
    def analyze_trends(self, subdivision, years=10):
        """Analyze rainfall trends over years"""
        data = self.historical_data[
            self.historical_data['SUBDIVISION'] == subdivision
        ].sort_values('YEAR').tail(years)
        
        if data.empty:
            return None
        
        # Calculate trends
        annual_avg = data['ANNUAL'].mean()
        annual_std = data['ANNUAL'].std()
        
        # Seasonal patterns
        monsoon_avg = data['Jun-Sep'].mean()
        winter_avg = data['Oct-Dec'].mean()
        summer_avg = data['Mar-May'].mean()
        
        # Trend direction
        years_list = data['YEAR'].values
        rainfall_list = data['ANNUAL'].values
        
        if len(years_list) > 1:
            trend_slope = np.polyfit(years_list, rainfall_list, 1)[0]
        else:
            trend_slope = 0
        
        return {
            'annual_average': round(annual_avg, 2),
            'standard_deviation': round(annual_std, 2),
            'monsoon_average': round(monsoon_avg, 2),
            'trend': 'increasing' if trend_slope > 0 else 'decreasing',
            'trend_magnitude': abs(round(trend_slope, 2)),
            'variability': 'high' if annual_std > annual_avg * 0.2 else 'moderate'
        }
    
    def predict_drought_risk(self, subdivision, current_year):
        """Predict drought risk based on historical patterns"""
        data = self.historical_data[
            self.historical_data['SUBDIVISION'] == subdivision
        ]
        
        if data.empty:
            return {'risk': 'unknown', 'probability': 0}
        
        # Calculate percentiles
        annual_rainfall = data['ANNUAL'].values
        p25 = np.percentile(annual_rainfall, 25)
        
        recent_years = data[data['YEAR'] >= current_year - 5]['ANNUAL'].mean()
        
        if recent_years < p25:
            return {
                'risk': 'high',
                'probability': 0.7,
                'recommendation': 'Water conservation measures strongly advised'
            }
        elif recent_years < np.percentile(annual_rainfall, 40):
            return {
                'risk': 'moderate',
                'probability': 0.4,
                'recommendation': 'Monitor water levels closely'
            }
        else:
            return {
                'risk': 'low',
                'probability': 0.2,
                'recommendation': 'Normal water management practices'
            }
    
    def get_optimal_planting_window(self, subdivision):
        """Determine optimal planting windows"""
        data = self.historical_data[
            self.historical_data['SUBDIVISION'] == subdivision
        ].tail(10)
        
        if data.empty:
            return None
        
        # Analyze monthly patterns
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        
        monthly_avg = {}
        for month in months:
            if month in data.columns:
                monthly_avg[month] = data[month].mean()
        
        # Find optimal windows
        kharif_start = next((m for m in ['JUN', 'JUL'] if monthly_avg.get(m, 0) > 100), 'JUN')
        rabi_start = next((m for m in ['OCT', 'NOV'] if monthly_avg.get(m, 0) > 50), 'NOV')
        
        return {
            'kharif_window': f'{kharif_start} - SEP',
            'rabi_window': f'{rabi_start} - FEB',
            'zaid_window': 'MAR - JUN',
            'confidence': 0.8
        }
