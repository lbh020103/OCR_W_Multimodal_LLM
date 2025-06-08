"""
Configuration file for OCR Multimodal LLM project
"""

# Server Configuration
SERVER_PORT = 5555
NGROK_ENABLED = True

# Model Configuration
MODEL_NAME = "5CD-AI/Vintern-1B-v2"
MODEL_DTYPE = "bfloat16"  # Options: "bfloat16", "float16", "float32"
LOW_CPU_MEM_USAGE = True

# Generation Configuration
GENERATION_CONFIG = {
    "max_new_tokens": 512,
    "do_sample": False,
    "num_beams": 3,
    "repetition_penalty": 3.5
}

# Image Processing Configuration
IMAGE_SIZE = 448
MAX_IMAGE_CHUNKS = 6
USE_THUMBNAIL = True

# Output Format Templates
OUTPUT_FORMATS = {
    "json": '''<image>\nNhận diện hoá đơn trong ảnh. Chỉ trả về phần liệt kê các mặt hàng hàng dưới dạng JSON:
[
  {
    "Tên món": "Tên món",
    "Số lượng": "Số lượng",
    "Đơn giá": "Đơn giá",
    "Thành tiền": "Thành tiền"
  },
]
''',
    "csv": '''<image>\nNhận diện hoá đơn trong ảnh. Chỉ trả về phần liệt kê các mặt hàng hàng dưới dạng CSV''',
    "text": '''<image>\nNhận diện toàn bộ nội dung hoá đơn trong ảnh này.'''
}

# API Configuration
ALLOWED_ORIGINS = ["*"]  # CORS settings
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size 