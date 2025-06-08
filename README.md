# OCR with Multimodal LLM

This project provides a solution for OCR (Optical Character Recognition) using a multimodal Large Language Model (LLM). It allows you to extract structured data from images of receipts and invoices using the Vintern-1B-v2 model.

## Directory Structure

```
ORC/
├── OCR_with_multimodal_LLM.ipynb  # Server component (Colab notebook)
├── main.py                        # Client component
└── README.md                      # This documentation
```

## Architecture

The system consists of two main components:

1. **Server Component** (OCR_with_multimodal_LLM.ipynb): A Colab notebook that:
   - Loads the Vintern-1B-v2 multimodal model
   - Sets up a Flask API server
   - Exposes the API through Ngrok for public access

2. **Client Component** (main.py): A Python script that:
   - Sends images to the server via API
   - Receives and processes OCR results

## Setup Instructions

### Server Setup (Google Colab)

1. Open `OCR_with_multimodal_LLM.ipynb` in Google Colab
2. Run the installation cell to install required dependencies
3. Run the model loading cell to initialize the Vintern-1B-v2 model
4. Set up your Ngrok authentication token:
   - Create a free account at [ngrok.com](https://ngrok.com)
   - Get your auth token from the ngrok dashboard
   - In Colab, go to "Secrets" tab and add your token as "ngrok_token"
5. Run the API server cell to start the Flask server with Ngrok
6. Copy the Ngrok URL displayed in the output (looks like `https://xxxx-xx-xx-xxx-xxx.ngrok-free.app`)

### Client Setup (Local Machine)

1. Install required dependencies:
   ```bash
   pip install requests
   ```
2. Open `main.py` and update the Ngrok URL:
   ```python
   url = "YOUR_NGROK_URL/ocr"  # Replace with your Ngrok URL
   ```
3. Run the client script to test:
   ```bash
   python main.py
   ```

## Usage

### API Endpoint

The API exposes a single endpoint:

- **POST /ocr**
  - Input: JSON payload with `image_url` field pointing to an image accessible via HTTP
  - Output: JSON response with structured OCR data

Example request:
```python
response = requests.post(
    url="https://your-ngrok-url.ngrok-free.app/ocr",
    json={"image_url": "https://example.com/path/to/receipt.jpg"}
)
```

### Client Usage

The `main.py` script provides a simple example of how to use the API:

```python
import requests

def perform_ocr(image_path):
    response = requests.post(
        url="https://your-ngrok-url.ngrok-free.app/ocr",
        json={"image_url": image_path}
    )
    if response.status_code == 200:
        return response.json().get("response_message")
    else:
        print("Error:", response.status_code, response.text)
        return None

# Example usage
image_path = "https://example.com/path/to/receipt.jpg"
result = perform_ocr(image_path)
print("OCR Result:", result)
```

## Model Details

This project uses the Vintern-1B-v2 model, a Vietnamese multimodal model capable of understanding both text and images. The model is specifically fine-tuned for:

- Receipt and invoice recognition
- Structured data extraction
- Vietnamese text understanding
- Table structure recognition

The model can output data in different formats (JSON or CSV) based on the prompt provided. For example:

```python
# JSON format prompt
prompt = '''<image>\nNhận diện hoá đơn trong ảnh. Chỉ trả về phần liệt kê các mặt hàng hàng dưới dạng JSON:
[
  {
    "Tên món": "Tên món",
    "Số lượng": "Số lượng",
    "Đơn giá": "Đơn giá",
    "Thành tiền": "Thành tiền"
  },
]
'''

# CSV format prompt
prompt = '''<image>\nNhận diện hoá đơn trong ảnh. Chỉ trả về phần liệt kê các mặt hàng hàng dưới dạng CSV'''
```

## Limitations

- The Ngrok URL changes every time you restart the server in Colab
- The server might timeout after extended periods of inactivity on Colab
- The model is optimized for Vietnamese receipts and invoices
- Performance depends on image quality and format

## Troubleshooting

- If the client cannot connect, check that the Ngrok URL is correct and the server is running
- If OCR results are poor, try using higher quality images or different image formats
- If Colab crashes, check your GPU/RAM usage and consider using a higher-tier Colab account

## License

This project uses the Vintern-1B-v2 model which is subject to its own license terms. Please refer to the [model card](https://huggingface.co/5CD-AI/Vintern-1B-v2) for more information. 