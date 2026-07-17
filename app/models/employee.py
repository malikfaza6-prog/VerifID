"""
Employee model - represents the pegawai table.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Employee:
    """Employee domain model."""
    id: Optional[int] = None
    nik: str = ""
    nama: str = ""
    departemen: str = ""
    jabatan: str = ""
    foto: Optional[str] = None
    status: str = "aktif"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    has_encoding: bool = False  # virtual field from JOIN

    @classmethod
    def from_dict(cls, data: dict) -> "Employee":
        return cls(
            id=data.get("id"),
            nik=data.get("nik", ""),
            nama=data.get("nama", ""),
            departemen=data.get("departemen", ""),
            jabatan=data.get("jabatan", ""),
            foto=data.get("foto"),
            status=data.get("status", "aktif"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            has_encoding=bool(data.get("has_encoding", False)),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nik": self.nik,
            "nama": self.nama,
            "departemen": self.departemen,
            "jabatan": self.jabatan,
            "foto": self.foto,
            "status": self.status,
            "has_encoding": self.has_encoding,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }
