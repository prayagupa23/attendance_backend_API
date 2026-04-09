from flask import Blueprint, request, jsonify
from db import get_db_connection
from services.fcm_service import (
    get_tokens_for_faculty_list,
    send_fcm_to_multiple
)

substitution_bp = Blueprint('substitution', __name__)

@substitution_bp.route('/substitution/request', methods=['POST'])
def request_substitution():
    data = request.json

    timetable_id = data.get('timetable_id')
    original_faculty = data.get('original_faculty_id')
    date = data.get('date')

    conn = get_db_connection()
    cur = conn.cursor()

    # 0. Check for existing substitution request
    cur.execute("""
        SELECT id FROM lecture_substitutions
        WHERE timetable_id = %s AND date = %s AND status = 'PENDING'
    """, (timetable_id, date))

    existing_request = cur.fetchone()
    if existing_request:
        cur.close()
        conn.close()
        return jsonify({"message": "Substitution already requested"}), 400

    # 1. Create substitution
    cur.execute("""
    INSERT INTO lecture_substitutions
    (timetable_id, original_faculty_id, original_faculty_name, date)
    SELECT %s, f.faculty_id, f.name, %s
    FROM faculty f
    WHERE f.faculty_id = %s
    RETURNING id
    """, (timetable_id, date, original_faculty))

    substitution_id = cur.fetchone()[0]

    # 2. Get eligible faculty (same batch logic)
    cur.execute("""
        SELECT faculty_id FROM faculty
        WHERE faculty_id != %s
    """, (original_faculty,))

    faculty_list = [row[0] for row in cur.fetchall()]

    # DEBUG: Print faculty list to verify original faculty is excluded
    print(f"Original faculty ID: {original_faculty}")
    print(f"Eligible faculty list (excluding original): {faculty_list}")
    print(f"Original faculty in list: {original_faculty in faculty_list}")

    conn.commit()
    cur.close()
    conn.close()

    # 3. Get tokens
    tokens = get_tokens_for_faculty_list(faculty_list)

    # 4. Send FCM
    if tokens:
        send_fcm_to_multiple(
            tokens,
            "Lecture Substitution Request",
            f"Faculty {original_faculty} needs a substitute"
        )

    return jsonify({
        "message": "Substitution request sent",
        "substitution_id": substitution_id
    })

@substitution_bp.route('/substitution/respond', methods=['POST'])
def respond_substitution():
    data = request.json

    substitution_id = data.get('substitution_id')
    faculty_id = data.get('faculty_id')
    action = data.get('action')  # ACCEPT / REJECT

    # DEBUG: Print incoming request details
    print(f"Substitution response request:")
    print(f"  substitution_id: {substitution_id}")
    print(f"  faculty_id: {faculty_id}")
    print(f"  action: {action}")

    conn = get_db_connection()
    cur = conn.cursor()

    # First, check if substitution exists and get complete details
    cur.execute("""
        SELECT id, timetable_id, original_faculty_id, substitute_faculty_id, status, date
        FROM lecture_substitutions 
        WHERE id = %s
    """, (substitution_id,))

    result = cur.fetchone()
    if not result:
        cur.close()
        conn.close()
        print(f"ERROR: Substitution ID {substitution_id} not found")
        return jsonify({"message": "Substitution request not found"}), 404

    substitution_details = {
        'id': result[0],
        'timetable_id': result[1], 
        'original_faculty_id': result[2],
        'substitute_faculty_id': result[3],
        'status': result[4],
        'date': result[5]
    }
    
    print(f"Complete substitution record: {substitution_details}")
    current_status = substitution_details['status']

    if action == "ACCEPT":
        print(f"Checking status: current_status = '{current_status}', expected = 'PENDING'")
        print(f"Status comparison: current_status != 'PENDING' = {current_status != 'PENDING'}")
        print(f"Status type: {type(current_status)}, length: {len(current_status) if current_status else 'None'}")
        
        if current_status != "PENDING":
            cur.close()
            conn.close()
            print(f"ERROR: Cannot accept substitution with status: '{current_status}'")
            return jsonify({"message": "Already taken"}), 400

        print(f"Status check passed. Proceeding with faculty validation...")
        
        # Check if faculty_id exists in faculty table
        cur.execute("""
            SELECT faculty_id, name FROM faculty 
            WHERE faculty_id = %s
        """, (faculty_id,))
        
        faculty_result = cur.fetchone()
        if not faculty_result:
            cur.close()
            conn.close()
            print(f"ERROR: Faculty ID {faculty_id} does not exist")
            return jsonify({"message": "Invalid faculty ID"}), 400
        
        print(f"Faculty validated: {faculty_result[0]} - {faculty_result[1]}")
        print(f"Proceeding with UPDATE query...")
        print(f"UPDATE parameters: faculty_id={faculty_id}, substitution_id={substitution_id}")
        
        cur.execute("""
        UPDATE lecture_substitutions
        SET 
            substitute_faculty_id = f.faculty_id,
            substitute_faculty_name = f.name,
            status = 'ACCEPTED'
        FROM faculty f
        WHERE f.faculty_id = %s
        AND lecture_substitutions.id = %s
        AND lecture_substitutions.status = 'PENDING'
        """, (faculty_id, substitution_id))

        print(f"UPDATE executed. Rows affected: {cur.rowcount}")
        
        if cur.rowcount == 0:
            cur.close()
            conn.close()
            print(f"ERROR: Update failed - no rows affected")
            return jsonify({"message": "Failed to accept substitution"}), 400

        print(f"SUCCESS: Substitution {substitution_id} accepted by faculty {faculty_id}")

    elif action == "REJECT":
        # optional logic for rejection
        print(f"REJECT action not implemented yet for substitution {substitution_id}")
        pass

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Response recorded"})

@substitution_bp.route('/substitution/requests', methods=['GET'])
def get_pending_requests():
    """Get pending substitution requests for a specific faculty"""
    faculty_id = request.args.get('faculty_id')
    
    if not faculty_id:
        return jsonify({"error": "faculty_id parameter is required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    print(f"DEBUG: Getting pending requests for faculty_id: {faculty_id}")
    
    cur.execute("""
        SELECT ls.id, ls.timetable_id, ls.original_faculty_id, 
               ls.original_faculty_name, ls.date, ls.created_at,
               t.course_name, t.start_time, t.end_time, t.room_number
        FROM lecture_substitutions ls
        JOIN timetable t ON ls.timetable_id = t.timetable_id
        WHERE ls.status = 'PENDING'
        AND ls.original_faculty_id != %s
        ORDER BY ls.date, t.start_time
    """, (faculty_id,))
    
    print(f"DEBUG: Query executed, rows returned: {cur.rowcount}")
    
    requests = []
    for row in cur.fetchall():
        requests.append({
            'id': row[0],
            'timetable_id': row[1],
            'original_faculty_id': row[2],
            'original_faculty_name': row[3],
            'date': str(row[4]),
            'created_at': str(row[5]),
            'course_name': row[6],
            'start_time': str(row[7]),
            'end_time': str(row[8]),
            'room_no': row[9]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({"pending_requests": requests})

@substitution_bp.route('/substitution/accepted', methods=['GET'])
def get_accepted_lectures():
    """Get accepted substitution lectures for a specific faculty"""
    faculty_id = request.args.get('faculty_id')
    
    if not faculty_id:
        return jsonify({"error": "faculty_id parameter is required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ls.id, ls.timetable_id, ls.original_faculty_id, 
               ls.original_faculty_name, ls.substitute_faculty_id,
               ls.substitute_faculty_name, ls.date, ls.created_at,
               t.course_name, t.start_time, t.end_time, t.room_number
        FROM lecture_substitutions ls
        JOIN timetable t ON ls.timetable_id = t.timetable_id
        WHERE ls.status = 'ACCEPTED'
        AND (ls.substitute_faculty_id = %s OR ls.original_faculty_id = %s)
        ORDER BY ls.date, t.start_time
    """, (faculty_id, faculty_id))
    
    accepted_lectures = []
    for row in cur.fetchall():
        accepted_lectures.append({
            'id': row[0],
            'timetable_id': row[1],
            'original_faculty_id': row[2],
            'original_faculty_name': row[3],
            'substitute_faculty_id': row[4],
            'substitute_faculty_name': row[5],
            'date': str(row[6]),
            'created_at': str(row[7]),
            'course_name': row[8],
            'start_time': str(row[9]),
            'end_time': str(row[10]),
            'room_no': row[11]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({"accepted_lectures": accepted_lectures})

@substitution_bp.route('/substitution/notifications', methods=['GET'])
def get_substitution_notifications():
    """Get substitution notifications for students in a specific batch"""
    batch = request.args.get('batch')
    
    if not batch:
        return jsonify({"error": "batch parameter is required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                ls.id,
                ls.original_faculty_id,
                ls.original_faculty_name,
                ls.substitute_faculty_id,
                ls.substitute_faculty_name,
                ls.date,
                ls.created_at,
                t.course_name,
                t.start_time,
                t.end_time,
                t.room_number,
                t.batch
            FROM lecture_substitutions ls
            JOIN timetable t ON ls.timetable_id = t.timetable_id
            WHERE ls.status = 'ACCEPTED'
            AND t.batch = %s
            AND ls.date >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY ls.date DESC, t.start_time DESC
        """, (batch,))
        
        notifications = []
        for row in cur.fetchall():
            notifications.append({
                'id': row[0],
                'original_faculty_id': row[1],
                'original_faculty_name': row[2],
                'substitute_faculty_id': row[3],
                'substitute_faculty_name': row[4],
                'date': str(row[5]),
                'created_at': str(row[6]),
                'course_name': row[7],
                'start_time': str(row[8]),
                'end_time': str(row[9]),
                'room_no': row[10],
                'batch': row[11]
            })
        
        cur.close()
        conn.close()
        
        print(f"DEBUG: Retrieved {len(notifications)} substitution notifications for batch {batch}")
        
        return jsonify({
            "substitution_notifications": notifications,
            "message": f"Successfully retrieved {len(notifications)} notifications"
        })
        
    except Exception as e:
        print(f"ERROR: Failed to get substitution notifications for batch {batch}: {str(e)}")
        cur.close()
        conn.close()
        return jsonify({"error": "Internal server error"}), 500