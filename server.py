"""
OCR Server with Flask API and Ngrok integration
"""

import os
import torch
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from pyngrok import ngrok
from werkzeug.utils import secure_filename
import yaml

from transformers import AutoModel, AutoTokenizer
import utils
from config import (
    SERVER_PORT, NGROK_ENABLED, MODEL_NAME, MODEL_DTYPE, LOW_CPU_MEM_USAGE,
    GENERATION_CONFIG, OUTPUT_FORMATS, ALLOWED_ORIGINS, MAX_CONTENT_LENGTH
)

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for model and tokenizer
model = None
tokenizer = None
device = utils.get_device()

def load_model():
    """Load model and tokenizer"""
    global model, tokenizer
    
    print(f"Loading model {MODEL_NAME}...")
    dtype = torch.bfloat16 if MODEL_DTYPE == "bfloat16" else torch.float16 if MODEL_DTYPE == "float16" else torch.float32
    
    model = AutoModel.from_pretrained(
        MODEL_NAME,
        torch_dtype=dtype,
        low_cpu_mem_usage=LOW_CPU_MEM_USAGE,
        trust_remote_code=True,
    ).eval().to(device)
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True, use_fast=False)
    print("Model loaded successfully!")

def ocr_process(image_tensor, output_format="json"):
    """Process image with OCR model"""
    if model is None or tokenizer is None:
        load_model()
    
    # Convert tensor to appropriate format and device
    if image_tensor.dtype != getattr(torch, MODEL_DTYPE):
        image_tensor = image_tensor.to(getattr(torch, MODEL_DTYPE))
    image_tensor = image_tensor.to(device)
    
    # Select prompt template based on output format
    prompt = OUTPUT_FORMATS.get(output_format.lower(), OUTPUT_FORMATS["text"])
    
    # Generate response
    response = model.chat(tokenizer, image_tensor, prompt, GENERATION_CONFIG)
    
    # Clean up to prevent memory leaks
    del image_tensor
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    
    return response

@app.route('/')
def index():
    """Render main UI page"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    """OCR API endpoint"""
    try:
        data = request.json or {}
        output_format = data.get('output_format', 'json').lower()
        
        # Check if output format is valid
        if output_format not in OUTPUT_FORMATS:
            return jsonify({"error": f"Invalid output format. Supported formats: {', '.join(OUTPUT_FORMATS.keys())}"}), 400
        
        # Process image from URL
        if 'image_url' in data:
            image_url = data['image_url']
            image_tensor = utils.load_image_from_url(image_url)
            response_message = ocr_process(image_tensor, output_format)
            return jsonify({"response_message": response_message})
        
        # Process image from base64
        elif 'image_base64' in data:
            image_base64 = data['image_base64']
            image_tensor = utils.load_image_from_base64(image_base64)
            response_message = ocr_process(image_tensor, output_format)
            return jsonify({"response_message": response_message})
        
        else:
            return jsonify({"error": "No image provided. Please provide either 'image_url' or 'image_base64'"}), 400
            
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['file']
        
        # If user does not select file, browser also submits empty part without filename
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        output_format = request.form.get('output_format', 'json').lower()
        
        # Check if output format is valid
        if output_format not in OUTPUT_FORMATS:
            return jsonify({"error": f"Invalid output format. Supported formats: {', '.join(OUTPUT_FORMATS.keys())}"}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process image
        image_tensor = utils.load_image_from_file(file_path)
        response_message = ocr_process(image_tensor, output_format)
        
        # Clean up file
        os.remove(file_path)
        
        return jsonify({"response_message": response_message})
        
    except Exception as e:
        print(f"Error processing upload: {str(e)}")
        return jsonify({"error": str(e)}), 500

def start_ngrok():
    """Initialize Ngrok tunnel"""
    try:
        # Try to read ngrok auth token from config file
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.config/ngrok/ngrok.yml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                auth_token = config.get('authtoken')
                if auth_token:
                    ngrok.set_auth_token(auth_token)
        
        # Start ngrok tunnel
        public_url = ngrok.connect(SERVER_PORT)
        print(f"Ngrok URL: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"Error starting Ngrok: {str(e)}")
        return None

if __name__ == "__main__":
    # Load model
    load_model()
    
    # Start Ngrok if enabled
    if NGROK_ENABLED:
        ngrok_url = start_ngrok()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=False) 