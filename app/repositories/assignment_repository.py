# app/repositories/assignment_repository.py
from app.repositories.base_repository import BaseRepository

class AssignmentRepository(BaseRepository):
    """Assignment data access layer"""
    
    def __init__(self):
        super().__init__('assignment')