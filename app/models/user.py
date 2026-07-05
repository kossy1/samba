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
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create model from dictionary"""
        return cls(
            user_id=data['user_id'],
            email=data['email'],
            password_hash=data['password_hash'],
            role=data['role'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            department=data.get('department'),
            phone=data.get('phone'),
            profile_image=data.get('profile_image'),
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
            last_login=datetime.fromisoformat(data['last_login']) if data.get('last_login') else None
        )

@dataclass
class Lecturer(User):
    """Lecturer-specific model extending User"""
    staff_id: str
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
    matric_no: str
    programme: str  # e.g., 'ND', 'HND'
    year_of_study: int
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