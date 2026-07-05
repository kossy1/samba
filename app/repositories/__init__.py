# app/repositories/__init__.py
from app.repositories.base_repository import BaseRepository
from app.repositories.user_repository import UserRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.material_repository import MaterialRepository
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.test_repository import TestRepository

__all__ = [
    'BaseRepository',
    'UserRepository',
    'CourseRepository',
    'DepartmentRepository',
    'MaterialRepository',
    'AssignmentRepository',
    'TestRepository'
]