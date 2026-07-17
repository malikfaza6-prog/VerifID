"""
Face recognizer - matches face encodings against known encodings from DB.
"""
import logging
import numpy as np
from typing import Optional, List, Tuple, Dict, Any

try:
    import face_recognition
    FR_AVAILABLE = True
except ImportError:
    FR_AVAILABLE = False

logger = logging.getLogger(__name__)


class RecognitionResult:
    """Result of a face recognition attempt."""
    def __init__(
        self,
        matched: bool,
        pegawai_id: Optional[int] = None,
        nama: str = "",
        nik: str = "",
        departemen: str = "",
        foto: Optional[str] = None,
        confidence: float = 0.0,
    ):
        self.matched = matched
        self.pegawai_id = pegawai_id
        self.nama = nama
        self.nik = nik
        self.departemen = departemen
        self.foto = foto
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matched": self.matched,
            "pegawai_id": self.pegawai_id,
            "nama": self.nama,
            "nik": self.nik,
            "departemen": self.departemen,
            "foto": self.foto,
            "confidence": round(self.confidence * 100, 1),
        }


def recognize_face(
    face_encoding: np.ndarray,
    known_encodings: List[dict],
    tolerance: float = 0.6,
) -> RecognitionResult:
    """
    Compare a face encoding against known encodings.
    
    Args:
        face_encoding: 128-d numpy array of the face to identify
        known_encodings: list of dicts with keys: pegawai_id, encoding (np.ndarray), 
                         nama, nik, departemen, foto
        tolerance: maximum face distance to consider a match (lower = stricter)
    
    Returns:
        RecognitionResult
    """
    if not FR_AVAILABLE or not known_encodings:
        return RecognitionResult(matched=False)

    try:
        db_encodings = [e["encoding"] for e in known_encodings]
        distances = face_recognition.face_distance(db_encodings, face_encoding)

        best_idx = int(np.argmin(distances))
        best_distance = float(distances[best_idx])

        if best_distance <= tolerance:
            best = known_encodings[best_idx]
            confidence = max(0.0, 1.0 - best_distance)
            return RecognitionResult(
                matched=True,
                pegawai_id=best.get("pegawai_id"),
                nama=best.get("nama", ""),
                nik=best.get("nik", ""),
                departemen=best.get("departemen", ""),
                foto=best.get("foto"),
                confidence=confidence,
            )
        return RecognitionResult(matched=False)

    except Exception as e:
        logger.error(f"Recognition error: {e}")
        return RecognitionResult(matched=False)
