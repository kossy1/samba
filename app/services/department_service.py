# app/services/department_service.py
from app.repositories.department_repository import DepartmentRepository
from datetime import datetime

class DepartmentService:
    """Service layer for department management"""
    
    def __init__(self):
        self.dept_repo = DepartmentRepository()
    
    def create_department(self, dept_data: dict):
        """Create a new department"""
        dept_data['created_at'] = datetime.now().isoformat()
        dept_data['updated_at'] = datetime.now().isoformat()
        dept_data['is_active'] = dept_data.get('is_active', True)
        
        return self.dept_repo.save(dept_data['dept_code'], dept_data)
    
    def get_department(self, dept_code: str):
        """Get a department by code"""
        return self.dept_repo.find_by_id(dept_code)
    
    def get_all_departments(self):
        """Get all departments"""
        return self.dept_repo.find_all()
    
    def update_department(self, dept_code: str, dept_data: dict):
        """Update a department"""
        existing = self.dept_repo.find_by_id(dept_code)
        if not existing:
            return None
        
        dept_data['updated_at'] = datetime.now().isoformat()
        existing.update(dept_data)
        return self.dept_repo.update(dept_code, existing)
    
    def delete_department(self, dept_code: str):
        """Delete a department"""
        return self.dept_repo.delete(dept_code)