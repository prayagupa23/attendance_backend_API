from flask import Blueprint, request, jsonify
from db import get_db_connection
from services.auth_service import login_service, faculty_login_service
from services.faculty_service import get_faculty_batches_service, get_student_count_service, get_assigned_courses_service, get_full_timetable_service, get_batch_faculty_service

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json
    
    response, status = login_service(request.json)
    return jsonify(response), status

    roll_number = data.get("roll_number")
    password = data.get("password")

    if not roll_number or not password:
        return jsonify({"error": "Missing credentials"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT student_id, password_hash, name, roll_number
            FROM students
            WHERE roll_number = %s
        """, (roll_number,))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if not user:
            return jsonify({"error": "Invalid roll number"}), 404

        db_student_id, db_password, name, db_roll = user

        if password != db_password:
            return jsonify({"error": "Invalid password"}), 401

        return jsonify({
            "message": "Login successful",
            "student_id": db_student_id,
            "roll_number": db_roll,
            "name": name
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@auth_bp.route("/faculty/login", methods=["POST"])
def faculty_login():
    response, status = faculty_login_service(request.json)
    return jsonify(response), status

@auth_bp.route("/api/faculty/batches", methods=["GET"])
def get_faculty_batches():
    faculty_id = request.args.get("faculty_id")
    response, status = get_faculty_batches_service(faculty_id)
    return jsonify(response), status

@auth_bp.route("/api/students/count", methods=["GET"])
def get_student_count():
    batch = request.args.get("batch")
    response, status = get_student_count_service(batch)
    return jsonify(response), status

@auth_bp.route("/api/faculty/assigned-courses", methods=["GET"])
def get_assigned_courses():
    faculty_id = request.args.get("faculty_id")
    response, status = get_assigned_courses_service(faculty_id)
    return jsonify(response), status

@auth_bp.route("/api/faculty/full-timetable", methods=["GET"])
def get_full_timetable():
    faculty_id = request.args.get("faculty_id")
    response, status = get_full_timetable_service(faculty_id)
    return jsonify(response), status

@auth_bp.route("/api/batch/faculty", methods=["GET"])
def get_batch_faculty():
    batch = request.args.get("batch")
    response, status = get_batch_faculty_service(batch)
    return jsonify(response), status