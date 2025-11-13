import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class CropPredictor:
    """Predict suitable crops based on conditions"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.crop_data = data_loader.get_crop_data()
        self._train_model()
    
    def _train_model(self):
        """Train crop recommendation model"""
        # Prepare features and labels
        features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        X = self.crop_data[features]
        y = self.crop_data['label']
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=20
        )
        self.model.fit(X_scaled, y)
        
        print(f"✅ Crop predictor trained with {len(self.crop_data)} samples")
    
    def recommend_crops(self, district_data, soil_type='loamy', season='kharif', top_n=5):
        """Recommend top N crops for given conditions"""
        
        # Extract rainfall based on season
        if season == 'kharif':
            rainfall = district_data['Jun-Sep']
        elif season == 'rabi':
            rainfall = district_data['Oct-Dec'] + district_data['Jan-Feb']
        else:  # zaid
            rainfall = district_data['Mar-May']
        
        # Estimated parameters based on soil type
        soil_params = self._get_soil_parameters(soil_type)
        
        # Create feature vector
        features = pd.DataFrame([{
            'N': soil_params['N'],
            'P': soil_params['P'],
            'K': soil_params['K'],
            'temperature': 25,  # Average temperature
            'humidity': 75,     # Average humidity
            'ph': soil_params['ph'],
            'rainfall': rainfall / 4  # Monthly average
        }])
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Get probabilities for all crops
        probabilities = self.model.predict_proba(features_scaled)[0]
        crop_names = self.model.classes_
        
        # Get top N recommendations
        top_indices = np.argsort(probabilities)[-top_n:][::-1]
        
        recommendations = []
        for idx in top_indices:
            crop_req = self.data_loader.get_crop_requirements(crop_names[idx])
            
            # Convert all numpy types to Python native types for JSON serialization
            recommendations.append({
                'crop': str(crop_names[idx]),
                'suitability_score': float(probabilities[idx]),
                'requirements': {
                    'crop': str(crop_req['crop']),
                    'N_avg': float(crop_req['N_avg']),
                    'P_avg': float(crop_req['P_avg']),
                    'K_avg': float(crop_req['K_avg']),
                    'temperature_avg': float(crop_req['temperature_avg']),
                    'humidity_avg': float(crop_req['humidity_avg']),
                    'ph_avg': float(crop_req['ph_avg']),
                    'rainfall_avg': float(crop_req['rainfall_avg']),
                    'N_range': (float(crop_req['N_range'][0]), float(crop_req['N_range'][1])),
                    'temperature_range': (float(crop_req['temperature_range'][0]), float(crop_req['temperature_range'][1])),
                    'humidity_range': (float(crop_req['humidity_range'][0]), float(crop_req['humidity_range'][1])),
                    'rainfall_range': (float(crop_req['rainfall_range'][0]), float(crop_req['rainfall_range'][1]))
                }
            })
        
        return recommendations
    
    def _get_soil_parameters(self, soil_type):
        """Get typical NPK and pH for soil types"""
        soil_params = {
            'sandy': {'N': 30, 'P': 20, 'K': 30, 'ph': 6.0},
            'loamy': {'N': 60, 'P': 40, 'K': 40, 'ph': 6.5},
            'clay': {'N': 80, 'P': 50, 'K': 50, 'ph': 7.0},
            'black': {'N': 70, 'P': 45, 'K': 45, 'ph': 7.5},
            'red': {'N': 50, 'P': 35, 'K': 35, 'ph': 6.2},
            'laterite': {'N': 40, 'P': 30, 'K': 30, 'ph': 5.5}
        }
        
        return soil_params.get(soil_type.lower(), soil_params['loamy'])
