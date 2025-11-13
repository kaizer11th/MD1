import requests
from datetime import datetime, timedelta

class WeatherIntegration:
    """Integrate external weather APIs for real-time data"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or "demo_key"  # Replace with actual API key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, lat, lon):
        """Get current weather for coordinates"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'],
                    'wind_speed': data['wind']['speed']
                }
            
            return None
            
        except Exception as e:
            print(f"Weather API error: {e}")
            return None
    
    def get_forecast(self, lat, lon, days=7):
        """Get weather forecast"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 3-hour intervals
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                forecast = []
                
                for item in data['list']:
                    forecast.append({
                        'datetime': item['dt_txt'],
                        'temperature': item['main']['temp'],
                        'humidity': item['main']['humidity'],
                        'rainfall': item.get('rain', {}).get('3h', 0),
                        'description': item['weather'][0]['description']
                    })
                
                return forecast
            
            return []
            
        except Exception as e:
            print(f"Forecast API error: {e}")
            return []
    
    def calculate_rainfall_prediction(self, lat, lon, months=3):
        """Predict rainfall for upcoming months"""
        forecast = self.get_forecast(lat, lon, days=7)
        
        if not forecast:
            return None
        
        total_rainfall = sum(item['rainfall'] for item in forecast)
        avg_per_day = total_rainfall / 7
        
        # Extrapolate for months (simplified)
        monthly_prediction = avg_per_day * 30
        
        return {
            'weekly_rainfall': round(total_rainfall, 2),
            'monthly_prediction': round(monthly_prediction, 2),
            'confidence': 0.7
        }
