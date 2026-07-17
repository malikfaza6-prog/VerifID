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
