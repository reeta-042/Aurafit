"""
Image processing utilities for AuraFit
Handles image upload, preprocessing, and optimization
"""

import logging
import io
from typing import Optional
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


def process_uploaded_image(image_bytes: bytes, max_size: int = 1024) -> Optional[bytes]:
    """
    Process and optimize uploaded image for API submission
    
    Args:
        image_bytes: Raw image bytes
        max_size: Maximum width/height in pixels
        
    Returns:
        Optimized image bytes in JPEG format
    """
    try:
        # Open image
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if necessary
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save as JPEG with compression
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        processed_bytes = output.getvalue()
        
        original_size = len(image_bytes)
        compressed_size = len(processed_bytes)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        logger.info(f"Image processed: {original_size} → {compressed_size} bytes ({compression_ratio:.1f}% reduction)")
        return processed_bytes
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return None


def get_image_dimensions(image_bytes: bytes) -> Optional[tuple]:
    """Get image dimensions without full processing"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        return img.size
    except Exception as e:
        logger.error(f"Error getting image dimensions: {e}")
        return None


def validate_image(image_bytes: bytes) -> bool:
    """Validate image format and integrity"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        return True
    except Exception as e:
        logger.error(f"Invalid image: {e}")
        return False
