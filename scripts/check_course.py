# scripts/check_course.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.services.course_service import CourseService
from app.services.user_service import UserService

def check_course(course_code):
    """Check course data"""
    app = create_app()
    with app.app_context():
        try:
            print(f"Checking course: {course_code}")
            
            course_service = CourseService()
            course = course_service.get_course(course_code)
            
            if course:
                print("✅ Course found:")
                print(f"  Code: {course.get('course_code')}")
                print(f"  Name: {course.get('course_name')}")
                print(f"  Lecturer ID: {course.get('lecturer_id')}")
                print(f"  Department: {course.get('department')}")
                print(f"  Enrolled Students: {len(course.get('enrolled_students', []))}")
                
                # Check if lecturer exists
                lecturer_id = course.get('lecturer_id')
                if lecturer_id:
                    user_service = UserService()
                    lecturer = user_service.get_user(lecturer_id)
                    if lecturer:
                        print(f"  Lecturer Name: {lecturer.get('first_name')} {lecturer.get('last_name')}")
                    else:
                        print("  ❌ Lecturer not found")
            else:
                print("❌ Course not found")
                
            # List all courses
            print("\n📚 All courses:")
            all_courses = course_service.get_all_courses()
            for c in all_courses:
                print(f"  {c.get('course_code')} - {c.get('course_name')} (Lecturer: {c.get('lecturer_id')})")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Check a specific course
    course_code = input("Enter course code to check (or press Enter to skip): ")
    if course_code:
        check_course(course_code)
    else:
        print("No course code provided. Checking all courses...")
        check_course(None)