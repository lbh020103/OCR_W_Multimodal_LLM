import base64
import requests

def perform_ocr(image_path):
    response = requests.post(
        url = "https://f5c0-34-16-223-163.ngrok-free.app/ocr",
        json = {
            "image_url": image_path
        }
    )
    print("Response:", response.elapsed.total_seconds())
    if response.status_code == 200:
        return response.json().get("response_message")
    else:
        print("Error:", response.status_code, response.text)
        return None

image_path = "https://marketplace.canva.com/EAF5whghycs/2/0/1131w/canva-h%C3%B3a-%C4%91%C6%A1n-xu%E1%BA%A5t-b%E1%BA%A3n-phong-c%C3%A1ch-c%C6%A1-b%E1%BA%A3n-%C4%91en-tr%E1%BA%AFng-I0bkvSytJQE.jpg"
result = perform_ocr(image_path)
print("OCR Result:", result)