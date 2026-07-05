# app/services/__init__.py
from app.services.user_service import UserService
from app.services.course_service import CourseService
from app.services.department_service import DepartmentService
from app.services.material_service import MaterialService
from app.services.assignment_service import AssignmentService
from app.services.test_service import TestService
from app.services.lecturer_service import LecturerService
from app.services.student_service import StudentService

__all__ = [
    'UserService',
    'CourseService',
    'DepartmentService',
    'MaterialService',
    'AssignmentService',
    'TestService',
    'LecturerService',
    'StudentService'
]