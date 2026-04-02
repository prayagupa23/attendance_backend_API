import os
from flask import Blueprint, request, jsonify, send_from_directory
from services.material_service import upload_material_service, get_materials_service

materials_bp = Blueprint("materials", __name__)
UPLOAD_FOLDER = "uploads/materials"


# API — Upload Material
@materials_bp.route("/materials/upload", methods=["POST"])
def upload_material():
    
    response, status = upload_material_service(request.form, request.files)
    return jsonify(response), status


# API — Get Materials by Batch
@materials_bp.route("/materials", methods=["GET"])
def get_materials():
    
    batch = request.args.get("batch")
    
    response, status = get_materials_service(batch)
    return jsonify(response), status


# API — Serve Files
@materials_bp.route("/materials/<faculty_id>/<batch>/<filename>", methods=["GET"])
def serve_file(faculty_id, batch, filename):
    
    file_path = os.path.join(UPLOAD_FOLDER, faculty_id, batch)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    return send_from_directory(file_path, filename)
