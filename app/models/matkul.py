"""
Matkul (mata kuliah) model - represents the matkul table.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Matkul:
    """Mata kuliah domain model."""
    id: Optional[int] = None
    kode: str = ""
    nama: str = ""
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Matkul":
        return cls(
            id=data.get("id"),
            kode=data.get("kode", ""),
            nama=data.get("nama", ""),
            created_at=data.get("created_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kode": self.kode,
            "nama": self.nama,
            "created_at": str(self.created_at) if self.created_at else None,
        }
