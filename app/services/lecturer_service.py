# app/services/lecturer_service.py
from app.services.course_service import CourseService
from app.services.user_service import UserService
from app.services.material_service import MaterialService
from app.services.assignment_service import AssignmentService
from app.services.test_service import TestService
from datetime import datetime
import uuid

class LecturerService:
    """Service layer for lecturer-specific operations"""
    
    def __init__(self):
        self.course_service = CourseService()
        self.user_service = UserService()
        self.material_service = MaterialService()
        self.assignment_service = AssignmentService()
        self.test_service = TestService()
    
    # ==================== COURSE MANAGEMENT ====================
    
    def get_lecturer_courses(self, lecturer_id):
        """Get all courses taught by a lecturer"""
        try:
            courses = self.course_service.get_all_courses()
            return [c for c in courses if c.get('lecturer_id') == lecturer_id]
        except Exception as e:
            print(f"Get lecturer courses error: {e}")
            return []
    
    def get_course_students(self, course_code):
        """Get all students enrolled in a course"""
        try:
            course = self.course_service.get_course(course_code)
            if not course:
                return []
            
            enrolled_students = course.get('enrolled_students', [])
            students = []
            for student_id in enrolled_students:
                student = self.user_service.get_user(student_id)
                if student:
                    students.append(student)
            return students
        except Exception as e:
            print(f"Get course students error: {e}")
            return []
    
    def get_course_materials(self, course_code):
        """Get all materials for a course"""
        try:
            return self.material_service.get_materials_by_course(course_code)
        except Exception as e:
            print(f"Get course materials error: {e}")
            return []
    
    def get_course_assignments(self, course_code):
        """Get all assignments for a course"""
        try:
            return self.assignment_service.get_assignments_by_course(course_code)
        except Exception as e:
            print(f"Get course assignments error: {e}")
            return []
    
    def get_course_tests(self, course_code):
        """Get all tests for a course"""
        try:
            return self.test_service.get_tests_by_course(course_code)
        except Exception as e:
            print(f"Get course tests error: {e}")
            return []
    
    # ==================== MATERIAL MANAGEMENT ====================
    
    def create_material(self, material_data):
        """Create a new material for a course"""
        try:
            return self.material_service.create_material(material_data)
        except Exception as e:
            print(f"Create material error: {e}")
            return None
    
    def delete_material(self, material_id):
        """Delete a material"""
        try:
            return self.material_service.delete_material(material_id)
        except Exception as e:
            print(f"Delete material error: {e}")
            return False
    
    # ==================== ASSIGNMENT MANAGEMENT ====================
    
    def create_assignment(self, assignment_data):
        """Create a new assignment for a course"""
        try:
            return self.assignment_service.create_assignment(assignment_data)
        except Exception as e:
            print(f"Create assignment error: {e}")
            return None
    
    def get_student_submissions(self, assignment_id):
        """Get all submissions for an assignment"""
        try:
            assignment = self.assignment_service.get_assignment(assignment_id)
            if not assignment:
                return []
            return assignment.get('submissions', [])
        except Exception as e:
            print(f"Get student submissions error: {e}")
            return []
    
    def grade_student_submission(self, assignment_id, student_id, grade, feedback=''):
        """Grade a student's submission"""
        try:
            assignment = self.assignment_service.get_assignment(assignment_id)
            if not assignment:
                return False
            
            submissions = assignment.get('submissions', [])
            for submission in submissions:
                if submission.get('student_id') == student_id:
                    submission['grade'] = grade
                    submission['feedback'] = feedback
                    submission['graded_at'] = datetime.now().isoformat()
                    assignment['updated_at'] = datetime.now().isoformat()
                    return self.assignment_service.update_assignment(assignment_id, assignment)
            
            return False
        except Exception as e:
            print(f"Grade submission error: {e}")
            return False
    
    # ==================== TEST MANAGEMENT ====================
    
    def create_test(self, test_data):
        """Create a new test for a course"""
        try:
            # Validate questions format
            questions = test_data.get('questions', [])
            if not questions:
                print("No questions provided")
                return None
            
            # Validate each question
            for i, q in enumerate(questions):
                if not q.get('question'):
                    raise ValueError(f"Question {i+1}: 'question' field is required")
                if not q.get('options') or len(q.get('options', [])) < 2:
                    raise ValueError(f"Question {i+1}: At least 2 options are required")
                if q.get('correct') is None or not isinstance(q.get('correct'), int):
                    raise ValueError(f"Question {i+1}: 'correct' index is required")
                if q.get('correct', 0) >= len(q.get('options', [])):
                    raise ValueError(f"Question {i+1}: Correct answer index is out of range")
                if 'marks' not in q:
                    q['marks'] = 1
            
            # Calculate total marks
            total_marks = sum(q.get('marks', 1) for q in questions)
            test_data['total_marks'] = total_marks
            
            return self.test_service.create_test(test_data)
        except Exception as e:
            print(f"Create test error: {e}")
            return None
    
    def delete_test(self, test_id):
        """Delete a test"""
        try:
            return self.test_service.delete_test(test_id)
        except Exception as e:
            print(f"Delete test error: {e}")
            return False
    
    # ==================== ANNOUNCEMENT MANAGEMENT ====================
    
    def send_announcement(self, course_code, announcement_data):
        """Send an announcement to students in a course"""
        try:
            course = self.course_service.get_course(course_code)
            if not course:
                return None
            
            if 'announcements' not in course:
                course['announcements'] = []
            
            announcement = {
                'id': f"ANN_{uuid.uuid4().hex[:8]}",
                'title': announcement_data.get('title'),
                'content': announcement_data.get('content'),
                'created_at': datetime.now().isoformat(),
                'created_by': announcement_data.get('created_by'),
                'course_code': course_code
            }
            
            course['announcements'].append(announcement)
            course['updated_at'] = datetime.now().isoformat()
            self.course_service.update_course(course_code, course)
            return announcement
        except Exception as e:
            print(f"Send announcement error: {e}")
            return None
    
    def get_course_announcements(self, course_code):
        """Get all announcements for a course"""
        try:
            course = self.course_service.get_course(course_code)
            if not course:
                return []
            return course.get('announcements', [])
        except Exception as e:
            print(f"Get course announcements error: {e}")
            return []