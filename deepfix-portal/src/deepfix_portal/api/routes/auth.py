"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, SignupRequest, AuthResponse, UserResponse
from ..utils import hash_password, verify_password, create_access_token, verify_token
from ..dependencies import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/login", response_model=AuthResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create access token
    token = create_access_token(data={"sub": user.id})

    return AuthResponse(user=UserResponse.model_validate(user), access_token=token)


@router.post("/signup", response_model=AuthResponse)
async def signup(signup_data: SignupRequest, db: Session = Depends(get_db)):
    """
    Signup endpoint
    """
    # Use email as username if username is not provided
    username = signup_data.username or signup_data.email

    # Check if user already exists
    existing_user = (
        db.query(User)
        .filter((User.email == signup_data.email) | (User.username == username))
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Hash password
    hashed_password = hash_password(signup_data.password)

    # Create new user
    new_user = User(
        email=signup_data.email,
        username=username,
        password=hashed_password,
        name=signup_data.name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create access token
    token = create_access_token(data={"sub": new_user.id})

    return AuthResponse(user=UserResponse.model_validate(new_user), access_token=token)


@router.post("/logout")
async def logout(_current_user: User = Depends(get_current_user)):
    """
    Logout endpoint

    Note: With JWT tokens, logout is primarily handled client-side by removing
    the token from storage. The token will remain valid until expiration.

    For immediate token invalidation, you would need to implement token blacklisting
    (store revoked tokens in a database/cache and check them on each request).
    """
    # Client should remove the token from storage
    # Token will expire naturally based on ACCESS_TOKEN_EXPIRE_MINUTES
    # The _current_user dependency ensures the user is authenticated
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Get current authenticated user
    """
    # Verify token and get user
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.model_validate(user)
