# app/repositories/user_repository.py
from app.repositories.base_repository import BaseRepository
from app.extensions import kv

class UserRepository(BaseRepository):
    """User data access layer"""
    
    def __init__(self):
        super().__init__('user')
    
    def _prepare_for_redis(self, data: dict):
        """Convert data to Redis-compatible format"""
        prepared = {}
        for key, value in data.items():
            if value is None:
                prepared[key] = ''
            elif isinstance(value, bool):
                prepared[key] = 1 if value else 0
            elif isinstance(value, (int, float, str)):
                prepared[key] = value
            else:
                prepared[key] = str(value)
        return prepared
    
    def save(self, user_id: str, user_data: dict):
        """Save user data"""
        # Prepare data for Redis
        prepared_data = self._prepare_for_redis(user_data)
        
        # Store in main user hash
        key = self._get_key(user_id)
        kv.hset(key, mapping=prepared_data)
        
        # Add to role-specific set
        role = user_data.get('role')
        if role:
            kv.sadd(f"users:role:{role}", user_id)
        
        # Add to all users set
        kv.sadd(self._get_all_key(), user_id)
        
        return user_data
    
    def find_by_id(self, user_id: str):
        """Find user by ID"""
        key = self._get_key(user_id)
        data = kv.hgetall(key)
        if data:
            # Convert back from Redis format
            return self._prepare_from_redis(data)
        return None
    
    def _prepare_from_redis(self, data: dict):
        """Convert Redis data back to Python format"""
        prepared = {}
        for key, value in data.items():
            if key in ['is_active', 'is_verified', 'is_admin']:
                prepared[key] = value == '1' or value == 1
            elif key in ['year_of_study', 'gpa']:
                try:
                    prepared[key] = float(value) if '.' in str(value) else int(value)
                except (ValueError, TypeError):
                    prepared[key] = value
            else:
                prepared[key] = value
        return prepared
    
    def find_all(self):
        """Find all users"""
        user_ids = kv.smembers(self._get_all_key())
        users = []
        for user_id in user_ids:
            user = self.find_by_id(user_id)
            if user:
                users.append(user)
        return users
    
    def find_by_role(self, role: str):
        """Find users by role"""
        user_ids = kv.smembers(f"users:role:{role}")
        users = []
        for user_id in user_ids:
            user = self.find_by_id(user_id)
            if user:
                users.append(user)
        return users
    
    def delete(self, user_id: str):
        """Delete user (hard delete)"""
        user_data = self.find_by_id(user_id)
        if user_data:
            # Remove from role set
            role = user_data.get('role')
            if role:
                kv.srem(f"users:role:{role}", user_id)
            
            # Remove from all users set
            kv.srem(self._get_all_key(), user_id)
            
            # Delete user data
            key = self._get_key(user_id)
            kv.delete(key)
            return True
        return False
    
    def update(self, user_id: str, user_data: dict):
        """Update user"""
        existing = self.find_by_id(user_id)
        if not existing:
            return None
        
        # Update hash
        prepared_data = self._prepare_for_redis(user_data)
        key = self._get_key(user_id)
        kv.hset(key, mapping=prepared_data)
        
        return user_data