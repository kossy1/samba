# app/services/assignment_service.py
from app.repositories.assignment_repository import AssignmentRepository
from datetime import datetime
import uuid

class AssignmentService:
    """Service layer for assignment management"""
    
    def __init__(self):
        self.assignment_repo = AssignmentRepository()
    
    def create_assignment(self, assignment_data: dict):
        """Create a new assignment"""
        assignment_data['assignment_id'] = f"ASS_{uuid.uuid4().hex[:8]}"
        assignment_data['created_at'] = datetime.now().isoformat()
        assignment_data['updated_at'] = datetime.now().isoformat()
        assignment_data['is_published'] = assignment_data.get('is_published', False)
        assignment_data['submissions'] = []
        
        return self.assignment_repo.save(assignment_data['assignment_id'], assignment_data)
    
    def get_assignment(self, assignment_id: str):
        """Get an assignment by ID"""
        return self.assignment_repo.find_by_id(assignment_id)
    
    def get_all_assignments(self):
        """Get all assignments"""
        return self.assignment_repo.find_all()
    
    def get_assignments_by_course(self, course_code: str):
        """Get assignments by course"""
        assignments = self.assignment_repo.find_all()
        return [a for a in assignments if a.get('course_code') == course_code]
    
    def update_assignment(self, assignment_id: str, assignment_data: dict):
        """Update an assignment"""
        existing = self.assignment_repo.find_by_id(assignment_id)
        if not existing:
            return None
        
        assignment_data['updated_at'] = datetime.now().isoformat()
        existing.update(assignment_data)
        return self.assignment_repo.update(assignment_id, existing)
    
    def delete_assignment(self, assignment_id: str):
        """Delete an assignment"""
        return self.assignment_repo.delete(assignment_id)
    
    def submit_assignment(self, assignment_id: str, student_id: str, submission_data: dict):
        """Submit an assignment"""
        assignment = self.assignment_repo.find_by_id(assignment_id)
        if not assignment:
            return False
        
        submission_data['student_id'] = student_id
        submission_data['submitted_at'] = datetime.now().isoformat()
        
        if 'submissions' not in assignment:
            assignment['submissions'] = []
        
        assignment['submissions'].append(submission_data)
        assignment['updated_at'] = datetime.now().isoformat()
        return self.assignment_repo.update(assignment_id, assignment)