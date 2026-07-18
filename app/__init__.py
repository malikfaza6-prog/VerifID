"""
Flask application factory.
"""
import logging
import os
from flask import Flask, session
from flask_session import Session
from config import get_config

cfg = get_config()

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=getattr(logging, cfg.LOG_LEVEL, "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(cfg.LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)

    # Load config
    app.config.from_object(cfg)

    # Session
    os.makedirs("flask_session", exist_ok=True)
    app.config["SESSION_FILE_DIR"] = "flask_session"
    Session(app)

    # Ensure upload folders exist
    os.makedirs(os.path.join(cfg.UPLOAD_FOLDER, "photos"), exist_ok=True)

    # Initialize database
    with app.app_context():
        try:
            from app.database.database import init_db
            from app.database.seed import run_seed
            init_db()
            run_seed()
        except Exception as e:
            logger.error(f"DB init failed: {e}")

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.employee import employee_bp
    from app.routes.face import face_bp
    from app.routes.attendance import attendance_bp
    from app.routes.users import user_bp
    from app.routes.matkul import matkul_bp
    from app.routes.dosen import dosen_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(face_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(matkul_bp)
    app.register_blueprint(dosen_bp)

    # Context processors
    @app.context_processor
    def inject_globals():
        from app.utils.constants import SESSION_USERNAME, SESSION_ROLE, SESSION_KELAS
        return {
            "current_username": session.get(SESSION_USERNAME, ""),
            "current_role": session.get(SESSION_ROLE, ""),
            "current_kelas": session.get(SESSION_KELAS, ""),
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template("errors/500.html"), 500

    logger.info("Flask app created successfully.")
    return app
