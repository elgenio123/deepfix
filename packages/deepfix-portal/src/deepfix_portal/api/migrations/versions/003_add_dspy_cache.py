"""Add dspy_cache table for database-backed DSPy caching

Revision ID: 003_add_dspy_cache
Revises: 002_add_password_reset
Create Date: 2024-12-14 00:00:00.000000

"""

from alembic import op
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "003_add_dspy_cache"
down_revision = "002_add_password_reset"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create dspy_cache table
    op.create_table(
        "dspy_cache",
        Column("id", String(), nullable=False, primary_key=True),
        Column("cache_key", String(), nullable=False),
        Column("model_name", String(), nullable=False),
        Column("request_json", Text(), nullable=False),
        Column("response_json", Text(), nullable=False),
        Column("hit_count", Integer(), nullable=False, server_default="0"),
        Column("created_at", DateTime(timezone=True), server_default=func.now()),
        Column("updated_at", DateTime(timezone=True), server_default=func.now()),
    )

    # Create unique index on cache_key
    op.create_index(
        "ix_dspy_cache_cache_key",
        "dspy_cache",
        ["cache_key"],
        unique=True,
    )

    # Create index on model_name for analytics queries
    op.create_index(
        "ix_dspy_cache_model_name",
        "dspy_cache",
        ["model_name"],
        unique=False,
    )


def downgrade() -> None:
    # Drop indexes first
    op.drop_index("ix_dspy_cache_model_name", table_name="dspy_cache")
    op.drop_index("ix_dspy_cache_cache_key", table_name="dspy_cache")

    # Drop table
    op.drop_table("dspy_cache")
