"""
User management routes.
"""
from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session

from app.middleware.auth import admin_required, get_current_user_id
from app.services.user_service import UserManagementService
from app.services.auth_service import AuthService
from app.utils.constants import DEFAULT_DEPARTMENTS

user_bp = Blueprint("users", __name__, url_prefix="/users")
user_service = UserManagementService()
auth_service = AuthService()


@user_bp.route("/")
@admin_required
def index():
    users = user_service.get_all()
    return render_template(
        "users/index.html", users=users, departments=DEFAULT_DEPARTMENTS, title="Manajemen User"
    )


@user_bp.route("/api", methods=["GET"])
@admin_required
def api_list():
    users = user_service.get_all()
    return jsonify({"success": True, "data": [u.to_dict() for u in users]})


@user_bp.route("/api", methods=["POST"])
@admin_required
def api_create():
    data = request.get_json() or request.form.to_dict()
    new_id, error = user_service.create(data)
    if error:
        return jsonify({"success": False, "message": error}), 400
    return jsonify({"success": True, "message": "User berhasil dibuat.", "id": new_id}), 201


@user_bp.route("/api/<int:user_id>", methods=["GET"])
@admin_required
def api_get(user_id: int):
    user = user_service.get_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User tidak ditemukan."}), 404
    return jsonify({"success": True, "data": user.to_dict()})


@user_bp.route("/api/<int:user_id>", methods=["PUT"])
@admin_required
def api_update(user_id: int):
    data = request.get_json() or request.form.to_dict()
    success, error = user_service.update(user_id, data)
    if not success:
        return jsonify({"success": False, "message": error}), 400
    return jsonify({"success": True, "message": "User berhasil diperbarui."})


@user_bp.route("/api/<int:user_id>", methods=["DELETE"])
@admin_required
def api_delete(user_id: int):
    current_id = get_current_user_id()
    success, error = user_service.delete(user_id, current_id)
    if not success:
        return jsonify({"success": False, "message": error}), 400
    return jsonify({"success": True, "message": "User berhasil dihapus."})
