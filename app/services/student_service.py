# app/services/student_service.py
from app.services.course_service import CourseService
from app.services.user_service import UserService
from app.services.material_service import MaterialService
from app.services.assignment_service import AssignmentService
from app.services.test_service import TestService
from datetime import datetime
import json

class StudentService:
    """Service layer for student operations"""
    
    def __init__(self):
        self.course_service = CourseService()
        self.user_service = UserService()
        self.material_service = MaterialService()
        self.assignment_service = AssignmentService()
        self.test_service = TestService()
    
    # ==================== LEVEL AND SEMESTER ====================
    
    def get_student_level_semester(self, student_id):
        """Get student's current level and semester"""
        try:
            student = self.user_service.get_user(student_id)
            if not student:
                return None, None
            
            level = student.get('current_level')
            semester = student.get('current_semester')
            
            # If not set, try to determine from year_of_study
            if not level:
                year = student.get('year_of_study', 1)
                if year == 1:
                    level = 'nd1'
                elif year == 2:
                    level = 'nd2'
                elif year == 3:
                    level = 'hnd1'
                elif year == 4:
                    level = 'hnd2'
                else:
                    level = 'nd1'
            
            if not semester:
                # Default to first semester if not set
                semester = 'first'
            
            return level, semester
        except Exception as e:
            print(f"Get student level semester error: {e}")
            return None, None
    
    def update_student_level_semester(self, student_id, level, semester):
        """Update student's current level and semester"""
        try:
            student = self.user_service.get_user(student_id)
            if not student:
                return False
            
            student['current_level'] = level
            student['current_semester'] = semester
            student['updated_at'] = datetime.now().isoformat()
            
            return self.user_service.update_user(student_id, student)
        except Exception as e:
            print(f"Update student level semester error: {e}")
            return False
    
    # ==================== COURSE MANAGEMENT ====================
    
    def get_enrolled_courses(self, student_id):
        """Get all courses a student is enrolled in with counts"""
        try:
            student = self.user_service.get_user(student_id)
            if not student:
                return []
            
            enrolled_codes = student.get('enrolled_courses', [])
            courses = []
            
            for code in enrolled_codes:
                course = self.course_service.get_course(code)
                if course:
                    # Add counts
                    materials = self.course_service.get_course_materials(code) or []
                    assignments = self.course_service.get_course_assignments(code) or []
                    tests = self.course_service.get_course_tests(code) or []
                    
                    course['materials_count'] = len(materials)
                    course['assignments_count'] = len(assignments)
                    course['tests_count'] = len(tests)
                    courses.append(course)
            
            return courses
        except Exception as e:
            print(f"Get enrolled courses error: {e}")
            return []
    
    def get_available_courses(self, student_id):
        """Get available courses based on student's level and semester"""
        try:
            student = self.user_service.get_user(student_id)
            if not student:
                return []
            
            enrolled_codes = student.get('enrolled_courses', [])
            level, semester = self.get_student_level_semester(student_id)
            
            if not level or not semester:
                return []
            
            # Get all active courses
            all_courses = self.course_service.get_all_courses()
            available_courses = []
            
            for course in all_courses:
                # Check if course is active and not already enrolled
                if not course.get('is_active', True):
                    continue
                
                if course.get('course_code') in enrolled_codes:
                    continue
                
                # Check if course matches student's level and semester
                course_level = course.get('level')
                course_semester = course.get('semester')
                
                # If course has level and semester, match them
                if course_level and course_semester:
                    if course_level == level and course_semester == semester:
                        available_courses.append(course)
                # If course doesn't have level/semester, show it (backward compatibility)
                elif not course_level and not course_semester:
                    available_courses.append(course)
            
            return available_courses
        except Exception as e:
            print(f"Get available courses error: {e}")
            return []
    
    def is_enrolled(self, student_id, course_code):
        """Check if student is enrolled in a course"""
        try:
            student = self.user_service.get_user(student_id)
            if not student:
                return False
            enrolled_codes = student.get('enrolled_courses', [])
            return course_code in enrolled_codes
        except Exception as e:
            print(f"Is enrolled error: {e}")
            return False
    
    def enroll_courses(self, student_id, course_codes):
        """Enroll student in multiple courses"""
        try:
            student = self.user_service.get_user(student_id)
            if not student:
                return {'success': 0, 'failed': course_codes}
            
            enrolled_codes = student.get('enrolled_courses', [])
            success_count = 0
            failed_courses = []
            
            for course_code in course_codes:
                # Check if already enrolled
                if course_code in enrolled_codes:
                    failed_courses.append(f"{course_code} (already enrolled)")
                    continue
                
                # Check if course exists and is active
                course = self.course_service.get_course(course_code)
                if not course:
                    failed_courses.append(f"{course_code} (course not found)")
                    continue
                
                if not course.get('is_active', True):
                    failed_courses.append(f"{course_code} (course is inactive)")
                    continue
                
                # Enroll student in course
                result = self.course_service.enroll_student(course_code, student_id)
                if result:
                    enrolled_codes.append(course_code)
                    success_count += 1
                else:
                    failed_courses.append(course_code)
            
            # Update student's enrolled courses
            student['enrolled_courses'] = enrolled_codes
            self.user_service.update_user(student_id, student)
            
            return {
                'success': success_count,
                'failed': failed_courses
            }
        except Exception as e:
            print(f"Enroll courses error: {e}")
            return {'success': 0, 'failed': course_codes}
    
    def drop_course(self, student_id, course_code):
        """Drop a course"""
        try:
            student = self.user_service.get_user(student_id)
            if not student:
                return False
            
            enrolled_codes = student.get('enrolled_courses', [])
            
            if course_code not in enrolled_codes:
                return False
            
            # Unenroll from course
            result = self.course_service.unenroll_student(course_code, student_id)
            if result:
                enrolled_codes.remove(course_code)
                student['enrolled_courses'] = enrolled_codes
                self.user_service.update_user(student_id, student)
                return True
            
            return False
        except Exception as e:
            print(f"Drop course error: {e}")
            return False
    
    # ==================== STATISTICS ====================
    
    def get_student_stats(self, student_id):
        """Get student statistics"""
        try:
            courses = self.get_enrolled_courses(student_id)
            
            total_courses = len(courses)
            total_materials = 0
            total_assignments = 0
            total_tests = 0
            pending_assignments = 0
            
            for course in courses:
                course_code = course.get('course_code')
                materials = self.course_service.get_course_materials(course_code) or []
                assignments = self.course_service.get_course_assignments(course_code) or []
                tests = self.course_service.get_course_tests(course_code) or []
                
                total_materials += len(materials)
                total_assignments += len(assignments)
                total_tests += len(tests)
                
                # Check pending assignments (not submitted)
                for assignment in assignments:
                    if assignment.get('is_published'):
                        if not self.has_submitted_assignment(student_id, assignment.get('assignment_id')):
                            pending_assignments += 1
            
            return {
                'total_courses': total_courses,
                'total_materials': total_materials,
                'total_assignments': total_assignments,
                'total_tests': total_tests,
                'pending_assignments': pending_assignments
            }
        except Exception as e:
            print(f"Get student stats error: {e}")
            return {}
    
    # ==================== ASSIGNMENTS ====================
    
    def get_pending_assignments(self, student_id):
        """Get all pending assignments for a student"""
        try:
            courses = self.get_enrolled_courses(student_id)
            pending = []
            
            for course in courses:
                course_code = course.get('course_code')
                assignments = self.course_service.get_course_assignments(course_code) or []
                
                for assignment in assignments:
                    if assignment.get('is_published'):
                        if not self.has_submitted_assignment(student_id, assignment.get('assignment_id')):
                            assignment['course_code'] = course_code
                            pending.append(assignment)
            
            return pending
        except Exception as e:
            print(f"Get pending assignments error: {e}")
            return []
    
    def has_submitted_assignment(self, student_id, assignment_id):
        """Check if student has submitted an assignment"""
        try:
            assignment = self.assignment_service.get_assignment(assignment_id)
            if not assignment:
                return False
            
            submissions = assignment.get('submissions', [])
            return any(s.get('student_id') == student_id for s in submissions)
        except Exception as e:
            print(f"Has submitted assignment error: {e}")
            return False
    
    def get_assignment_submission(self, student_id, assignment_id):
        """Get a student's submission for an assignment"""
        try:
            assignment = self.assignment_service.get_assignment(assignment_id)
            if not assignment:
                return None
            
            submissions = assignment.get('submissions', [])
            for submission in submissions:
                if submission.get('student_id') == student_id:
                    return submission
            
            return None
        except Exception as e:
            print(f"Get assignment submission error: {e}")
            return None
    
    def submit_assignment(self, assignment_id, submission_data):
        """Submit an assignment"""
        try:
            assignment = self.assignment_service.get_assignment(assignment_id)
            if not assignment:
                return False
            
            if 'submissions' not in assignment:
                assignment['submissions'] = []
            
            assignment['submissions'].append(submission_data)
            assignment['updated_at'] = datetime.now().isoformat()
            
            return self.assignment_service.update_assignment(assignment_id, assignment)
        except Exception as e:
            print(f"Submit assignment error: {e}")
            return False
    
    # ==================== TESTS ====================
    
    def has_attempted_test(self, student_id, test_id):
        """Check if student has attempted a test"""
        try:
            test = self.test_service.get_test(test_id)
            if not test:
                return False
            
            attempts = test.get('attempts', [])
            return any(a.get('student_id') == student_id for a in attempts)
        except Exception as e:
            print(f"Has attempted test error: {e}")
            return False
    
    def get_test_attempt(self, student_id, test_id):
        """Get a student's test attempt"""
        try:
            test = self.test_service.get_test(test_id)
            if not test:
                return None
            
            attempts = test.get('attempts', [])
            for attempt in attempts:
                if attempt.get('student_id') == student_id:
                    return attempt
            
            return None
        except Exception as e:
            print(f"Get test attempt error: {e}")
            return None
    
    def calculate_test_score(self, test, answers):
        """Calculate test score from answers"""
        try:
            questions = test.get('questions', [])
            total_marks = 0
            obtained_marks = 0
            correct_count = 0
            
            for i, q in enumerate(questions):
                marks = q.get('marks', 1)
                total_marks += marks
                
                for a in answers:
                    if a.get('question_index') == i:
                        if a.get('answer') == q.get('correct'):
                            correct_count += 1
                            obtained_marks += marks
                        break
            
            return {
                'total_marks': total_marks,
                'obtained_marks': obtained_marks,
                'correct_count': correct_count,
                'total_questions': len(questions)
            }
        except Exception as e:
            print(f"Calculate test score error: {e}")
            return {'total_marks': 0, 'obtained_marks': 0, 'correct_count': 0, 'total_questions': 0}
    
    def submit_test_attempt(self, test_id, attempt_data):
        """Submit a test attempt"""
        try:
            test = self.test_service.get_test(test_id)
            if not test:
                return False
            
            if 'attempts' not in test:
                test['attempts'] = []
            
            test['attempts'].append(attempt_data)
            test['updated_at'] = datetime.now().isoformat()
            
            return self.test_service.update_test(test_id, test)
        except Exception as e:
            print(f"Submit test attempt error: {e}")
            return False
    
    # ==================== ACTIVITIES ====================
    
    def get_recent_activities(self, student_id, limit=5):
        """Get recent activities for a student"""
        try:
            activities = []
            
            # Get recent assignment submissions
            courses = self.get_enrolled_courses(student_id)
            for course in courses:
                course_code = course.get('course_code')
                assignments = self.course_service.get_course_assignments(course_code) or []
                
                for assignment in assignments:
                    submissions = assignment.get('submissions', [])
                    for submission in submissions:
                        if submission.get('student_id') == student_id:
                            activities.append({
                                'icon': '📝',
                                'text': f'Submitted "{assignment.get("title")}"',
                                'time': submission.get('submitted_at', '')[:16]
                            })
            
            # Get recent test attempts
            for course in courses:
                course_code = course.get('course_code')
                tests = self.course_service.get_course_tests(course_code) or []
                
                for test in tests:
                    attempts = test.get('attempts', [])
                    for attempt in attempts:
                        if attempt.get('student_id') == student_id:
                            activities.append({
                                'icon': '✍️',
                                'text': f'Completed "{test.get("title")}" (Score: {attempt.get("score")}/{attempt.get("total_marks")})',
                                'time': attempt.get('submitted_at', '')[:16]
                            })
            
            # Sort by time (newest first) and limit
            activities.sort(key=lambda x: x.get('time', ''), reverse=True)
            return activities[:limit]
        except Exception as e:
            print(f"Get recent activities error: {e}")
            return []