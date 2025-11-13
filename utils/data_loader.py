import pandas as pd
import os

class DataLoader:
    """Load and manage all datasets"""
    
    def __init__(self):
        self.data_dir = 'data'
        self._load_datasets()
    
    def _load_datasets(self):
        """Load all CSV datasets"""
        # Crop recommendation data
        self.crop_data = pd.read_csv(
            os.path.join(self.data_dir, 'Crop_recommendation.csv')
        )
        
        # Rainfall data with coordinates
        self.rainfall_data = pd.read_csv(
            os.path.join(self.data_dir, 'rainfall_lat_long.csv')
        )
        
        # City coordinates
        self.city_lat = pd.read_csv(
            os.path.join(self.data_dir, 'city_lat.csv')
        )
        
        # District-wise rainfall normals
        self.district_rainfall = pd.read_csv(
            os.path.join(self.data_dir, 'district-wise-rainfall-normal.csv')
        )
        
        print("✅ All datasets loaded successfully")
        print(f"   - Crop recommendations: {len(self.crop_data)} records")
        print(f"   - Districts with rainfall data: {len(self.district_rainfall)}")
    
    def get_crop_data(self):
        """Get crop recommendation dataset"""
        return self.crop_data.copy()
    
    def get_rainfall_data(self):
        """Get rainfall data with coordinates"""
        return self.rainfall_data.copy()
    
    def get_district_data(self, state=None, district=None):
        """Get district rainfall data"""
        df = self.district_rainfall.copy()
        
        if state:
            df = df[df['STATE_UT_NAME'].str.upper() == state.upper()]
        
        if district:
            df = df[df['DISTRICT'].str.upper() == district.upper()]
        
        return df
    
    def get_location_hierarchy(self):
        """Get hierarchical structure of states and districts"""
        hierarchy = {}
        
        for _, row in self.district_rainfall.iterrows():
            state = row['STATE_UT_NAME']
            district = row['DISTRICT']
            
            if state not in hierarchy:
                hierarchy[state] = []
            
            if district not in hierarchy[state]:
                hierarchy[state].append(district)
        
        return hierarchy
    
    def get_available_crops(self):
        """Get list of all available crops"""
        return sorted(self.crop_data['label'].unique().tolist())
    
    def get_crop_requirements(self, crop_name):
        """Get average requirements for a specific crop"""
        crop_df = self.crop_data[self.crop_data['label'] == crop_name]
        
        if crop_df.empty:
            return None
        
        return {
            'crop': crop_name,
            'N_avg': crop_df['N'].mean(),
            'P_avg': crop_df['P'].mean(),
            'K_avg': crop_df['K'].mean(),
            'temperature_avg': crop_df['temperature'].mean(),
            'humidity_avg': crop_df['humidity'].mean(),
            'ph_avg': crop_df['ph'].mean(),
            'rainfall_avg': crop_df['rainfall'].mean(),
            'N_range': (crop_df['N'].min(), crop_df['N'].max()),
            'temperature_range': (crop_df['temperature'].min(), crop_df['temperature'].max()),
            'humidity_range': (crop_df['humidity'].min(), crop_df['humidity'].max()),
            'rainfall_range': (crop_df['rainfall'].min(), crop_df['rainfall'].max())
        }
