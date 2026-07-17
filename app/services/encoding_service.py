"""
Encoding service - business logic for face registration workflow.
"""
import logging
import numpy as np
from typing import Optional, Tuple, List

from app.repositories.encoding_repository import EncodingRepository
from app.repositories.employee_repository import EmployeeRepository
from app.models.face_encoding import FaceEncoding
from app.camera.encoder import get_face_encodings, average_encoding, bgr_to_rgb
from app.camera.detector import is_well_lit, is_sharp

logger = logging.getLogger(__name__)


class EncodingService:
    """Business logic for face encoding registration."""

    def __init__(self):
        self._enc_repo = EncodingRepository()
        self._emp_repo = EmployeeRepository()

    def process_frame_for_registration(self, frame_bgr: np.ndarray) -> dict:
        """
        Process a single frame during registration.
        Returns dict with status, face_count, quality_ok, encoding (if detected).
        """
        if not is_well_lit(frame_bgr):
            return {"status": "poor_lighting", "face_count": 0, "quality_ok": False}

        if not is_sharp(frame_bgr):
            return {"status": "blur", "face_count": 0, "quality_ok": False}

        frame_rgb = bgr_to_rgb(frame_bgr)
        try:
            import face_recognition
            locations = face_recognition.face_locations(frame_rgb, model="hog")
        except Exception:
            return {"status": "error", "face_count": 0, "quality_ok": False}

        face_count = len(locations)

        if face_count == 0:
            return {"status": "no_face", "face_count": 0, "quality_ok": False}

        if face_count > 1:
            return {"status": "multiple_faces", "face_count": face_count, "quality_ok": False}

        encodings = get_face_encodings(frame_rgb)
        if not encodings:
            return {"status": "encoding_failed", "face_count": 1, "quality_ok": False}

        return {
            "status": "ok",
            "face_count": 1,
            "quality_ok": True,
            "encoding": encodings[0],
        }

    def save_registration(
        self, pegawai_id: int, encodings: List[np.ndarray]
    ) -> Tuple[bool, str]:
        """Average collected encodings and save to DB."""
        if not encodings:
            return False, "Tidak ada encoding yang berhasil dikumpulkan."

        emp = self._emp_repo.find_by_id(pegawai_id)
        if not emp:
            return False, "Pegawai tidak ditemukan."

        avg = average_encoding(encodings)
        if avg is None:
            return False, "Gagal membuat rata-rata encoding."

        enc = FaceEncoding(
            pegawai_id=pegawai_id,
            encoding=FaceEncoding.encode_numpy(avg),
        )
        try:
            self._enc_repo.save(enc)
            logger.info(f"Face encoding saved for employee ID={pegawai_id}")
            return True, "Wajah berhasil didaftarkan."
        except Exception as e:
            logger.error(f"Save encoding error: {e}")
            return False, "Gagal menyimpan encoding ke database."

    def has_encoding(self, pegawai_id: int) -> bool:
        return self._enc_repo.has_encoding(pegawai_id)

    def delete_encoding(self, pegawai_id: int) -> bool:
        return self._enc_repo.delete_by_employee(pegawai_id)

    def get_all_known_encodings(self, kelas: str = "") -> List[dict]:
        """Load all face encodings for recognition, returning list of dicts.
        Scoped to a `kelas` (prodi) when provided.
        """
        encodings = self._enc_repo.find_all(kelas=kelas)
        result = []
        for enc_obj in encodings:
            arr = enc_obj.get_numpy_encoding()
            if arr is not None:
                result.append({
                    "pegawai_id": enc_obj.pegawai_id,
                    "encoding": arr,
                    "nama": getattr(enc_obj, "nama", ""),
                    "nik": getattr(enc_obj, "nik", ""),
                    "departemen": getattr(enc_obj, "departemen", ""),
                    "foto": getattr(enc_obj, "foto", None),
                })
        return result
