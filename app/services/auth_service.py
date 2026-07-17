"""
Auth service - handles login, logout, session management.
"""
import logging
from typing import Optional, Tuple
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.security import verify_password, hash_password
from app.utils.validator import validate_login

logger = logging.getLogger(__name__)


class AuthService:
    """Business logic for authentication."""

    def __init__(self):
        self._repo = UserRepository()

    def login(self, username: str, password: str) -> Tuple[Optional[User], str]:
        """
        Authenticate a user.
        Returns (User, error_message). User is None on failure.
        """
        valid, msg = validate_login({"username": username, "password": password})
        if not valid:
            return None, msg

        user = self._repo.find_by_username(username)
        if not user:
            logger.warning(f"Login attempt with unknown username: {username}")
            return None, "Username atau password salah."

        if not user.is_active:
            return None, "Akun tidak aktif. Hubungi administrator."

        if not verify_password(password, user.password_hash):
            logger.warning(f"Failed login for user: {username}")
            return None, "Username atau password salah."

        logger.info(f"User {username} logged in successfully.")
        return user, ""

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self._repo.find_by_id(user_id)

    def log_activity(self, username: str, activity: str, ip: str = "") -> None:
        self._repo.log_activity(username, activity, ip)

    def get_recent_logs(self, limit: int = 10):
        return self._repo.get_recent_logs(limit)
