from flask import Flask, render_template, request, jsonify
import os
from PIL import Image
import pandas as pd
import numpy as np
from utils.data_loader import DataLoader
from utils.location_matcher import LocationMatcher
from models.crop_predictor import CropPredictor
from models.yield_predictor import YieldPredictor

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max

# JSON encoder for numpy types
def convert_to_json_serializable(obj):
    """Convert numpy/pandas types to Python native types"""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    return obj

# Initialize components
data_loader = DataLoader()
location_matcher = LocationMatcher(data_loader)
crop_predictor = CropPredictor(data_loader)
yield_predictor = YieldPredictor(data_loader)


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get list of available states and districts"""
    locations = data_loader.get_location_hierarchy()
    return jsonify(locations)


@app.route('/api/crops', methods=['GET'])
def get_crops():
    """Get list of available crops"""
    crops = data_loader.get_available_crops()
    return jsonify({'crops': crops})


@app.route('/disease-diagnosis', methods=['POST'])
def disease_diagnosis():
    """Detect crop disease from uploaded image"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save and process image
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    try:
        img = Image.open(filepath)
        
        # Crop coordinates (if provided)
        left = int(request.form.get('left', 0))
        top = int(request.form.get('top', 0))
        right = int(request.form.get('right', img.width))
        bottom = int(request.form.get('bottom', img.height))
        
        cropped = img.crop((left, top, right, bottom))
        cropped_path = os.path.join(app.config['UPLOAD_FOLDER'], f"cropped_{file.filename}")
        cropped.save(cropped_path)
        
        # Placeholder for disease detection (integrate your model here)
        result = {
            'disease': 'Sample Disease Name',
            'confidence': 0.85,
            'remedy': 'Apply organic neem oil spray every 7 days',
            'image_url': f'/{cropped_path}'
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/yield-prediction', methods=['POST'])
def yield_prediction():
    """Predict crop yield based on input parameters"""
    try:
        data = request.json
        crop = data.get('crop')
        location = data.get('location')
        soil_type = data.get('soil_type')
        
        # Get location data
        district_data = location_matcher.get_district_data(location)
        
        if not district_data:
            return jsonify({'error': 'Location not found'}), 404
        
        # Predict yield
        prediction = yield_predictor.predict_yield(
            crop=crop,
            district_data=district_data,
            soil_type=soil_type
        )
        
        return jsonify(prediction)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/crop-recommendation', methods=['POST'])
def crop_recommendation():
    """Recommend best crops for given conditions"""
    try:
        data = request.json
        location = data.get('location')
        soil_type = data.get('soil_type', 'loamy')
        season = data.get('season', 'kharif')
        
        # Get location climate data
        district_data = location_matcher.get_district_data(location)
        
        if not district_data:
            return jsonify({'error': 'Location not found'}), 404
        
        # Get recommendations
        recommendations = crop_predictor.recommend_crops(
            district_data=district_data,
            soil_type=soil_type,
            season=season
        )
        
        # Convert to JSON serializable format
        recommendations = convert_to_json_serializable(recommendations)
        
        return jsonify(recommendations)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/farm-report', methods=['POST'])
def farm_report():
    """Generate comprehensive farm report"""
    try:
        data = request.json
        location = data.get('location')
        farm_info = data.get('farm_info', '')
        seasonal_data = data.get('seasonal_data', '')
        language = data.get('language', 'English')
        
        # Get location data
        district_data = location_matcher.get_district_data(location)
        
        if not district_data:
            return jsonify({'error': 'Location not found'}), 404
        
        # Generate comprehensive report
        report = {
            'location_analysis': {
                'district': district_data['DISTRICT'],
                'state': district_data['STATE_UT_NAME'],
                'annual_rainfall': district_data['ANNUAL'],
                'monsoon_rainfall': district_data['Jun-Sep'],
            },
            'recommended_crops': crop_predictor.recommend_crops(district_data),
            'seasonal_planning': _generate_seasonal_plan(district_data),
            'irrigation_advice': _generate_irrigation_advice(district_data),
            'soil_management': _generate_soil_advice(district_data),
            'language': language
        }
        
        return jsonify(report)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _generate_seasonal_plan(district_data):
    """Generate seasonal farming plan"""
    return {
        'kharif': {
            'months': 'June-September',
            'rainfall': district_data['Jun-Sep'],
            'suitable_crops': ['rice', 'maize', 'cotton', 'jute']
        },
        'rabi': {
            'months': 'October-March',
            'rainfall': district_data['Oct-Dec'] + district_data['Jan-Feb'],
            'suitable_crops': ['wheat', 'chickpea', 'lentil']
        },
        'zaid': {
            'months': 'March-June',
            'rainfall': district_data['Mar-May'],
            'suitable_crops': ['watermelon', 'muskmelon', 'cucumber']
        }
    }


def _generate_irrigation_advice(district_data):
    """Generate irrigation recommendations"""
    annual_rf = district_data['ANNUAL']
    
    if annual_rf < 750:
        return {
            'category': 'Low rainfall zone',
            'advice': 'Drip irrigation and mulching recommended',
            'water_conservation': 'Critical'
        }
    elif annual_rf < 1500:
        return {
            'category': 'Moderate rainfall zone',
            'advice': 'Supplemental irrigation during dry spells',
            'water_conservation': 'Important'
        }
    else:
        return {
            'category': 'High rainfall zone',
            'advice': 'Focus on drainage and water harvesting',
            'water_conservation': 'Moderate'
        }


def _generate_soil_advice(district_data):
    """Generate soil management advice"""
    return {
        'npk_recommendation': {
            'N': 'Nitrogen management based on crop requirement',
            'P': 'Apply phosphorus based on soil test',
            'K': 'Potassium supplementation needed'
        },
        'organic_matter': 'Incorporate farm yard manure or compost',
        'ph_management': 'Maintain pH between 6.0-7.5 for optimal growth'
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
