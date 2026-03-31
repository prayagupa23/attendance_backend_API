#auth_service.py
from db import get_db_connection

def login_service(data):

    roll_number = data.get("roll_number")
    password = data.get("password")

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
        return {"error": "Invalid roll number"}, 404

    db_student_id, db_password, name, db_roll = user

    if password != db_password:
        return {"error": "Invalid password"}, 401

    return {
        "message": "Login successful",
        "student_id": db_student_id,
        "roll_number": db_roll,
        "name": name
    }, 200

def faculty_login_service(data):

    faculty_id = data.get("faculty_id")
    password = data.get("password")

    if not faculty_id or not password:
        return {"error": "Missing credentials"}, 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT faculty_id, password_hash, name, email, department, designation
            FROM faculty
            WHERE faculty_id = %s
        """, (faculty_id,))

        user = cur.fetchone()

        cur.close()
        conn.close()

        # ❌ Faculty not found
        if not user:
            return {"error": "Invalid faculty ID"}, 404

        db_faculty_id, db_password, name, email, department, designation = user

        # 🔑 Password check (plain text as per your system)
        if password != db_password:
            return {"error": "Invalid password"}, 401

        # ✅ Success
        return {
            "message": "Login successful",
            "faculty_id": db_faculty_id,
            "name": name,
            "email": email,
            "department": department,
            "designation": designation
        }, 200

    except Exception as e:
        return {"error": str(e)}, 500