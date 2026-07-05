# app/services/test_service.py
from app.repositories.test_repository import TestRepository
from datetime import datetime
import uuid

class TestService:
    """Service layer for test management"""
    
    def __init__(self):
        self.test_repo = TestRepository()
    
    def create_test(self, test_data: dict):
        """Create a new test"""
        test_data['test_id'] = f"TEST_{uuid.uuid4().hex[:8]}"
        test_data['created_at'] = datetime.now().isoformat()
        test_data['updated_at'] = datetime.now().isoformat()
        test_data['is_published'] = test_data.get('is_published', False)
        test_data['attempts'] = []
        
        return self.test_repo.save(test_data['test_id'], test_data)
    
    def get_test(self, test_id: str):
        """Get a test by ID"""
        return self.test_repo.find_by_id(test_id)
    
    def get_all_tests(self):
        """Get all tests"""
        return self.test_repo.find_all()
    
    def get_tests_by_course(self, course_code: str):
        """Get tests by course"""
        tests = self.test_repo.find_all()
        return [t for t in tests if t.get('course_code') == course_code]
    
    def update_test(self, test_id: str, test_data: dict):
        """Update a test"""
        existing = self.test_repo.find_by_id(test_id)
        if not existing:
            return None
        
        test_data['updated_at'] = datetime.now().isoformat()
        existing.update(test_data)
        return self.test_repo.update(test_id, existing)
    
    def delete_test(self, test_id: str):
        """Delete a test"""
        return self.test_repo.delete(test_id)
    
    def submit_test_attempt(self, test_id: str, student_id: str, answers: list):
        """Submit a test attempt"""
        test = self.test_repo.find_by_id(test_id)
        if not test:
            return False
        
        attempt_data = {
            'student_id': student_id,
            'answers': answers,
            'submitted_at': datetime.now().isoformat(),
            'score': None  # To be graded
        }
        
        if 'attempts' not in test:
            test['attempts'] = []
        
        test['attempts'].append(attempt_data)
        test['updated_at'] = datetime.now().isoformat()
        return self.test_repo.update(test_id, test)