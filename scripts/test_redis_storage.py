# scripts/test_redis_storage.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.services.user_service import UserService

def test_storage():
    """Test Redis storage with proper data types"""
    app = create_app()
    with app.app_context():
        user_service = UserService()
        
        # Test data
        test_user = {
            'user_id': 'test_user',
            'email': 'test@polyibadan.edu.ng',
            'password': 'Test@123456',
            'role': 'student',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True,
            'year_of_study': 2,
            'gpa': 3.5
        }
        
        print("Creating test user...")
        result = user_service.create_user(test_user)
        if result:
            print("✅ Test user created successfully")
        else:
            print("❌ Failed to create test user")
            return
        
        # Retrieve user
        print("Retrieving test user...")
        user = user_service.get_user('test_user')
        if user:
            print("✅ Test user retrieved successfully")
            print(f"   Name: {user.get('first_name')} {user.get('last_name')}")
            print(f"   Active: {user.get('is_active')}")
            print(f"   Year: {user.get('year_of_study')}")
            print(f"   GPA: {user.get('gpa')}")
        else:
            print("❌ Failed to retrieve test user")

if __name__ == "__main__":
    test_storage()