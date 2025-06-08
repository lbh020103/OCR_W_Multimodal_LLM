# OCR with Multimodal LLM

This project provides a solution for OCR (Optical Character Recognition) using a multimodal Large Language Model (LLM). It allows you to extract structured data from images of receipts and invoices using the Vintern-1B-v2 model.

## Directory Structure

```
ORC/
├── server.py                     # Main server implementation
├── config.py                     # Configuration settings
├── utils.py                      # Utility functions
├── main.py                       # Client component
├── static/                       # Static assets
│   ├── css/                      # CSS stylesheets
│   └── js/                       # JavaScript files
├── templates/                    # HTML templates
│   └── index.html                # Web UI template
├── uploads/                      # Temporary folder for uploads
└── README.md                     # This documentation
```

## Features

- **Multiple Input Methods**:
  - Process images from URLs
  - Process local image files via upload
  - Process base64-encoded images

- **Multiple Output Formats**:
  - JSON format for structured data
  - CSV format for tabular data
  - Plain text for full document transcription

- **Web Interface**:
  - User-friendly web UI for uploading and processing images
  - Image preview functionality
  - Result copy button

- **Client Library**:
  - Command-line interface for batch processing
  - Supports all input methods and output formats
  - Result saving to files

## Architecture

The system consists of two main components:

1. **Server Component** (server.py):
   - Loads the Vintern-1B-v2 multimodal model
   - Sets up a Flask API server
   - Exposes the API through Ngrok for public access
   - Provides a web interface for direct use

2. **Client Component** (main.py):
   - Sends images to the server via API
   - Supports multiple input methods
   - Supports multiple output formats
   - Command-line interface for easy integration

## Setup Instructions

### Server Setup

#### Google Colab (using OCR_with_multimodal_LLM.ipynb)
1. Open `OCR_with_multimodal_LLM.ipynb` in Google Colab
2. Run the installation cell to install required dependencies
3. Run the model loading cell to initialize the Vintern-1B-v2 model
4. Set up your Ngrok authentication token:
   - Create a free account at [ngrok.com](https://ngrok.com)
   - Get your auth token from the ngrok dashboard
   - In Colab, go to "Secrets" tab and add your token as "ngrok_token"
5. Run the API server cell to start the Flask server with Ngrok
6. Copy the Ngrok URL displayed in the output

#### Local Setup (using server.py)
1. Install required dependencies:
   ```bash
   pip install flask flask-cors pyngrok pyyaml pillow torch torchvision transformers
   ```
2. Create a `.config/ngrok/ngrok.yml` file with your authtoken:
   ```yaml
   authtoken: YOUR_NGROK_TOKEN
   ```
3. Run the server:
   ```bash
   python server.py
   ```

### Client Setup

1. Install required dependencies:
   ```bash
   pip install requests pillow
   ```
2. Run the client:
   ```bash
   # Process image from URL
   python main.py --url https://example.com/image.jpg --format json
   
   # Process local image file
   python main.py --file path/to/image.jpg --format csv
   
   # Process and save result to file
   python main.py --file path/to/image.jpg --output result.txt
   ```

## Usage

### Web Interface

1. Open the server URL in a web browser
2. Upload an image file or provide an image URL
3. Select the desired output format
4. Click "Process Image" or "Process URL"
5. View the results and use the copy button to copy them

### API Endpoints

The API exposes two main endpoints:

- **POST /ocr**
  - Process images from URL or base64 data
  - Input: JSON payload with `image_url` or `image_base64` field and optional `output_format`
  - Output: JSON response with `response_message` field

- **POST /upload**
  - Process uploaded image files
  - Input: Form data with `file` field and optional `output_format`
  - Output: JSON response with `response_message` field

Example request for URL processing:
```python
response = requests.post(
    url="https://your-server-url/ocr",
    json={
        "image_url": "https://example.com/receipt.jpg",
        "output_format": "json"
    }
)
```

### Command-Line Client

The `main.py` script provides a command-line interface for the OCR service:

```bash
# Basic usage
python main.py --url https://example.com/receipt.jpg

# Specify server URL
python main.py --server https://your-server-url --url https://example.com/receipt.jpg

# Process local file
python main.py --file path/to/receipt.jpg

# Change output format
python main.py --url https://example.com/receipt.jpg --format csv

# Save result to file
python main.py --url https://example.com/receipt.jpg --output result.json
```

## Configuration

The `config.py` file contains various settings that can be modified:

- Server port and Ngrok settings
- Model configuration (name, dtype, etc.)
- Generation parameters
- Image processing settings
- Output format templates

## Model Details

This project uses the Vintern-1B-v2 model, a Vietnamese multimodal model capable of understanding both text and images. The model is specifically fine-tuned for:

- Receipt and invoice recognition
- Structured data extraction
- Vietnamese text understanding
- Table structure recognition

The model can output data in different formats (JSON, CSV, or plain text) based on the prompt provided.

## Limitations

- The Ngrok URL changes every time you restart the server
- The server might timeout after extended periods of inactivity
- The model is optimized for Vietnamese receipts and invoices
- Performance depends on image quality and format

## Troubleshooting

- If the client cannot connect, check that the server URL is correct and the server is running
- If OCR results are poor, try using higher quality images or different image formats
- If you're getting memory errors, try reducing the `MAX_IMAGE_CHUNKS` in config.py
- For large images, the processing might take longer than expected

## License

This project uses the Vintern-1B-v2 model which is subject to its own license terms. Please refer to the [model card](https://huggingface.co/5CD-AI/Vintern-1B-v2) for more information. 