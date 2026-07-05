# app/routes/admin.py
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify, current_app, send_file
from app.utils.decorators import admin_required
from app.services.user_service import UserService
from app.services.course_service import CourseService
from app.services.department_service import DepartmentService
from app.services.material_service import MaterialService
from app.services.assignment_service import AssignmentService
from app.services.test_service import TestService
import json
import csv
import io
from datetime import datetime
import traceback
from io import BytesIO, StringIO

# Define the blueprint
bp = Blueprint('admin', __name__)

# ==================== DASHBOARD ====================

@bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard overview"""
    try:
        user_service = UserService()
        course_service = CourseService()
        department_service = DepartmentService()
        material_service = MaterialService()
        assignment_service = AssignmentService()
        test_service = TestService()
        
        # Get statistics with error handling
        stats = {
            'total_students': len(user_service.get_users_by_role('student')),
            'total_lecturers': len(user_service.get_users_by_role('lecturer')),
            'total_courses': len(course_service.get_all_courses()),
            'total_departments': len(department_service.get_all_departments()),
            'total_materials': len(material_service.get_all_materials()),
            'total_assignments': len(assignment_service.get_all_assignments()),
            'total_tests': len(test_service.get_all_tests()),
            'recent_users': user_service.get_recent_users(5),
            'recent_courses': course_service.get_recent_courses(5)
        }
        
        return render_template('admin/dashboard.html', 
                              user_name=session.get('user_name', 'Admin'),
                              stats=stats)
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {e}")
        traceback.print_exc()
        return render_template('admin/dashboard.html', 
                              user_name=session.get('user_name', 'Admin'),
                              stats={
                                  'total_students': 0,
                                  'total_lecturers': 0,
                                  'total_courses': 0,
                                  'total_departments': 0,
                                  'total_materials': 0,
                                  'total_assignments': 0,
                                  'total_tests': 0,
                                  'recent_users': [],
                                  'recent_courses': []
                              })

# ==================== USER MANAGEMENT ====================

@bp.route('/users')
@admin_required
def users():
    """Manage users"""
    try:
        user_service = UserService()
        users = user_service.get_all_users()
        return render_template('admin/users.html', users=users)
    except Exception as e:
        current_app.logger.error(f"Users error: {e}")
        flash('Error loading users', 'error')
        return render_template('admin/users.html', users=[])

@bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create a new user"""
    if request.method == 'POST':
        user_data = {
            'user_id': request.form.get('user_id'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'role': request.form.get('role'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'department': request.form.get('department'),
            'phone': request.form.get('phone'),
            'is_active': request.form.get('is_active') == 'on'
        }
        
        # Add role-specific fields
        if user_data['role'] == 'student':
            matric_no = request.form.get('matric_no')
            if not matric_no:
                flash('Matric Number is required for students', 'error')
                departments = get_departments()
                return render_template('admin/create_user.html', departments=departments)
            user_data['matric_no'] = matric_no
            user_data['programme'] = request.form.get('programme')
            user_data['year_of_study'] = int(request.form.get('year_of_study', 1))
            # Set default level and semester based on year_of_study
            year = user_data['year_of_study']
            if year == 1:
                user_data['current_level'] = 'nd1'
            elif year == 2:
                user_data['current_level'] = 'nd2'
            elif year == 3:
                user_data['current_level'] = 'hnd1'
            elif year >= 4:
                user_data['current_level'] = 'hnd2'
            else:
                user_data['current_level'] = 'nd1'
            user_data['current_semester'] = 'first'
        elif user_data['role'] == 'lecturer':
            staff_id = request.form.get('staff_id')
            if not staff_id:
                flash('Staff ID is required for lecturers', 'error')
                departments = get_departments()
                return render_template('admin/create_user.html', departments=departments)
            user_data['staff_id'] = staff_id
            user_data['specialization'] = request.form.get('specialization')
        
        user_service = UserService()
        result = user_service.create_user(user_data)
        
        if result:
            flash('User created successfully!', 'success')
            return redirect(url_for('admin.users'))
        else:
            flash('Failed to create user. Please check the data.', 'error')
    
    departments = get_departments()
    return render_template('admin/create_user.html', departments=departments)

@bp.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit a user"""
    user_service = UserService()
    user = user_service.get_user(user_id)
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.users'))
    
    if request.method == 'POST':
        user_data = {
            'email': request.form.get('email'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'department': request.form.get('department'),
            'phone': request.form.get('phone'),
            'is_active': request.form.get('is_active') == 'on'
        }
        
        # For students, update matric number if provided
        if user.get('role') == 'student':
            matric_no = request.form.get('matric_no')
            if matric_no:
                user_data['matric_no'] = matric_no
        
        # For lecturers, update staff ID if provided
        if user.get('role') == 'lecturer':
            staff_id = request.form.get('staff_id')
            if staff_id:
                user_data['staff_id'] = staff_id
        
        # Update password if provided
        if request.form.get('password'):
            user_data['password'] = request.form.get('password')
        
        result = user_service.update_user(user_id, user_data)
        if result:
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.users'))
        else:
            flash('Failed to update user.', 'error')
    
    departments = get_departments()
    return render_template('admin/edit_user.html', user=user, departments=departments)

@bp.route('/users/<user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user"""
    if user_id == 'admin':
        flash('Cannot delete admin user', 'error')
        return redirect(url_for('admin.users'))
    
    user_service = UserService()
    result = user_service.delete_user(user_id)
    
    if result:
        flash('User deleted successfully!', 'success')
        return redirect(url_for('admin.users'))
    else:
        flash('Failed to delete user', 'error')
        return redirect(url_for('admin.users'))

# ==================== STUDENT LEVEL MANAGEMENT ====================

@bp.route('/users/<user_id>/update-level', methods=['POST'])
@admin_required
def update_student_level(user_id):
    """Update student's level and semester"""
    try:
        level = request.form.get('level')
        semester = request.form.get('semester')
        matric_no = request.form.get('matric_no')
        
        if not level or not semester:
            flash('Level and semester are required', 'error')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        user_service = UserService()
        user = user_service.get_user(user_id)
        
        if not user or user.get('role') != 'student':
            flash('Student not found', 'error')
            return redirect(url_for('admin.users'))
        
        user['current_level'] = level
        user['current_semester'] = semester
        if matric_no:
            user['matric_no'] = matric_no
        user['updated_at'] = datetime.now().isoformat()
        
        result = user_service.update_user(user_id, user)
        
        if result:
            level_display = {
                'nd1': 'ND I',
                'nd2': 'ND II',
                'hnd1': 'HND I',
                'hnd2': 'HND II'
            }.get(level, level.upper())
            
            semester_display = {
                'first': 'First',
                'second': 'Second'
            }.get(semester, semester.capitalize())
            
            flash(f'Student level updated to {level_display} - {semester_display} Semester', 'success')
        else:
            flash('Failed to update student level', 'error')
        
        return redirect(url_for('admin.edit_user', user_id=user_id))
    except Exception as e:
        current_app.logger.error(f"Update student level error: {e}")
        flash('Error updating student level', 'error')
        return redirect(url_for('admin.users'))

# ==================== COURSE MANAGEMENT ====================

@bp.route('/courses')
@admin_required
def courses():
    """Manage courses"""
    try:
        course_service = CourseService()
        courses = course_service.get_all_courses()
        return render_template('admin/courses.html', courses=courses)
    except Exception as e:
        current_app.logger.error(f"Courses error: {e}")
        flash('Error loading courses', 'error')
        return render_template('admin/courses.html', courses=[])

@bp.route('/courses/create', methods=['GET', 'POST'])
@admin_required
def create_course():
    """Create a new course"""
    if request.method == 'POST':
        course_data = {
            'course_code': request.form.get('course_code'),
            'course_name': request.form.get('course_name'),
            'description': request.form.get('description'),
            'department': request.form.get('department'),
            'credits': int(request.form.get('credits', 3)),
            'lecturer_id': request.form.get('lecturer_id'),
            'level': request.form.get('level'),
            'semester': request.form.get('semester'),
            'academic_year': request.form.get('academic_year'),
            'is_active': request.form.get('is_active') == 'on'
        }
        
        # Validate required fields
        if not course_data['course_code'] or not course_data['course_name']:
            flash('Course Code and Course Name are required', 'error')
            return render_template('admin/create_course.html', 
                                  lecturers=get_lecturers(), 
                                  departments=get_departments())
        
        if not course_data['level']:
            flash('Please select a level', 'error')
            return render_template('admin/create_course.html', 
                                  lecturers=get_lecturers(), 
                                  departments=get_departments())
        
        if not course_data['semester']:
            flash('Please select a semester', 'error')
            return render_template('admin/create_course.html', 
                                  lecturers=get_lecturers(), 
                                  departments=get_departments())
        
        course_service = CourseService()
        
        # Check if course code already exists
        existing = course_service.get_course(course_data['course_code'])
        if existing:
            flash(f'Course code {course_data["course_code"]} already exists', 'error')
            return render_template('admin/create_course.html', 
                                  lecturers=get_lecturers(), 
                                  departments=get_departments())
        
        result = course_service.create_course(course_data)
        
        if result:
            flash('Course created successfully!', 'success')
            return redirect(url_for('admin.courses'))
        else:
            flash('Failed to create course. Please check the data.', 'error')
    
    lecturers = get_lecturers()
    departments = get_departments()
    return render_template('admin/create_course.html', 
                          lecturers=lecturers, 
                          departments=departments)

@bp.route('/courses/<course_code>/edit', methods=['GET', 'POST'])
@admin_required
def edit_course(course_code):
    """Edit a course"""
    course_service = CourseService()
    course = course_service.get_course(course_code)
    
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('admin.courses'))
    
    if request.method == 'POST':
        course_data = {
            'course_name': request.form.get('course_name'),
            'description': request.form.get('description'),
            'department': request.form.get('department'),
            'credits': int(request.form.get('credits', 3)),
            'lecturer_id': request.form.get('lecturer_id'),
            'level': request.form.get('level'),
            'semester': request.form.get('semester'),
            'academic_year': request.form.get('academic_year'),
            'is_active': request.form.get('is_active') == 'on'
        }
        
        # Validate required fields
        if not course_data['course_name']:
            flash('Course Name is required', 'error')
            return render_template('admin/edit_course.html', 
                                  course=course,
                                  lecturers=get_lecturers(), 
                                  departments=get_departments())
        
        if not course_data['level']:
            flash('Please select a level', 'error')
            return render_template('admin/edit_course.html', 
                                  course=course,
                                  lecturers=get_lecturers(), 
                                  departments=get_departments())
        
        if not course_data['semester']:
            flash('Please select a semester', 'error')
            return render_template('admin/edit_course.html', 
                                  course=course,
                                  lecturers=get_lecturers(), 
                                  departments=get_departments())
        
        result = course_service.update_course(course_code, course_data)
        if result:
            flash('Course updated successfully!', 'success')
            return redirect(url_for('admin.courses'))
        else:
            flash('Failed to update course.', 'error')
    
    lecturers = get_lecturers()
    departments = get_departments()
    return render_template('admin/edit_course.html', 
                          course=course, 
                          lecturers=lecturers, 
                          departments=departments)

@bp.route('/courses/<course_code>/delete', methods=['POST'])
@admin_required
def delete_course(course_code):
    """Delete a course"""
    course_service = CourseService()
    result = course_service.delete_course(course_code)
    
    if result:
        flash('Course deleted successfully!', 'success')
        return redirect(url_for('admin.courses'))
    else:
        flash('Failed to delete course', 'error')
        return redirect(url_for('admin.courses'))

# ==================== DEPARTMENT MANAGEMENT ====================

@bp.route('/departments')
@admin_required
def departments():
    """Manage departments"""
    try:
        department_service = DepartmentService()
        departments = department_service.get_all_departments()
        return render_template('admin/departments.html', departments=departments)
    except Exception as e:
        current_app.logger.error(f"Departments error: {e}")
        flash('Error loading departments', 'error')
        return render_template('admin/departments.html', departments=[])

@bp.route('/departments/create', methods=['GET', 'POST'])
@admin_required
def create_department():
    """Create a new department"""
    if request.method == 'POST':
        department_data = {
            'dept_code': request.form.get('dept_code'),
            'dept_name': request.form.get('dept_name'),
            'faculty': request.form.get('faculty'),
            'head_of_department': request.form.get('head_of_department'),
            'description': request.form.get('description'),
            'is_active': request.form.get('is_active') == 'on'
        }
        
        department_service = DepartmentService()
        result = department_service.create_department(department_data)
        
        if result:
            flash('Department created successfully!', 'success')
            return redirect(url_for('admin.departments'))
        else:
            flash('Failed to create department.', 'error')
    
    return render_template('admin/create_department.html')

@bp.route('/departments/<dept_code>/edit', methods=['GET', 'POST'])
@admin_required
def edit_department(dept_code):
    """Edit a department"""
    department_service = DepartmentService()
    
    if request.method == 'POST':
        department_data = {
            'dept_name': request.form.get('dept_name'),
            'faculty': request.form.get('faculty'),
            'head_of_department': request.form.get('head_of_department'),
            'description': request.form.get('description'),
            'is_active': request.form.get('is_active') == 'on'
        }
        
        result = department_service.update_department(dept_code, department_data)
        if result:
            flash('Department updated successfully!', 'success')
            return redirect(url_for('admin.departments'))
        else:
            flash('Failed to update department.', 'error')
    
    department = department_service.get_department(dept_code)
    return render_template('admin/edit_department.html', department=department)

@bp.route('/departments/<dept_code>/delete', methods=['POST'])
@admin_required
def delete_department(dept_code):
    """Delete a department"""
    department_service = DepartmentService()
    result = department_service.delete_department(dept_code)
    
    if result:
        flash('Department deleted successfully!', 'success')
        return redirect(url_for('admin.departments'))
    else:
        flash('Failed to delete department', 'error')
        return redirect(url_for('admin.departments'))

# ==================== MATERIAL MANAGEMENT ====================

@bp.route('/materials')
@admin_required
def materials():
    """Manage materials"""
    try:
        material_service = MaterialService()
        materials = material_service.get_all_materials()
        return render_template('admin/materials.html', materials=materials)
    except Exception as e:
        current_app.logger.error(f"Materials error: {e}")
        flash('Error loading materials', 'error')
        return render_template('admin/materials.html', materials=[])

@bp.route('/materials/create', methods=['GET', 'POST'])
@admin_required
def create_material():
    """Create a new material"""
    if request.method == 'POST':
        material_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'course_code': request.form.get('course_code'),
            'material_type': request.form.get('material_type'),
            'file_url': request.form.get('file_url'),
            'uploaded_by': session.get('user_id'),
            'is_published': request.form.get('is_published') == 'on'
        }
        
        material_service = MaterialService()
        result = material_service.create_material(material_data)
        
        if result:
            flash('Material created successfully!', 'success')
            return redirect(url_for('admin.materials'))
        else:
            flash('Failed to create material.', 'error')
    
    courses = get_courses()
    return render_template('admin/create_material.html', courses=courses)

@bp.route('/materials/<material_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_material(material_id):
    """Edit a material"""
    material_service = MaterialService()
    
    if request.method == 'POST':
        material_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'course_code': request.form.get('course_code'),
            'material_type': request.form.get('material_type'),
            'file_url': request.form.get('file_url'),
            'is_published': request.form.get('is_published') == 'on'
        }
        
        result = material_service.update_material(material_id, material_data)
        if result:
            flash('Material updated successfully!', 'success')
            return redirect(url_for('admin.materials'))
        else:
            flash('Failed to update material.', 'error')
    
    material = material_service.get_material(material_id)
    courses = get_courses()
    return render_template('admin/edit_material.html', 
                          material=material, 
                          courses=courses)

@bp.route('/materials/<material_id>/delete', methods=['POST'])
@admin_required
def delete_material(material_id):
    """Delete a material"""
    material_service = MaterialService()
    result = material_service.delete_material(material_id)
    
    if result:
        flash('Material deleted successfully!', 'success')
        return redirect(url_for('admin.materials'))
    else:
        flash('Failed to delete material', 'error')
        return redirect(url_for('admin.materials'))

# ==================== ASSIGNMENT MANAGEMENT ====================

@bp.route('/assignments')
@admin_required
def assignments():
    """Manage assignments"""
    try:
        assignment_service = AssignmentService()
        assignments = assignment_service.get_all_assignments()
        return render_template('admin/assignments.html', assignments=assignments)
    except Exception as e:
        current_app.logger.error(f"Assignments error: {e}")
        flash('Error loading assignments', 'error')
        return render_template('admin/assignments.html', assignments=[])

@bp.route('/assignments/create', methods=['GET', 'POST'])
@admin_required
def create_assignment():
    """Create a new assignment"""
    if request.method == 'POST':
        assignment_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'course_code': request.form.get('course_code'),
            'due_date': request.form.get('due_date'),
            'total_marks': int(request.form.get('total_marks', 100)),
            'instructions': request.form.get('instructions'),
            'attachment_url': request.form.get('attachment_url'),
            'created_by': session.get('user_id'),
            'is_published': request.form.get('is_published') == 'on'
        }
        
        assignment_service = AssignmentService()
        result = assignment_service.create_assignment(assignment_data)
        
        if result:
            flash('Assignment created successfully!', 'success')
            return redirect(url_for('admin.assignments'))
        else:
            flash('Failed to create assignment.', 'error')
    
    courses = get_courses()
    return render_template('admin/create_assignment.html', courses=courses)

@bp.route('/assignments/<assignment_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_assignment(assignment_id):
    """Edit an assignment"""
    assignment_service = AssignmentService()
    
    if request.method == 'POST':
        assignment_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'course_code': request.form.get('course_code'),
            'due_date': request.form.get('due_date'),
            'total_marks': int(request.form.get('total_marks', 100)),
            'instructions': request.form.get('instructions'),
            'attachment_url': request.form.get('attachment_url'),
            'is_published': request.form.get('is_published') == 'on'
        }
        
        result = assignment_service.update_assignment(assignment_id, assignment_data)
        if result:
            flash('Assignment updated successfully!', 'success')
            return redirect(url_for('admin.assignments'))
        else:
            flash('Failed to update assignment.', 'error')
    
    assignment = assignment_service.get_assignment(assignment_id)
    courses = get_courses()
    return render_template('admin/edit_assignment.html', 
                          assignment=assignment, 
                          courses=courses)

@bp.route('/assignments/<assignment_id>/delete', methods=['POST'])
@admin_required
def delete_assignment(assignment_id):
    """Delete an assignment"""
    assignment_service = AssignmentService()
    result = assignment_service.delete_assignment(assignment_id)
    
    if result:
        flash('Assignment deleted successfully!', 'success')
        return redirect(url_for('admin.assignments'))
    else:
        flash('Failed to delete assignment', 'error')
        return redirect(url_for('admin.assignments'))

# ==================== TEST MANAGEMENT ====================

@bp.route('/tests')
@admin_required
def tests():
    """Manage tests"""
    try:
        test_service = TestService()
        tests = test_service.get_all_tests()
        return render_template('admin/tests.html', tests=tests)
    except Exception as e:
        current_app.logger.error(f"Tests error: {e}")
        flash('Error loading tests', 'error')
        return render_template('admin/tests.html', tests=[])

@bp.route('/tests/create', methods=['GET', 'POST'])
@admin_required
def create_test():
    """Create a new test"""
    if request.method == 'POST':
        test_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'course_code': request.form.get('course_code'),
            'test_type': request.form.get('test_type'),
            'duration_minutes': int(request.form.get('duration_minutes', 60)),
            'total_marks': int(request.form.get('total_marks', 100)),
            'instructions': request.form.get('instructions'),
            'questions': json.loads(request.form.get('questions', '[]')),
            'created_by': session.get('user_id'),
            'is_published': request.form.get('is_published') == 'on'
        }
        
        test_service = TestService()
        result = test_service.create_test(test_data)
        
        if result:
            flash('Test created successfully!', 'success')
            return redirect(url_for('admin.tests'))
        else:
            flash('Failed to create test.', 'error')
    
    courses = get_courses()
    return render_template('admin/create_test.html', courses=courses)

@bp.route('/tests/<test_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_test(test_id):
    """Edit a test"""
    test_service = TestService()
    
    if request.method == 'POST':
        test_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'course_code': request.form.get('course_code'),
            'test_type': request.form.get('test_type'),
            'duration_minutes': int(request.form.get('duration_minutes', 60)),
            'total_marks': int(request.form.get('total_marks', 100)),
            'instructions': request.form.get('instructions'),
            'questions': json.loads(request.form.get('questions', '[]')),
            'is_published': request.form.get('is_published') == 'on'
        }
        
        result = test_service.update_test(test_id, test_data)
        if result:
            flash('Test updated successfully!', 'success')
            return redirect(url_for('admin.tests'))
        else:
            flash('Failed to update test.', 'error')
    
    test = test_service.get_test(test_id)
    courses = get_courses()
    return render_template('admin/edit_test.html', 
                          test=test, 
                          courses=courses)

@bp.route('/tests/<test_id>/delete', methods=['POST'])
@admin_required
def delete_test(test_id):
    """Delete a test"""
    test_service = TestService()
    result = test_service.delete_test(test_id)
    
    if result:
        flash('Test deleted successfully!', 'success')
        return redirect(url_for('admin.tests'))
    else:
        flash('Failed to delete test', 'error')
        return redirect(url_for('admin.tests'))

# ==================== BULK UPLOAD ====================

@bp.route('/bulk-upload')
@admin_required
def bulk_upload():
    """Bulk upload page"""
    return render_template('admin/bulk_upload.html', user_name=session.get('user_name', 'Admin'))

@bp.route('/bulk-upload/students', methods=['POST'])
@admin_required
def bulk_upload_students():
    """Bulk upload students from CSV with level and semester support"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'File must be CSV format'}), 400
        
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        user_service = UserService()
        
        results = {
            'success': 0,
            'failed': 0,
            'errors': [],
            'total': 0
        }
        
        for row in csv_input:
            results['total'] += 1
            try:
                # Validate required fields
                required_fields = ['user_id', 'email', 'first_name', 'last_name', 'matric_no']
                for field in required_fields:
                    if not row.get(field):
                        raise ValueError(f"Missing required field: {field}")
                
                # Check if user already exists
                existing = user_service.get_user(row['user_id'])
                if existing:
                    results['failed'] += 1
                    results['errors'].append(f"User {row['user_id']} already exists")
                    continue
                
                # Get level from CSV or derive from year_of_study
                level = row.get('level', '').lower()
                year_of_study = int(row.get('year_of_study', 1))
                
                if not level:
                    if year_of_study == 1:
                        level = 'nd1'
                    elif year_of_study == 2:
                        level = 'nd2'
                    elif year_of_study == 3:
                        level = 'hnd1'
                    elif year_of_study >= 4:
                        level = 'hnd2'
                    else:
                        level = 'nd1'
                
                # Validate level
                valid_levels = ['nd1', 'nd2', 'hnd1', 'hnd2']
                if level not in valid_levels:
                    raise ValueError(f"Invalid level: {level}. Must be nd1, nd2, hnd1, hnd2")
                
                # Get semester
                semester = row.get('semester', 'first').lower()
                if semester not in ['first', 'second']:
                    semester = 'first'
                
                # Create user data
                user_data = {
                    'user_id': row['user_id'],
                    'email': row['email'],
                    'password': row.get('password', 'Student@123'),
                    'role': 'student',
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'department': row.get('department'),
                    'phone': row.get('phone'),
                    'is_active': row.get('is_active', 'true').lower() == 'true',
                    'matric_no': row['matric_no'],
                    'programme': row.get('programme', 'ND'),
                    'year_of_study': year_of_study,
                    'current_level': level,
                    'current_semester': semester
                }
                
                result = user_service.create_user(user_data)
                if result:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to create user: {row['user_id']}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error in row {results['total']}: {str(e)}")
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        current_app.logger.error(f"Bulk upload students error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/bulk-upload/departments', methods=['POST'])
@admin_required
def bulk_upload_departments():
    """Bulk upload departments from CSV"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'File must be CSV format'}), 400
        
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        department_service = DepartmentService()
        
        results = {
            'success': 0,
            'failed': 0,
            'errors': [],
            'total': 0
        }
        
        for row in csv_input:
            results['total'] += 1
            try:
                # Validate required fields
                if not row.get('dept_code') or not row.get('dept_name'):
                    raise ValueError("dept_code and dept_name are required")
                
                # Check if department already exists
                existing = department_service.get_department(row['dept_code'])
                if existing:
                    results['failed'] += 1
                    results['errors'].append(f"Department {row['dept_code']} already exists")
                    continue
                
                # Create department data
                dept_data = {
                    'dept_code': row['dept_code'],
                    'dept_name': row['dept_name'],
                    'faculty': row.get('faculty'),
                    'head_of_department': row.get('head_of_department'),
                    'description': row.get('description'),
                    'is_active': row.get('is_active', 'true').lower() == 'true'
                }
                
                result = department_service.create_department(dept_data)
                if result:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to create department: {row['dept_code']}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error in row {results['total']}: {str(e)}")
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        current_app.logger.error(f"Bulk upload departments error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/bulk-upload/courses', methods=['POST'])
@admin_required
def bulk_upload_courses():
    """Bulk upload courses from CSV with level and semester support"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'File must be CSV format'}), 400
        
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        course_service = CourseService()
        
        results = {
            'success': 0,
            'failed': 0,
            'errors': [],
            'total': 0
        }
        
        for row in csv_input:
            results['total'] += 1
            try:
                # Validate required fields
                if not row.get('course_code') or not row.get('course_name'):
                    raise ValueError("course_code and course_name are required")
                
                # Validate level
                level = row.get('level', '').lower()
                valid_levels = ['nd1', 'nd2', 'hnd1', 'hnd2']
                if not level:
                    raise ValueError("level is required (nd1, nd2, hnd1, hnd2)")
                if level not in valid_levels:
                    raise ValueError(f"Invalid level: {level}. Must be nd1, nd2, hnd1, hnd2")
                
                # Validate semester
                semester = row.get('semester', '').lower()
                if not semester:
                    raise ValueError("semester is required (first, second)")
                if semester not in ['first', 'second']:
                    raise ValueError(f"Invalid semester: {semester}. Must be first or second")
                
                # Check if course already exists
                existing = course_service.get_course(row['course_code'])
                if existing:
                    results['failed'] += 1
                    results['errors'].append(f"Course {row['course_code']} already exists")
                    continue
                
                # Create course data with level and semester
                course_data = {
                    'course_code': row['course_code'],
                    'course_name': row['course_name'],
                    'description': row.get('description'),
                    'department': row.get('department'),
                    'credits': int(row.get('credits', 3)),
                    'lecturer_id': row.get('lecturer_id'),
                    'level': level,
                    'semester': semester,
                    'academic_year': row.get('academic_year'),
                    'is_active': row.get('is_active', 'true').lower() == 'true'
                }
                
                result = course_service.create_course(course_data)
                if result:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to create course: {row['course_code']}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error in row {results['total']}: {str(e)}")
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        current_app.logger.error(f"Bulk upload courses error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/bulk-upload/templates/<template_type>')
@admin_required
def download_template(template_type):
    """Download CSV template for bulk upload with level support"""
    templates = {
        'students': [
            'user_id', 'email', 'first_name', 'last_name', 'password', 
            'matric_no', 'department', 'phone', 'programme', 'year_of_study', 
            'level', 'semester', 'is_active'
        ],
        'departments': [
            'dept_code', 'dept_name', 'faculty', 'head_of_department', 
            'description', 'is_active'
        ],
        'courses': [
            'course_code', 'course_name', 'description', 'department', 
            'credits', 'lecturer_id', 'level', 'semester', 'academic_year', 'is_active'
        ]
    }
    
    if template_type not in templates:
        return jsonify({'error': 'Invalid template type'}), 400
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(templates[template_type])
    
    # Add sample rows with level support
    if template_type == 'students':
        writer.writerow([
            'STU001', 'student1@polyibadan.edu.ng', 'John', 'Doe', 'Student@123',
            '2024/1001', 'CSC', '08012345678', 'ND', '1',
            'nd1', 'first', 'true'
        ])
        writer.writerow([
            'STU002', 'student2@polyibadan.edu.ng', 'Jane', 'Smith', 'Student@123',
            '2024/1002', 'ENG', '08087654321', 'HND', '2',
            'nd2', 'second', 'true'
        ])
        writer.writerow([
            'STU003', 'student3@polyibadan.edu.ng', 'Michael', 'Johnson', 'Student@123',
            '2024/1003', 'MED', '08011223344', 'ND', '3',
            'hnd1', 'first', 'true'
        ])
    elif template_type == 'departments':
        writer.writerow(['CSC', 'Computer Science', 'Science', 'Dr. Ade Adeyemi', 'Department of Computer Science', 'true'])
        writer.writerow(['ENG', 'Engineering', 'Engineering', 'Prof. Bello Bello', 'Department of Engineering', 'true'])
        writer.writerow(['MED', 'Medicine', 'Science', 'Dr. Chinwe Okafor', 'Department of Medicine', 'true'])
    elif template_type == 'courses':
        writer.writerow(['CSC101', 'Introduction to Programming', 'Basic programming concepts', 'CSC', '3', 'LEC001', 'nd1', 'first', '2024/2025', 'true'])
        writer.writerow(['CSC102', 'Data Structures', 'Advanced programming', 'CSC', '3', 'LEC001', 'nd1', 'second', '2024/2025', 'true'])
        writer.writerow(['ENG101', 'Engineering Mathematics', 'Basic engineering math', 'ENG', '3', 'LEC002', 'nd2', 'first', '2024/2025', 'true'])
        writer.writerow(['CSC201', 'Database Systems', 'Database design and management', 'CSC', '3', 'LEC001', 'hnd1', 'first', '2024/2025', 'true'])
        writer.writerow(['CSC202', 'Software Engineering', 'Software development methodologies', 'CSC', '3', 'LEC001', 'hnd1', 'second', '2024/2025', 'true'])
        writer.writerow(['ENG201', 'Engineering Design', 'Advanced engineering design', 'ENG', '3', 'LEC002', 'hnd2', 'first', '2024/2025', 'true'])
    
    output.seek(0)
    bytes_data = BytesIO(output.getvalue().encode('utf-8'))
    
    return send_file(
        bytes_data,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{template_type}_template_with_level.csv'
    )

# ==================== HELPER FUNCTIONS ====================

def get_departments():
    """Get all departments"""
    try:
        department_service = DepartmentService()
        return department_service.get_all_departments()
    except:
        return []

def get_lecturers():
    """Get all lecturers"""
    try:
        user_service = UserService()
        return user_service.get_users_by_role('lecturer')
    except:
        return []

def get_courses():
    """Get all courses"""
    try:
        course_service = CourseService()
        return course_service.get_all_courses()
    except:
        return []