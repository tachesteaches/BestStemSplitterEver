#!/bin/bash

# Create necessary directories
mkdir -p templates uploads

# Create the index.html file
cat > templates/index.html << 'EOL'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BestStemSplitterEver</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/dropzone/5.9.3/min/dropzone.min.css">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .dropzone {
            border: 2px dashed #0087F7;
            border-radius: 5px;
            background: white;
            min-height: 200px;
            padding: 20px;
            box-sizing: border-box;
        }
        .dropzone .dz-message {
            font-weight: 400;
            text-align: center;
            margin: 2em 0;
        }
        .stems-container {
            margin-top: 30px;
        }
        .stems-list {
            margin-top: 10px;
            border: 1px solid #eee;
            padding: 10px;
            border-radius: 5px;
            max-height: 300px;
            overflow-y: auto;
        }
        .stem-item {
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
        .stem-item:last-child {
            border-bottom: none;
        }
        .stem-item a {
            color: #0087F7;
            text-decoration: none;
        }
        .stem-item a:hover {
            text-decoration: underline;
        }
        .status {
            padding: 10px;
            margin-top: 10px;
            border-radius: 5px;
            display: none;
        }
        .success {
            background-color: #dff0d8;
            color: #3c763d;
            display: block;
        }
        .error {
            background-color: #f2dede;
            color: #a94442;
            display: block;
        }
    </style>
</head>
<body>
    <h1>BestStemSplitterEver</h1>
    
    <div class="container">
        <div>
            <h2>Upload Song for Stem Splitting</h2>
            <p>
                Drag and drop your audio files here or click to browse. 
                Supported formats: MP3, WAV, FLAC, OGG, M4A, AAC. 
                Maximum file size: 100MB.
            </p>
            <form id="upload-form" action="/upload" class="dropzone">
                <div class="dz-message" data-dz-message>
                    <span>Drop audio files here to split into stems</span>
                </div>
            </form>
            
            <div id="status" class="status"></div>
        </div>
        
        <div class="stems-container">
            <h2>Available Stems</h2>
            <p>Download your processed stems here:</p>
            <div id="stems-list" class="stems-list">
                <p>No stems available yet. Upload a song to generate stems.</p>
            </div>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/dropzone/5.9.3/min/dropzone.min.js"></script>
    <script>
        // Configure Dropzone
        Dropzone.autoDiscover = false;
        
        const myDropzone = new Dropzone("#upload-form", {
            paramName: "file",
            maxFilesize: 100, // MB
            acceptedFiles: ".mp3,.wav,.flac,.ogg,.m4a,.aac",
            timeout: 180000, // 3 minutes
            dictDefaultMessage: "Drop audio files here to split into stems",
            init: function() {
                this.on("success", function(file, response) {
                    const statusEl = document.getElementById("status");
                    statusEl.textContent = "File processed successfully! Check the stems list below.";
                    statusEl.className = "status success";
                    
                    // Refresh the stems list
                    loadStems();
                    
                    // Clear the upload after 2 seconds
                    setTimeout(() => {
                        this.removeFile(file);
                    }, 2000);
                });
                
                this.on("error", function(file, errorMessage) {
                    const statusEl = document.getElementById("status");
                    statusEl.textContent = typeof errorMessage === "string" 
                        ? errorMessage 
                        : (errorMessage.error || "An error occurred during upload");
                    statusEl.className = "status error";
                });
                
                this.on("sending", function(file) {
                    const statusEl = document.getElementById("status");
                    statusEl.textContent = "Processing file... This may take a few minutes.";
                    statusEl.className = "status";
                    statusEl.style.display = "block";
                    statusEl.style.backgroundColor = "#fcf8e3";
                    statusEl.style.color = "#8a6d3b";
                });
            }
        });
        
        // Function to load available stems
        function loadStems() {
            fetch('/stems')
                .then(response => response.json())
                .then(files => {
                    const stemsListEl = document.getElementById("stems-list");
                    
                    if (files.length === 0) {
                        stemsListEl.innerHTML = "<p>No stems available yet. Upload a song to generate stems.</p>";
                        return;
                    }
                    
                    stemsListEl.innerHTML = '';
                    files.forEach(file => {
                        const div = document.createElement('div');
                        div.className = 'stem-item';
                        
                        const link = document.createElement('a');
                        link.href = `/download/${encodeURIComponent(file)}`;
                        link.textContent = file;
                        
                        div.appendChild(link);
                        stemsListEl.appendChild(div);
                    });
                })
                .catch(error => {
                    console.error('Error loading stems:', error);
                    document.getElementById("stems-list").innerHTML = 
                        "<p>Error loading stems. Please refresh the page and try again.</p>";
                });
        }
        
        // Load stems on page load
        document.addEventListener('DOMContentLoaded', loadStems);
    </script>
</body>
</html>
EOL

# Create web_server.py
cat > web_server.py << 'EOL'
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
    app.run(debug=True, host='0.0.0.0', port=5000)
EOL

# Make the script executable
chmod +x web_server.py

echo "Setup complete! To run the web server, execute: python web_server.py" 