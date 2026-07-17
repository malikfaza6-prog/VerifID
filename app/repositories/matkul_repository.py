"""
Matkul repository - handles mata kuliah DB operations.
"""
import logging
from typing import Optional, List
from app.database.database import get_connection
from app.models.matkul import Matkul

logger = logging.getLogger(__name__)


class MatkulRepository:
    """Repository for Matkul CRUD operations."""

    def find_all(self) -> List[Matkul]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM matkul ORDER BY nama ASC")
            rows = cursor.fetchall()
            return [Matkul.from_dict(r) for r in rows]
        finally:
            cursor.close()
            conn.close()

    def find_by_id(self, matkul_id: int) -> Optional[Matkul]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM matkul WHERE id = %s", (matkul_id,))
            row = cursor.fetchone()
            return Matkul.from_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_by_kode(self, kode: str) -> Optional[Matkul]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM matkul WHERE kode = %s", (kode,))
            row = cursor.fetchone()
            return Matkul.from_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def create(self, m: Matkul) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO matkul (kode, nama) VALUES (%s, %s)",
                (m.kode, m.nama),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def update(self, m: Matkul) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE matkul SET kode=%s, nama=%s WHERE id=%s",
                (m.kode, m.nama, m.id),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete(self, matkul_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM matkul WHERE id = %s", (matkul_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
