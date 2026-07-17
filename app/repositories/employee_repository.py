"""
Employee repository - handles all employee DB operations.
"""
import logging
from typing import Optional, List, Tuple
from app.database.database import get_connection
from app.models.employee import Employee

logger = logging.getLogger(__name__)


class EmployeeRepository:
    """Repository for Employee CRUD operations."""

    def find_by_id(self, emp_id: int) -> Optional[Employee]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT p.*, 
                          (SELECT COUNT(*) FROM face_encodings fe WHERE fe.pegawai_id = p.id) > 0 AS has_encoding
                   FROM pegawai p WHERE p.id = %s""",
                (emp_id,),
            )
            row = cursor.fetchone()
            return Employee.from_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_by_nik(self, nik: str) -> Optional[Employee]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM pegawai WHERE nik = %s", (nik,))
            row = cursor.fetchone()
            return Employee.from_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_all_paginated(
        self, search: str = "", page: int = 1, per_page: int = 10
    ) -> Tuple[List[Employee], int]:
        """Returns employees and total count for pagination."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            offset = (page - 1) * per_page
            search_param = f"%{search}%"

            # Count
            cursor.execute(
                """SELECT COUNT(*) AS total FROM pegawai
                   WHERE nama LIKE %s OR nik LIKE %s OR departemen LIKE %s""",
                (search_param, search_param, search_param),
            )
            total = cursor.fetchone()["total"]

            # Data
            cursor.execute(
                """SELECT p.*, 
                          (SELECT COUNT(*) FROM face_encodings fe WHERE fe.pegawai_id = p.id) > 0 AS has_encoding
                   FROM pegawai p
                   WHERE p.nama LIKE %s OR p.nik LIKE %s OR p.departemen LIKE %s
                   ORDER BY p.created_at DESC
                   LIMIT %s OFFSET %s""",
                (search_param, search_param, search_param, per_page, offset),
            )
            rows = cursor.fetchall()
            return [Employee.from_dict(r) for r in rows], total
        finally:
            cursor.close()
            conn.close()

    def find_all_active(self) -> List[Employee]:
        """Get all active employees (for dropdowns)."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM pegawai WHERE status='aktif' ORDER BY nama ASC"
            )
            return [Employee.from_dict(r) for r in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def count_all(self) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM pegawai WHERE status='aktif'")
            return cursor.fetchone()[0]
        finally:
            cursor.close()
            conn.close()

    def create(self, emp: Employee) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO pegawai (nik, nama, departemen, jabatan, foto, status)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (emp.nik, emp.nama, emp.departemen, emp.jabatan, emp.foto, emp.status),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def update(self, emp: Employee) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """UPDATE pegawai SET nik=%s, nama=%s, departemen=%s, jabatan=%s,
                   foto=%s, status=%s WHERE id=%s""",
                (emp.nik, emp.nama, emp.departemen, emp.jabatan, emp.foto, emp.status, emp.id),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete(self, emp_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM pegawai WHERE id = %s", (emp_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def get_departments(self) -> List[str]:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT departemen FROM pegawai WHERE departemen IS NOT NULL ORDER BY departemen")
            return [r[0] for r in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()
