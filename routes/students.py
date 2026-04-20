from flask import Blueprint, request, jsonify
from services.student_service import get_students_by_year_and_batch

students_bp = Blueprint("students", __name__)


# API - Get Students by Year and Lab Batch
@students_bp.route("/students", methods=["GET"])
def get_students():
    """
    Fetch students by year and lab_batch query parameters
    Returns roll_number and name for matching students
    
    Query Parameters:
    - year: The academic year to filter students by (FYCO, SYCO, TYCO)
    - lab_batch: The lab batch to filter students by (C1, C2, etc.)
    
    Examples:
    - /students?year=FYCO&lab_batch=C1
    - /students?year=SYCO&lab_batch=C2
    - /students?year=TYCO&lab_batch=C1
    """
    year = request.args.get('year')
    lab_batch = request.args.get('lab_batch')
    
    if not year or not lab_batch:
        return jsonify({
            "error": "Both year and lab_batch query parameters are required"
        }), 400
    
    result, status = get_students_by_year_and_batch(year, lab_batch)
    return jsonify(result), status
