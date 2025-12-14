"""
SQLAlchemy database models
"""

import uuid

from deepfix_core.models import RequestLog
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(Text, unique=True, nullable=False, index=True)
    email = Column(Text, unique=True, nullable=False, index=True)
    password = Column(Text, nullable=False)  # Should be hashed
    name = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(Text, nullable=True)
    email_verification_token_expires = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(Text, nullable=True)
    password_reset_token_expires = Column(DateTime(timezone=True), nullable=True)


class APIKey(Base):
    """API Key model"""

    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)  # Foreign key to users.id
    key = Column(String, unique=True, nullable=False, index=True)  # The actual API key
    name = Column(Text, nullable=True)  # Optional name for the key
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)


class DSPyCache(Base):
    """DSPy LLM cache model for database-backed caching"""

    __tablename__ = "dspy_cache"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cache_key = Column(String, unique=True, nullable=False, index=True)  # SHA256 hash
    model_name = Column(String, nullable=False, index=True)  # LLM model identifier
    request_json = Column(Text, nullable=False)  # JSON serialized request
    response_json = Column(Text, nullable=False)  # JSON serialized response
    hit_count = Column(Integer, default=0, nullable=False)  # Number of cache hits
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# Re-export RequestLog from deepfix_core for convenience
__all__ = ["User", "APIKey", "RequestLog", "DSPyCache"]
