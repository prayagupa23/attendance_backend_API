from flask import Blueprint, request, jsonify
from db import get_db_connection  # ✅ FIX 1: Corrected function name

fcm_bp = Blueprint('fcm', __name__)

@fcm_bp.route('/save-token', methods=['POST'])
def save_token():
    data = request.json

    faculty_id = data.get("faculty_id")
    token = data.get("token")
    # ✅ FIX 2: Added faculty_name variable (or set to None if not in payload)
    faculty_name = data.get("faculty_name") 

    conn = get_db_connection() # ✅ FIX 1: Match the new name
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO fcm_tokens (faculty_id, faculty_name, token)
            VALUES (%s, %s, %s)
            ON CONFLICT (token)
            DO UPDATE SET 
                faculty_id = EXCLUDED.faculty_id,
                faculty_name = EXCLUDED.faculty_name,
                updated_at = CURRENT_TIMESTAMP
        """, (faculty_id, faculty_name, token))

        conn.commit()
        return jsonify({"message": "Token saved"}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()