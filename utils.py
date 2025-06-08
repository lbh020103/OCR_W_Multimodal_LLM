"""
Utility functions for OCR Multimodal LLM project
"""

import base64
import io
import os
import requests
import torch
import torchvision.transforms as T
from PIL import Image
from torchvision.transforms.functional import InterpolationMode
from config import IMAGE_SIZE, MAX_IMAGE_CHUNKS, USE_THUMBNAIL

# Image handling constants
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

def build_transform(input_size=IMAGE_SIZE):
    """Build image transformation pipeline"""
    transform = T.Compose([
        T.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
        T.Resize((input_size, input_size), interpolation=InterpolationMode.BICUBIC),
        T.ToTensor(),
        T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])
    return transform

def find_closest_aspect_ratio(aspect_ratio, target_ratios, width, height, image_size):
    """Find the closest aspect ratio for image processing"""
    best_ratio_diff = float('inf')
    best_ratio = (1, 1)
    area = width * height
    for ratio in target_ratios:
        target_aspect_ratio = ratio[0] / ratio[1]
        ratio_diff = abs(aspect_ratio - target_aspect_ratio)
        if ratio_diff < best_ratio_diff:
            best_ratio_diff = ratio_diff
            best_ratio = ratio
        elif ratio_diff == best_ratio_diff:
            if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                best_ratio = ratio
    return best_ratio

def dynamic_preprocess(image, min_num=1, max_num=MAX_IMAGE_CHUNKS, image_size=IMAGE_SIZE, use_thumbnail=USE_THUMBNAIL):
    """Process image into chunks for model input"""
    orig_width, orig_height = image.size
    aspect_ratio = orig_width / orig_height

    # calculate the existing image aspect ratio
    target_ratios = set(
        (i, j) for n in range(min_num, max_num + 1) for i in range(1, n + 1) for j in range(1, n + 1) if
        i * j <= max_num and i * j >= min_num)
    target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])

    # find the closest aspect ratio to the target
    target_aspect_ratio = find_closest_aspect_ratio(
        aspect_ratio, target_ratios, orig_width, orig_height, image_size)

    # calculate the target width and height
    target_width = image_size * target_aspect_ratio[0]
    target_height = image_size * target_aspect_ratio[1]
    blocks = target_aspect_ratio[0] * target_aspect_ratio[1]

    # resize the image
    resized_img = image.resize((target_width, target_height))
    processed_images = []
    for i in range(blocks):
        box = (
            (i % (target_width // image_size)) * image_size,
            (i // (target_width // image_size)) * image_size,
            ((i % (target_width // image_size)) + 1) * image_size,
            ((i // (target_width // image_size)) + 1) * image_size
        )
        # split the image
        split_img = resized_img.crop(box)
        processed_images.append(split_img)
    assert len(processed_images) == blocks
    if use_thumbnail and len(processed_images) != 1:
        thumbnail_img = image.resize((image_size, image_size))
        processed_images.append(thumbnail_img)
    return processed_images

def load_image_from_url(image_url, input_size=IMAGE_SIZE, max_num=MAX_IMAGE_CHUNKS):
    """Load image from URL and process it for model input"""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        image = Image.open(io.BytesIO(response.content)).convert('RGB')
        return process_image(image, input_size, max_num)
    except Exception as e:
        raise ValueError(f"Error loading image from URL: {str(e)}")

def load_image_from_file(file_path, input_size=IMAGE_SIZE, max_num=MAX_IMAGE_CHUNKS):
    """Load image from local file and process it for model input"""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")
        image = Image.open(file_path).convert('RGB')
        return process_image(image, input_size, max_num)
    except Exception as e:
        raise ValueError(f"Error loading image from file: {str(e)}")

def load_image_from_base64(base64_string, input_size=IMAGE_SIZE, max_num=MAX_IMAGE_CHUNKS):
    """Load image from base64 string and process it for model input"""
    try:
        # Remove the data URL prefix if present (e.g., "data:image/jpeg;base64,")
        if ',' in base64_string:
            base64_string = base64_string.split(',', 1)[1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        return process_image(image, input_size, max_num)
    except Exception as e:
        raise ValueError(f"Error loading image from base64: {str(e)}")

def process_image(image, input_size=IMAGE_SIZE, max_num=MAX_IMAGE_CHUNKS):
    """Process PIL Image for model input"""
    transform = build_transform(input_size=input_size)
    images = dynamic_preprocess(image, image_size=input_size, use_thumbnail=USE_THUMBNAIL, max_num=max_num)
    pixel_values = [transform(image) for image in images]
    pixel_values = torch.stack(pixel_values)
    return pixel_values

def get_device():
    """Get the appropriate device (CUDA if available, otherwise CPU)"""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu") 