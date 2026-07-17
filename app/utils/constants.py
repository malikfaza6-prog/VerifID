"""
Constants for the attendance system.
"""

# Attendance status
STATUS_HADIR = "hadir"
STATUS_TERLAMBAT = "terlambat"
STATUS_PULANG = "pulang"

# Work hours (24h format)
WORK_START_HOUR = 8
WORK_START_MINUTE = 0
LATE_THRESHOLD_MINUTE = 15  # minutes after WORK_START to be considered late

# User roles
ROLE_ADMIN = "admin"
ROLE_OPERATOR = "operator"
ROLE_KELAS = "kelas"

# Session keys
SESSION_USER_ID = "user_id"
SESSION_USERNAME = "username"
SESSION_ROLE = "role"
SESSION_KELAS = "kelas"

# Pagination
DEFAULT_PER_PAGE = 10

# File upload
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_UPLOAD_SIZE_MB = 16

# Face recognition
MIN_FACE_CONFIDENCE = 0.4
DEFAULT_TOLERANCE = 0.6
FRAMES_REQUIRED = 30
ATTENDANCE_COOLDOWN_SECONDS = 30

# Kelas/Prodi (defaults)
DEFAULT_DEPARTMENTS = [
    "FTI",
    "FEB",
    "FH",
    "FISIP",
    "FT",
    "FK",
]
