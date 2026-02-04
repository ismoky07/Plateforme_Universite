"""
Users API Routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_admin_user, get_current_user
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_users(
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_admin_user)
):
    """
    List all users (admin only)

    - **role**: Optional filter by user role
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    # Import here to avoid circular import
    from app.api.v1.auth import USERS_DB

    users = []
    for username, user_data in USERS_DB.items():
        user_role = user_data.get("role")
        if isinstance(user_role, UserRole):
            user_role = user_role.value

        if role and user_role != role.value:
            continue

        users.append({
            "username": username,
            "email": user_data.get("email"),
            "full_name": user_data.get("full_name"),
            "role": user_role,
            "is_active": user_data.get("is_active", True),
            "created_at": user_data.get("created_at")
        })

    return users[skip:skip + limit]


@router.get("/{username}")
async def get_user(
    username: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get user by username

    Users can only view their own profile unless they are admin.
    """
    from app.api.v1.auth import USERS_DB

    # Check if user can view this profile
    if current_user.get("role") != UserRole.ADMIN.value and current_user.get("sub") != username:
        raise ForbiddenException("Vous ne pouvez voir que votre propre profil")

    user = USERS_DB.get(username)
    if not user:
        raise NotFoundException("Utilisateur", username)

    user_role = user.get("role")
    if isinstance(user_role, UserRole):
        user_role = user_role.value

    return {
        "username": username,
        "email": user.get("email"),
        "full_name": user.get("full_name"),
        "role": user_role,
        "is_active": user.get("is_active", True),
        "created_at": user.get("created_at")
    }


@router.put("/{username}")
async def update_user(
    username: str,
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_admin_user)
):
    """
    Update user (admin only)
    """
    from app.api.v1.auth import USERS_DB

    user = USERS_DB.get(username)
    if not user:
        raise NotFoundException("Utilisateur", username)

    if full_name:
        user["full_name"] = full_name
    if email:
        user["email"] = email
    if is_active is not None:
        user["is_active"] = is_active

    USERS_DB[username] = user

    return {"message": f"Utilisateur {username} mis a jour"}


@router.delete("/{username}")
async def delete_user(
    username: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Deactivate user (admin only)

    Users are not actually deleted, just deactivated.
    """
    from app.api.v1.auth import USERS_DB

    user = USERS_DB.get(username)
    if not user:
        raise NotFoundException("Utilisateur", username)

    # Don't allow deleting yourself
    if current_user.get("sub") == username:
        raise ForbiddenException("Vous ne pouvez pas supprimer votre propre compte")

    user["is_active"] = False
    USERS_DB[username] = user

    return {"message": f"Utilisateur {username} desactive"}
