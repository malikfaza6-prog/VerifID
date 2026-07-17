"""
Auth routes - login, logout endpoints.
"""
from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from app.services.auth_service import AuthService
from app.utils.constants import SESSION_USER_ID, SESSION_USERNAME, SESSION_ROLE, SESSION_KELAS

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()


@auth_bp.route("/login", methods=["GET"])
def login_page():
    if SESSION_USER_ID in session:
        if session.get(SESSION_ROLE) == "admin":
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("dashboard.root"))
    return render_template("login.html")


@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user, error = auth_service.login(username, password)
    if error:
        flash(error, "danger")
        return render_template("login.html", username=username)

    session.clear()
    session[SESSION_USER_ID] = user.id
    session[SESSION_USERNAME] = user.username
    session[SESSION_ROLE] = user.role
    session[SESSION_KELAS] = user.kelas or ""
    session.permanent = False

    ip = request.remote_addr or ""
    auth_service.log_activity(user.username, "Login berhasil", ip)

    flash(f"Selamat datang, {user.username}!", "success")
    if user.role == "admin":
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("dashboard.root"))


@auth_bp.route("/logout")
def logout():
    username = session.get(SESSION_USERNAME, "")
    if username:
        auth_service.log_activity(username, "Logout", request.remote_addr or "")
    session.clear()
    flash("Anda telah logout.", "info")
    return redirect(url_for("auth.login_page"))
