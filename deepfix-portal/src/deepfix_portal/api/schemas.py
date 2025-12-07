"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    username: str


class UserResponse(UserBase):
    id: str
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    username: Optional[str] = None


# Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    username: Optional[str] = None


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: Optional[str] = None  # If using JWT


# API Key Schemas
class APIKeyCreate(BaseModel):
    name: Optional[str] = None


class APIKeyResponse(BaseModel):
    id: str
    key: str
    name: Optional[str]
    created_at: datetime
    last_used: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class APIKeyValidationRequest(BaseModel):
    key: str


class APIKeyValidationResponse(BaseModel):
    key_id: str
    key_name: Optional[str]
    key_is_active: bool
    user_id: str
    user_email: EmailStr
    user_name: Optional[str]
    user_is_active: bool


# Password Reset Schemas
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

