import numpy as np

class YieldPredictor:
    """Predict crop yield based on conditions"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
    
    def predict_yield(self, crop, district_data, soil_type):
        """Predict yield for given crop and conditions"""
        
        # Get crop requirements
        crop_req = self.data_loader.get_crop_requirements(crop)
        
        if not crop_req:
            return {'error': f'Crop "{crop}" not found'}
        
        # Calculate stress factors
        rainfall_stress = self._calculate_rainfall_stress(
            district_data['ANNUAL'],
            crop_req['rainfall_avg']
        )
        
        # Base yield (tonnes per hectare) - typical values
        base_yields = {
            'rice': 3.5, 'wheat': 3.2, 'maize': 2.8,
            'cotton': 1.5, 'sugarcane': 70, 'jute': 2.0
        }
        
        base_yield = base_yields.get(crop, 2.0)
        
        # Adjust for stress
        predicted_yield = base_yield * (1 - rainfall_stress * 0.3)
        
        return {
            'crop': crop,
            'predicted_yield_per_hectare': round(predicted_yield, 2),
            'unit': 'tonnes',
            'rainfall_stress': round(rainfall_stress, 2),
            'confidence': 0.75,
            'recommendations': self._generate_yield_recommendations(
                rainfall_stress,
                crop
            )
        }
    
    def _calculate_rainfall_stress(self, actual_rainfall, optimal_rainfall):
        """Calculate stress factor based on rainfall deviation"""
        deviation = abs(actual_rainfall - optimal_rainfall) / optimal_rainfall
        return min(deviation, 1.0)  # Cap at 100% stress
    
    def _generate_yield_recommendations(self, stress, crop):
        """Generate recommendations to improve yield"""
        recommendations = []
        
        if stress > 0.3:
            recommendations.append("High stress detected. Consider irrigation.")
        if stress > 0.5:
            recommendations.append("Severe stress. Implement water conservation techniques.")
        
        recommendations.append(f"Use certified {crop} seeds for better yield.")
        recommendations.append("Apply balanced NPK fertilizers based on soil test.")
        
        return recommendations
