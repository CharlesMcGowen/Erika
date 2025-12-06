#!/usr/bin/env python3
"""
Erika Database Session Management
=================================

SQLAlchemy database session management for Erika Gmail OAuth.

Author: Living Archive team
Version: 1.0.0
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment variable
# Users should set DATABASE_URL environment variable
# Example: postgresql://user:password@localhost:5432/dbname
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('ERIKA_DATABASE_URL')

if not DATABASE_URL:
    logger.warning("⚠️ DATABASE_URL not set. Database operations will fail.")
    logger.warning("   Set DATABASE_URL environment variable, e.g.:")
    logger.warning("   export DATABASE_URL='postgresql://user:password@localhost:5432/erika'")
    # Use a placeholder that will fail gracefully
    DATABASE_URL = 'postgresql://user:password@localhost:5432/erika'

# Create base class for models
Base = declarative_base()

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

# Scoped session for thread safety
Session = scoped_session(SessionLocal)


def get_db():
    """
    Get database session (dependency injection pattern)
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session():
    """
    Context manager for database sessions
    
    Usage:
        with db_session() as session:
            # Use session
            pass
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Initialize database tables"""
    # Import all models to register them with Base
    from . import models  # noqa: F401
    
    try:
        # Use checkfirst=True to skip existing tables/indexes
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database tables: {e}")
        raise


def drop_db():
    """Drop all database tables (use with caution!)"""
    from .models import Base
    Base.metadata.drop_all(bind=engine)
    logger.warning("⚠️ All database tables dropped")


# Export
__all__ = [
    'Base',
    'engine',
    'SessionLocal',
    'Session',
    'get_db',
    'db_session',
    'init_db',
    'drop_db',
    'DATABASE_URL',
]

