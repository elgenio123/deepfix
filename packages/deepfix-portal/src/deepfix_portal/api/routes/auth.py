"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from datetime import datetime, timezone, timedelta

from ..database import get_db
from ..models import User
from ..schemas import (
    LoginRequest,
    SignupRequest,
    AuthResponse,
    UserResponse,
    SignupResponse,
    EmailVerificationRequest,
    EmailVerificationResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from ..utils import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    create_verification_token,
    verify_verification_token,
)
from ..dependencies import get_current_user
from ..email_service import send_verification_email, send_password_reset_email

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/login", response_model=AuthResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
    except OperationalError as exc:
        raise HTTPException(
            status_code=503, detail="Database unavailable. Please retry shortly."
        ) from exc

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create access token
    token = create_access_token(data={"sub": user.id})

    return AuthResponse(user=UserResponse.model_validate(user), access_token=token)


@router.post("/signup", response_model=SignupResponse)
async def signup(signup_data: SignupRequest, db: Session = Depends(get_db)):
    """
    Signup endpoint
    Creates a new user and sends verification email
    """
    # Use email as username if username is not provided
    username = signup_data.username or signup_data.email

    try:
        # Check if user already exists
        existing_user = (
            db.query(User)
            .filter((User.email == signup_data.email) | (User.username == username))
            .first()
        )
    except OperationalError as exc:
        raise HTTPException(
            status_code=503, detail="Database unavailable. Please retry shortly."
        ) from exc
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Hash password
    hashed_password = hash_password(signup_data.password)

    # Create new user (without token first)
    new_user = User(
        email=signup_data.email,
        username=username,
        password=hashed_password,
        name=signup_data.name,
        email_verified=False,
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503, detail="Unable to save user. Please retry shortly."
        ) from exc

    # Generate verification token using user ID
    verification_token = create_verification_token(new_user.id)
    token_expires = datetime.now(timezone.utc) + timedelta(hours=24)

    # Update user with verification token
    new_user.email_verification_token = verification_token
    new_user.email_verification_token_expires = token_expires
    try:
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Unable to save verification token. Please retry shortly.",
        ) from exc

    # Send verification email
    try:
        await send_verification_email(
            email=new_user.email, token=verification_token, name=new_user.name
        )
    except Exception as e:
        # Log error but don't fail signup - user can request resend
        print(f"Failed to send verification email: {e}")

    return SignupResponse(
        message="Account created! Please check your email to verify your account.",
        email=signup_data.email,
    )


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


@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    verification_data: EmailVerificationRequest, db: Session = Depends(get_db)
):
    """
    Verify email address with verification token
    """
    # Verify the token
    user_id = verify_verification_token(verification_data.token)
    if not user_id:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification token"
        )

    # Find user by ID (token contains user ID)
    try:
        user = db.query(User).filter(User.id == user_id).first()
    except OperationalError as exc:
        raise HTTPException(
            status_code=503, detail="Database unavailable. Please retry shortly."
        ) from exc

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if email is already verified
    if user.email_verified:
        return EmailVerificationResponse(
            message="Email is already verified. You can log in to your account."
        )

    # Check if token matches and hasn't expired
    if (
        user.email_verification_token != verification_data.token
        or user.email_verification_token_expires is None
        or user.email_verification_token_expires < datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification token"
        )

    # Mark email as verified and clear token
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_token_expires = None

    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503, detail="Unable to verify email. Please retry shortly."
        ) from exc

    return EmailVerificationResponse(
        message="Email verified successfully! You can now log in."
    )


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(
    resend_data: ResendVerificationRequest, db: Session = Depends(get_db)
):
    """
    Resend verification email
    """
    try:
        user = db.query(User).filter(User.email == resend_data.email).first()
    except OperationalError as exc:
        raise HTTPException(
            status_code=503, detail="Database unavailable. Please retry shortly."
        ) from exc

    if not user:
        # Don't reveal if email exists or not for security
        return ResendVerificationResponse(message="A verification link has been sent.")

    if user.email_verified:
        return ResendVerificationResponse(message="Email is already verified.")

    # Generate new verification token using user ID
    verification_token = create_verification_token(user.id)
    token_expires = datetime.now(timezone.utc) + timedelta(hours=24)

    # Update user with new token
    user.email_verification_token = verification_token
    user.email_verification_token_expires = token_expires

    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Unable to resend verification. Please retry shortly.",
        ) from exc

    # Send verification email
    try:
        await send_verification_email(
            email=user.email, token=verification_token, name=user.name
        )
    except Exception as e:
        # Log error but return success message for security
        print(f"Failed to send verification email: {e}")

    return ResendVerificationResponse(message="A verification link has been sent.")


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    forgot_data: ForgotPasswordRequest, db: Session = Depends(get_db)
):
    """
    Request password reset email
    """
    try:
        user = db.query(User).filter(User.email == forgot_data.email).first()
    except OperationalError as exc:
        raise HTTPException(
            status_code=503, detail="Database unavailable. Please retry shortly."
        ) from exc

    # Always return success message to prevent email enumeration
    success_message = (
        "If an account exists with this email, a password reset link has been sent."
    )

    if not user:
        return ForgotPasswordResponse(message=success_message)

    # Generate password reset token using user ID
    reset_token = create_verification_token(user.id)
    token_expires = datetime.now(timezone.utc) + timedelta(hours=1)

    # Update user with reset token
    user.password_reset_token = reset_token
    user.password_reset_token_expires = token_expires

    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Unable to process request. Please retry shortly.",
        ) from exc

    # Send password reset email
    try:
        await send_password_reset_email(
            email=user.email, token=reset_token, name=user.name
        )
    except Exception as e:
        # Log error but return success message for security
        print(f"Failed to send password reset email: {e}")

    return ForgotPasswordResponse(message=success_message)


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    reset_data: ResetPasswordRequest, db: Session = Depends(get_db)
):
    """
    Reset password with token
    """
    # Verify the token
    user_id = verify_verification_token(reset_data.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Find user by ID
    try:
        user = db.query(User).filter(User.id == user_id).first()
    except OperationalError as exc:
        raise HTTPException(
            status_code=503, detail="Database unavailable. Please retry shortly."
        ) from exc

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if token matches and hasn't expired
    if (
        user.password_reset_token != reset_data.token
        or user.password_reset_token_expires is None
        or user.password_reset_token_expires < datetime.now(timezone.utc)
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Update password and clear reset token
    user.password = hash_password(reset_data.new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None

    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503, detail="Unable to reset password. Please retry shortly."
        ) from exc

    return ResetPasswordResponse(
        message="Password reset successfully! You can now log in with your new password."
    )


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


@router.get("/me/with-keys")
async def get_current_user_with_api_keys(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Get current authenticated user along with their API keys.
    This eliminates the need for separate /me and /api-keys requests.
    """
    from ..models import APIKey
    from ..schemas import APIKeyResponse, UserWithApiKeysResponse

    # Verify token and get user
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch API keys for the user
    api_keys = (
        db.query(APIKey)
        .filter(APIKey.user_id == user_id)
        .order_by(APIKey.created_at.desc())
        .all()
    )

    return UserWithApiKeysResponse(
        user=UserResponse.model_validate(user),
        api_keys=[APIKeyResponse.model_validate(key) for key in api_keys],
    )
