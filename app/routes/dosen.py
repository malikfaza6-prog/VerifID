"""
Dosen routes - dosen hanya bisa melihat & mengedit absensi
untuk mata kuliah yang mereka ampu sendiri (di-scope via session matkul_id).
"""
from flask import Blueprint, request, jsonify, render_template, session

from app.middleware.auth import dosen_required, get_current_matkul_id, get_current_username
from app.services.attendance_service import AttendanceService
from app.services.matkul_service import MatkulService
from app.services.employee_service import EmployeeService
from app.services.auth_service import AuthService

dosen_bp = Blueprint("dosen", __name__, url_prefix="/dosen")
att_service = AttendanceService()
matkul_service = MatkulService()
emp_service = EmployeeService()
auth_service = AuthService()


@dosen_bp.route("/")
@dosen_required
def index():
    matkul_id = get_current_matkul_id()
    matkul = matkul_service.get_by_id(matkul_id)
    return render_template("dosen/index.html", matkul=matkul, title="Absensi Mata Kuliah Saya")


@dosen_bp.route("/api")
@dosen_required
def api_list():
    matkul_id = get_current_matkul_id()
    search = request.args.get("search", "")
    tanggal_from = request.args.get("tanggal_from") or None
    tanggal_to = request.args.get("tanggal_to") or None
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 15))

    result = att_service.get_matkul_attendance(
        matkul_id, search, tanggal_from, tanggal_to, page, per_page
    )
    return jsonify({"success": True, **result})


@dosen_bp.route("/api/<int:att_id>", methods=["PUT"])
@dosen_required
def api_update(att_id: int):
    matkul_id = get_current_matkul_id()
    data = request.get_json() or {}
    status = data.get("status", "")
    jam_masuk = data.get("jam_masuk", "")

    success, message = att_service.update_attendance_manual(att_id, matkul_id, status, jam_masuk)
    if success:
        auth_service.log_activity(
            get_current_username(),
            f"Dosen mengoreksi absensi ID={att_id} jadi status={status}",
            request.remote_addr or "",
        )
    return jsonify({"success": success, "message": message}), (200 if success else 400)


@dosen_bp.route("/api", methods=["POST"])
@dosen_required
def api_create_manual():
    matkul_id = get_current_matkul_id()
    data = request.get_json() or {}

    success, message = att_service.add_manual_attendance(
        matkul_id=matkul_id,
        pegawai_id=data.get("pegawai_id"),
        tanggal=data.get("tanggal"),
        jam_masuk=data.get("jam_masuk", ""),
        status=data.get("status", "hadir"),
    )
    if success:
        auth_service.log_activity(
            get_current_username(),
            f"Dosen menambahkan absensi manual utk pegawai_id={data.get('pegawai_id')}",
            request.remote_addr or "",
        )
    return jsonify({"success": success, "message": message}), (201 if success else 400)


@dosen_bp.route("/api/mahasiswa-list")
@dosen_required
def api_mahasiswa_list():
    """Daftar mahasiswa aktif untuk dropdown pencarian saat tambah absensi manual."""
    search = request.args.get("search", "").lower()
    employees = emp_service.get_all_active()
    items = [
        {"id": e.id, "nik": e.nik, "nama": e.nama, "departemen": e.departemen}
        for e in employees
        if not search or search in e.nama.lower() or search in e.nik.lower()
    ]
    return jsonify({"success": True, "data": items[:50]})
