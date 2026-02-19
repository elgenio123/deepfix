"""Add password reset fields to users table

Revision ID: 002_add_password_reset
Revises: 001_add_email_verification
Create Date: 2024-01-02 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import DateTime, Text

# revision identifiers, used by Alembic.
revision = "002_add_password_reset"
down_revision = "001_add_email_verification"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add password reset fields to users table
    op.add_column("users", sa.Column("password_reset_token", Text(), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "password_reset_token_expires", DateTime(timezone=True), nullable=True
        ),
    )


def downgrade() -> None:
    # Remove password reset fields
    op.drop_column("users", "password_reset_token_expires")
    op.drop_column("users", "password_reset_token")
