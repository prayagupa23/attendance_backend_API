#sessions.py
from flask import Blueprint, request, jsonify
from services.session_service import create_session_service, get_active_sessions_service

sessions_bp = Blueprint("sessions", __name__)

@sessions_bp.route("/sessions/create", methods=["POST"])
def create_session():
    response, status = create_session_service(request.json)
    return jsonify(response), status

@sessions_bp.route("/sessions/active", methods=["GET"])
def get_active_sessions():
    response, status = get_active_sessions_service()
    return jsonify(response), status