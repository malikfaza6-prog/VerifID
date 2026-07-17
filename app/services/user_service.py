"""
User management service - CRUD for admin/operator accounts.
"""
import logging
from typing import Optional, Tuple, List

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.security import hash_password
from app.utils.validator import validate_user

logger = logging.getLogger(__name__)


class UserManagementService:
    """Business logic for managing user accounts."""

    def __init__(self):
        self._repo = UserRepository()

    def get_all(self) -> List[User]:
        return self._repo.find_all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._repo.find_by_id(user_id)

    def create(self, data: dict) -> Tuple[Optional[int], str]:
        valid, msg = validate_user(data, is_create=True)
        if not valid:
            return None, msg

        existing = self._repo.find_by_username(data["username"].strip())
        if existing:
            return None, f"Username '{data['username']}' sudah digunakan."

        user = User(
            username=data["username"].strip(),
            password_hash=hash_password(data["password"]),
            role=data["role"],
            kelas=(data.get("kelas") or "").strip() or None,
        )
        try:
            new_id = self._repo.create(user)
            logger.info(f"User created: {user.username} ({user.role})")
            return new_id, ""
        except Exception as e:
            logger.error(f"Create user error: {e}")
            return None, "Gagal membuat akun user."

    def update(self, user_id: int, data: dict) -> Tuple[bool, str]:
        is_create = bool(data.get("password"))
        valid, msg = validate_user(data, is_create=False)
        if not valid:
            return False, msg

        user = self._repo.find_by_id(user_id)
        if not user:
            return False, "User tidak ditemukan."

        existing = self._repo.find_by_username(data["username"].strip())
        if existing and existing.id != user_id:
            return False, f"Username '{data['username']}' sudah digunakan."

        user.username = data["username"].strip()
        user.role = data["role"]
        user.kelas = (data.get("kelas") or "").strip() or None
        user.is_active = int(data.get("is_active", 1))
        if data.get("password"):
            user.password_hash = hash_password(data["password"])

        try:
            success = self._repo.update(user)
            logger.info(f"User updated: ID={user_id}")
            return success, ""
        except Exception as e:
            logger.error(f"Update user error: {e}")
            return False, "Gagal memperbarui user."

    def delete(self, user_id: int, current_user_id: int) -> Tuple[bool, str]:
        if user_id == current_user_id:
            return False, "Tidak dapat menghapus akun sendiri."
        try:
            success = self._repo.delete(user_id)
            logger.info(f"User deleted: ID={user_id}")
            return success, ""
        except Exception as e:
            logger.error(f"Delete user error: {e}")
            return False, "Gagal menghapus user."
