"""
Recognition service - face recognition during attendance scanning.
"""
import logging
import time
from datetime import date, datetime
from typing import Optional, Dict, Any, List

import numpy as np

from app.camera.encoder import get_face_encodings, bgr_to_rgb
from app.camera.detector import detect_faces_cv
from app.camera.recognizer import recognize_face, RecognitionResult
from app.services.encoding_service import EncodingService
from config import get_config

logger = logging.getLogger(__name__)
cfg = get_config()

# Cooldown tracking: {pegawai_id: last_recognized_timestamp}
_cooldown_tracker: Dict[int, float] = {}


class RecognitionService:
    """Business logic for real-time face recognition."""

    def __init__(self):
        self._enc_service = EncodingService()
        self._known_encodings: Dict[str, List[dict]] = {}
        self._encodings_loaded_at: Dict[str, float] = {}

    def _refresh_encodings(self, kelas: str = "", force: bool = False) -> None:
        """Refresh known encodings cache (per kelas) every 60 seconds."""
        now = time.time()
        last_loaded = self._encodings_loaded_at.get(kelas, 0)
        if force or (now - last_loaded) > 60:
            self._known_encodings[kelas] = self._enc_service.get_all_known_encodings(kelas=kelas)
            self._encodings_loaded_at[kelas] = now
            logger.info(
                f"Encodings refreshed for kelas='{kelas or 'ALL'}': "
                f"{len(self._known_encodings[kelas])} faces loaded."
            )

    def process_attendance_frame(self, frame_bgr: np.ndarray, kelas: str = "") -> dict:
        """
        Process a camera frame for attendance.
        `kelas` scopes recognition to mahasiswa of that prodi/kelas only
        (used when the kiosk session is logged in as a 'kelas' account).
        Returns dict with recognition result info.
        """
        self._refresh_encodings(kelas=kelas)

        faces = detect_faces_cv(frame_bgr)
        if not faces:
            return {"status": "no_face", "face_count": 0}

        frame_rgb = bgr_to_rgb(frame_bgr)
        encodings = get_face_encodings(frame_rgb)

        if not encodings:
            return {"status": "no_encoding", "face_count": len(faces)}

        # Use the first detected face
        face_enc = encodings[0]
        result = recognize_face(
            face_enc,
            self._known_encodings.get(kelas, []),
            tolerance=cfg.FACE_RECOGNITION_TOLERANCE,
        )

        if not result.matched:
            return {"status": "unknown", "face_count": len(faces), "result": result.to_dict()}

        # Check cooldown
        pid = result.pegawai_id
        if pid in _cooldown_tracker:
            elapsed = time.time() - _cooldown_tracker[pid]
            if elapsed < cfg.ATTENDANCE_COOLDOWN:
                remaining = int(cfg.ATTENDANCE_COOLDOWN - elapsed)
                return {
                    "status": "cooldown",
                    "face_count": len(faces),
                    "result": result.to_dict(),
                    "cooldown_remaining": remaining,
                }

        return {
            "status": "recognized",
            "face_count": len(faces),
            "result": result.to_dict(),
        }

    def mark_cooldown(self, pegawai_id: int) -> None:
        """Mark employee as recently processed to prevent double scanning."""
        _cooldown_tracker[pegawai_id] = time.time()

    def force_refresh(self) -> None:
        """Invalidate cached encodings for all kelas so next scan reloads fresh data."""
        self._known_encodings = {}
        self._encodings_loaded_at = {}
