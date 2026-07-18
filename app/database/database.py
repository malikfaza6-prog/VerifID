"""
Database module - handles MySQL connection pool.
"""
import logging
import mysql.connector
from mysql.connector import pooling, Error
from config import get_config

logger = logging.getLogger(__name__)
config = get_config()

_pool = None


def get_pool() -> pooling.MySQLConnectionPool:
    """Get or create the connection pool (singleton)."""
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="attendance_pool",
            pool_size=5,
            pool_reset_session=True,
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            autocommit=False,
        )
        logger.info("Database connection pool created.")
    return _pool


def get_connection() -> mysql.connector.MySQLConnection:
    """Get a connection from the pool."""
    return get_pool().get_connection()


def init_db() -> None:
    """Initialize database: create tables if they don't exist."""
    conn = None
    cursor = None
    try:
        # First connect without selecting a database to create it if needed
        conn_no_db = mysql.connector.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            charset="utf8mb4",
        )
        cursor_no_db = conn_no_db.cursor()
        cursor_no_db.execute(
            f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn_no_db.commit()
        cursor_no_db.close()
        conn_no_db.close()

        conn = get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('admin', 'operator', 'kelas', 'dosen') NOT NULL DEFAULT 'operator',
                kelas VARCHAR(50) DEFAULT NULL,
                matkul_id INT DEFAULT NULL,
                is_active TINYINT(1) NOT NULL DEFAULT 1,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Pegawai (Employee) table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pegawai (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nik VARCHAR(20) NOT NULL UNIQUE,
                nama VARCHAR(100) NOT NULL,
                departemen VARCHAR(100),
                jabatan VARCHAR(100),
                foto VARCHAR(255),
                status ENUM('aktif', 'nonaktif') NOT NULL DEFAULT 'aktif',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Face Encodings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS face_encodings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pegawai_id INT NOT NULL,
                encoding LONGBLOB NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pegawai_id) REFERENCES pegawai(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Mata Kuliah table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matkul (
                id INT AUTO_INCREMENT PRIMARY KEY,
                kode VARCHAR(20) NOT NULL UNIQUE,
                nama VARCHAR(150) NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pegawai_id INT NOT NULL,
                matkul_id INT DEFAULT NULL,
                tanggal DATE NOT NULL,
                jam_masuk TIME,
                jam_keluar TIME,
                confidence FLOAT,
                status ENUM('hadir', 'terlambat', 'pulang') NOT NULL DEFAULT 'hadir',
                device VARCHAR(100),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pegawai_id) REFERENCES pegawai(id) ON DELETE CASCADE,
                FOREIGN KEY (matkul_id) REFERENCES matkul(id) ON DELETE SET NULL,
                UNIQUE KEY uq_absen_matkul_harian (pegawai_id, tanggal, matkul_id),
                INDEX idx_tanggal (tanggal),
                INDEX idx_pegawai_tanggal (pegawai_id, tanggal)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Activity Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user VARCHAR(100) NOT NULL,
                activity TEXT NOT NULL,
                ip_address VARCHAR(45),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        conn.commit()
        logger.info("Database tables initialized successfully.")

    except Error as e:
        logger.error(f"Database initialization error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
