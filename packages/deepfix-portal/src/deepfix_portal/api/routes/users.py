"""
User management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import User
from ..schemas import UserResponse
from ..dependencies import get_current_user, get_admin_user

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(
    admin_user: User = Depends(get_admin_user), db: Session = Depends(get_db)
):
    """
    List all users (admin only)
    """
    users = db.query(User).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user by ID
    Users can view their own profile, admins can view any user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Users can only view their own profile unless they're admin
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile",
        )

    return UserResponse.model_validate(user)
