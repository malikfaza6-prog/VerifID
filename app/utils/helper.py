"""
Helper utilities - date formatting, pagination helpers, etc.
"""
import os
import uuid
import logging
from datetime import datetime, time
from typing import Any, Dict, Optional
from app.utils.constants import WORK_START_HOUR, WORK_START_MINUTE, LATE_THRESHOLD_MINUTE

logger = logging.getLogger(__name__)


def paginate(total: int, page: int, per_page: int) -> Dict[str, Any]:
    """Compute pagination metadata."""
    total_pages = max(1, -(-total // per_page))  # ceiling division
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if page < total_pages else None,
    }


def determine_attendance_status(jam_masuk: time) -> str:
    """Determine hadir or terlambat based on check-in time."""
    threshold = time(
        WORK_START_HOUR,
        WORK_START_MINUTE + LATE_THRESHOLD_MINUTE,
    )
    return "terlambat" if jam_masuk > threshold else "hadir"


def generate_unique_filename(original_filename: str) -> str:
    """Generate a UUID-based filename keeping the original extension."""
    ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else "jpg"
    return f"{uuid.uuid4().hex}.{ext}"


def format_timedelta_seconds(seconds: float) -> str:
    """Format seconds into HH:MM:SS string."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def success_response(data: Any = None, message: str = "Success") -> Dict:
    return {"success": True, "message": message, "data": data}


def error_response(message: str = "Error", code: int = 400) -> Dict:
    return {"success": False, "message": message, "code": code}
