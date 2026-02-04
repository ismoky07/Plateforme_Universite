"""
Authentication API Routes
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    decode_access_token
)
from app.core.exceptions import UnauthorizedException, BadRequestException
from app.api.deps import get_current_user
from app.models.user import UserRole

router = APIRouter()


# Request/Response Models
class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


class StudentLoginRequest(BaseModel):
    """Student login request (simplified)"""
    numero_etudiant: str
    nom: str
    prenom: str


class RegisterRequest(BaseModel):
    """User registration request"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.STUDENT


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


# In-memory user store (replace with database in production)
# This is a simplified version - in production, use a proper database
USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@universite.fr",
        "hashed_password": get_password_hash("admin123"),
        "full_name": "Administrateur",
        "role": UserRole.ADMIN,
        "is_active": True,
        "created_at": datetime.now().isoformat()
    },
    "prof": {
        "username": "prof",
        "email": "prof@universite.fr",
        "hashed_password": get_password_hash("prof123"),
        "full_name": "Professeur Martin",
        "role": UserRole.PROFESSOR,
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
}


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT tokens

    - **username**: User's username
    - **password**: User's password
    """
    user = USERS_DB.get(request.username)

    if not user:
        raise UnauthorizedException("Identifiants invalides")

    if not verify_password(request.password, user["hashed_password"]):
        raise UnauthorizedException("Identifiants invalides")

    if not user.get("is_active", True):
        raise UnauthorizedException("Compte desactive")

    # Create tokens
    access_token = create_access_token(
        subject=user["username"],
        role=user["role"].value if isinstance(user["role"], UserRole) else user["role"]
    )
    refresh_token = create_refresh_token(subject=user["username"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=480 * 60,  # 8 hours in seconds
        user={
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"].value if isinstance(user["role"], UserRole) else user["role"]
        }
    )


@router.post("/login/student", response_model=TokenResponse)
async def student_login(request: StudentLoginRequest):
    """
    Simplified student login (no password required)

    This creates a session for students to submit exams.
    - **numero_etudiant**: Student number
    - **nom**: Last name
    - **prenom**: First name
    """
    # Create a student session
    student_id = f"student_{request.numero_etudiant}"

    access_token = create_access_token(
        subject=student_id,
        role=UserRole.STUDENT.value,
        additional_claims={
            "numero_etudiant": request.numero_etudiant,
            "nom": request.nom,
            "prenom": request.prenom
        }
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=480 * 60,
        user={
            "username": student_id,
            "full_name": f"{request.prenom} {request.nom}",
            "role": UserRole.STUDENT.value,
            "numero_etudiant": request.numero_etudiant
        }
    )


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    Register a new user

    Only admins can create professor/admin accounts in production.
    """
    if request.username in USERS_DB:
        raise BadRequestException("Nom d'utilisateur deja pris")

    # Create new user
    new_user = {
        "username": request.username,
        "email": request.email,
        "hashed_password": get_password_hash(request.password),
        "full_name": request.full_name,
        "role": request.role,
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }

    USERS_DB[request.username] = new_user

    # Create tokens
    access_token = create_access_token(
        subject=new_user["username"],
        role=new_user["role"].value
    )
    refresh_token = create_refresh_token(subject=new_user["username"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=480 * 60,
        user={
            "username": new_user["username"],
            "email": new_user["email"],
            "full_name": new_user["full_name"],
            "role": new_user["role"].value
        }
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    payload = decode_access_token(request.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedException("Token de rafraichissement invalide")

    username = payload.get("sub")
    user = USERS_DB.get(username)

    if not user:
        raise UnauthorizedException("Utilisateur non trouve")

    # Create new access token
    access_token = create_access_token(
        subject=user["username"],
        role=user["role"].value if isinstance(user["role"], UserRole) else user["role"]
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=480 * 60,
        user={
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"].value if isinstance(user["role"], UserRole) else user["role"]
        }
    )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    return {
        "username": current_user.get("sub"),
        "role": current_user.get("role"),
        "numero_etudiant": current_user.get("numero_etudiant"),
        "nom": current_user.get("nom"),
        "prenom": current_user.get("prenom")
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user (invalidate token on client side)

    Note: JWT tokens are stateless, so actual invalidation
    should be handled by the client by discarding the token.
    For production, consider using a token blacklist.
    """
    return {"message": "Deconnexion reussie"}
