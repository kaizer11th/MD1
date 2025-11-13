import pandas as pd
from fuzzywuzzy import fuzz

class LocationMatcher:
    """Match user location to district data"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.district_data = data_loader.get_rainfall_data()
    
    def get_district_data(self, location_query):
        """
        Match location query to district data
        location_query can be: "District, State" or just "District"
        """
        if not location_query:
            return None
        
        # Parse location
        parts = [p.strip() for p in location_query.split(',')]
        
        if len(parts) == 2:
            district, state = parts
            return self._exact_match(state, district)
        else:
            return self._fuzzy_match(parts[0])
    
    def _exact_match(self, state, district):
        """Exact match for state and district"""
        matches = self.district_data[
            (self.district_data['STATE_UT_NAME'].str.upper() == state.upper()) &
            (self.district_data['DISTRICT'].str.upper() == district.upper())
        ]
        
        if not matches.empty:
            return matches.iloc[0].to_dict()
        
        return None
    
    def _fuzzy_match(self, query):
        """Fuzzy match for district name"""
        best_match = None
        best_score = 0
        
        for _, row in self.district_data.iterrows():
            district = row['DISTRICT']
            score = fuzz.ratio(query.upper(), district.upper())
            
            if score > best_score:
                best_score = score
                best_match = row
        
        if best_score > 70:  # Threshold for fuzzy matching
            return best_match.to_dict()
        
        return None
    
    def get_nearby_districts(self, lat, lon, radius_km=50):
        """Get districts within specified radius"""
        # Simplified implementation - actual would use haversine distance
        # This requires the coordinate data
        return []
