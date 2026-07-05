# app/models/user.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import json

@dataclass
class User:
    """User model representing all system users"""
    user_id: str
    email: str
    password_hash: str
    role: str
    first_name: str
    last_name: str
    department: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary for Redis storage"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'department': self.department,
            'phone': self.phone,
            'profile_image': self.profile_image,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login
        }


@dataclass
class Lecturer:
    """Lecturer model - separate from User to avoid inheritance issues"""
    user_id: str
    email: str
    password_hash: str
    role: str
    first_name: str
    last_name: str
    staff_id: str
    department: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: bool = True
    specialization: Optional[str] = None
    office_location: Optional[str] = None
    consultation_hours: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary for Redis storage"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'staff_id': self.staff_id,
            'department': self.department,
            'phone': self.phone,
            'profile_image': self.profile_image,
            'is_active': self.is_active,
            'specialization': self.specialization,
            'office_location': self.office_location,
            'consultation_hours': self.consultation_hours,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login
        }


@dataclass
class Student:
    """Student model - separate from User to avoid inheritance issues"""
    user_id: str
    email: str
    password_hash: str
    role: str
    first_name: str
    last_name: str
    matric_no: str
    programme: str
    year_of_study: int
    department: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: bool = True
    faculty: Optional[str] = None
    enrolled_courses: List[str] = field(default_factory=list)
    gpa: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary for Redis storage"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'matric_no': self.matric_no,
            'programme': self.programme,
            'year_of_study': self.year_of_study,
            'department': self.department,
            'phone': self.phone,
            'profile_image': self.profile_image,
            'is_active': self.is_active,
            'faculty': self.faculty,
            'enrolled_courses': json.dumps(self.enrolled_courses),
            'gpa': self.gpa,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login
        }