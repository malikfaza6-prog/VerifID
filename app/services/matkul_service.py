"""
Matkul service - business logic for mata kuliah management.
"""
import logging
from typing import Optional, Tuple, List

from app.models.matkul import Matkul
from app.repositories.matkul_repository import MatkulRepository
from app.utils.validator import validate_matkul

logger = logging.getLogger(__name__)


class MatkulService:
    """Business logic for mata kuliah CRUD operations."""

    def __init__(self):
        self._repo = MatkulRepository()

    def get_all(self) -> List[Matkul]:
        return self._repo.find_all()

    def get_by_id(self, matkul_id: int) -> Optional[Matkul]:
        return self._repo.find_by_id(matkul_id)

    def create(self, data: dict) -> Tuple[Optional[int], str]:
        valid, msg = validate_matkul(data)
        if not valid:
            return None, msg

        existing = self._repo.find_by_kode(data["kode"].strip())
        if existing:
            return None, f"Kode mata kuliah '{data['kode']}' sudah terdaftar."

        m = Matkul(kode=data["kode"].strip(), nama=data["nama"].strip())
        try:
            new_id = self._repo.create(m)
            logger.info(f"Matkul created: {m.kode} - {m.nama}")
            return new_id, ""
        except Exception as e:
            logger.error(f"Create matkul error: {e}")
            return None, "Gagal menyimpan mata kuliah."

    def update(self, matkul_id: int, data: dict) -> Tuple[bool, str]:
        valid, msg = validate_matkul(data)
        if not valid:
            return False, msg

        m = self._repo.find_by_id(matkul_id)
        if not m:
            return False, "Mata kuliah tidak ditemukan."

        existing = self._repo.find_by_kode(data["kode"].strip())
        if existing and existing.id != matkul_id:
            return False, f"Kode mata kuliah '{data['kode']}' sudah digunakan."

        m.kode = data["kode"].strip()
        m.nama = data["nama"].strip()
        try:
            success = self._repo.update(m)
            return success, ""
        except Exception as e:
            logger.error(f"Update matkul error: {e}")
            return False, "Gagal memperbarui mata kuliah."

    def delete(self, matkul_id: int) -> Tuple[bool, str]:
        try:
            success = self._repo.delete(matkul_id)
            return success, ""
        except Exception as e:
            logger.error(f"Delete matkul error: {e}")
            return False, "Gagal menghapus mata kuliah."
