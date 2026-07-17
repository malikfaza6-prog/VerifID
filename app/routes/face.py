"""
Face registration routes.
"""
import base64
import json
import numpy as np
from flask import Blueprint, request, jsonify, render_template, session

from app.middleware.auth import login_required, get_current_username
from app.services.encoding_service import EncodingService
from app.services.employee_service import EmployeeService
from app.services.auth_service import AuthService
from app.utils.image_utils import base64_to_numpy

face_bp = Blueprint("face", __name__, url_prefix="/wajah")
enc_service = EncodingService()
emp_service = EmployeeService()
auth_service = AuthService()

# In-memory buffer for collected encodings per session key
_registration_buffer: dict = {}


@face_bp.route("/")
@login_required
def index():
    employees = emp_service.get_all_active()
    return render_template(
        "face/index.html",
        employees=employees,
        title="Registrasi Wajah",
    )


@face_bp.route("/api/check/<int:emp_id>")
@login_required
def check_encoding(emp_id: int):
    has = enc_service.has_encoding(emp_id)
    emp = emp_service.get_by_id(emp_id)
    if not emp:
        return jsonify({"success": False, "message": "Pegawai tidak ditemukan."}), 404
    return jsonify({
        "success": True,
        "has_encoding": has,
        "employee": emp.to_dict(),
    })


@face_bp.route("/api/process-frame", methods=["POST"])
@login_required
def process_frame():
    """
    Process a single registration frame.
    Expects JSON: {pegawai_id, frame_b64 (base64 image), session_key}
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data received."}), 400

    session_key = data.get("session_key", "")
    frame_b64 = data.get("frame_b64", "")
    pegawai_id = data.get("pegawai_id")

    if not frame_b64 or not pegawai_id:
        return jsonify({"success": False, "message": "Data tidak lengkap."}), 400

    try:
        frame_bgr = base64_to_numpy(frame_b64)
    except Exception:
        return jsonify({"success": False, "message": "Frame tidak valid."}), 400

    result = enc_service.process_frame_for_registration(frame_bgr)

    if result["status"] == "multiple_faces":
        return jsonify({
            "success": False,
            "status": "multiple_faces",
            "message": "Hanya boleh satu wajah.",
        })

    if result["status"] != "ok":
        messages = {
            "no_face": "Tidak ada wajah terdeteksi.",
            "poor_lighting": "Pencahayaan kurang. Perbaiki cahaya.",
            "blur": "Gambar buram. Jaga kamera tetap stabil.",
            "encoding_failed": "Gagal memproses wajah. Coba lagi.",
        }
        return jsonify({
            "success": False,
            "status": result["status"],
            "message": messages.get(result["status"], "Gagal memproses frame."),
        })

    # Store encoding in buffer
    if session_key not in _registration_buffer:
        _registration_buffer[session_key] = []

    encoding_bytes = result["encoding"].tobytes()
    _registration_buffer[session_key].append(encoding_bytes)
    count = len(_registration_buffer[session_key])

    return jsonify({
        "success": True,
        "status": "ok",
        "collected": count,
        "message": f"Frame {count} berhasil diambil.",
    })


@face_bp.route("/api/register", methods=["POST"])
@login_required
def register():
    """Finalize registration: average collected encodings and save."""
    data = request.get_json()
    session_key = data.get("session_key", "")
    pegawai_id = data.get("pegawai_id")

    if not session_key or not pegawai_id:
        return jsonify({"success": False, "message": "Data tidak lengkap."}), 400

    frames = _registration_buffer.get(session_key, [])
    if len(frames) < 10:
        return jsonify({"success": False, "message": f"Data wajah tidak cukup. Hanya {len(frames)} frame."}), 400

    encodings = [np.frombuffer(b, dtype=np.float64) for b in frames]
    _registration_buffer.pop(session_key, None)

    success, message = enc_service.save_registration(pegawai_id, encodings)
    if success:
        auth_service.log_activity(
            get_current_username(),
            f"Registrasi wajah pegawai ID={pegawai_id}",
            request.remote_addr or "",
        )
    return jsonify({"success": success, "message": message})


@face_bp.route("/api/delete/<int:emp_id>", methods=["DELETE"])
@login_required
def delete_encoding(emp_id: int):
    success = enc_service.delete_encoding(emp_id)
    return jsonify({"success": success, "message": "Encoding dihapus." if success else "Tidak ada encoding."})
