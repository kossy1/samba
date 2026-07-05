# app/services/user_service.py
import json
from datetime import datetime
from app.repositories.user_repository import UserRepository
from app.utils.security import hash_password, verify_password

class UserService:
    """Service layer for user management"""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def authenticate(self, user_id: str, password: str):
        """Authenticate a user"""
        user_data = self.user_repo.find_by_id(user_id)
        
        if not user_data:
            return None
        
        # Check if user is active
        if not user_data.get('is_active', True):
            return None
        
        # Verify password
        stored_hash = user_data.get('password_hash')
        if not stored_hash or not verify_password(password, stored_hash):
            return None
        
        # Update last login
        self.update_last_login(user_id)
        
        # Return user object based on role
        return self._create_user_object(user_data)
    
    def create_user(self, user_data: dict):
        """Create a new user"""
        # Hash password
        if 'password' in user_data:
            user_data['password_hash'] = hash_password(user_data['password'])
            del user_data['password']
        
        # Set timestamps
        user_data['created_at'] = datetime.now().isoformat()
        user_data['updated_at'] = datetime.now().isoformat()
        user_data['is_active'] = user_data.get('is_active', True)
        
        return self.user_repo.save(user_data['user_id'], user_data)
    
    def get_user(self, user_id: str):
        """Get user by ID"""
        return self.user_repo.find_by_id(user_id)
    
    def get_all_users(self):
        """Get all users"""
        return self.user_repo.find_all()
    
    def get_users_by_role(self, role: str):
        """Get users by role"""
        return self.user_repo.find_by_role(role)
    
    def update_user(self, user_id: str, user_data: dict):
        """Update user"""
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
    
    def delete_user(self, user_id: str):
        """Delete user (soft delete)"""
        return self.user_repo.delete(user_id)
    
    def update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        user_data = self.user_repo.find_by_id(user_id)
        if user_data:
            user_data['last_login'] = datetime.now().isoformat()
            self.user_repo.update(user_id, user_data)
    
    def _create_user_object(self, user_data: dict):
        """Create appropriate user object based on role"""
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
                department=user_data.get('department'),
                phone=user_data.get('phone'),
                profile_image=user_data.get('profile_image'),
                is_active=user_data.get('is_active', True),
                matric_no=user_data.get('matric_no', 'STU0001'),
                programme=user_data.get('programme', 'ND'),
                year_of_study=user_data.get('year_of_study', 1),
                faculty=user_data.get('faculty'),
                enrolled_courses=json.loads(user_data.get('enrolled_courses', '[]')),
                gpa=user_data.get('gpa')
            )
        elif role == 'lecturer':
            return Lecturer(
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
                staff_id=user_data.get('staff_id', 'LEC0001'),
                specialization=user_data.get('specialization'),
                office_location=user_data.get('office_location'),
                consultation_hours=user_data.get('consultation_hours')
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
                is_active=user_data.get('is_active', True)
            )