"""
Encoding repository - handles face encoding DB operations.
"""
import logging
from typing import Optional, List
from app.database.database import get_connection
from app.models.face_encoding import FaceEncoding

logger = logging.getLogger(__name__)


class EncodingRepository:
    """Repository for FaceEncoding CRUD operations."""

    def find_by_employee(self, pegawai_id: int) -> Optional[FaceEncoding]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM face_encodings WHERE pegawai_id = %s ORDER BY created_at DESC LIMIT 1",
                (pegawai_id,),
            )
            row = cursor.fetchone()
            return FaceEncoding.from_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_all(self, kelas: str = "") -> List[FaceEncoding]:
        """Load all encodings for recognition (bulk load).
        If `kelas` is provided, only load mahasiswa whose `departemen`
        (dipakai sebagai kode kelas/prodi) matches - untuk kiosk yang
        login sebagai akun kelas tertentu (mis. FTI).
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """SELECT fe.*, p.nama, p.nik, p.departemen, p.foto
                       FROM face_encodings fe
                       JOIN pegawai p ON p.id = fe.pegawai_id
                       WHERE p.status = 'aktif'"""
            params: tuple = ()
            if kelas:
                query += " AND TRIM(LOWER(p.departemen)) = TRIM(LOWER(%s))"
                params = (kelas,)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            encodings = []
            for r in rows:
                enc = FaceEncoding.from_dict(r)
                enc.__dict__.update({
                    "nama": r.get("nama", ""),
                    "nik": r.get("nik", ""),
                    "departemen": r.get("departemen", ""),
                    "foto": r.get("foto"),
                })
                encodings.append(enc)
            return encodings
        finally:
            cursor.close()
            conn.close()

    def save(self, enc: FaceEncoding) -> int:
        """Insert or replace encoding for an employee."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Delete existing first
            cursor.execute("DELETE FROM face_encodings WHERE pegawai_id = %s", (enc.pegawai_id,))
            cursor.execute(
                "INSERT INTO face_encodings (pegawai_id, encoding) VALUES (%s, %s)",
                (enc.pegawai_id, enc.encoding),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete_by_employee(self, pegawai_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM face_encodings WHERE pegawai_id = %s", (pegawai_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def has_encoding(self, pegawai_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM face_encodings WHERE pegawai_id = %s", (pegawai_id,)
            )
            return cursor.fetchone()[0] > 0
        finally:
            cursor.close()
            conn.close()
