# app/repositories/course_repository.py
from app.repositories.base_repository import BaseRepository

class CourseRepository(BaseRepository):
    """Course data access layer"""
    
    def __init__(self):
        super().__init__('course')