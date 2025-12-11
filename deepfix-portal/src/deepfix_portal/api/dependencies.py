"""
FastAPI dependencies for authentication, etc.
"""

import os
import time
from functools import lru_cache
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db, SessionLocal
from .models import User
from .utils import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Lightweight TTL bucket helper for lru_cache-backed lookups
USER_CACHE_TTL_SECONDS = 60


def _user_cache_bucket() -> int:
    return int(time.time() / USER_CACHE_TTL_SECONDS)


@lru_cache(maxsize=256)
def _cached_user_lookup(user_id: str, _bucket: int) -> Optional[User]:
    """
    Cached user fetch to avoid repeated DB hits on hot paths.
    The TTL bucket parameter ensures periodic refresh.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = verify_token(token)
    if user_id is None:
        raise credentials_exception

    user = _cached_user_lookup(user_id, _user_cache_bucket())
    if user is None:
        raise credentials_exception

    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure the current user is an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


async def verify_service_token(
    x_service_token: Optional[str] = Header(default=None),
) -> None:
    """
    Verify the shared service token for server-to-server requests.
    """
    PORTAL_SERVICE_TOKEN = os.getenv("DEEPFIX_PORTAL_SERVICE_TOKEN")

    if PORTAL_SERVICE_TOKEN is None or PORTAL_SERVICE_TOKEN == "":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service token is not configured",
        )
    if not x_service_token or x_service_token != PORTAL_SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service token",
        )
