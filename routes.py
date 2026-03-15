from flask import Blueprint, request, jsonify
from storage import read_attendance, write_attendance, attendance_exists

attendance_bp = Blueprint("attendance", __name__)


# API 1 — Mark Attendance
@attendance_bp.route("/attendance/mark", methods=["POST"])
def mark_attendance():

    data = request.json

    student_id = data.get("student_id")
    session_id = data.get("session_id")
    timestamp = data.get("timestamp")
    device_id = data.get("device_id")

    if attendance_exists(student_id, session_id):
        return jsonify({
            "message": "Attendance already marked"
        }), 400

    records = read_attendance()

    new_record = {
        "student_id": student_id,
        "session_id": session_id,
        "timestamp": timestamp,
        "device_id": device_id
    }

    records.append(new_record)

    write_attendance(records)

    return jsonify({
        "message": "Attendance marked successfully",
        "data": new_record
    })


# API 2 — Get Session Attendance
@attendance_bp.route("/attendance/session/<session_id>", methods=["GET"])
def get_session_attendance(session_id):

    records = read_attendance()

    result = []

    for r in records:
        if r["session_id"] == session_id:
            result.append(r)

    return jsonify(result)