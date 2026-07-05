# scripts/check_courses.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.services.course_service import CourseService

def check_courses():
    """Check all courses in the system"""
    app = create_app()
    with app.app_context():
        try:
            course_service = CourseService()
            
            # Get all courses
            courses = course_service.get_all_courses()
            
            print(f"\n📚 Total Courses: {len(courses)}")
            print("-" * 50)
            
            if courses:
                for course in courses:
                    print(f"  Course Code: {course.get('course_code')}")
                    print(f"  Name: {course.get('course_name')}")
                    print(f"  Department: {course.get('department', 'N/A')}")
                    print(f"  Lecturer: {course.get('lecturer_id', 'N/A')}")
                    print(f"  Active: {course.get('is_active', True)}")
                    print(f"  Enrolled Students: {len(course.get('enrolled_students', []))}")
                    print("-" * 30)
            else:
                print("  No courses found. Please add some courses through the admin panel.")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_courses()