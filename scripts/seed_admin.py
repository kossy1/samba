# scripts/seed_admin.py
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.services.user_service import UserService
from app.utils.security import hash_password

def seed_admin():
    """Create initial admin user"""
    app = create_app()
    with app.app_context():
        user_service = UserService()
        
        # Check if admin already exists
        admin = user_service.get_user('admin')
        if admin:
            print("⚠️ Admin user already exists")
            return
        
        # Create admin user
        admin_data = {
            'user_id': 'admin',
            'email': os.getenv('SEED_ADMIN_EMAIL', 'admin@polyibadan.edu.ng'),
            'password': os.getenv('SEED_ADMIN_PASSWORD', 'Admin@Poly2024!'),
            'role': 'admin',
            'first_name': os.getenv('SEED_ADMIN_FIRST_NAME', 'System'),
            'last_name': os.getenv('SEED_ADMIN_LAST_NAME', 'Administrator'),
            'is_active': True
        }
        
        user_service.create_user(admin_data)
        print("✅ Admin user created successfully!")
        print(f"   User ID: admin")
        print(f"   Password: {admin_data['password']}")

if __name__ == "__main__":
    seed_admin()