# app/models/user.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import json

@dataclass
class User:
    """User model representing all system users"""
    # All required fields (no defaults) first
    user_id: str
    email: str
    password_hash: str
    role: str  # 'admin', 'lecturer', 'student'
    first_name: str
    last_name: str
    
    # Then optional fields with defaults
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
    # All required fields with no defaults first
    user_id: str
    email: str
    password_hash: str
    role: str
    first_name: str
    last_name: str
    staff_id: str
    
    # Then optional fields with defaults
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
    # All required fields with no defaults first
    user_id: str
    email: str
    password_hash: str
    role: str
    first_name: str
    last_name: str
    matric_no: str  # Required for student login
    programme: str
    year_of_study: int
    
    # Then optional fields with defaults
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
    # Level and semester fields for course filtering
    current_level: Optional[str] = None  # nd1, nd2, hnd1, hnd2
    current_semester: Optional[str] = None  # first, second
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def level_display(self) -> str:
        """Get display name for level"""
        levels = {
            'nd1': 'ND I',
            'nd2': 'ND II',
            'hnd1': 'HND I',
            'hnd2': 'HND II'
        }
        return levels.get(self.current_level, self.current_level or 'Not Set')
    
    @property
    def semester_display(self) -> str:
        """Get display name for semester"""
        semesters = {
            'first': 'First Semester',
            'second': 'Second Semester'
        }
        return semesters.get(self.current_semester, self.current_semester or 'Not Set')
    
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
            'last_login': self.last_login,
            'current_level': self.current_level,
            'current_semester': self.current_semester
        }