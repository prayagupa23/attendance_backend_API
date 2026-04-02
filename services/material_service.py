import os
import time
from werkzeug.utils import secure_filename
from db import get_db_connection


UPLOAD_FOLDER = "uploads/materials"
ALLOWED_EXTENSIONS = set()  # Allow all file types
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


def allowed_file(filename):
    return '.' in filename


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def upload_material_service(form_data, files):
    # Extract form data
    title = form_data.get("title")
    description = form_data.get("description", "")
    faculty_id = form_data.get("faculty_id")
    batch = form_data.get("batch")
    
    # Get file
    if 'file' not in files:
        return {"error": "No file provided"}, 400
    
    file = files['file']
    if file.filename == '':
        return {"error": "No file selected"}, 400
    
    # Validate required fields
    if not title or not faculty_id or not batch:
        return {"error": "Missing required fields: title, faculty_id, batch"}, 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return {"error": "File size exceeds 100MB limit"}, 400
    
    if not allowed_file(file.filename):
        return {"error": "Invalid file name"}, 400
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    timestamp = str(int(time.time()))
    unique_filename = f"{timestamp}_{original_filename}"
    
    # Create directory structure
    upload_path = os.path.join(UPLOAD_FOLDER, faculty_id, batch)
    os.makedirs(upload_path, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_path, unique_filename)
    file.save(file_path)
    
    # Get file details
    file_type = get_file_extension(original_filename)
    file_url = f"/materials/{faculty_id}/{batch}/{unique_filename}"
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insert material metadata
        cur.execute("""
            INSERT INTO materials (title, description, file_url, file_name, file_type, file_size, faculty_id, batch)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, (title, description, file_url, original_filename, file_type, file_size, faculty_id, batch))
        
        result = cur.fetchone()
        material_id = result[0]
        created_at = result[1]
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "message": "Upload successful",
            "file_url": file_url,
            "file_type": file_type,
            "file_size": file_size,
            "material_id": material_id,
            "created_at": str(created_at)
        }, 201
        
    except Exception as e:
        # Clean up uploaded file if database insertion fails
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"error": str(e)}, 500


def get_materials_service(batch):
    if not batch:
        return {"error": "Batch parameter is required"}, 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fetch materials for the specified batch, ordered by created_at desc
        cur.execute("""
            SELECT id, title, description, file_url, file_type, file_size, faculty_id, created_at
            FROM materials
            WHERE batch = %s
            ORDER BY created_at DESC
        """, (batch,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "title": r[1],
                "description": r[2],
                "file_url": r[3],
                "file_type": r[4],
                "file_size": r[5],
                "faculty_id": r[6],
                "created_at": str(r[7])
            })
        
        return result, 200
        
    except Exception as e:
        return {"error": str(e)}, 500
