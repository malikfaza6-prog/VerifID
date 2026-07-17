"""
Face detector - wraps OpenCV face detection.
"""
import logging
import numpy as np
from typing import List, Tuple, Optional

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

logger = logging.getLogger(__name__)

# Face detection using OpenCV Haar Cascade
_FACE_CASCADE = None


def _get_cascade():
    global _FACE_CASCADE
    if _FACE_CASCADE is None and CV2_AVAILABLE:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _FACE_CASCADE = cv2.CascadeClassifier(cascade_path)
    return _FACE_CASCADE


def detect_faces_cv(frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """Detect faces using OpenCV Haar Cascade. Returns list of (x, y, w, h)."""
    if not CV2_AVAILABLE:
        return []
    cascade = _get_cascade()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )
    if len(faces) == 0:
        return []
    return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]


def is_well_lit(frame: np.ndarray, min_brightness: int = 60) -> bool:
    """Check if the frame has sufficient lighting."""
    if not CV2_AVAILABLE:
        return True
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(gray.mean()) >= min_brightness


def is_sharp(frame: np.ndarray, threshold: float = 100.0) -> bool:
    """Check if the frame is sharp (not blurry) using Laplacian variance."""
    if not CV2_AVAILABLE:
        return True
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var()) >= threshold


def draw_face_box(
    frame: np.ndarray,
    faces: List[Tuple[int, int, int, int]],
    color: Tuple[int, int, int] = (0, 255, 0),
    label: str = "",
) -> np.ndarray:
    """Draw bounding boxes around detected faces."""
    if not CV2_AVAILABLE:
        return frame
    result = frame.copy()
    for (x, y, w, h) in faces:
        cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)
        if label:
            cv2.putText(
                result, label, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
            )
    return result
