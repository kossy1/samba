# scripts/reset_admin_password.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.services.user_service import UserService
from app.utils.security_simple import hash_password
from app.extensions import kv

def reset_admin_password():
    """Reset admin password"""
    app = create_app()
    with app.app_context():
        try:
            user_service = UserService()
            
            # Check if admin exists
            admin = user_service.get_user('admin')
            if admin:
                print("✅ Admin user found. Resetting password...")
                
                # New password
                new_password = 'Admin@Poly2024!'
                
                # Hash the new password
                new_hash = hash_password(new_password)
                
                # Update the user data
                admin['password_hash'] = new_hash
                admin['updated_at'] = datetime.now().isoformat()
                
                # Save to Redis
                result = user_service.update_user('admin', admin)
                
                if result:
                    print(f"✅ Password reset successfully!")
                    print(f"   User ID: admin")
                    print(f"   New Password: {new_password}")
                    print(f"   New Hash: {new_hash[:50]}...")
                else:
                    print("❌ Failed to reset password")
            else:
                print("❌ Admin user not found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    reset_admin_password()