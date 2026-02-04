"""
User Models
"""
from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User role enumeration"""
    STUDENT = "student"
    PROFESSOR = "professor"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.STUDENT
    is_active: bool = True


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    """User model for responses"""
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(User):
    """User model with hashed password (internal use)"""
    hashed_password: str


class StudentInfo(BaseModel):
    """Student-specific information for login"""
    numero_etudiant: str = Field(..., description="Student number")
    nom: str = Field(..., description="Last name")
    prenom: str = Field(..., description="First name")


class ProfessorInfo(BaseModel):
    """Professor-specific information"""
    departement: Optional[str] = None
    matieres: List[str] = []


class UserPermissions(BaseModel):
    """User permissions model"""
    can_view: bool = True
    can_edit: bool = False
    can_delete: bool = False
    can_export: bool = False
    can_validate: bool = False
    can_manage_users: bool = False


# Role-based permissions
ROLE_PERMISSIONS = {
    UserRole.ADMIN: UserPermissions(
        can_view=True,
        can_edit=True,
        can_delete=True,
        can_export=True,
        can_validate=True,
        can_manage_users=True
    ),
    UserRole.PROFESSOR: UserPermissions(
        can_view=True,
        can_edit=True,
        can_delete=False,
        can_export=True,
        can_validate=True,
        can_manage_users=False
    ),
    UserRole.STUDENT: UserPermissions(
        can_view=True,
        can_edit=False,
        can_delete=False,
        can_export=False,
        can_validate=False,
        can_manage_users=False
    )
}
