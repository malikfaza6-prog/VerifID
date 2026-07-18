"""
Attendance service - business logic for recording attendance.
"""
import logging
from datetime import date, datetime, time as dtime
from typing import Tuple, Optional, List, Dict, Any

from app.models.attendance import Attendance
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.employee_repository import EmployeeRepository
from app.utils.helper import determine_attendance_status, paginate

logger = logging.getLogger(__name__)


class AttendanceService:
    """Business logic for attendance operations."""

    def __init__(self):
        self._att_repo = AttendanceRepository()
        self._emp_repo = EmployeeRepository()

    def get_matkul_attendance(
        self,
        matkul_id: int,
        search: str = "",
        tanggal_from: Optional[str] = None,
        tanggal_to: Optional[str] = None,
        page: int = 1,
        per_page: int = 15,
    ) -> Dict[str, Any]:
        """Riwayat absensi untuk satu matkul (dipakai dosen)."""
        records, total = self._att_repo.find_by_matkul_paginated(
            matkul_id, search, tanggal_from, tanggal_to, page, per_page
        )
        return {
            "data": [r.to_dict() for r in records],
            "meta": paginate(total, page, per_page),
        }

    def update_attendance_manual(
        self, att_id: int, matkul_id: int, status: str, jam_masuk: str
    ) -> Tuple[bool, str]:
        """Dosen mengoreksi status/jam kehadiran - hanya utk record di matkulnya sendiri."""
        att = self._att_repo.find_by_id(att_id)
        if not att:
            return False, "Data absensi tidak ditemukan."
        if att.matkul_id != matkul_id:
            return False, "Anda tidak memiliki akses untuk mengubah absensi ini."
        if status not in ("hadir", "terlambat", "pulang"):
            return False, "Status tidak valid."
        try:
            self._att_repo.update_manual(att_id, status, jam_masuk or None)
            logger.info(f"Absensi ID={att_id} dikoreksi manual jadi status={status}")
            return True, "Absensi berhasil diperbarui."
        except Exception as e:
            logger.error(f"Update manual attendance error: {e}")
            return False, "Gagal memperbarui absensi."

    def add_manual_attendance(
        self, matkul_id: int, pegawai_id: int, tanggal: str, jam_masuk: str, status: str
    ) -> Tuple[bool, str]:
        """Dosen menambahkan absensi manual untuk mahasiswa yang tidak sempat scan."""
        if status not in ("hadir", "terlambat", "pulang"):
            return False, "Status tidak valid."

        try:
            tgl = datetime.strptime(tanggal, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return False, "Tanggal tidak valid."

        existing = self._att_repo.find_today_by_employee_matkul(pegawai_id, tgl, matkul_id)
        if existing:
            return False, "Mahasiswa ini sudah memiliki absensi untuk mata kuliah & tanggal tersebut."

        att = Attendance(
            pegawai_id=pegawai_id,
            matkul_id=matkul_id,
            tanggal=tgl,
            jam_masuk=jam_masuk or None,
            confidence=None,
            status=status,
            device="manual-dosen",
        )
        try:
            att_id = self._att_repo.create(att)
            att.id = att_id
            logger.info(f"Absensi manual ditambahkan dosen: pegawai_id={pegawai_id}, matkul_id={matkul_id}")
            return True, "Absensi manual berhasil ditambahkan."
        except Exception as e:
            logger.error(f"Add manual attendance error: {e}")
            return False, "Gagal menambahkan absensi manual."

    def record_attendance(
        self,
        pegawai_id: int,
        matkul_id: int,
        confidence: float,
        device: str = "webcam",
    ) -> Tuple[bool, str, Optional[Attendance]]:
        """
        Record absensi mahasiswa untuk satu mata kuliah.
        Satu mahasiswa bisa absen beberapa matkul per hari, tapi tidak boleh
        absen dua kali untuk matkul yang sama di hari yang sama.
        Returns (success, message, attendance_record).
        """
        today = date.today()
        now = datetime.now().time()
        now_str = now.strftime("%H:%M:%S")

        existing = self._att_repo.find_today_by_employee_matkul(pegawai_id, today, matkul_id)
        if existing:
            matkul_label = f" ({existing.matkul_nama})" if existing.matkul_nama else ""
            return False, f"Sudah absen untuk mata kuliah ini hari ini{matkul_label}.", existing

        status = determine_attendance_status(now)
        att = Attendance(
            pegawai_id=pegawai_id,
            matkul_id=matkul_id,
            tanggal=today,
            jam_masuk=now,
            confidence=confidence,
            status=status,
            device=device,
        )
        try:
            att_id = self._att_repo.create(att)
            att.id = att_id
            logger.info(f"Absensi tercatat: pegawai_id={pegawai_id}, matkul_id={matkul_id}, status={status}")
            msg = f"Absensi berhasil. Status: {status.upper()}. Jam: {now_str}"
            return True, msg, att
        except Exception as e:
            logger.error(f"Record attendance error: {e}")
            return False, "Gagal menyimpan absensi.", None

    def get_paginated_history(
        self,
        search: str = "",
        departemen: str = "",
        tanggal_from: str = "",
        tanggal_to: str = "",
        page: int = 1,
        per_page: int = 10,
    ) -> Tuple[List[Attendance], Dict[str, Any]]:
        records, total = self._att_repo.find_all_paginated(
            search, departemen, tanggal_from or None, tanggal_to or None, page, per_page
        )
        meta = paginate(total, page, per_page)
        return records, meta

    def get_today_summary(self) -> dict:
        today = date.today()
        total_employees = self._emp_repo.count_all()
        summary = self._att_repo.get_today_summary(today)
        hadir = summary["hadir"]
        terlambat = summary["terlambat"]
        belum_hadir = max(0, total_employees - hadir)
        return {
            "total_pegawai": total_employees,
            "hadir": hadir,
            "terlambat": terlambat,
            "belum_hadir": belum_hadir,
        }

    def get_today_attendance_list(self) -> List[dict]:
        """Realtime status of every active mahasiswa for today (hadir/terlambat/belum)."""
        today = date.today()
        rows = self._att_repo.get_today_status_all_employees(today)
        result = []
        for r in rows:
            status = r["status"] or "belum"
            result.append({
                "nik": r["nik"],
                "nama": r["nama"],
                "departemen": r["departemen"],
                "jabatan": r["jabatan"],
                "foto": r["foto"],
                "jam_masuk": r["jam_masuk"],
                "jam_keluar": r["jam_keluar"],
                "status": status,
                "matkul_nama": r.get("matkul_nama"),
                "matkul_count": r.get("matkul_count") or 0,
            })
        return result

    def get_weekly_chart_data(self) -> List[dict]:

        rows = self._att_repo.get_weekly_chart_data()
        result = []
        for r in rows:
            result.append({
                "tanggal": str(r["tanggal"]),
                "total": int(r["total"]),
                "terlambat": int(r["terlambat"] or 0),
            })
        return result

    def get_all_for_export(self, **kwargs) -> List[Attendance]:
        return self._att_repo.find_all_for_export(**kwargs)
