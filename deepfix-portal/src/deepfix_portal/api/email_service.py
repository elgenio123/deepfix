"""
Email service for sending verification emails
"""

import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from urllib.parse import urlparse


def get_smtp_config():
    """
    Get SMTP configuration from environment variables
    """
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "username": os.getenv("SMTP_USER"),
        "password": os.getenv("SMTP_PASSWORD"),
        "from_email": os.getenv(
            "SMTP_FROM_EMAIL", os.getenv("SMTP_USER", "noreply@deepfix.com")
        ),
        "from_name": os.getenv("SMTP_FROM_NAME", "DeepFix"),
        "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
    }


def get_frontend_url() -> str:
    """
    Get frontend URL from environment variable and validate it.

    In production, FRONTEND_URL must be set to a valid domain (not localhost).
    This ensures verification links work correctly in production environments.

    Returns:
        str: The frontend URL, normalized (trailing slashes removed)

    Raises:
        ValueError: If FRONTEND_URL is not set or is invalid in production
    """
    frontend_url = os.getenv("FRONTEND_URL")

    # Check if FRONTEND_URL is set
    if not frontend_url:
        # In development, allow localhost default
        # In production, this should be explicitly set
        is_production = os.getenv("ENVIRONMENT", "").lower() in ("production", "prod")
        if is_production:
            raise ValueError(
                "FRONTEND_URL environment variable must be set in production. "
                "Please set it to your production domain (e.g., https://app.deepfix.com)"
            )
        # Development fallback
        frontend_url = "http://localhost:5173"
        print(
            "[WARNING] FRONTEND_URL not set, using default localhost. "
            "Set FRONTEND_URL environment variable for production."
        )

    # Normalize the URL (remove trailing slashes)
    frontend_url = frontend_url.rstrip("/")

    # Validate URL format
    try:
        parsed = urlparse(frontend_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid FRONTEND_URL format: {frontend_url}")
    except Exception as e:
        raise ValueError(f"Invalid FRONTEND_URL format: {frontend_url}. Error: {e}")

    # Warn if using localhost in production-like environments
    is_production = os.getenv("ENVIRONMENT", "").lower() in ("production", "prod")
    if is_production and ("localhost" in frontend_url or "127.0.0.1" in frontend_url):
        raise ValueError(
            f"FRONTEND_URL cannot be localhost in production: {frontend_url}. "
            "Please set FRONTEND_URL to your production domain."
        )

    return frontend_url


async def send_verification_email(
    email: str, token: str, name: Optional[str] = None
) -> None:
    """
    Send email verification email to user

    Args:
        email: User's email address
        token: Verification token
        name: User's name (optional)
    """
    config = get_smtp_config()
    frontend_url = get_frontend_url()

    # Check if SMTP is configured
    if not config["username"] or not config["password"]:
        # In development, just log instead of sending
        print(f"[EMAIL] Verification email would be sent to {email}")
        print(f"[EMAIL] Verification link: {frontend_url}/verify-email?token={token}")
        return

    verification_link = f"{frontend_url}/verify-email?token={token}"
    user_name = name or "there"

    # Create email message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify your DeepFix account"
    message["From"] = f"{config['from_name']} <{config['from_email']}>"
    message["To"] = email

    # Plain text version
    text_content = f"""
                    Hello {user_name},

                    Welcome to DeepFix! Please verify your email address by clicking the link below:

                    {verification_link}

                    This link will expire in 24 hours.

                    If you didn't create an account with DeepFix, please ignore this email.

                    Best regards,
                    The DeepFix Team
                """

    # HTML version
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h1 style="color: #2563eb; margin-top: 0;">Welcome to DeepFix!</h1>
            <p>Hello {user_name},</p>
            <p>Thank you for signing up! Please verify your email address to complete your account setup.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_link}" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">Verify Email Address</a>
            </div>
            <p style="font-size: 14px; color: #666;">Or copy and paste this link into your browser:</p>
            <p style="font-size: 12px; color: #999; word-break: break-all;">{verification_link}</p>
            <p style="font-size: 14px; color: #666; margin-top: 30px;">This link will expire in 24 hours.</p>
            <p style="font-size: 14px; color: #666; margin-top: 20px;">If you didn't create an account with DeepFix, please ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; margin: 0;">Best regards,<br>The DeepFix Team</p>
        </div>
    </body>
    </html>
    """

    # Attach both versions
    text_part = MIMEText(text_content, "plain")
    html_part = MIMEText(html_content, "html")
    message.attach(text_part)
    message.attach(html_part)

    # Send email
    try:
        await aiosmtplib.send(
            message,
            hostname=config["host"],
            port=config["port"],
            username=config["username"],
            password=config["password"],
            use_tls=config["use_tls"],  # Use STARTTLS for port 587
        )
    except Exception as e:
        # Log error but don't fail the signup process
        print(f"[EMAIL] Failed to send verification email to {email}: {e}")
        raise
