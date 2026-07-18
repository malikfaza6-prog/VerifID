"""
Attendance repository - handles all attendance DB operations.
"""
import logging
from datetime import date, datetime
from typing import Optional, List, Tuple
from app.database.database import get_connection
from app.models.attendance import Attendance

logger = logging.getLogger(__name__)


class AttendanceRepository:
    """Repository for Attendance CRUD operations."""

    def find_by_id(self, att_id: int) -> Optional[Attendance]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT a.*, p.nama, p.nik, p.departemen, p.foto,
                          m.nama AS matkul_nama, m.kode AS matkul_kode
                   FROM attendance a
                   JOIN pegawai p ON p.id = a.pegawai_id
                   LEFT JOIN matkul m ON m.id = a.matkul_id
                   WHERE a.id = %s""",
                (att_id,),
            )
            row = cursor.fetchone()
            return Attendance.from_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_by_matkul_paginated(
        self,
        matkul_id: int,
        search: str = "",
        tanggal_from: Optional[str] = None,
        tanggal_to: Optional[str] = None,
        page: int = 1,
        per_page: int = 15,
    ) -> Tuple[List[Attendance], int]:
        """Riwayat absensi khusus untuk satu matkul (dipakai halaman dosen)."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            offset = (page - 1) * per_page
            params = [matkul_id]
            conditions = ["a.matkul_id = %s"]

            if search:
                conditions.append("(p.nama LIKE %s OR p.nik LIKE %s)")
                params += [f"%{search}%", f"%{search}%"]
            if tanggal_from:
                conditions.append("a.tanggal >= %s")
                params.append(tanggal_from)
            if tanggal_to:
                conditions.append("a.tanggal <= %s")
                params.append(tanggal_to)

            where_clause = " AND ".join(conditions)

            cursor.execute(
                f"SELECT COUNT(*) AS total FROM attendance a JOIN pegawai p ON p.id = a.pegawai_id WHERE {where_clause}",
                params,
            )
            total = cursor.fetchone()["total"]

            cursor.execute(
                f"""SELECT a.*, p.nama, p.nik, p.departemen, p.foto,
                           m.nama AS matkul_nama, m.kode AS matkul_kode
                    FROM attendance a
                    JOIN pegawai p ON p.id = a.pegawai_id
                    LEFT JOIN matkul m ON m.id = a.matkul_id
                    WHERE {where_clause}
                    ORDER BY a.tanggal DESC, a.jam_masuk DESC
                    LIMIT %s OFFSET %s""",
                params + [per_page, offset],
            )
            rows = cursor.fetchall()
            return [Attendance.from_dict(r) for r in rows], total
        finally:
            cursor.close()
            conn.close()

    def update_manual(self, att_id: int, status: str, jam_masuk: Optional[str]) -> bool:
        """Dosen mengoreksi status/jam kehadiran secara manual."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE attendance SET status=%s, jam_masuk=%s WHERE id=%s",
                (status, jam_masuk, att_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def find_today_by_employee_matkul(self, pegawai_id: int, today: date, matkul_id: int) -> Optional[Attendance]:
        """Check whether the student has already absen for this matkul today."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT a.*, p.nama, p.nik, p.departemen, p.foto,
                          m.nama AS matkul_nama, m.kode AS matkul_kode
                   FROM attendance a
                   JOIN pegawai p ON p.id = a.pegawai_id
                   LEFT JOIN matkul m ON m.id = a.matkul_id
                   WHERE a.pegawai_id = %s AND a.tanggal = %s AND a.matkul_id <=> %s
                   LIMIT 1""",
                (pegawai_id, today, matkul_id),
            )
            row = cursor.fetchone()
            return Attendance.from_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_all_paginated(
        self,
        search: str = "",
        departemen: str = "",
        tanggal_from: Optional[str] = None,
        tanggal_to: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> Tuple[List[Attendance], int]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            offset = (page - 1) * per_page
            params = []
            conditions = ["1=1"]

            if search:
                conditions.append("(p.nama LIKE %s OR p.nik LIKE %s)")
                params += [f"%{search}%", f"%{search}%"]
            if departemen:
                conditions.append("p.departemen = %s")
                params.append(departemen)
            if tanggal_from:
                conditions.append("a.tanggal >= %s")
                params.append(tanggal_from)
            if tanggal_to:
                conditions.append("a.tanggal <= %s")
                params.append(tanggal_to)

            where_clause = " AND ".join(conditions)

            cursor.execute(
                f"SELECT COUNT(*) AS total FROM attendance a JOIN pegawai p ON p.id = a.pegawai_id WHERE {where_clause}",
                params,
            )
            total = cursor.fetchone()["total"]

            cursor.execute(
                f"""SELECT a.*, p.nama, p.nik, p.departemen, p.foto,
                           m.nama AS matkul_nama, m.kode AS matkul_kode
                    FROM attendance a
                    JOIN pegawai p ON p.id = a.pegawai_id
                    LEFT JOIN matkul m ON m.id = a.matkul_id
                    WHERE {where_clause}
                    ORDER BY a.tanggal DESC, a.jam_masuk DESC
                    LIMIT %s OFFSET %s""",
                params + [per_page, offset],
            )
            rows = cursor.fetchall()
            return [Attendance.from_dict(r) for r in rows], total
        finally:
            cursor.close()
            conn.close()

    def get_today_summary(self, today: date) -> dict:
        """Summary based on DISTINCT students (a student may absen for several
        mata kuliah in one day, but should only be counted once for hadir/terlambat)."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT
                      COUNT(DISTINCT a.pegawai_id) AS hadir,
                      COUNT(DISTINCT CASE WHEN a.status = 'terlambat' THEN a.pegawai_id END) AS terlambat
                   FROM attendance a
                   WHERE a.tanggal = %s AND a.status IN ('hadir', 'terlambat')""",
                (today,),
            )
            row = cursor.fetchone()
            return {
                "hadir": int(row["hadir"] or 0),
                "terlambat": int(row["terlambat"] or 0),
            }
        finally:
            cursor.close()
            conn.close()

    def get_today_status_all_employees(self, today: date) -> List[dict]:
        """Return every active mahasiswa joined with their latest attendance
        scan today (if any) - used for the dashboard status table."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT p.id, p.nik, p.nama, p.departemen, p.jabatan, p.foto,
                          latest.jam_masuk, latest.jam_keluar, latest.status,
                          latest.matkul_nama, latest.matkul_count
                   FROM pegawai p
                   LEFT JOIN (
                        SELECT a.pegawai_id, a.jam_masuk, a.jam_keluar, a.status,
                               m.nama AS matkul_nama,
                               cnt.matkul_count,
                               ROW_NUMBER() OVER (
                                   PARTITION BY a.pegawai_id
                                   ORDER BY a.created_at DESC, a.id DESC
                               ) AS rn
                        FROM attendance a
                        LEFT JOIN matkul m ON m.id = a.matkul_id
                        JOIN (
                            SELECT pegawai_id, COUNT(*) AS matkul_count
                            FROM attendance WHERE tanggal = %s GROUP BY pegawai_id
                        ) cnt ON cnt.pegawai_id = a.pegawai_id
                        WHERE a.tanggal = %s
                   ) latest ON latest.pegawai_id = p.id AND latest.rn = 1
                   WHERE p.status = 'aktif'
                   ORDER BY
                          CASE WHEN latest.status IS NULL THEN 1 ELSE 0 END,
                          p.nama ASC""",
                (today, today),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_weekly_chart_data(self) -> List[dict]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT DATE(tanggal) AS tanggal,
                          COUNT(DISTINCT pegawai_id) AS total,
                          COUNT(DISTINCT CASE WHEN status='terlambat' THEN pegawai_id END) AS terlambat
                   FROM attendance
                   WHERE tanggal >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                   GROUP BY DATE(tanggal)
                   ORDER BY tanggal ASC"""
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def create(self, att: Attendance) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO attendance (pegawai_id, matkul_id, tanggal, jam_masuk, jam_keluar, confidence, status, device)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (att.pegawai_id, att.matkul_id, att.tanggal, att.jam_masuk, att.jam_keluar,
                 att.confidence, att.status, att.device),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def find_all_for_export(
        self,
        search: str = "",
        departemen: str = "",
        tanggal_from: Optional[str] = None,
        tanggal_to: Optional[str] = None,
    ) -> List[Attendance]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            params = []
            conditions = ["1=1"]

            if search:
                conditions.append("(p.nama LIKE %s OR p.nik LIKE %s)")
                params += [f"%{search}%", f"%{search}%"]
            if departemen:
                conditions.append("p.departemen = %s")
                params.append(departemen)
            if tanggal_from:
                conditions.append("a.tanggal >= %s")
                params.append(tanggal_from)
            if tanggal_to:
                conditions.append("a.tanggal <= %s")
                params.append(tanggal_to)

            where_clause = " AND ".join(conditions)
            cursor.execute(
                f"""SELECT a.*, p.nama, p.nik, p.departemen, p.foto,
                           m.nama AS matkul_nama, m.kode AS matkul_kode
                    FROM attendance a
                    JOIN pegawai p ON p.id = a.pegawai_id
                    LEFT JOIN matkul m ON m.id = a.matkul_id
                    WHERE {where_clause}
                    ORDER BY a.tanggal DESC, p.nama ASC""",
                params,
            )
            return [Attendance.from_dict(r) for r in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()
