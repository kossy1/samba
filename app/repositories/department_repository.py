# app/repositories/department_repository.py
from app.repositories.base_repository import BaseRepository

class DepartmentRepository(BaseRepository):
    """Department data access layer"""
    
    def __init__(self):
        super().__init__('department')