# app/services/user_service.py
import json
from datetime import datetime
from app.repositories.user_repository import UserRepository
from app.utils.security_simple import hash_password, verify_password

class UserService:
    """Service layer for user management"""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def authenticate(self, user_id: str, password: str):
        """Authenticate a user by user_id"""
        try:
            user_data = self.user_repo.find_by_id(user_id)
            
            if not user_data:
                print(f"User not found: {user_id}")
                return None
            
            print(f"User found: {user_data.get('user_id')}")
            
            # Check if user is active
            if not user_data.get('is_active', True):
                print(f"User is inactive: {user_id}")
                return None
            
            # Verify password
            stored_hash = user_data.get('password_hash')
            if not stored_hash:
                print(f"No password hash for user: {user_id}")
                return None
                
            if not verify_password(password, stored_hash):
                print(f"Password verification failed for user: {user_id}")
                return None
            
            print(f"Authentication successful for user: {user_id}")
            
            # Update last login
            self.update_last_login(user_id)
            
            # Return user object based on role
            return self._create_user_object(user_data)
        except Exception as e:
            print(f"Authentication error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def find_by_matric(self, matric_no: str):
        """Find a student by matric number"""
        try:
            all_users = self.user_repo.find_all()
            for user in all_users:
                if user.get('role') == 'student' and user.get('matric_no') == matric_no:
                    return user
            return None
        except Exception as e:
            print(f"Find by matric error: {e}")
            return None
    
    def find_by_email(self, email: str):
        """Find a user by email"""
        try:
            all_users = self.user_repo.find_all()
            for user in all_users:
                if user.get('email') == email:
                    return user
            return None
        except Exception as e:
            print(f"Find by email error: {e}")
            return None
    
    def find_by_identifier(self, identifier: str):
        """Find user by username, email, or matric number"""
        try:
            # First try as user_id
            user = self.user_repo.find_by_id(identifier)
            if user:
                return user
            
            # Then try as email
            user = self.find_by_email(identifier)
            if user:
                return user
            
            # Finally try as matric number (students only)
            user = self.find_by_matric(identifier)
            if user:
                return user
            
            return None
        except Exception as e:
            print(f"Find by identifier error: {e}")
            return None
    
    def create_user(self, user_data: dict):
        """Create a new user"""
        try:
            # Hash password
            if 'password' in user_data:
                user_data['password_hash'] = hash_password(user_data['password'])
                # Remove plain password
                del user_data['password']
            
            # Set timestamps
            user_data['created_at'] = datetime.now().isoformat()
            user_data['updated_at'] = datetime.now().isoformat()
            user_data['is_active'] = user_data.get('is_active', True)
            
            # Save to repository
            result = self.user_repo.save(user_data['user_id'], user_data)
            return user_data if result else None
        except Exception as e:
            print(f"Create user error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_user(self, user_id: str):
        """Get user by ID"""
        try:
            return self.user_repo.find_by_id(user_id)
        except Exception as e:
            print(f"Get user error: {e}")
            return None
    
    def get_all_users(self):
        """Get all users"""
        try:
            return self.user_repo.find_all()
        except Exception as e:
            print(f"Get all users error: {e}")
            return []
    
    def get_users_by_role(self, role: str):
        """Get users by role"""
        try:
            return self.user_repo.find_by_role(role)
        except Exception as e:
            print(f"Get users by role error: {e}")
            return []
    
    def get_recent_users(self, limit=5):
        """Get recent users"""
        try:
            users = self.user_repo.find_all()
            # Sort by created_at if available
            users.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return users[:limit]
        except Exception as e:
            print(f"Get recent users error: {e}")
            return []
    
    def update_user(self, user_id: str, user_data: dict):
        """Update user"""
        try:
            existing = self.user_repo.find_by_id(user_id)
            if not existing:
                return None
            
            # Update timestamp
            user_data['updated_at'] = datetime.now().isoformat()
            
            # If password is being updated, hash it
            if 'password' in user_data:
                user_data['password_hash'] = hash_password(user_data['password'])
                del user_data['password']
            
            # Merge with existing data
            existing.update(user_data)
            
            return self.user_repo.update(user_id, existing)
        except Exception as e:
            print(f"Update user error: {e}")
            return None
    
    def delete_user(self, user_id: str):
        """Delete user (hard delete)"""
        try:
            return self.user_repo.delete(user_id)
        except Exception as e:
            print(f"Delete user error: {e}")
            return False
    
    def update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        try:
            user_data = self.user_repo.find_by_id(user_id)
            if user_data:
                user_data['last_login'] = datetime.now().isoformat()
                self.user_repo.update(user_id, user_data)
        except Exception as e:
            print(f"Update last login error: {e}")
    
    def _create_user_object(self, user_data: dict):
        """Create appropriate user object based on role"""
        try:
            from app.models.user import User, Lecturer, Student
            
            role = user_data.get('role')
            
            if role == 'student':
                return Student(
                    user_id=user_data['user_id'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    role=role,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    matric_no=user_data.get('matric_no', 'STU0001'),
                    programme=user_data.get('programme', 'ND'),
                    year_of_study=user_data.get('year_of_study', 1),
                    department=user_data.get('department'),
                    phone=user_data.get('phone'),
                    profile_image=user_data.get('profile_image'),
                    is_active=user_data.get('is_active', True),
                    faculty=user_data.get('faculty'),
                    enrolled_courses=json.loads(user_data.get('enrolled_courses', '[]')),
                    gpa=user_data.get('gpa'),
                    created_at=user_data.get('created_at'),
                    updated_at=user_data.get('updated_at'),
                    last_login=user_data.get('last_login'),
                    current_level=user_data.get('current_level'),
                    current_semester=user_data.get('current_semester')
                )
            elif role == 'lecturer':
                return Lecturer(
                    user_id=user_data['user_id'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    role=role,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    staff_id=user_data.get('staff_id', 'LEC0001'),
                    department=user_data.get('department'),
                    phone=user_data.get('phone'),
                    profile_image=user_data.get('profile_image'),
                    is_active=user_data.get('is_active', True),
                    specialization=user_data.get('specialization'),
                    office_location=user_data.get('office_location'),
                    consultation_hours=user_data.get('consultation_hours'),
                    created_at=user_data.get('created_at'),
                    updated_at=user_data.get('updated_at'),
                    last_login=user_data.get('last_login')
                )
            else:
                return User(
                    user_id=user_data['user_id'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    role=role,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    department=user_data.get('department'),
                    phone=user_data.get('phone'),
                    profile_image=user_data.get('profile_image'),
                    is_active=user_data.get('is_active', True),
                    created_at=user_data.get('created_at'),
                    updated_at=user_data.get('updated_at'),
                    last_login=user_data.get('last_login')
                )
        except Exception as e:
            print(f"Create user object error: {e}")
            import traceback
            traceback.print_exc()
            return None