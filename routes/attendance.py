from flask import Blueprint, request, jsonify
from db import get_db_connection
from services.attendance_service import mark_attendance_service, get_session_attendance_service

attendance_bp = Blueprint("attendance", __name__)


# API 1 — Mark Attendance
@attendance_bp.route("/attendance/mark", methods=["POST"])
def mark_attendance():

    data = request.json
    
    response, status = mark_attendance_service(request.json)
    return jsonify(response), status


# API 2 — Get Session Attendance
@attendance_bp.route("/attendance/session/<session_id>", methods=["GET"])
def get_session_attendance(session_id):
    
    result, status = get_session_attendance_service(session_id)
    return jsonify(result), status