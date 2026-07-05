# scripts/seed_admin.py
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.services.user_service import UserService

def seed_admin():
    """Create initial admin user"""
    print("🚀 Creating admin user...")
    
    app = create_app()
    with app.app_context():
        try:
            user_service = UserService()
            
            # Check if admin already exists
            admin = user_service.get_user('admin')
            if admin:
                print("⚠️ Admin user already exists")
                print(f"   User ID: admin")
                print(f"   Name: {admin.get('first_name')} {admin.get('last_name')}")
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
            
            result = user_service.create_user(admin_data)
            if result:
                print("✅ Admin user created successfully!")
                print(f"   User ID: admin")
                print(f"   Password: {admin_data['password']}")
                print(f"   Email: {admin_data['email']}")
            else:
                print("❌ Failed to create admin user")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    seed_admin()