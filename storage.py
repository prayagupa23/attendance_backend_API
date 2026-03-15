import json

FILE_PATH = "attendance.json"


def read_attendance():

    with open(FILE_PATH, "r") as f:
        data = json.load(f)

    return data


def write_attendance(data):

    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)


def attendance_exists(student_id, session_id):

    records = read_attendance()

    for r in records:
        if r["student_id"] == student_id and r["session_id"] == session_id:
            return True

    return False