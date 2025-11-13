import os

print("🔍 Checking CropSenseAI Setup...\n")

# Check current directory
print(f"Current directory: {os.getcwd()}")

# Check if data folder exists
if os.path.exists('data'):
    print("✅ 'data' folder exists")
    
    # List files in data folder
    files = os.listdir('data')
    print(f"   Files found: {len(files)}")
    
    # Check for required files
    required = [
        'Crop_recommendation.csv',
        'rainfall_lat_long.csv',
        'city_lat.csv',
        'district-wise-rainfall-normal.csv'
    ]
    
    for filename in required:
        if filename in files:
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} - MISSING!")
else:
    print("❌ 'data' folder NOT FOUND!")
    print("   Please create it and add CSV files")

# Check other folders
for folder in ['models', 'utils', 'static', 'templates']:
    if os.path.exists(folder):
        print(f"✅ '{folder}' folder exists")
    else:
        print(f"❌ '{folder}' folder MISSING!")
