"""
Dashboard routes.
"""
from flask import Blueprint, render_template, session, redirect, url_for

from app.middleware.auth import login_required, get_current_username
from app.utils.constants import SESSION_ROLE
from app.services.attendance_service import AttendanceService
from app.services.auth_service import AuthService

dashboard_bp = Blueprint("dashboard", __name__)
att_service = AttendanceService()
auth_service = AuthService()


@dashboard_bp.route("/")
@login_required
def root():
    if session.get(SESSION_ROLE) == "admin":
        return redirect(url_for("dashboard.index"))
    return render_template("kiosk.html")


@dashboard_bp.route("/dashboard")
@login_required
def index():
    summary = att_service.get_today_summary()
    today_list = att_service.get_today_attendance_list()
    recent_logs = auth_service.get_recent_logs(limit=8)
    return render_template(
        "dashboard.html",
        summary=summary,
        today_list=today_list,
        recent_logs=recent_logs,
        title="Dashboard",
    )
