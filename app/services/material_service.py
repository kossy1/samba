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
        material_data['material_id'] = f"MAT_{uuid.uuid4().hex[:8]}"
        material_data['created_at'] = datetime.now().isoformat()
        material_data['updated_at'] = datetime.now().isoformat()
        material_data['is_published'] = material_data.get('is_published', False)
        material_data['downloads'] = 0
        
        return self.material_repo.save(material_data['material_id'], material_data)
    
    def get_material(self, material_id: str):
        """Get a material by ID"""
        return self.material_repo.find_by_id(material_id)
    
    def get_all_materials(self):
        """Get all materials"""
        return self.material_repo.find_all()
    
    def get_materials_by_course(self, course_code: str):
        """Get materials by course"""
        materials = self.material_repo.find_all()
        return [m for m in materials if m.get('course_code') == course_code]
    
    def update_material(self, material_id: str, material_data: dict):
        """Update a material"""
        existing = self.material_repo.find_by_id(material_id)
        if not existing:
            return None
        
        material_data['updated_at'] = datetime.now().isoformat()
        existing.update(material_data)
        return self.material_repo.update(material_id, existing)
    
    def delete_material(self, material_id: str):
        """Delete a material"""
        return self.material_repo.delete(material_id)
    
    def increment_downloads(self, material_id: str):
        """Increment download count"""
        material = self.material_repo.find_by_id(material_id)
        if material:
            material['downloads'] = material.get('downloads', 0) + 1
            return self.material_repo.update(material_id, material)
        return False