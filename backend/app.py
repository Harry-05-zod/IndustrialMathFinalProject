from flask_cors import CORS
from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def military_to_am_pm(military_time):
    """Convert military integer time (e.g., 930) to '9:30 AM' format."""
    hours = military_time // 100
    minutes = military_time % 100
    t = datetime.strptime(f"{hours}:{minutes}", "%H:%M")
    return t.strftime("%I:%M %p")

@app.route('/')
def home():
    return "✅ Flask server running!"

@app.route('/predict', methods=['GET'])
def predict():
    crn = request.args.get('crn')

    if not crn:
        return jsonify({'error': 'Missing CRN parameter'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get Room, Building, BeginTime, EndTime, Course Info for given CRN
    query_get_class = """
    SELECT cm.Room, cm.Building, cm.BeginTime, cm.EndTime, sr.CourseTitle, sr.Subject, sr.CourseNumber
    FROM ClassMeetings cm
    JOIN StudentRegistrations sr ON cm.CRN = sr.CRN
    WHERE cm.CRN = ?
    """
    cursor.execute(query_get_class, (crn,))
    class_info = cursor.fetchone()

    if not class_info:
        conn.close()
        return jsonify({'error': 'CRN not found'}), 404

    room = class_info['Room']
    building = class_info['Building']
    begintime = class_info['BeginTime']
    endtime = class_info['EndTime']
    course_title = class_info['CourseTitle']
    subject = class_info['Subject']
    course_number = class_info['CourseNumber']

    messages = []
    conflict_detected = False
    overcapacity_detected = False
    overlap_minutes_total = None
    overcapacity_percent = None

    # Check for overlaps
    overlap_query = """
    SELECT CRN, BeginTime, EndTime
    FROM ClassMeetings
    WHERE Room = ?
      AND CRN != ?
      AND (
        (BeginTime BETWEEN ? AND ?) OR
        (EndTime BETWEEN ? AND ?) OR
        (? BETWEEN BeginTime AND EndTime) OR
        (? BETWEEN BeginTime AND EndTime)
      )
    """
    cursor.execute(overlap_query, (room, crn, begintime, endtime, begintime, endtime, begintime, endtime))
    overlaps = cursor.fetchall()

    for row in overlaps:
        conflict_detected = True
        overlap_start = max(begintime, row['BeginTime'])
        overlap_end = min(endtime, row['EndTime'])
        overlap_duration_minutes = max(0, ((overlap_end // 100) * 60 + (overlap_end % 100)) -
                                           ((overlap_start // 100) * 60 + (overlap_start % 100)))

        if overlap_minutes_total is None:
            overlap_minutes_total = overlap_duration_minutes
        else:
            overlap_minutes_total += overlap_duration_minutes

        messages.append(
            f"⚡ Conflict with CRN {row['CRN']}: Overlap from {military_to_am_pm(overlap_start)} to {military_to_am_pm(overlap_end)} ({overlap_duration_minutes} minutes)"
        )

    # Check for overcapacity
    capacity_query = """
    SELECT sr.Enrl_Actual, cm.RoomCapacity
    FROM StudentRegistrations sr
    JOIN ClassMeetings cm ON sr.CRN = cm.CRN
    WHERE sr.CRN = ?
    """
    cursor.execute(capacity_query, (crn,))
    cap_result = cursor.fetchone()

    if cap_result:
        enrolled = cap_result['Enrl_Actual']
        room_capacity = cap_result['RoomCapacity']

        if room_capacity and enrolled and enrolled > room_capacity:
            overcapacity_detected = True
            extra_students = enrolled - room_capacity
            overcapacity_percent = round((extra_students / room_capacity) * 100, 2)
            messages.append(
                f"🚨 Overcapacity: Room capacity {room_capacity}, but {enrolled} students enrolled (Over by {extra_students})"
            )

    conn.close()

    return jsonify({
        'crn': crn,
        'building': building,
        'room': room,
        'begintime': military_to_am_pm(begintime),
        'endtime': military_to_am_pm(endtime),
        'conflict': conflict_detected,
        'overcapacity': overcapacity_detected,
        'messages': messages if messages else ["✅ No issues detected"],
        'notes': {
            'overlap_minutes': overlap_minutes_total,
            'overcapacity_percent': overcapacity_percent
        },
        'course_title': course_title,
        'subject': subject,
        'course_number': course_number
    })

@app.route('/predict-overenrollment', methods=['GET'])
def predict_overenrollment():
    crn = request.args.get('crn')

    if not crn:
        return jsonify({'error': 'Missing CRN parameter'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT Enrl_Actual, RoomCapacity
    FROM StudentRegistrations
    JOIN ClassMeetings ON StudentRegistrations.CRN = ClassMeetings.CRN
    WHERE StudentRegistrations.CRN = ?
    """
    cursor.execute(query, (crn,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({'error': 'CRN not found'}), 404

    enrolled = row['Enrl_Actual']
    capacity = row['RoomCapacity']
    conn.close()

    if not enrolled or not capacity:
        return jsonify({'error': 'Missing enrollment or room capacity info'}), 400

    overenrollment = enrolled - capacity

    if overenrollment <= 0:
        prediction = "Low Risk of Over-Enrollment"
    elif overenrollment <= 10:
        prediction = "Medium Risk of Over-Enrollment"
    else:
        prediction = "High Risk of Over-Enrollment"

    return jsonify({
        'crn': crn,
        'average_overenrollment': overenrollment,
        'prediction': prediction
    })

@app.route('/search-courses', methods=['GET'])
def search_courses():
    search_term = request.args.get('q')

    if not search_term:
        return jsonify({'error': 'Missing search query'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT DISTINCT CourseTitle, CRN
    FROM StudentRegistrations
    WHERE CourseTitle LIKE ?
    LIMIT 10
    """
    cursor.execute(query, (f"%{search_term}%",))
    results = cursor.fetchall()

    courses = [{'course_title': row['CourseTitle'], 'crn': row['CRN']} for row in results]

    conn.close()

    return jsonify(courses)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
