"""
Attendance model - represents the attendance table.
"""
from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional


@dataclass
class Attendance:
    """Attendance domain model."""
    id: Optional[int] = None
    pegawai_id: Optional[int] = None
    matkul_id: Optional[int] = None
    tanggal: Optional[date] = None
    jam_masuk: Optional[time] = None
    jam_keluar: Optional[time] = None
    confidence: Optional[float] = None
    status: str = "hadir"
    device: Optional[str] = None
    created_at: Optional[datetime] = None
    # Virtual fields from JOIN
    nama: str = ""
    nik: str = ""
    departemen: str = ""
    foto: Optional[str] = None
    matkul_nama: str = ""
    matkul_kode: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Attendance":
        return cls(
            id=data.get("id"),
            pegawai_id=data.get("pegawai_id"),
            matkul_id=data.get("matkul_id"),
            tanggal=data.get("tanggal"),
            jam_masuk=data.get("jam_masuk"),
            jam_keluar=data.get("jam_keluar"),
            confidence=data.get("confidence"),
            status=data.get("status", "hadir"),
            device=data.get("device"),
            created_at=data.get("created_at"),
            nama=data.get("nama", ""),
            nik=data.get("nik", ""),
            departemen=data.get("departemen", ""),
            foto=data.get("foto"),
            matkul_nama=data.get("matkul_nama", ""),
            matkul_kode=data.get("matkul_kode", ""),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pegawai_id": self.pegawai_id,
            "matkul_id": self.matkul_id,
            "matkul_nama": self.matkul_nama,
            "matkul_kode": self.matkul_kode,
            "tanggal": str(self.tanggal) if self.tanggal else None,
            "jam_masuk": str(self.jam_masuk) if self.jam_masuk else None,
            "jam_keluar": str(self.jam_keluar) if self.jam_keluar else None,
            "confidence": round(self.confidence * 100, 1) if self.confidence else None,
            "status": self.status,
            "device": self.device,
            "nama": self.nama,
            "nik": self.nik,
            "departemen": self.departemen,
            "foto": self.foto,
        }
