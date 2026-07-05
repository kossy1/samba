# app/repositories/test_repository.py
from app.repositories.base_repository import BaseRepository

class TestRepository(BaseRepository):
    """Test data access layer"""
    
    def __init__(self):
        super().__init__('test')