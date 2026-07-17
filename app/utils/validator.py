"""
Input validators for the attendance system.
"""
import re
from typing import Tuple


def validate_employee(data: dict) -> Tuple[bool, str]:
    """Validate employee form data."""
    nik = data.get("nik", "").strip()
    nama = data.get("nama", "").strip()

    if not nik:
        return False, "NIK tidak boleh kosong."
    if not re.match(r"^\d{8,20}$", nik):
        return False, "NIK harus berupa angka 8-20 digit."
    if not nama:
        return False, "Nama tidak boleh kosong."
    if len(nama) < 3:
        return False, "Nama minimal 3 karakter."
    if len(nama) > 100:
        return False, "Nama maksimal 100 karakter."
    return True, ""


def validate_user(data: dict, is_create: bool = True) -> Tuple[bool, str]:
    """Validate user form data."""
    username = data.get("username", "").strip()
    password = data.get("password", "")
    role = data.get("role", "")
    kelas = data.get("kelas", "").strip() if data.get("kelas") else ""

    if not username:
        return False, "Username tidak boleh kosong."
    if not re.match(r"^[a-zA-Z0-9_]{3,50}$", username):
        return False, "Username hanya boleh huruf, angka, dan underscore (3-50 karakter)."
    if is_create and not password:
        return False, "Password tidak boleh kosong."
    if password and len(password) < 6:
        return False, "Password minimal 6 karakter."
    if role not in ("admin", "operator", "kelas"):
        return False, "Role tidak valid."
    if role == "kelas" and not kelas:
        return False, "Kelas/Prodi wajib diisi untuk akun bertipe Kelas."
    return True, ""


def validate_login(data: dict) -> Tuple[bool, str]:
    if not data.get("username"):
        return False, "Username tidak boleh kosong."
    if not data.get("password"):
        return False, "Password tidak boleh kosong."
    return True, ""


def validate_matkul(data: dict) -> Tuple[bool, str]:
    """Validate mata kuliah form data."""
    kode = data.get("kode", "").strip()
    nama = data.get("nama", "").strip()

    if not kode:
        return False, "Kode mata kuliah tidak boleh kosong."
    if len(kode) > 20:
        return False, "Kode mata kuliah maksimal 20 karakter."
    if not nama:
        return False, "Nama mata kuliah tidak boleh kosong."
    if len(nama) < 3:
        return False, "Nama mata kuliah minimal 3 karakter."
    return True, ""
