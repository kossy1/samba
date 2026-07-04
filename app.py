import os
import json
from flask import Flask, request, session, redirect, url_for, render_template, jsonify
from upstash_redis import Redis
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "a-very-secret-key-for-development")

# --- Initialize Vercel KV (Redis) ---
# This will automatically use the Vercel KV environment variables in production
# or fallback to localhost for local development.
kv = Redis(
    url=os.getenv("KV_REST_API_URL", "http://localhost:6379"),
    token=os.getenv("KV_REST_API_TOKEN", "")
)

# --- Role-Based Access Control Decorator ---
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] != required_role:
                return redirect(url_for('login', error='Unauthorized Access'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Helper Functions (Data Access) ---
def get_courses():
    """Fetch all courses from the database."""
    courses_data = kv.get('courses')
    return json.loads(courses_data) if courses_data else []

def get_students():
    """Fetch all students."""
    students_data = kv.get('students')
    return json.loads(students_data) if students_data else []

def get_lecturers():
    """Fetch all lecturers."""
    lecturers_data = kv.get('lecturers')
    return json.loads(lecturers_data) if lecturers_data else []

# --- Routes ---

@app.route('/')
def home():
    """Redirect to login page."""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        # --- Authentication Logic (Replace with proper hashing) ---
        # This is a simplified example. Use a secure method for production.
        user_data = kv.hgetall(f"user:{user_id}")
        if user_data and user_data.get('password') == password:
            session['user_id'] = user_id
            session['user_name'] = user_data.get('name')
            session['user_role'] = user_data.get('role')
            if user_data.get('role') == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user_data.get('role') == 'lecturer':
                return redirect(url_for('lecturer_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Admin Module Routes ---
@app.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    # Add real statistics from KV
    context = {
        'total_students': len(get_students()),
        'total_lecturers': len(get_lecturers()),
        'total_courses': len(get_courses())
    }
    return render_template('admin_dashboard.html', **context)

# --- Lecturer Module Routes ---
@app.route('/lecturer/dashboard')
@role_required('lecturer')
def lecturer_dashboard():
    # Fetch courses for this specific lecturer
    lecturer_id = session['user_id']
    # --- Logic to fetch courses for this lecturer from KV ---
    lecturer_courses = []
    for course in get_courses():
        if course.get('lecturer_id') == lecturer_id:
            lecturer_courses.append(course)
    
    return render_template('lecturer_dashboard.html', courses=lecturer_courses)

# --- Student Module Routes ---
@app.route('/student/dashboard')
@role_required('student')
def student_dashboard():
    # Fetch enrolled courses for this student
    student_id = session['user_id']
    # --- Logic to fetch enrolled courses for this student from KV ---
    student_courses = []
    for course in get_courses():
        if student_id in course.get('enrolled_students', []):
            student_courses.append(course)
    
    return render_template('student_dashboard.html', courses=student_courses)

# --- API endpoints for dynamic interactions ---
# (POST announcements, submit assignments, etc.)

if __name__ == '__main__':
    # This runs only in local development
    app.run(debug=True, host='0.0.0.0', port=5000)