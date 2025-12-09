"""
SQLAlchemy database models
"""
import uuid

from deepfix_core.models import RequestLog
from sqlalchemy import Boolean, Column, DateTime, String, Text, text
from sqlalchemy.sql import func

from .database import Base

# Re-export RequestLog from deepfix_core for convenience
__all__ = ["User", "APIKey", "RequestLog"]


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(Text, unique=True, nullable=False, index=True)
    email = Column(Text, unique=True, nullable=False, index=True)
    password = Column(Text, nullable=False)  # Should be hashed
    name = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False, nullable=False)


class APIKey(Base):
    """API Key model"""
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)  # Foreign key to users.id
    key = Column(String, unique=True, nullable=False, index=True)  # The actual API key
    name = Column(Text, nullable=True)  # Optional name for the key
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    is_active = Column(Boolean, default=True)

