"""
Configuration module for Attendance System.
Loads environment variables and provides config classes.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    DEBUG: bool = False
    TESTING: bool = False
    
    # Session
    SESSION_TYPE: str = os.getenv("SESSION_TYPE", "filesystem")
    SESSION_PERMANENT: bool = False
    SESSION_USE_SIGNER: bool = True
    PERMANENT_SESSION_LIFETIME: int = 3600  # 1 hour
    
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "attendance_system")
    
    # File Upload
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "app/static/uploads")
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))
    ALLOWED_EXTENSIONS: set = {"png", "jpg", "jpeg", "gif", "webp"}
    
    # Face Recognition
    FACE_RECOGNITION_TOLERANCE: float = float(os.getenv("FACE_RECOGNITION_TOLERANCE", "0.6"))
    MIN_FRAMES_REQUIRED: int = int(os.getenv("MIN_FRAMES_REQUIRED", "30"))
    ATTENDANCE_COOLDOWN: int = int(os.getenv("ATTENDANCE_COOLDOWN", "30"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG: bool = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG: bool = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING: bool = True
    DEBUG: bool = True


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)()
