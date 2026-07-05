# app/services/material_service.py
from app.repositories.material_repository import MaterialRepository
from datetime import datetime
import uuid

class MaterialService:
    """Service layer for material management"""
    
    def __init__(self):
        self.material_repo = MaterialRepository()
    
    def create_material(self, material_data: dict):
        """Create a new material"""
        try:
            material_data['material_id'] = f"MAT_{uuid.uuid4().hex[:8]}"
            material_data['created_at'] = datetime.now().isoformat()
            material_data['updated_at'] = datetime.now().isoformat()
            material_data['is_published'] = material_data.get('is_published', False)
            material_data['downloads'] = 0
            material_data['file_name'] = material_data.get('file_name', '')
            
            return self.material_repo.save(material_data['material_id'], material_data)
        except Exception as e:
            print(f"Create material error: {e}")
            return None
    
    def get_material(self, material_id: str):
        """Get a material by ID"""
        try:
            return self.material_repo.find_by_id(material_id)
        except Exception as e:
            print(f"Get material error: {e}")
            return None
    
    def get_all_materials(self):
        """Get all materials"""
        try:
            return self.material_repo.find_all()
        except Exception as e:
            print(f"Get all materials error: {e}")
            return []
    
    def get_materials_by_course(self, course_code: str):
        """Get materials by course"""
        try:
            materials = self.material_repo.find_all()
            return [m for m in materials if m.get('course_code') == course_code]
        except Exception as e:
            print(f"Get materials by course error: {e}")
            return []
    
    def update_material(self, material_id: str, material_data: dict):
        """Update a material"""
        try:
            existing = self.material_repo.find_by_id(material_id)
            if not existing:
                return None
            
            material_data['updated_at'] = datetime.now().isoformat()
            existing.update(material_data)
            return self.material_repo.update(material_id, existing)
        except Exception as e:
            print(f"Update material error: {e}")
            return None
    
    def delete_material(self, material_id: str):
        """Delete a material"""
        try:
            # Also delete the physical file if needed
            material = self.material_repo.find_by_id(material_id)
            if material and material.get('file_url'):
                # Optionally delete the file from the filesystem
                pass
            return self.material_repo.delete(material_id)
        except Exception as e:
            print(f"Delete material error: {e}")
            return False
    
    def increment_downloads(self, material_id: str):
        """Increment download count"""
        try:
            material = self.material_repo.find_by_id(material_id)
            if material:
                material['downloads'] = material.get('downloads', 0) + 1
                return self.material_repo.update(material_id, material)
            return False
        except Exception as e:
            print(f"Increment downloads error: {e}")
            return False