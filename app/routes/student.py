# app/routes/student.py
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify, current_app
from app.utils.decorators import student_required
from app.services.student_service import StudentService
from app.services.course_service import CourseService
from app.services.user_service import UserService
from app.services.material_service import MaterialService
from app.services.assignment_service import AssignmentService
from app.services.test_service import TestService
from datetime import datetime
import json
import os
import traceback
from werkzeug.utils import secure_filename

bp = Blueprint('student', __name__)

# ==================== FILE UPLOAD CONFIGURATION ====================

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 
    'txt', 'md', 'csv', 'zip', 'rar', '7z',
    'jpg', 'jpeg', 'png', 'gif', 'svg',
    'mp4', 'avi', 'mov', 'mp3', 'wav'
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== DASHBOARD ====================

@bp.route('/dashboard')
@student_required
def dashboard():
    """Student dashboard"""
    try:
        student_id = session.get('user_id')
        student_service = StudentService()
        user_service = UserService()
        
        # Get student data
        student = user_service.get_user(student_id)
        if not student:
            flash('Student not found', 'error')
            return redirect(url_for('auth.logout'))
        
        # Store matric number in session if not already
        if 'matric_no' not in session and student.get('matric_no'):
            session['matric_no'] = student.get('matric_no')
        
        # Get enrolled courses with details
        enrolled_courses = student_service.get_enrolled_courses(student_id)
        
        # Get statistics
        stats = student_service.get_student_stats(student_id)
        
        # Get pending assignments
        pending_assignments = student_service.get_pending_assignments(student_id)
        
        # Get recent activities
        recent_activities = student_service.get_recent_activities(student_id, 5)
        
        return render_template('student/dashboard.html',
                              user_name=session.get('user_name', 'Student'),
                              student=student,
                              courses=enrolled_courses,
                              stats=stats,
                              pending_assignments=pending_assignments,
                              recent_activities=recent_activities)
    except Exception as e:
        current_app.logger.error(f"Student dashboard error: {e}")
        traceback.print_exc()
        flash('Error loading dashboard', 'error')
        return render_template('student/dashboard.html',
                              user_name=session.get('user_name', 'Student'),
                              courses=[],
                              stats={},
                              pending_assignments=[],
                              recent_activities=[])

# ==================== COURSE DETAIL ====================

@bp.route('/course/<course_code>')
@student_required
def course_detail(course_code):
    """View course details"""
    try:
        student_id = session.get('user_id')
        student_service = StudentService()
        course_service = CourseService()
        
        # Check if student is enrolled
        if not student_service.is_enrolled(student_id, course_code):
            flash('You are not enrolled in this course', 'error')
            return redirect(url_for('student.dashboard'))
        
        # Get course data
        course = course_service.get_course(course_code)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('student.dashboard'))
        
        # Get course materials, assignments, tests, announcements
        materials = course_service.get_course_materials(course_code) or []
        assignments = course_service.get_course_assignments(course_code) or []
        tests = course_service.get_course_tests(course_code) or []
        announcements = course_service.get_course_announcements(course_code) or []
        
        # Check submission status for assignments
        for assignment in assignments:
            assignment['submitted'] = student_service.has_submitted_assignment(
                student_id, assignment.get('assignment_id')
            )
            if assignment['submitted']:
                submission = student_service.get_assignment_submission(
                    student_id, assignment.get('assignment_id')
                )
                if submission:
                    assignment['grade'] = submission.get('grade')
                    assignment['feedback'] = submission.get('feedback')
        
        # Check test attempts
        for test in tests:
            test['attempted'] = student_service.has_attempted_test(
                student_id, test.get('test_id')
            )
            if test['attempted']:
                attempt = student_service.get_test_attempt(
                    student_id, test.get('test_id')
                )
                if attempt:
                    test['score'] = attempt.get('score')
                    test['total_marks'] = attempt.get('total_marks')
        
        return render_template('student/course_detail.html',
                              course=course,
                              materials=materials,
                              assignments=assignments,
                              tests=tests,
                              announcements=announcements)
    except Exception as e:
        current_app.logger.error(f"Course detail error: {e}")
        traceback.print_exc()
        flash('Error loading course details', 'error')
        return redirect(url_for('student.dashboard'))

# ==================== COURSE REGISTRATION ====================

@bp.route('/register-courses')
@student_required
def register_courses():
    """View available courses for registration based on level and semester"""
    try:
        student_id = session.get('user_id')
        current_app.logger.info(f"Loading register courses for student: {student_id}")
        
        student_service = StudentService()
        user_service = UserService()
        
        # Get student data
        student = user_service.get_user(student_id)
        if not student:
            current_app.logger.error(f"Student not found: {student_id}")
            flash('Student not found', 'error')
            return redirect(url_for('student.dashboard'))
        
        # Get student's level and semester
        level, semester = student_service.get_student_level_semester(student_id)
        current_app.logger.info(f"Student level: {level}, semester: {semester}")
        
        # Get currently enrolled courses
        enrolled_codes = student.get('enrolled_courses', [])
        
        # Get available courses based on level and semester
        available_courses = student_service.get_available_courses(student_id)
        
        # Get level display name
        level_display = {
            'nd1': 'ND I',
            'nd2': 'ND II', 
            'hnd1': 'HND I',
            'hnd2': 'HND II'
        }.get(level, level.upper() if level else 'Not Set')
        
        semester_display = {
            'first': 'First Semester',
            'second': 'Second Semester'
        }.get(semester, semester.capitalize() if semester else 'Not Set')
        
        current_app.logger.info(f"Available courses: {len(available_courses)}")
        
        if not level or not semester:
            flash('Your level and semester are not set. Please contact the administrator.', 'warning')
        
        return render_template('student/register_courses.html',
                              user_name=session.get('user_name', 'Student'),
                              student=student,
                              available_courses=available_courses,
                              enrolled_courses=enrolled_codes,
                              current_level=level,
                              current_semester=semester,
                              level_display=level_display,
                              semester_display=semester_display)
    except Exception as e:
        current_app.logger.error(f"Register courses error: {e}")
        traceback.print_exc()
        flash(f'Error loading courses: {str(e)}', 'error')
        return render_template('student/register_courses.html',
                              user_name=session.get('user_name', 'Student'),
                              student={},
                              available_courses=[],
                              enrolled_courses=[],
                              current_level=None,
                              current_semester=None,
                              level_display='Not Set',
                              semester_display='Not Set')

@bp.route('/register-courses/enroll', methods=['POST'])
@student_required
def enroll_courses():
    """Enroll in selected courses"""
    try:
        student_id = session.get('user_id')
        student_service = StudentService()
        
        # Get selected courses
        selected_courses = request.form.getlist('courses')
        
        if not selected_courses:
            flash('Please select at least one course to register', 'warning')
            return redirect(url_for('student.register_courses'))
        
        # Process enrollment
        result = student_service.enroll_courses(student_id, selected_courses)
        
        if result['success'] > 0:
            flash(f'Successfully enrolled in {result["success"]} course(s)!', 'success')
        if result['failed']:
            flash(f'Failed to enroll in: {", ".join(result["failed"])}', 'warning')
        
        return redirect(url_for('student.dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Enroll courses error: {e}")
        traceback.print_exc()
        flash('Error enrolling in courses', 'error')
        return redirect(url_for('student.register_courses'))

@bp.route('/register-courses/drop/<course_code>', methods=['POST'])
@student_required
def drop_course(course_code):
    """Drop a course"""
    try:
        student_id = session.get('user_id')
        student_service = StudentService()
        
        result = student_service.drop_course(student_id, course_code)
        
        if result:
            flash(f'Successfully dropped {course_code}', 'success')
        else:
            flash(f'Failed to drop {course_code}', 'error')
        
        return redirect(url_for('student.dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Drop course error: {e}")
        traceback.print_exc()
        flash('Error dropping course', 'error')
        return redirect(url_for('student.dashboard'))

# ==================== MATERIAL VIEW ====================

@bp.route('/materials/<material_id>/view')
@student_required
def view_material(material_id):
    """View a material"""
    try:
        material_service = MaterialService()
        material = material_service.get_material(material_id)
        
        if not material:
            flash('Material not found', 'error')
            return redirect(url_for('student.dashboard'))
        
        # Increment download count
        material_service.increment_downloads(material_id)
        
        # Redirect to the file URL
        if material.get('file_url'):
            return redirect(material['file_url'])
        else:
            flash('No file available', 'error')
            return redirect(request.referrer or url_for('student.dashboard'))
    except Exception as e:
        current_app.logger.error(f"View material error: {e}")
        flash('Error viewing material', 'error')
        return redirect(url_for('student.dashboard'))

# ==================== ASSIGNMENT SUBMISSION ====================

@bp.route('/assignments/<assignment_id>/submit', methods=['GET', 'POST'])
@student_required
def submit_assignment(assignment_id):
    """Submit an assignment"""
    try:
        student_id = session.get('user_id')
        student_service = StudentService()
        assignment_service = AssignmentService()
        user_service = UserService()
        
        assignment = assignment_service.get_assignment(assignment_id)
        if not assignment:
            flash('Assignment not found', 'error')
            return redirect(url_for('student.dashboard'))
        
        # Check if student is enrolled in the course
        course_code = assignment.get('course_code')
        if not student_service.is_enrolled(student_id, course_code):
            flash('You are not enrolled in this course', 'error')
            return redirect(url_for('student.dashboard'))
        
        # Check if already submitted
        if student_service.has_submitted_assignment(student_id, assignment_id):
            flash('You have already submitted this assignment', 'warning')
            return redirect(url_for('student.course_detail', course_code=course_code))
        
        if request.method == 'POST':
            # Handle file upload
            file_url = None
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename:
                    if allowed_file(file.filename):
                        # Create assignment-specific folder
                        assignment_folder = os.path.join(UPLOAD_FOLDER, 'assignments', assignment_id)
                        os.makedirs(assignment_folder, exist_ok=True)
                        
                        # Secure filename and save
                        original_filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        unique_filename = f"{student_id}_{timestamp}_{original_filename}"
                        file_path = os.path.join(assignment_folder, unique_filename)
                        file.save(file_path)
                        
                        file_url = f"/static/uploads/assignments/{assignment_id}/{unique_filename}"
                    else:
                        flash('File type not allowed', 'error')
                        return redirect(url_for('student.submit_assignment', assignment_id=assignment_id))
            
            if not file_url and not request.form.get('text_submission'):
                flash('Please provide a file or text submission', 'error')
                return redirect(url_for('student.submit_assignment', assignment_id=assignment_id))
            
            # Get student data
            student = user_service.get_user(student_id)
            
            # Create submission
            submission_data = {
                'student_id': student_id,
                'student_name': student.get('first_name') + ' ' + student.get('last_name'),
                'matric_no': student.get('matric_no'),
                'file_url': file_url,
                'text_submission': request.form.get('text_submission'),
                'submitted_at': datetime.now().isoformat(),
                'grade': None,
                'feedback': ''
            }
            
            result = student_service.submit_assignment(assignment_id, submission_data)
            
            if result:
                flash('Assignment submitted successfully!', 'success')
            else:
                flash('Failed to submit assignment', 'error')
            
            return redirect(url_for('student.course_detail', course_code=course_code))
        
        return render_template('student/submit_assignment.html',
                              assignment=assignment)
    except Exception as e:
        current_app.logger.error(f"Submit assignment error: {e}")
        traceback.print_exc()
        flash('Error submitting assignment', 'error')
        return redirect(url_for('student.dashboard'))

# ==================== TEST TAKING ====================

@bp.route('/tests/<test_id>/take', methods=['GET', 'POST'])
@student_required
def take_test(test_id):
    """Take a test"""
    try:
        student_id = session.get('user_id')
        student_service = StudentService()
        test_service = TestService()
        user_service = UserService()
        
        test = test_service.get_test(test_id)
        if not test:
            flash('Test not found', 'error')
            return redirect(url_for('student.dashboard'))
        
        # Check if student is enrolled in the course
        course_code = test.get('course_code')
        if not student_service.is_enrolled(student_id, course_code):
            flash('You are not enrolled in this course', 'error')
            return redirect(url_for('student.dashboard'))
        
        # Check if already attempted
        if student_service.has_attempted_test(student_id, test_id):
            flash('You have already taken this test', 'warning')
            return redirect(url_for('student.course_detail', course_code=course_code))
        
        if request.method == 'POST':
            # Get answers from form
            answers = []
            questions = test.get('questions', [])
            
            for i, q in enumerate(questions):
                answer = request.form.get(f'question_{i}')
                if answer is not None:
                    answers.append({
                        'question_index': i,
                        'answer': int(answer) if answer.isdigit() else answer
                    })
            
            # Get student data
            student = user_service.get_user(student_id)
            
            # Calculate score
            score_data = student_service.calculate_test_score(test, answers)
            
            # Save attempt
            attempt_data = {
                'student_id': student_id,
                'student_name': student.get('first_name') + ' ' + student.get('last_name'),
                'matric_no': student.get('matric_no'),
                'answers': answers,
                'submitted_at': datetime.now().isoformat(),
                'score': score_data['obtained_marks'],
                'total_marks': score_data['total_marks'],
                'correct_count': score_data['correct_count'],
                'total_questions': len(questions)
            }
            
            result = student_service.submit_test_attempt(test_id, attempt_data)
            
            if result:
                flash(f'Test submitted! You scored {score_data["obtained_marks"]}/{score_data["total_marks"]}', 'success')
            else:
                flash('Failed to submit test', 'error')
            
            return redirect(url_for('student.test_result', test_id=test_id))
        
        return render_template('student/take_test.html',
                              test=test)
    except Exception as e:
        current_app.logger.error(f"Take test error: {e}")
        traceback.print_exc()
        flash('Error taking test', 'error')
        return redirect(url_for('student.dashboard'))

# ==================== TEST RESULTS ====================

@bp.route('/tests/<test_id>/result')
@student_required
def test_result(test_id):
    """View test results"""
    try:
        student_id = session.get('user_id')
        student_service = StudentService()
        test_service = TestService()
        
        test = test_service.get_test(test_id)
        if not test:
            flash('Test not found', 'error')
            return redirect(url_for('student.dashboard'))
        
        # Get student's attempt
        attempt = student_service.get_test_attempt(student_id, test_id)
        
        if not attempt:
            flash('You have not taken this test yet', 'warning')
            return redirect(url_for('student.course_detail', course_code=test.get('course_code')))
        
        return render_template('student/test_result.html',
                              test=test,
                              attempt=attempt)
    except Exception as e:
        current_app.logger.error(f"Test result error: {e}")
        flash('Error loading test results', 'error')
        return redirect(url_for('student.dashboard'))