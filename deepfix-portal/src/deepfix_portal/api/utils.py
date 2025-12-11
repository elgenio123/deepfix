"""
Utility functions for authentication, password hashing, etc.
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import os
import hashlib

# Use SHA256 truncation for passwords longer than 72 bytes (bcrypt limit)
pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=True
)


def get_secret_key() -> str:
    """
    Get the secret key from the environment
    """
    SECRET_KEY = os.getenv("DEEPFIX_PORTAL_SECRET_KEY")
    if SECRET_KEY is None or SECRET_KEY == "":
        raise ValueError("DEEPFIX_PORTAL_SECRET_KEY is not set")
    return SECRET_KEY


def get_algorithm() -> str:
    """
    Get the algorithm from the environment
    """
    ALGORITHM = os.getenv("DEEPFIX_PORTAL_ALGORITHM")
    if ALGORITHM is None or ALGORITHM == "":
        raise ValueError("DEEPFIX_PORTAL_ALGORITHM is not set")
    return ALGORITHM


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    For passwords longer than 72 bytes, pre-hash with SHA256
    """
    # Bcrypt has a 72-byte limit, so pre-hash long passwords
    if len(password.encode("utf-8")) > 72:
        password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    For passwords longer than 72 bytes, pre-hash with SHA256
    """
    # Bcrypt has a 72-byte limit, so pre-hash long passwords
    if len(plain_password.encode("utf-8")) > 72:
        plain_password = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=get_algorithm())
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify and decode a JWT token
    Returns user ID if valid, None otherwise
    """

    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[get_algorithm()])
        user_id: str = payload.get("sub")
        return user_id
    except JWTError:
        return None
