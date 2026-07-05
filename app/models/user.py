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
    role: str  # 'admin', 'lecturer', 'student'
    first_name: str
    last_name: str
    department: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


@dataclass
class Lecturer(User):
    """Lecturer-specific model extending User"""
    # All fields with no default values must come first
    staff_id: str
    # Then fields with default values
    specialization: Optional[str] = None
    office_location: Optional[str] = None
    consultation_hours: Optional[str] = None
    
    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({
            'staff_id': self.staff_id,
            'specialization': self.specialization,
            'office_location': self.office_location,
            'consultation_hours': self.consultation_hours
        })
        return base_dict


@dataclass
class Student(User):
    """Student-specific model extending User"""
    # All fields with no default values must come first
    matric_no: str
    programme: str  # e.g., 'ND', 'HND'
    year_of_study: int
    # Then fields with default values
    faculty: Optional[str] = None
    enrolled_courses: List[str] = field(default_factory=list)
    gpa: Optional[float] = None
    
    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({
            'matric_no': self.matric_no,
            'programme': self.programme,
            'year_of_study': self.year_of_study,
            'faculty': self.faculty,
            'enrolled_courses': json.dumps(self.enrolled_courses),
            'gpa': self.gpa
        })
        return base_dict