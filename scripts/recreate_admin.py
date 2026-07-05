# scripts/recreate_admin.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.extensions import kv
from app.services.user_service import UserService
from datetime import datetime

def recreate_admin():
    """Delete and recreate admin user"""
    app = create_app()
    with app.app_context():
        try:
            # Delete existing admin
            kv.delete('user:admin')
            kv.srem('user:all', 'admin')
            kv.srem('users:role:admin', 'admin')
            print("✅ Deleted existing admin user")
            
            # Create new admin
            user_service = UserService()
            admin_data = {
                'user_id': 'admin',
                'email': 'admin@polyibadan.edu.ng',
                'password': 'Admin@Poly2024!',
                'role': 'admin',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_active': True
            }
            
            result = user_service.create_user(admin_data)
            if result:
                print("✅ Admin user recreated successfully!")
                print(f"   User ID: admin")
                print(f"   Password: Admin@Poly2024!")
            else:
                print("❌ Failed to recreate admin user")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    recreate_admin()