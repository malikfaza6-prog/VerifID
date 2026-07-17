"""
Face encoder - generates face encodings using face_recognition library.
"""
import logging
import numpy as np
from typing import Optional, List, Tuple

try:
    import face_recognition
    FR_AVAILABLE = True
except ImportError:
    FR_AVAILABLE = False
    logging.warning("face_recognition library not installed. Face encoding will not work.")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

logger = logging.getLogger(__name__)


def get_face_encodings(frame_rgb: np.ndarray) -> List[np.ndarray]:
    """
    Given an RGB frame, return list of 128-d face encodings.
    Uses face_recognition library (dlib under the hood).
    """
    if not FR_AVAILABLE:
        logger.error("face_recognition not available.")
        return []
    try:
        locations = face_recognition.face_locations(frame_rgb, model="hog")
        encodings = face_recognition.face_encodings(frame_rgb, locations)
        return encodings
    except Exception as e:
        logger.error(f"Encoding error: {e}")
        return []


def average_encoding(encodings: List[np.ndarray]) -> Optional[np.ndarray]:
    """Average multiple face encodings into one representative encoding."""
    if not encodings:
        return None
    return np.mean(encodings, axis=0)


def compare_encodings(
    known_encoding: np.ndarray,
    face_encoding: np.ndarray,
    tolerance: float = 0.6,
) -> Tuple[bool, float]:
    """
    Compare a known encoding to a candidate.
    Returns (is_match, confidence_0_to_1).
    """
    from typing import Tuple
    if not FR_AVAILABLE:
        return False, 0.0
    try:
        distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
        is_match = bool(distance <= tolerance)
        # Convert distance to confidence (0=far/bad, 1=close/good)
        confidence = max(0.0, 1.0 - float(distance))
        return is_match, confidence
    except Exception as e:
        logger.error(f"Compare encoding error: {e}")
        return False, 0.0


def bgr_to_rgb(frame: np.ndarray) -> np.ndarray:
    """Convert BGR (OpenCV) frame to RGB for face_recognition."""
    if CV2_AVAILABLE:
        import cv2
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame[:, :, ::-1]
