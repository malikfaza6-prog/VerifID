"""
Image utilities - file saving, resizing, format conversion.
"""
import os
import logging
import base64
from io import BytesIO
from typing import Optional, Tuple

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_profile_photo(
    file_storage, upload_dir: str, filename: str
) -> Optional[str]:
    """Save an uploaded profile photo, resizing to 300x300."""
    try:
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)

        if PIL_AVAILABLE:
            img = Image.open(file_storage)
            img = img.convert("RGB")
            img.thumbnail((300, 300), Image.LANCZOS)
            img.save(filepath, "JPEG", quality=85)
        else:
            file_storage.save(filepath)

        return filename
    except Exception as e:
        logger.error(f"Error saving profile photo: {e}")
        return None


def delete_photo(upload_dir: str, filename: str) -> None:
    """Delete a photo file if it exists."""
    if filename:
        filepath = os.path.join(upload_dir, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                logger.warning(f"Could not delete photo {filename}: {e}")


def base64_to_numpy(b64_string: str):
    """Convert a base64-encoded image string to a numpy array (BGR)."""
    import numpy as np
    import cv2
    if "," in b64_string:
        b64_string = b64_string.split(",", 1)[1]
    img_bytes = base64.b64decode(b64_string)
    nparr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def numpy_to_base64(frame) -> str:
    """Convert a numpy BGR frame to base64 JPEG string."""
    import cv2
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")
