#session_service.py
from db import get_db_connection

def create_session_service(data):

    course_code = data.get("course_code")
    faculty_id = data.get("faculty_id")

    if not course_code or not faculty_id:
        return {"error": "Missing fields"}, 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert session (UUID auto-generated)
        cur.execute("""
            INSERT INTO sessions (course_code, faculty_id, start_time, end_time, status)
            VALUES (%s, %s, NOW(), NOW() + INTERVAL '10 minutes', 'ACTIVE')
            RETURNING session_id
        """, (course_code, faculty_id))

        session_id = cur.fetchone()[0]

        conn.commit()

        cur.close()
        conn.close()

        return {
            "message": "Session created",
            "session_id": str(session_id)
        }, 201

    except Exception as e:
        return {"error": str(e)}, 500
    
def get_active_sessions_service():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT session_id, course_code, faculty_id, start_time, end_time
        FROM sessions
        WHERE NOW() BETWEEN start_time AND end_time
        AND status = 'ACTIVE'
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    result = []

    for r in rows:
        result.append({
            "session_id": str(r[0]),
            "course_code": r[1],
            "faculty_id": r[2],
            "start_time": str(r[3]),
            "end_time": str(r[4])
        })

    return result, 200