"""Base database configuration and session management.

This module provides the SQLAlchemy Base, engine, and session factory for the application.

TODO: Migrate to Alembic for proper database migrations instead of using create_all().
      For now, create_all() works for development but won't handle schema changes in production.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from taskflow.utils.config import settings
from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models.

    All models should inherit from this class to be registered with SQLAlchemy.
    """
    pass


# Create engine with SQLite
# In production, this should use a proper database like PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=settings.DEBUG,  # Log SQL statements in debug mode
)

# Session factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize the database by creating all tables.

    This imports all models to ensure they're registered with SQLAlchemy,
    then creates all tables defined in the models.

    Note: This uses create_all() which is fine for development but doesn't
    handle migrations. TODO: Switch to Alembic for production use.
    """
    # Import all models to ensure they're registered with Base.metadata
    from taskflow.models.user import User  # noqa: F401
    from taskflow.models.project import Project  # noqa: F401
    from taskflow.models.task import Task  # noqa: F401

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    print("Database initialized successfully!")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get a database session.

    Usage:
        with get_db() as db:
            # Use db session
            pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
