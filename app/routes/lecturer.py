# app/routes/lecturer.py
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify, current_app, send_file
from app.utils.decorators import lecturer_required
from app.services.lecturer_service import LecturerService
from app.services.course_service import CourseService
from app.services.material_service import MaterialService
from app.services.assignment_service import AssignmentService
from app.services.test_service import TestService
from datetime import datetime
import json
import os
import csv
import io
import traceback
from werkzeug.utils import secure_filename

# Define the blueprint
bp = Blueprint('lecturer', __name__)

# ==================== FILE UPLOAD CONFIGURATION ====================

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 
    'txt', 'md', 'csv', 'zip', 'rar', '7z',
    'jpg', 'jpeg', 'png', 'gif', 'svg', 'bmp',
    'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv',
    'mp3', 'wav', 'aac', 'flac', 'ogg',
    'json', 'xml', 'html', 'css', 'js'
}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_icon(filename):
    """Get icon for file type"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    icons = {
        'pdf': '📄', 'doc': '📝', 'docx': '📝',
        'ppt': '📊', 'pptx': '📊',
        'xls': '📈', 'xlsx': '📈',
        'txt': '📃', 'md': '📃', 'csv': '📊',
        'zip': '📦', 'rar': '📦', '7z': '📦',
        'mp4': '🎬', 'avi': '🎬', 'mov': '🎬', 'mkv': '🎬',
        'mp3': '🎵', 'wav': '🎵', 'aac': '🎵',
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'svg': '🖼️',
        'json': '📋', 'xml': '📋', 'html': '🌐', 'css': '🎨', 'js': '⚡'
    }
    return icons.get(ext, '📁')

# ==================== DASHBOARD ====================

@bp.route('/dashboard')
@lecturer_required
def dashboard():
    """Lecturer dashboard"""
    try:
        lecturer_id = session.get('user_id')
        lecturer_service = LecturerService()
        
        courses = lecturer_service.get_lecturer_courses(lecturer_id)
        
        # Get statistics
        total_students = 0
        total_materials = 0
        total_assignments = 0
        total_tests = 0
        
        for course in courses:
            total_students += len(course.get('enrolled_students', []))
            total_materials += len(lecturer_service.get_course_materials(course.get('course_code')))
            total_assignments += len(lecturer_service.get_course_assignments(course.get('course_code')))
            total_tests += len(lecturer_service.get_course_tests(course.get('course_code')))
        
        stats = {
            'total_courses': len(courses),
            'total_students': total_students,
            'total_materials': total_materials,
            'total_assignments': total_assignments,
            'total_tests': total_tests,
            'recent_courses': courses[:5]
        }
        
        return render_template('lecturer/dashboard.html', 
                              user_name=session.get('user_name', 'Lecturer'),
                              courses=courses,
                              stats=stats)
    except Exception as e:
        current_app.logger.error(f"Lecturer dashboard error: {e}")
        traceback.print_exc()
        flash('Error loading dashboard', 'error')
        return render_template('lecturer/dashboard.html', 
                              user_name=session.get('user_name', 'Lecturer'),
                              courses=[],
                              stats={})

# ==================== COURSE DETAIL ====================

@bp.route('/course/<course_code>')
@lecturer_required
def course_detail(course_code):
    """View course details"""
    try:
        current_app.logger.info(f"Loading course detail for: {course_code}")
        
        lecturer_service = LecturerService()
        course_service = CourseService()
        
        # Get course
        course = course_service.get_course(course_code)
        
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('lecturer.dashboard'))
        
        # Check if lecturer owns this course
        lecturer_id = session.get('user_id')
        if course.get('lecturer_id') != lecturer_id:
            flash('You do not have permission to view this course', 'error')
            return redirect(url_for('lecturer.dashboard'))
        
        # Get course data
        students = lecturer_service.get_course_students(course_code) or []
        materials = lecturer_service.get_course_materials(course_code) or []
        assignments = lecturer_service.get_course_assignments(course_code) or []
        tests = lecturer_service.get_course_tests(course_code) or []
        announcements = lecturer_service.get_course_announcements(course_code) or []
        
        return render_template('lecturer/course_detail.html',
                              course=course,
                              students=students,
                              materials=materials,
                              assignments=assignments,
                              tests=tests,
                              announcements=announcements)
                              
    except Exception as e:
        current_app.logger.error(f"Course detail error: {e}")
        traceback.print_exc()
        flash('Error loading course details', 'error')
        return redirect(url_for('lecturer.dashboard'))

# ==================== STUDENT MANAGEMENT ====================

@bp.route('/course/<course_code>/students')
@lecturer_required
def course_students(course_code):
    """View students enrolled in a course"""
    try:
        lecturer_service = LecturerService()
        course_service = CourseService()
        
        course = course_service.get_course(course_code)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('lecturer.dashboard'))
        
        students = lecturer_service.get_course_students(course_code)
        
        return render_template('lecturer/students.html',
                              course=course,
                              students=students)
    except Exception as e:
        current_app.logger.error(f"Course students error: {e}")
        traceback.print_exc()
        flash('Error loading students', 'error')
        return redirect(url_for('lecturer.dashboard'))

# ==================== ANNOUNCEMENT MANAGEMENT ====================

@bp.route('/course/<course_code>/announcements', methods=['GET', 'POST'])
@lecturer_required
def manage_announcements(course_code):
    """Manage announcements for a course"""
    try:
        lecturer_service = LecturerService()
        course_service = CourseService()
        
        course = course_service.get_course(course_code)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('lecturer.dashboard'))
        
        if request.method == 'POST':
            announcement_data = {
                'title': request.form.get('title'),
                'content': request.form.get('content'),
                'created_by': session.get('user_id')
            }
            
            result = lecturer_service.send_announcement(course_code, announcement_data)
            if result:
                flash('Announcement sent successfully!', 'success')
            else:
                flash('Failed to send announcement', 'error')
            
            return redirect(url_for('lecturer.manage_announcements', course_code=course_code))
        
        announcements = lecturer_service.get_course_announcements(course_code)
        
        return render_template('lecturer/announcements.html',
                              course=course,
                              announcements=announcements)
    except Exception as e:
        current_app.logger.error(f"Manage announcements error: {e}")
        traceback.print_exc()
        flash('Error loading announcements', 'error')
        return redirect(url_for('lecturer.dashboard'))

# ==================== MATERIAL MANAGEMENT ====================

@bp.route('/course/<course_code>/materials', methods=['GET', 'POST'])
@lecturer_required
def manage_materials(course_code):
    """Manage materials for a course"""
    try:
        lecturer_service = LecturerService()
        course_service = CourseService()
        
        course = course_service.get_course(course_code)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('lecturer.dashboard'))
        
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            material_type = request.form.get('material_type')
            is_published = request.form.get('is_published') == 'on'
            
            if not title:
                flash('Title is required', 'error')
                return redirect(url_for('lecturer.manage_materials', course_code=course_code))
            
            file_url = None
            file_name = None
            
            # Handle file upload
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename:
                    if allowed_file(file.filename):
                        # Create course-specific folder
                        course_folder = os.path.join(UPLOAD_FOLDER, course_code)
                        os.makedirs(course_folder, exist_ok=True)
                        
                        # Secure filename and save
                        original_filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        unique_filename = f"{timestamp}_{original_filename}"
                        file_path = os.path.join(course_folder, unique_filename)
                        file.save(file_path)
                        
                        # Generate URL for the file
                        file_url = f"/static/uploads/{course_code}/{unique_filename}"
                        file_name = original_filename
                        
                        current_app.logger.info(f"File uploaded: {file_path}")
                    else:
                        flash(f'File type not allowed. Allowed types: {", ".join(sorted(ALLOWED_EXTENSIONS))}', 'error')
                        return redirect(url_for('lecturer.manage_materials', course_code=course_code))
                elif request.form.get('file_url'):
                    # Use URL if provided instead of file upload
                    file_url = request.form.get('file_url')
                    file_name = file_url.split('/')[-1] if '/' in file_url else None
            
            if not file_url:
                flash('Please provide a file or a file URL', 'error')
                return redirect(url_for('lecturer.manage_materials', course_code=course_code))
            
            material_data = {
                'title': title,
                'description': description,
                'course_code': course_code,
                'material_type': material_type,
                'file_url': file_url,
                'file_name': file_name,
                'file_icon': get_file_icon(file_name or file_url),
                'uploaded_by': session.get('user_id'),
                'is_published': is_published
            }
            
            result = lecturer_service.create_material(material_data)
            if result:
                flash('Material uploaded successfully!', 'success')
            else:
                flash('Failed to upload material', 'error')
            
            return redirect(url_for('lecturer.manage_materials', course_code=course_code))
        
        materials = lecturer_service.get_course_materials(course_code)
        
        return render_template('lecturer/materials.html',
                              course=course,
                              materials=materials)
    except Exception as e:
        current_app.logger.error(f"Manage materials error: {e}")
        traceback.print_exc()
        flash('Error loading materials', 'error')
        return redirect(url_for('lecturer.dashboard'))

@bp.route('/materials/<material_id>/delete', methods=['POST'])
@lecturer_required
def delete_material(material_id):
    """Delete a material"""
    try:
        material_service = MaterialService()
        
        # Get material to find file path
        material = material_service.get_material(material_id)
        if material and material.get('file_url'):
            # Delete the physical file if it exists in uploads folder
            file_path = material['file_url'].replace('/static/uploads/', '')
            full_path = os.path.join(UPLOAD_FOLDER, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                current_app.logger.info(f"File deleted: {full_path}")
        
        result = material_service.delete_material(material_id)
        
        if result:
            flash('Material deleted successfully!', 'success')
        else:
            flash('Failed to delete material', 'error')
        
        return redirect(request.referrer or url_for('lecturer.dashboard'))
    except Exception as e:
        current_app.logger.error(f"Delete material error: {e}")
        traceback.print_exc()
        flash('Error deleting material', 'error')
        return redirect(url_for('lecturer.dashboard'))

@bp.route('/materials/<material_id>/download')
@lecturer_required
def download_material(material_id):
    """Download a material"""
    try:
        material_service = MaterialService()
        material = material_service.get_material(material_id)
        
        if not material:
            flash('Material not found', 'error')
            return redirect(url_for('lecturer.dashboard'))
        
        # Increment download count
        material_service.increment_downloads(material_id)
        
        # Redirect to the file URL
        if material.get('file_url'):
            return redirect(material['file_url'])
        else:
            flash('No file available for download', 'error')
            return redirect(url_for('lecturer.dashboard'))
    except Exception as e:
        current_app.logger.error(f"Download material error: {e}")
        flash('Error downloading material', 'error')
        return redirect(url_for('lecturer.dashboard'))

# ==================== ASSIGNMENT MANAGEMENT ====================

@bp.route('/course/<course_code>/assignments', methods=['GET', 'POST'])
@lecturer_required
def manage_assignments(course_code):
    """Manage assignments for a course"""
    try:
        lecturer_service = LecturerService()
        course_service = CourseService()
        
        course = course_service.get_course(course_code)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('lecturer.dashboard'))
        
        if request.method == 'POST':
            assignment_data = {
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'course_code': course_code,
                'due_date': request.form.get('due_date'),
                'total_marks': int(request.form.get('total_marks', 100)),
                'instructions': request.form.get('instructions'),
                'attachment_url': request.form.get('attachment_url'),
                'created_by': session.get('user_id'),
                'is_published': request.form.get('is_published') == 'on'
            }
            
            result = lecturer_service.create_assignment(assignment_data)
            if result:
                flash('Assignment created successfully!', 'success')
            else:
                flash('Failed to create assignment', 'error')
            
            return redirect(url_for('lecturer.manage_assignments', course_code=course_code))
        
        assignments = lecturer_service.get_course_assignments(course_code)
        
        return render_template('lecturer/assignments.html',
                              course=course,
                              assignments=assignments)
    except Exception as e:
        current_app.logger.error(f"Manage assignments error: {e}")
        traceback.print_exc()
        flash('Error loading assignments', 'error')
        return redirect(url_for('lecturer.dashboard'))

@bp.route('/assignments/<assignment_id>/submissions')
@lecturer_required
def view_submissions(assignment_id):
    """View submissions for an assignment"""
    try:
        lecturer_service = LecturerService()
        assignment_service = AssignmentService()
        
        assignment = assignment_service.get_assignment(assignment_id)
        if not assignment:
            flash('Assignment not found', 'error')
            return redirect(url_for('lecturer.dashboard'))
        
        submissions = lecturer_service.get_student_submissions(assignment_id)
        
        return render_template('lecturer/submissions.html',
                              assignment=assignment,
                              submissions=submissions)
    except Exception as e:
        current_app.logger.error(f"View submissions error: {e}")
        traceback.print_exc()
        flash('Error loading submissions', 'error')
        return redirect(url_for('lecturer.dashboard'))

@bp.route('/assignments/<assignment_id>/grade', methods=['POST'])
@lecturer_required
def grade_submission(assignment_id):
    """Grade a student's submission"""
    try:
        lecturer_service = LecturerService()
        
        student_id = request.form.get('student_id')
        grade = float(request.form.get('grade', 0))
        feedback = request.form.get('feedback', '')
        
        result = lecturer_service.grade_student_submission(assignment_id, student_id, grade, feedback)
        
        if result:
            flash('Submission graded successfully!', 'success')
        else:
            flash('Failed to grade submission', 'error')
        
        return redirect(url_for('lecturer.view_submissions', assignment_id=assignment_id))
    except Exception as e:
        current_app.logger.error(f"Grade submission error: {e}")
        traceback.print_exc()
        flash('Error grading submission', 'error')
        return redirect(url_for('lecturer.dashboard'))

@bp.route('/assignments/<assignment_id>/delete', methods=['POST'])
@lecturer_required
def delete_assignment(assignment_id):
    """Delete an assignment"""
    try:
        assignment_service = AssignmentService()
        result = assignment_service.delete_assignment(assignment_id)
        
        if result:
            flash('Assignment deleted successfully!', 'success')
        else:
            flash('Failed to delete assignment', 'error')
        
        return redirect(request.referrer or url_for('lecturer.dashboard'))
    except Exception as e:
        current_app.logger.error(f"Delete assignment error: {e}")
        traceback.print_exc()
        flash('Error deleting assignment', 'error')
        return redirect(url_for('lecturer.dashboard'))

# ==================== TEST MANAGEMENT ====================

@bp.route('/course/<course_code>/tests', methods=['GET', 'POST'])
@lecturer_required
def manage_tests(course_code):
    """Manage tests for a course"""
    try:
        lecturer_service = LecturerService()
        course_service = CourseService()
        
        course = course_service.get_course(course_code)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('lecturer.dashboard'))
        
        if request.method == 'POST':
            # Check if CSV file was uploaded
            if 'csv_file' in request.files and request.files['csv_file'].filename:
                csv_file = request.files['csv_file']
                if csv_file and csv_file.filename.endswith('.csv'):
                    try:
                        # Parse CSV
                        stream = io.StringIO(csv_file.stream.read().decode("UTF8"), newline=None)
                        csv_reader = csv.DictReader(stream)
                        
                        questions = []
                        for row in csv_reader:
                            try:
                                options = json.loads(row.get('options', '[]'))
                            except:
                                options = []
                            
                            question = {
                                'question': row.get('question', ''),
                                'options': options,
                                'correct': int(row.get('correct', 0)),
                                'marks': int(row.get('marks', 1))
                            }
                            questions.append(question)
                        
                        if not questions:
                            flash('No valid questions found in CSV', 'error')
                            return redirect(url_for('lecturer.manage_tests', course_code=course_code))
                        
                        # Create test from CSV data
                        test_data = {
                            'title': request.form.get('title') or f"Test from CSV ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
                            'description': request.form.get('description', 'Test imported from CSV'),
                            'course_code': course_code,
                            'test_type': request.form.get('test_type', 'quiz'),
                            'duration_minutes': int(request.form.get('duration_minutes', 60)),
                            'total_marks': sum(q.get('marks', 1) for q in questions),
                            'instructions': request.form.get('instructions', ''),
                            'questions': questions,
                            'created_by': session.get('user_id'),
                            'is_published': request.form.get('is_published') == 'on'
                        }
                        
                        result = lecturer_service.create_test(test_data)
                        if result:
                            flash(f'Test created successfully with {len(questions)} questions from CSV!', 'success')
                        else:
                            flash('Failed to create test from CSV', 'error')
                        
                        return redirect(url_for('lecturer.manage_tests', course_code=course_code))
                        
                    except Exception as e:
                        current_app.logger.error(f"CSV import error: {e}")
                        traceback.print_exc()
                        flash(f'Error importing CSV: {str(e)}', 'error')
                        return redirect(url_for('lecturer.manage_tests', course_code=course_code))
                else:
                    flash('Please upload a valid CSV file', 'error')
                    return redirect(url_for('lecturer.manage_tests', course_code=course_code))
            
            # Regular form submission with JSON questions
            try:
                questions = json.loads(request.form.get('questions', '[]'))
                if not questions:
                    flash('Please add at least one question', 'error')
                    return redirect(url_for('lecturer.manage_tests', course_code=course_code))
            except json.JSONDecodeError as e:
                flash(f'Invalid JSON format: {str(e)}', 'error')
                return redirect(url_for('lecturer.manage_tests', course_code=course_code))
            except Exception as e:
                flash(f'Error parsing questions: {str(e)}', 'error')
                return redirect(url_for('lecturer.manage_tests', course_code=course_code))
            
            # Validate questions
            for i, q in enumerate(questions):
                if not q.get('question'):
                    flash(f'Question {i+1}: Question text is required', 'error')
                    return redirect(url_for('lecturer.manage_tests', course_code=course_code))
                if not q.get('options') or len(q.get('options', [])) < 2:
                    flash(f'Question {i+1}: At least 2 options are required', 'error')
                    return redirect(url_for('lecturer.manage_tests', course_code=course_code))
                if q.get('correct') is None:
                    flash(f'Question {i+1}: Correct answer index is required', 'error')
                    return redirect(url_for('lecturer.manage_tests', course_code=course_code))
            
            # Calculate total marks from questions
            total_marks = sum(q.get('marks', 1) for q in questions)
            
            test_data = {
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'course_code': course_code,
                'test_type': request.form.get('test_type'),
                'duration_minutes': int(request.form.get('duration_minutes', 60)),
                'total_marks': total_marks,
                'instructions': request.form.get('instructions'),
                'questions': questions,
                'created_by': session.get('user_id'),
                'is_published': request.form.get('is_published') == 'on'
            }
            
            result = lecturer_service.create_test(test_data)
            if result:
                flash(f'Test created successfully with {len(questions)} questions!', 'success')
            else:
                flash('Failed to create test', 'error')
            
            return redirect(url_for('lecturer.manage_tests', course_code=course_code))
        
        tests = lecturer_service.get_course_tests(course_code)
        
        return render_template('lecturer/tests.html',
                              course=course,
                              tests=tests)
    except Exception as e:
        current_app.logger.error(f"Manage tests error: {e}")
        traceback.print_exc()
        flash('Error loading tests', 'error')
        return redirect(url_for('lecturer.dashboard'))

@bp.route('/tests/<test_id>/delete', methods=['POST'])
@lecturer_required
def delete_test(test_id):
    """Delete a test"""
    try:
        lecturer_service = LecturerService()
        result = lecturer_service.delete_test(test_id)
        
        if result:
            flash('Test deleted successfully!', 'success')
        else:
            flash('Failed to delete test', 'error')
        
        return redirect(request.referrer or url_for('lecturer.dashboard'))
    except Exception as e:
        current_app.logger.error(f"Delete test error: {e}")
        traceback.print_exc()
        flash('Error deleting test', 'error')
        return redirect(url_for('lecturer.dashboard'))

# ==================== CSV TEMPLATE DOWNLOAD ====================

@bp.route('/tests/template/download')
@lecturer_required
def download_test_template():
    """Download CSV template for test questions"""
    try:
        # Create CSV template
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['question', 'options', 'correct', 'marks'])
        
        # Add sample rows
        sample_questions = [
            ['What is the capital of France?', '["Paris", "London", "Berlin", "Madrid"]', '0', '1'],
            ['What is 2 + 2?', '["3", "4", "5", "6"]', '1', '1'],
            ['Which planet is known as the Red Planet?', '["Venus", "Mars", "Jupiter", "Saturn"]', '1', '2']
        ]
        
        for row in sample_questions:
            writer.writerow(row)
        
        # Create response
        output.seek(0)
        bytes_data = io.BytesIO(output.getvalue().encode('utf-8'))
        
        return send_file(
            bytes_data,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'test_questions_template_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    except Exception as e:
        current_app.logger.error(f"Download template error: {e}")
        flash('Error downloading template', 'error')
        return redirect(request.referrer or url_for('lecturer.dashboard'))

# ==================== DEBUG ROUTE ====================

@bp.route('/debug/course/<course_code>')
@lecturer_required
def debug_course(course_code):
    """Debug route to check course data"""
    try:
        course_service = CourseService()
        course = course_service.get_course(course_code)
        
        if course:
            return jsonify({
                'found': True,
                'course': course,
                'lecturer_id': session.get('user_id'),
                'course_lecturer': course.get('lecturer_id'),
                'matches': course.get('lecturer_id') == session.get('user_id')
            })
        else:
            return jsonify({
                'found': False,
                'course_code': course_code
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500