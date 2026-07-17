"""
Employee routes - REST API + page rendering.
"""
import os
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash

from app.middleware.auth import login_required, admin_required, get_current_username
from app.services.employee_service import EmployeeService
from app.services.auth_service import AuthService
from app.utils.constants import DEFAULT_DEPARTMENTS

employee_bp = Blueprint("employee", __name__, url_prefix="/pegawai")
emp_service = EmployeeService()
auth_service = AuthService()


@employee_bp.route("/")
@login_required
def index():
    search = request.args.get("search", "")
    page = int(request.args.get("page", 1))
    employees, meta = emp_service.get_paginated(search=search, page=page)
    departments = emp_service.get_departments() or DEFAULT_DEPARTMENTS
    return render_template(
        "employee/index.html",
        employees=employees,
        meta=meta,
        search=search,
        departments=departments,
        title="Data Pegawai",
    )


@employee_bp.route("/api", methods=["GET"])
@login_required
def api_list():
    search = request.args.get("search", "")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    employees, meta = emp_service.get_paginated(search=search, page=page, per_page=per_page)
    return jsonify({
        "success": True,
        "data": [e.to_dict() for e in employees],
        "meta": meta,
    })


@employee_bp.route("/api", methods=["POST"])
@login_required
def api_create():
    data = request.form.to_dict()
    file_storage = request.files.get("foto")
    new_id, error = emp_service.create(data, file_storage)
    if error:
        return jsonify({"success": False, "message": error}), 400
    auth_service.log_activity(
        get_current_username(),
        f"Tambah pegawai ID={new_id}, NIK={data.get('nik')}",
        request.remote_addr or "",
    )
    return jsonify({"success": True, "message": "Pegawai berhasil ditambahkan.", "id": new_id}), 201


@employee_bp.route("/api/<int:emp_id>", methods=["GET"])
@login_required
def api_get(emp_id: int):
    emp = emp_service.get_by_id(emp_id)
    if not emp:
        return jsonify({"success": False, "message": "Pegawai tidak ditemukan."}), 404
    return jsonify({"success": True, "data": emp.to_dict()})


@employee_bp.route("/api/<int:emp_id>", methods=["PUT"])
@login_required
def api_update(emp_id: int):
    data = request.form.to_dict()
    file_storage = request.files.get("foto")
    success, error = emp_service.update(emp_id, data, file_storage)
    if not success:
        return jsonify({"success": False, "message": error}), 400
    auth_service.log_activity(
        get_current_username(),
        f"Update pegawai ID={emp_id}",
        request.remote_addr or "",
    )
    return jsonify({"success": True, "message": "Pegawai berhasil diperbarui."})


@employee_bp.route("/api/<int:emp_id>", methods=["DELETE"])
@admin_required
def api_delete(emp_id: int):
    success, error = emp_service.delete(emp_id)
    if not success:
        return jsonify({"success": False, "message": error}), 400
    auth_service.log_activity(
        get_current_username(),
        f"Hapus pegawai ID={emp_id}",
        request.remote_addr or "",
    )
    return jsonify({"success": True, "message": "Pegawai berhasil dihapus."})
