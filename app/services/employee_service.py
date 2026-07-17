"""
Employee service - business logic for employee management.
"""
import logging
import os
from typing import Optional, Tuple, List, Dict, Any
from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.utils.validator import validate_employee
from app.utils.image_utils import save_profile_photo, delete_photo, allowed_file
from app.utils.helper import paginate, generate_unique_filename
from config import get_config

logger = logging.getLogger(__name__)
cfg = get_config()


class EmployeeService:
    """Business logic for employee CRUD operations."""

    def __init__(self):
        self._repo = EmployeeRepository()

    def get_paginated(
        self, search: str = "", page: int = 1, per_page: int = 10
    ) -> Tuple[List[Employee], Dict[str, Any]]:
        employees, total = self._repo.find_all_paginated(search, page, per_page)
        meta = paginate(total, page, per_page)
        return employees, meta

    def get_by_id(self, emp_id: int) -> Optional[Employee]:
        return self._repo.find_by_id(emp_id)

    def get_all_active(self) -> List[Employee]:
        return self._repo.find_all_active()

    def get_departments(self) -> List[str]:
        return self._repo.get_departments()

    def create(
        self, data: dict, file_storage=None
    ) -> Tuple[Optional[int], str]:
        valid, msg = validate_employee(data)
        if not valid:
            return None, msg

        # Check NIK uniqueness
        existing = self._repo.find_by_nik(data["nik"].strip())
        if existing:
            return None, f"NIK {data['nik']} sudah terdaftar."

        emp = Employee(
            nik=data["nik"].strip(),
            nama=data["nama"].strip(),
            departemen=data.get("departemen", "").strip(),
            jabatan=data.get("jabatan", "").strip(),
            status=data.get("status", "aktif"),
        )

        # Handle photo upload
        if file_storage and file_storage.filename:
            if not allowed_file(file_storage.filename):
                return None, "Format foto tidak didukung. Gunakan JPG, PNG, atau WEBP."
            filename = generate_unique_filename(file_storage.filename)
            upload_dir = os.path.join(cfg.UPLOAD_FOLDER, "photos")
            saved = save_profile_photo(file_storage, upload_dir, filename)
            if saved:
                emp.foto = f"photos/{filename}"

        try:
            new_id = self._repo.create(emp)
            logger.info(f"Employee created: ID={new_id}, NIK={emp.nik}, Nama={emp.nama}")
            return new_id, ""
        except Exception as e:
            logger.error(f"Create employee error: {e}")
            return None, "Gagal menyimpan data pegawai."

    def update(
        self, emp_id: int, data: dict, file_storage=None
    ) -> Tuple[bool, str]:
        valid, msg = validate_employee(data)
        if not valid:
            return False, msg

        emp = self._repo.find_by_id(emp_id)
        if not emp:
            return False, "Pegawai tidak ditemukan."

        # NIK uniqueness check (exclude self)
        existing = self._repo.find_by_nik(data["nik"].strip())
        if existing and existing.id != emp_id:
            return False, f"NIK {data['nik']} sudah digunakan oleh pegawai lain."

        old_foto = emp.foto
        emp.nik = data["nik"].strip()
        emp.nama = data["nama"].strip()
        emp.departemen = data.get("departemen", "").strip()
        emp.jabatan = data.get("jabatan", "").strip()
        emp.status = data.get("status", "aktif")

        # Handle photo upload
        if file_storage and file_storage.filename:
            if not allowed_file(file_storage.filename):
                return False, "Format foto tidak didukung."
            filename = generate_unique_filename(file_storage.filename)
            upload_dir = os.path.join(cfg.UPLOAD_FOLDER, "photos")
            saved = save_profile_photo(file_storage, upload_dir, filename)
            if saved:
                emp.foto = f"photos/{filename}"
                # Delete old photo
                if old_foto:
                    delete_photo(cfg.UPLOAD_FOLDER, old_foto)

        try:
            success = self._repo.update(emp)
            if success:
                logger.info(f"Employee updated: ID={emp_id}")
            return success, ""
        except Exception as e:
            logger.error(f"Update employee error: {e}")
            return False, "Gagal memperbarui data pegawai."

    def delete(self, emp_id: int) -> Tuple[bool, str]:
        emp = self._repo.find_by_id(emp_id)
        if not emp:
            return False, "Pegawai tidak ditemukan."
        try:
            success = self._repo.delete(emp_id)
            if success and emp.foto:
                delete_photo(cfg.UPLOAD_FOLDER, emp.foto)
            logger.info(f"Employee deleted: ID={emp_id}")
            return success, ""
        except Exception as e:
            logger.error(f"Delete employee error: {e}")
            return False, "Gagal menghapus pegawai."
