# app/services/course_service.py
from app.repositories.course_repository import CourseRepository
from datetime import datetime
import uuid

class CourseService:
    """Service layer for course management"""
    
    def __init__(self):
        self.course_repo = CourseRepository()
    
    def create_course(self, course_data: dict):
        """Create a new course"""
        course_data['course_code'] = course_data.get('course_code', f"COURSE_{uuid.uuid4().hex[:8]}")
        course_data['created_at'] = datetime.now().isoformat()
        course_data['updated_at'] = datetime.now().isoformat()
        course_data['is_active'] = course_data.get('is_active', True)
        course_data['enrolled_students'] = []
        
        return self.course_repo.save(course_data['course_code'], course_data)
    
    def get_course(self, course_code: str):
        """Get a course by code"""
        return self.course_repo.find_by_id(course_code)
    
    def get_all_courses(self):
        """Get all courses"""
        return self.course_repo.find_all()
    
    def get_courses_by_lecturer(self, lecturer_id: str):
        """Get courses by lecturer"""
        courses = self.course_repo.find_all()
        return [c for c in courses if c.get('lecturer_id') == lecturer_id]
    
    def update_course(self, course_code: str, course_data: dict):
        """Update a course"""
        existing = self.course_repo.find_by_id(course_code)
        if not existing:
            return None
        
        course_data['updated_at'] = datetime.now().isoformat()
        existing.update(course_data)
        return self.course_repo.update(course_code, existing)
    
    def delete_course(self, course_code: str):
        """Delete a course"""
        return self.course_repo.delete(course_code)
    
    def get_recent_courses(self, limit=5):
        """Get recent courses"""
        courses = self.course_repo.find_all()
        # Sort by created_at if available
        courses.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return courses[:limit]
    
    def enroll_student(self, course_code: str, student_id: str):
        """Enroll a student in a course"""
        course = self.course_repo.find_by_id(course_code)
        if not course:
            return False
        
        if 'enrolled_students' not in course:
            course['enrolled_students'] = []
        
        if student_id not in course['enrolled_students']:
            course['enrolled_students'].append(student_id)
            course['updated_at'] = datetime.now().isoformat()
            return self.course_repo.update(course_code, course)
        
        return True
    
    def unenroll_student(self, course_code: str, student_id: str):
        """Unenroll a student from a course"""
        course = self.course_repo.find_by_id(course_code)
        if not course:
            return False
        
        if 'enrolled_students' in course and student_id in course['enrolled_students']:
            course['enrolled_students'].remove(student_id)
            course['updated_at'] = datetime.now().isoformat()
            return self.course_repo.update(course_code, course)
        
        return True