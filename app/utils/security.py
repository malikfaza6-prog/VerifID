"""
Security utilities - password hashing, token generation.
"""
import secrets
import bcrypt
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain-text password against its hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_hex(length)
