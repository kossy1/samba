# scripts/check_admin_password.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.extensions import kv

def check_admin_password():
    """Check the stored password hash for admin"""
    app = create_app()
    with app.app_context():
        # Get admin user data from Redis
        user_data = kv.hgetall('user:admin')
        
        if user_data:
            print("✅ Admin user found in Redis:")
            print(f"   User ID: {user_data.get('user_id')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Password Hash: {user_data.get('password_hash')[:50]}...")
            print(f"   Password Hash Length: {len(user_data.get('password_hash', ''))}")
            print(f"   Is Active: {user_data.get('is_active')}")
            print(f"   Role: {user_data.get('role')}")
        else:
            print("❌ Admin user not found in Redis")

if __name__ == "__main__":
    check_admin_password()