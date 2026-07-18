"""
Auth middleware - session checks and login_required decorator.
"""
import logging
from functools import wraps
from typing import Callable

from flask import session, redirect, url_for, flash, request
from app.utils.constants import SESSION_USER_ID, SESSION_USERNAME, SESSION_ROLE, SESSION_KELAS, SESSION_MATKUL_ID

logger = logging.getLogger(__name__)


def login_required(f: Callable) -> Callable:
    """Decorator: redirect to login if not authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if SESSION_USER_ID not in session:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f: Callable) -> Callable:
    """Decorator: require admin role."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get(SESSION_ROLE) != "admin":
            flash("Akses ditolak. Hanya admin yang diperbolehkan.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated_function


def dosen_required(f: Callable) -> Callable:
    """Decorator: require dosen role, with a matkul assigned."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get(SESSION_ROLE) != "dosen":
            flash("Akses ditolak. Halaman ini khusus untuk dosen.", "danger")
            return redirect(url_for("dashboard.root"))
        if not session.get(SESSION_MATKUL_ID):
            flash("Akun dosen ini belum ditautkan ke mata kuliah manapun. Hubungi admin.", "warning")
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user_id() -> int:
    return session.get(SESSION_USER_ID)


def get_current_username() -> str:
    return session.get(SESSION_USERNAME, "unknown")


def get_current_role() -> str:
    return session.get(SESSION_ROLE, "operator")


def get_current_kelas() -> str:
    """Returns the prodi/kelas code tied to a 'kelas' login (e.g. 'FTI')."""
    return session.get(SESSION_KELAS, "")


def get_current_matkul_id() -> int:
    """Returns the matkul_id tied to a 'dosen' login."""
    return session.get(SESSION_MATKUL_ID) or None
