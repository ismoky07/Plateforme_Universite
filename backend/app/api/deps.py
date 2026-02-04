"""
API Dependencies - Authentication, authorization, and common dependencies
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import UserRole, User

# HTTP Bearer token security
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current authenticated user from JWT token

    Returns:
        User payload from JWT token
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise UnauthorizedException("Token invalide ou expire")

    return payload


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get current active user

    Returns:
        Active user payload
    """
    # In a real app, you'd check against a database
    # For now, we trust the JWT token
    return current_user


def require_role(allowed_roles: List[UserRole]):
    """
    Dependency factory to require specific user roles

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role([UserRole.ADMIN]))])
    """
    async def role_checker(current_user: dict = Depends(get_current_active_user)):
        user_role = current_user.get("role")
        if user_role not in [role.value for role in allowed_roles]:
            raise ForbiddenException(
                f"Acces reserve aux roles: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user

    return role_checker


# Convenience dependencies for specific roles
async def get_admin_user(
    current_user: dict = Depends(require_role([UserRole.ADMIN]))
) -> dict:
    """Require admin role"""
    return current_user


async def get_professor_user(
    current_user: dict = Depends(require_role([UserRole.PROFESSOR, UserRole.ADMIN]))
) -> dict:
    """Require professor or admin role"""
    return current_user


async def get_student_user(
    current_user: dict = Depends(require_role([UserRole.STUDENT, UserRole.PROFESSOR, UserRole.ADMIN]))
) -> dict:
    """Require student, professor, or admin role"""
    return current_user


# Optional authentication (for public endpoints that behave differently when authenticated)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[dict]:
    """
    Get optional user - doesn't fail if not authenticated

    Returns:
        User payload or None
    """
    if credentials is None:
        return None

    payload = decode_access_token(credentials.credentials)
    return payload
