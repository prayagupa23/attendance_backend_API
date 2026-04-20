from db import get_db_connection

def get_students_by_year_and_batch(year, lab_batch):
    """
    Fetch students by year and lab_batch from the students table
    Returns roll_number and name for matching students
    Valid year enum values: 'FYCO', 'SYCO', 'TYCO'
    Valid lab_batch values: 'C1', 'C2', etc.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT roll_number, name 
        FROM students 
        WHERE year = %s AND lab_batch = %s
        ORDER BY roll_number
        """
        
        cursor.execute(query, (year, lab_batch))
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        students = []
        for row in results:
            students.append({
                "roll_number": row[0],
                "name": row[1]
            })
        
        cursor.close()
        conn.close()
        
        return students, 200
        
    except Exception as e:
        return {"error": str(e)}, 500
