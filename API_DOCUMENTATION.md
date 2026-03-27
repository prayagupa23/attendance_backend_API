# Attendance Management API Documentation

## Overview

This is a Flask-based Attendance Management API that handles student attendance tracking for educational sessions.

## Features

- Tracks student attendance across different sessions
- Stores attendance data in a JSON file (`attendance.json`)
- Prevents duplicate attendance entries
- Provides RESTful endpoints for attendance operations
- CORS enabled for cross-origin requests

## Base URL

```
http://localhost:5000
```

## Data Structure

Each attendance record contains:
- `student_id`: Unique student identifier
- `session_id`: Unique session identifier  
- `timestamp`: When attendance was marked (ISO format)
- `device_id`: Device used to mark attendance

Example record:
```json
{
    "student_id": "S12345",
    "session_id": "SESSION_789",
    "timestamp": "2026-03-14T10:21:00",
    "device_id": "abc123device"
}
```

## Endpoints

### 1. Mark Attendance

**POST** `/attendance/mark`

Records attendance for a student in a specific session.

#### Request Body
```json
{
    "student_id": "string",
    "session_id": "string", 
    "timestamp": "string",
    "device_id": "string"
}
```

#### Responses

**Success (201)**
```json
{
    "message": "Attendance marked successfully",
    "data": {
        "student_id": "S12345",
        "session_id": "SESSION_789",
        "timestamp": "2026-03-14T10:21:00",
        "device_id": "abc123device"
    }
}
```

**Error (400) - Duplicate Attendance**
```json
{
    "message": "Attendance already marked"
}
```

### 2. Get Session Attendance

**GET** `/attendance/session/<session_id>`

Retrieves all attendance records for a specific session.

#### URL Parameters
- `session_id` (string): The unique identifier of the session

#### Responses

**Success (200)**
```json
[
    {
        "student_id": "S12345",
        "session_id": "SESSION_789",
        "timestamp": "2026-03-14T10:21:00",
        "device_id": "abc123device"
    },
    {
        "student_id": "S67890",
        "session_id": "SESSION_789",
        "timestamp": "2026-03-14T10:22:15",
        "device_id": "def456device"
    }
]
```

**Empty Result (200)**
```json
[]
```

## Technical Details

- **Framework**: Flask
- **CORS**: Enabled for all origins
- **Server**: Runs on `0.0.0.0:5000` in debug mode
- **Storage**: JSON file (`attendance.json`)
- **Architecture**: Blueprint-based route organization

## Error Handling

The API includes validation for:
- Duplicate attendance prevention
- Required field validation (student_id, session_id, timestamp, device_id)
- JSON parsing errors

## Usage Examples

### Mark Attendance (curl)
```bash
curl -X POST http://localhost:5000/attendance/mark \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "S12345",
    "session_id": "SESSION_789",
    "timestamp": "2026-03-14T10:21:00",
    "device_id": "abc123device"
  }'
```

### Get Session Attendance (curl)
```bash
curl http://localhost:5000/attendance/session/SESSION_789
```

## File Structure

```
attendance_backend/
├── app.py              # Main Flask application
├── routes.py           # API endpoints definition
├── storage.py          # Data persistence layer
├── attendance.json     # Data storage file
└── API_DOCUMENTATION.md # This documentation
```
