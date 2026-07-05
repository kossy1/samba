# scripts/test_password_verification.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.extensions import kv
from app.utils.security_simple import hash_password, verify_password

def test_password_verification():
    """Test password verification directly"""
    app = create_app()
    with app.app_context():
        # Get admin user data
        user_data = kv.hgetall('user:admin')
        
        if not user_data:
            print("❌ Admin user not found")
            return
        
        stored_hash = user_data.get('password_hash')
        print(f"Stored hash: {stored_hash}")
        print(f"Hash length: {len(stored_hash) if stored_hash else 0}")
        
        # Test with correct password
        test_password = 'Admin@Poly2024!'
        print(f"\nTesting with correct password: {test_password}")
        result = verify_password(test_password, stored_hash)
        print(f"Result: {result}")
        
        # Test with wrong password
        wrong_password = 'WrongPassword123!'
        print(f"\nTesting with wrong password: {wrong_password}")
        result = verify_password(wrong_password, stored_hash)
        print(f"Result: {result}")
        
        # Generate new hash and test
        print(f"\nGenerating new hash for: {test_password}")
        new_hash = hash_password(test_password)
        print(f"New hash: {new_hash[:50]}...")
        result = verify_password(test_password, new_hash)
        print(f"Verification with new hash: {result}")

if __name__ == "__main__":
    test_password_verification()