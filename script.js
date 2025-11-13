from flask import Flask, render_template, request
import os
from PIL import Image

app = Flask(_name_)


UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/crop', methods=['POST'])
def crop_image():
    if 'file' not in request.files:
        return "❌ No file part"
    file = request.files['file']
    if file.filename == '':
        return "❌ No selected file"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    
    img = Image.open(filepath)

    
    try:
        left = int(request.form.get('left', 0))
        top = int(request.form.get('top', 0))
        right = int(request.form.get('right', img.width))
        bottom = int(request.form.get('bottom', img.height))
    except ValueError:
        return "⚠ Invalid crop coordinates"

    
    cropped = img.crop((left, top, right, bottom))
    cropped_path = os.path.join(app.config['UPLOAD_FOLDER'], "cropped_" + file.filename)
    cropped.save(cropped_path)

    return f"""
    <h2>✅ Image cropped successfully!</h2>
    <img src='/{cropped_path}' width='300'><br>
    <a href='/'>Go Back</a>
    """


if _name_ == '_main_':
    app.run(debug=True)