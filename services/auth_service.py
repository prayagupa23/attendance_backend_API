#auth_service.py
from db import get_db_connection

def login_service(data):

    roll_number = data.get("roll_number")
    password = data.get("password")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT student_id, password_hash, name, email, phone, date_of_birth, address, department, year, roll_number, sgpa, lab_batch
        FROM students
        WHERE roll_number = %s
    """, (roll_number,))

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return {"error": "Invalid roll number"}, 404

    db_student_id, db_password, name, email, phone, date_of_birth, address, department, year, db_roll, sgpa, lab_batch = user

    if password != db_password:
        return {"error": "Invalid password"}, 401

    return {
        "message": "Login successful",
        "student_id": db_student_id,
        "name": name,
        "email": email,
        "phone": phone,
        "date_of_birth": str(date_of_birth) if date_of_birth else None,
        "address": address,
        "department": department,
        "year": year,
        "roll_number": db_roll,
        "sgpa": float(sgpa) if sgpa else None,
        "lab_batch": lab_batch
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