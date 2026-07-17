"""
Matkul (mata kuliah) management routes.
"""
from flask import Blueprint, request, jsonify, render_template

from app.middleware.auth import admin_required, login_required
from app.services.matkul_service import MatkulService

matkul_bp = Blueprint("matkul", __name__, url_prefix="/matkul")
matkul_service = MatkulService()


@matkul_bp.route("/")
@admin_required
def index():
    items = matkul_service.get_all()
    return render_template("matkul/index.html", items=items, title="Mata Kuliah")


@matkul_bp.route("/api", methods=["GET"])
@login_required
def api_list():
    """List all matkul - accessible to any logged-in role (used by kiosk selector)."""
    items = matkul_service.get_all()
    return jsonify({"success": True, "data": [m.to_dict() for m in items]})


@matkul_bp.route("/api", methods=["POST"])
@admin_required
def api_create():
    data = request.get_json() or request.form.to_dict()
    new_id, error = matkul_service.create(data)
    if error:
        return jsonify({"success": False, "message": error}), 400
    return jsonify({"success": True, "message": "Mata kuliah berhasil ditambahkan.", "id": new_id}), 201


@matkul_bp.route("/api/<int:matkul_id>", methods=["GET"])
@admin_required
def api_get(matkul_id: int):
    m = matkul_service.get_by_id(matkul_id)
    if not m:
        return jsonify({"success": False, "message": "Mata kuliah tidak ditemukan."}), 404
    return jsonify({"success": True, "data": m.to_dict()})


@matkul_bp.route("/api/<int:matkul_id>", methods=["PUT"])
@admin_required
def api_update(matkul_id: int):
    data = request.get_json() or request.form.to_dict()
    success, error = matkul_service.update(matkul_id, data)
    if not success:
        return jsonify({"success": False, "message": error}), 400
    return jsonify({"success": True, "message": "Mata kuliah berhasil diperbarui."})


@matkul_bp.route("/api/<int:matkul_id>", methods=["DELETE"])
@admin_required
def api_delete(matkul_id: int):
    success, error = matkul_service.delete(matkul_id)
    if not success:
        return jsonify({"success": False, "message": error}), 400
    return jsonify({"success": True, "message": "Mata kuliah berhasil dihapus."})
