# app/repositories/material_repository.py
from app.repositories.base_repository import BaseRepository

class MaterialRepository(BaseRepository):
    """Material data access layer"""
    
    def __init__(self):
        super().__init__('material')