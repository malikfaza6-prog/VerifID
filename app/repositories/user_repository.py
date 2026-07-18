"""
User repository - handles all user DB operations.
"""
import logging
from typing import Optional, List
from app.database.database import get_connection
from app.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User CRUD operations."""

    def find_by_id(self, user_id: int) -> Optional[User]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT u.*, m.nama AS matkul_nama, m.kode AS matkul_kode
                   FROM users u
                   LEFT JOIN matkul m ON m.id = u.matkul_id
                   WHERE u.id = %s""",
                (user_id,),
            )
            row = cursor.fetchone()
            return User.from_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_by_username(self, username: str) -> Optional[User]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT u.*, m.nama AS matkul_nama, m.kode AS matkul_kode
                   FROM users u
                   LEFT JOIN matkul m ON m.id = u.matkul_id
                   WHERE u.username = %s""",
                (username,),
            )
            row = cursor.fetchone()
            return User.from_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_all(self) -> List[User]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT u.*, m.nama AS matkul_nama, m.kode AS matkul_kode
                   FROM users u
                   LEFT JOIN matkul m ON m.id = u.matkul_id
                   ORDER BY u.created_at DESC"""
            )
            rows = cursor.fetchall()
            return [User.from_dict(r) for r in rows]
        finally:
            cursor.close()
            conn.close()

    def find_by_matkul_id(self, matkul_id: int) -> Optional[User]:
        """Cari akun dosen yang sudah mengampu matkul tertentu (untuk cek 1 matkul = 1 dosen)."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM users WHERE matkul_id = %s AND role = 'dosen' LIMIT 1",
                (matkul_id,),
            )
            row = cursor.fetchone()
            return User.from_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def create(self, user: User) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, kelas, matkul_id) VALUES (%s, %s, %s, %s, %s)",
                (user.username, user.password_hash, user.role, user.kelas, user.matkul_id),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def update(self, user: User) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """UPDATE users SET username=%s, password_hash=%s, role=%s, kelas=%s, matkul_id=%s, is_active=%s
                   WHERE id=%s""",
                (user.username, user.password_hash, user.role, user.kelas, user.matkul_id, user.is_active, user.id),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete(self, user_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def clear_matkul_assignment(self, matkul_id: int) -> None:
        """Lepaskan dosen dari matkul yang akan dihapus (set matkul_id jadi NULL)."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET matkul_id = NULL WHERE matkul_id = %s", (matkul_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def log_activity(self, user: str, activity: str, ip_address: str = "") -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO logs (user, activity, ip_address) VALUES (%s, %s, %s)",
                (user, activity, ip_address),
            )
            conn.commit()
        except Exception as e:
            logger.warning(f"Failed to log activity: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def get_recent_logs(self, limit: int = 10) -> List[dict]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM logs ORDER BY created_at DESC LIMIT %s", (limit,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
