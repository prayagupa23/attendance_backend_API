from db import get_db_connection


def mark_attendance_service(data):
    roll_number = data.get("roll_number")  # roll_number from frontend
    session_id = data.get("session_id")
    device_id = data.get("device_id")
    timestamp = data.get("timestamp")

    if not roll_number or not session_id:
        return {"error": "Missing required fields"}, 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 🔍 1. Convert roll_number → student_id
        cur.execute("""
            SELECT student_id FROM students WHERE roll_number = %s
        """, (roll_number,))
        student = cur.fetchone()

        if not student:
            cur.close()
            conn.close()
            return {"error": "Student not found"}, 404

        student_id = student[0]

        # 🔍 2. Check session validity (10-minute logic)
        cur.execute("""
            SELECT 1 FROM sessions
            WHERE session_id = %s
            AND NOW() BETWEEN start_time AND end_time
            AND status = 'ACTIVE'
        """, (session_id,))
        session = cur.fetchone()

        if not session:
            cur.close()
            conn.close()
            return {"error": "Session expired or invalid"}, 400

        # 🔍 3. Check duplicate attendance
        cur.execute("""
            SELECT 1 FROM attendance
            WHERE student_id = %s AND session_id = %s
        """, (student_id, session_id))

        if cur.fetchone():
            cur.close()
            conn.close()
            return {"error": "Attendance already marked"}, 400

        # ✅ 4. Insert attendance
        if timestamp:
            cur.execute("""
                INSERT INTO attendance (student_id, session_id, device_id, marked_at)
                VALUES (%s, %s, %s, %s)
            """, (student_id, session_id, device_id, timestamp))
        else:
            cur.execute("""
                INSERT INTO attendance (student_id, session_id, device_id)
                VALUES (%s, %s, %s)
            """, (student_id, session_id, device_id))

        conn.commit()

        cur.close()
        conn.close()

        return {
            "message": "Attendance marked successfully"
        }, 200

    except Exception as e:
        return {"error": str(e)}, 500


def get_session_attendance_service(session_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT a.student_id, s.name, s.roll_number,
                   a.device_id, a.marked_at, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.session_id = %s
        """, (session_id,))

        rows = cur.fetchall()

        cur.close()
        conn.close()

        result = []

        for r in rows:
            result.append({
                "roll_number": r[2],
                "name": r[1],
                "device_id": r[3],
                "marked_at": str(r[4]),
                "status": r[5]
            })

        return result, 200

    except Exception as e:
        return {"error": str(e)}, 500