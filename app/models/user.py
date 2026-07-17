"""
User model - represents the users table.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User domain model."""
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    role: str = "operator"
    kelas: Optional[str] = None
    is_active: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data.get("id"),
            username=data.get("username", ""),
            password_hash=data.get("password_hash", ""),
            role=data.get("role", "operator"),
            kelas=data.get("kelas"),
            is_active=data.get("is_active", 1),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "kelas": self.kelas,
            "is_active": self.is_active,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }

    def is_admin(self) -> bool:
        return self.role == "admin"
