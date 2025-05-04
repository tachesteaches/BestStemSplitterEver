#!/usr/bin/env python3
import os
import subprocess
import sys
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import yaml

# Create Flask app
app = Flask(__name__)

# Load configuration
def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.yaml")
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)
    return None

config = load_config()

# Configure upload settings
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Flask app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser might submit an empty file
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the file with stem_splitter.py
        try:
            output_dir = config['paths']['output_dir'] if config else './stems'
            cmd = f'python stem_splitter.py "{filepath}" -o "{output_dir}"'
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                return jsonify({
                    'success': False,
                    'message': 'Error processing file',
                    'error': stderr.decode('utf-8')
                }), 500
            
            return jsonify({
                'success': True,
                'message': 'File uploaded and processed successfully',
                'filename': filename,
                'output_dir': output_dir
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Error during processing',
                'error': str(e)
            }), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/download/<path:filename>')
def download_file(filename):
    output_dir = config['paths']['output_dir'] if config else './stems'
    return send_from_directory(output_dir, filename, as_attachment=True)

@app.route('/stems')
def list_stems():
    output_dir = config['paths']['output_dir'] if config else './stems'
    if not os.path.exists(output_dir):
        return jsonify([])
    
    files = []
    for (dirpath, dirnames, filenames) in os.walk(output_dir):
        for filename in filenames:
            if allowed_file(filename):
                # Create relative path from output_dir
                rel_path = os.path.relpath(os.path.join(dirpath, filename), output_dir)
                files.append(rel_path)
    
    return jsonify(files)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(config['paths']['temp_dir'] if config else './temp', exist_ok=True)
    os.makedirs(config['paths']['output_dir'] if config else './stems', exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=3000)
