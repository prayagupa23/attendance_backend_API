import pandas as pd
import os

FILE_PATH = "attendance.xlsx"


def read_attendance():
    
    if not os.path.exists(FILE_PATH):
        # Create empty DataFrame with proper columns if file doesn't exist
        df = pd.DataFrame(columns=["student_id", "session_id", "timestamp", "device_id"])
        df.to_excel(FILE_PATH, index=False)
        return []
    
    df = pd.read_excel(FILE_PATH)
    
    # Convert DataFrame to list of dictionaries
    records = df.to_dict('records')
    return records


def write_attendance(data):
    
    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(data)
    
    # Ensure all required columns exist
    required_columns = ["student_id", "session_id", "timestamp", "device_id"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
    
    # Write to Excel file
    df.to_excel(FILE_PATH, index=False)


def attendance_exists(student_id, session_id):
    
    records = read_attendance()
    
    for r in records:
        if r["student_id"] == student_id and r["session_id"] == session_id:
            return True
    
    return False