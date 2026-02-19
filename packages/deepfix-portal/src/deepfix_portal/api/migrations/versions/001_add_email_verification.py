"""Add email verification fields to users table

Revision ID: 001_add_email_verification
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Boolean, DateTime, Text

# revision identifiers, used by Alembic.
revision = "001_add_email_verification"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add email verification fields to users table
    op.add_column(
        "users",
        sa.Column("email_verified", Boolean(), nullable=False, server_default="false"),
    )
    op.add_column("users", sa.Column("email_verification_token", Text(), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "email_verification_token_expires", DateTime(timezone=True), nullable=True
        ),
    )


def downgrade() -> None:
    # Remove email verification fields
    op.drop_column("users", "email_verification_token_expires")
    op.drop_column("users", "email_verification_token")
    op.drop_column("users", "email_verified")
