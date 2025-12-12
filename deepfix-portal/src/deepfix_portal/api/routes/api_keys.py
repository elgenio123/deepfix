"""
API Key management routes
"""

import secrets
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import APIKey, User
from ..schemas import (
    APIKeyCreate,
    APIKeyResponse,
    APIKeyValidationRequest,
    APIKeyValidationResponse,
)
from ..dependencies import (
    get_current_user,
    verify_service_token,
    _cached_api_key_lookup,
    _api_key_cache_bucket,
)

router = APIRouter()


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    List all API keys for the current user
    """
    # Get API keys for current user
    api_keys = (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id, APIKey.is_active == True)
        .all()
    )
    return api_keys


@router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a new API key for the current user
    """
    # Generate secure API key
    api_key = f"df_live_{secrets.token_urlsafe(32)}"

    # Create API key record
    new_key = APIKey(user_id=current_user.id, key=api_key, name=key_data.name)
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    _cached_api_key_lookup.cache_clear()
    return new_key


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Revoke (deactivate) an API key
    """
    # Find and deactivate API key
    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == current_user.id)
        .first()
    )
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.is_active = False
    db.commit()
    _cached_api_key_lookup.cache_clear()
    return {"message": "API key revoked successfully"}


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get details of a specific API key
    """
    # Get API key
    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == current_user.id)
        .first()
    )
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return api_key


@router.post(
    "/validate",
    response_model=APIKeyValidationResponse,
    dependencies=[Depends(verify_service_token)],
)
async def validate_api_key(
    request: APIKeyValidationRequest,
    db: Session = Depends(get_db),
):
    """
    Validate an API key for server-to-server access (used by deepfix-server).
    """
    cached = _cached_api_key_lookup(request.key, _api_key_cache_bucket())
    if not cached:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
    (
        key_id,
        key_name,
        key_is_active,
        user_id,
        user_email,
        user_name,
        user_is_active,
    ) = cached

    if not key_is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key is inactive",
        )
    if not user_is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key owner is inactive or missing",
        )

    # Update last_used on the live DB object using the request-scoped session
    api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if api_key:
        api_key.last_used = datetime.now(timezone.utc)
    db.commit()

    return APIKeyValidationResponse(
        key_id=key_id,
        key_name=key_name,
        key_is_active=key_is_active,
        user_id=user_id,
        user_email=user_email,
        user_name=user_name,
        user_is_active=user_is_active,
    )
