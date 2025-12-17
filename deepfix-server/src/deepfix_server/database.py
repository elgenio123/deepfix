"""
Database configuration and session management for deepfix-server.
"""

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from .config import DatabaseConfig

# Global engine and session factory
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def init_database(config: DatabaseConfig) -> None:
    """Initialize the database engine and session factory.

    Args:
        config: DatabaseConfig with connection URL and settings.
    """
    global _engine, _SessionLocal
    _engine = create_engine(config.database_url, echo=config.echo)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_engine() -> Optional[Engine]:
    """Get the database engine.

    Returns:
        The SQLAlchemy engine, or None if not initialized.
    """
    return _engine


def get_session() -> Session:
    """Create a new database session.

    Returns:
        A new SQLAlchemy session.

    Raises:
        RuntimeError: If the database has not been initialized.
    """
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _SessionLocal()


def get_db():
    """Dependency to get database session.

    Yields:
        A database session that will be closed after use.

    Raises:
        RuntimeError: If the database has not been initialized.
    """
    db = get_session()
    try:
        yield db
    finally:
        db.close()
