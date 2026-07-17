"""
Database seeder - creates default admin user and sample data.
"""
import logging
import bcrypt
from app.database.database import get_connection

logger = logging.getLogger(__name__)


def seed_users() -> None:
    """Seed default admin and operator users."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if admin already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", ("admin",))
        if cursor.fetchone():
            logger.info("Seed: admin user already exists, skipping.")
            return

        password_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode("utf-8")
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            ("admin", password_hash, "admin"),
        )

        op_hash = bcrypt.hashpw(b"operator123", bcrypt.gensalt()).decode("utf-8")
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            ("operator", op_hash, "operator"),
        )

        conn.commit()
        logger.info("Seed: default users created (admin / admin123, operator / operator123)")
    except Exception as e:
        conn.rollback()
        logger.error(f"Seed error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def run_seed() -> None:
    """Run all seeders."""
    seed_users()
    logger.info("Database seeding complete.")
