# app/services/course_service.py
from app.repositories.course_repository import CourseRepository
from app.services.material_service import MaterialService
from app.services.assignment_service import AssignmentService
from app.services.test_service import TestService
from datetime import datetime
import uuid

class CourseService:
    """Service layer for course management"""
    
    def __init__(self):
        self.course_repo = CourseRepository()
        self.material_service = MaterialService()
        self.assignment_service = AssignmentService()
        self.test_service = TestService()
    
    # ==================== LEVEL AND SEMESTER CONSTANTS ====================
    
    LEVELS = {
        'nd1': 'ND I',
        'nd2': 'ND II',
        'hnd1': 'HND I',
        'hnd2': 'HND II'
    }
    
    SEMESTERS = {
        'first': 'First Semester',
        'second': 'Second Semester'
    }
    
    def get_levels(self):
        """Get all available levels"""
        return self.LEVELS
    
    def get_semesters(self):
        """Get all available semesters"""
        return self.SEMESTERS
    
    def get_level_semester_display(self, level, semester):
        """Get display text for level and semester combination"""
        level_text = self.LEVELS.get(level, level)
        semester_text = self.SEMESTERS.get(semester, semester)
        return f"{level_text} - {semester_text}"
    
    # ==================== COURSE CRUD OPERATIONS ====================
    
    def create_course(self, course_data: dict):
        """Create a new course"""
        try:
            course_data['course_code'] = course_data.get('course_code', f"COURSE_{uuid.uuid4().hex[:8]}")
            course_data['created_at'] = datetime.now().isoformat()
            course_data['updated_at'] = datetime.now().isoformat()
            course_data['is_active'] = course_data.get('is_active', True)
            course_data['enrolled_students'] = []
            
            # Ensure level and semester are set
            course_data['level'] = course_data.get('level', 'nd1')
            course_data['semester'] = course_data.get('semester', 'first')
            
            return self.course_repo.save(course_data['course_code'], course_data)
        except Exception as e:
            print(f"Create course error: {e}")
            return None
    
    def get_course(self, course_code: str):
        """Get a course by code"""
        try:
            course = self.course_repo.find_by_id(course_code)
            if course and 'enrolled_students' not in course:
                course['enrolled_students'] = []
            return course
        except Exception as e:
            print(f"Get course error: {e}")
            return None
    
    def get_all_courses(self):
        """Get all courses"""
        try:
            return self.course_repo.find_all()
        except Exception as e:
            print(f"Get all courses error: {e}")
            return []
    
    def get_courses_by_level(self, level: str):
        """Get courses by level"""
        try:
            courses = self.course_repo.find_all()
            return [c for c in courses if c.get('level') == level]
        except Exception as e:
            print(f"Get courses by level error: {e}")
            return []
    
    def get_courses_by_semester(self, semester: str):
        """Get courses by semester"""
        try:
            courses = self.course_repo.find_all()
            return [c for c in courses if c.get('semester') == semester]
        except Exception as e:
            print(f"Get courses by semester error: {e}")
            return []
    
    def get_courses_by_level_semester(self, level: str, semester: str):
        """Get courses by level and semester"""
        try:
            courses = self.course_repo.find_all()
            return [c for c in courses if c.get('level') == level and c.get('semester') == semester]
        except Exception as e:
            print(f"Get courses by level and semester error: {e}")
            return []
    
    def get_courses_by_lecturer(self, lecturer_id: str):
        """Get courses by lecturer"""
        try:
            courses = self.course_repo.find_all()
            return [c for c in courses if c.get('lecturer_id') == lecturer_id]
        except Exception as e:
            print(f"Get courses by lecturer error: {e}")
            return []
    
    def update_course(self, course_code: str, course_data: dict):
        """Update a course"""
        try:
            existing = self.course_repo.find_by_id(course_code)
            if not existing:
                return None
            
            course_data['updated_at'] = datetime.now().isoformat()
            existing.update(course_data)
            return self.course_repo.update(course_code, existing)
        except Exception as e:
            print(f"Update course error: {e}")
            return None
    
    def delete_course(self, course_code: str):
        """Delete a course"""
        try:
            return self.course_repo.delete(course_code)
        except Exception as e:
            print(f"Delete course error: {e}")
            return False
    
    def get_recent_courses(self, limit=5):
        """Get recent courses"""
        try:
            courses = self.course_repo.find_all()
            courses.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return courses[:limit]
        except Exception as e:
            print(f"Get recent courses error: {e}")
            return []
    
    def enroll_student(self, course_code: str, student_id: str):
        """Enroll a student in a course"""
        try:
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
        except Exception as e:
            print(f"Enroll student error: {e}")
            return False
    
    def unenroll_student(self, course_code: str, student_id: str):
        """Unenroll a student from a course"""
        try:
            course = self.course_repo.find_by_id(course_code)
            if not course:
                return False
            
            if 'enrolled_students' in course and student_id in course['enrolled_students']:
                course['enrolled_students'].remove(student_id)
                course['updated_at'] = datetime.now().isoformat()
                return self.course_repo.update(course_code, course)
            
            return True
        except Exception as e:
            print(f"Unenroll student error: {e}")
            return False
    
    def get_course_materials(self, course_code: str):
        """Get all materials for a course"""
        try:
            return self.material_service.get_materials_by_course(course_code)
        except Exception as e:
            print(f"Get course materials error: {e}")
            return []
    
    def get_course_assignments(self, course_code: str):
        """Get all assignments for a course"""
        try:
            return self.assignment_service.get_assignments_by_course(course_code)
        except Exception as e:
            print(f"Get course assignments error: {e}")
            return []
    
    def get_course_tests(self, course_code: str):
        """Get all tests for a course"""
        try:
            return self.test_service.get_tests_by_course(course_code)
        except Exception as e:
            print(f"Get course tests error: {e}")
            return []
    
    def get_course_announcements(self, course_code: str):
        """Get all announcements for a course"""
        try:
            course = self.course_repo.find_by_id(course_code)
            if not course:
                return []
            return course.get('announcements', [])
        except Exception as e:
            print(f"Get course announcements error: {e}")
            return []