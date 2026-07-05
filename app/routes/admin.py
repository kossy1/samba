# app/routes/admin.py - Working version with all methods
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify, current_app
from app.utils.decorators import admin_required
from app.services.user_service import UserService
from app.services.course_service import CourseService
from app.services.department_service import DepartmentService
from app.services.material_service import MaterialService
from app.services.assignment_service import AssignmentService
from app.services.test_service import TestService

bp = Blueprint('admin', __name__)

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
        import traceback
        traceback.print_exc()
        # Return a simple dashboard with error message
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