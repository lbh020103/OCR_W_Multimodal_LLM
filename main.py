"""
Client for OCR with Multimodal LLM API
"""

import os
import argparse
import base64
import requests
from PIL import Image


def perform_ocr_with_url(server_url, image_url, output_format="json"):
    """Perform OCR using image URL"""
    try:
        response = requests.post(
            url=f"{server_url}/ocr",
            json={
                "image_url": image_url,
                "output_format": output_format
            },
            timeout=120  # Increased timeout for large images
        )
        
        print(f"Response time: {response.elapsed.total_seconds():.2f} seconds")
        
        if response.status_code == 200:
            return response.json().get("response_message")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def perform_ocr_with_file(server_url, image_path, output_format="json"):
    """Perform OCR using local image file"""
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        with open(image_path, "rb") as file:
            files = {"file": (os.path.basename(image_path), file, "image/jpeg")}
            data = {"output_format": output_format}
            
            response = requests.post(
                url=f"{server_url}/upload",
                files=files,
                data=data,
                timeout=120  # Increased timeout for large images
            )
        
        print(f"Response time: {response.elapsed.total_seconds():.2f} seconds")
        
        if response.status_code == 200:
            return response.json().get("response_message")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def perform_ocr_with_base64(server_url, image_path, output_format="json"):
    """Perform OCR using base64-encoded image"""
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        with open(image_path, "rb") as file:
            image_data = file.read()
            base64_data = base64.b64encode(image_data).decode("utf-8")
            
        response = requests.post(
            url=f"{server_url}/ocr",
            json={
                "image_base64": base64_data,
                "output_format": output_format
            },
            timeout=120  # Increased timeout for large images
        )
        
        print(f"Response time: {response.elapsed.total_seconds():.2f} seconds")
        
        if response.status_code == 200:
            return response.json().get("response_message")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def save_result(result, output_file=None):
    """Save OCR result to file if specified"""
    if output_file and result:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(result)
        print(f"Result saved to {output_file}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Client for OCR with Multimodal LLM API")
    parser.add_argument("--server", default="https://f5c0-34-16-223-163.ngrok-free.app", 
                        help="Server URL")
    
    # Image source (mutually exclusive group)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--url", help="Image URL")
    source_group.add_argument("--file", help="Local image file path")
    source_group.add_argument("--base64", help="Local image file path (will be base64 encoded)")
    
    # Additional options
    parser.add_argument("--format", choices=["json", "csv", "text"], default="json",
                       help="Output format (default: json)")
    parser.add_argument("--output", help="Output file to save the result")
    
    args = parser.parse_args()
    
    # Perform OCR based on the provided image source
    if args.url:
        print(f"Processing image URL: {args.url}")
        result = perform_ocr_with_url(args.server, args.url, args.format)
    elif args.file:
        print(f"Processing local file: {args.file}")
        result = perform_ocr_with_file(args.server, args.file, args.format)
    elif args.base64:
        print(f"Processing local file as base64: {args.base64}")
        result = perform_ocr_with_base64(args.server, args.base64, args.format)
    
    # Print and save result
    if result:
        print("\nOCR Result:")
        print(result)
        save_result(result, args.output)
    else:
        print("OCR processing failed.")


if __name__ == "__main__":
    main()