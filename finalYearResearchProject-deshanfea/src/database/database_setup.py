# src/database/database_setup.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from src.utils.config import Config

# Singleton engine — created once, reused everywhere
engine = create_engine(
    Config.DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite
)

SessionLocal = sessionmaker(bind=engine)


def setup_database():
    """Initialize database tables"""
    Base.metadata.create_all(engine)
    print("Database setup completed!")
    return engine


def get_session():
    """Get a database session (for non-FastAPI code like automation, scripts, etc.)
    Caller is responsible for closing the session."""
    return SessionLocal()


def get_db():
    """FastAPI dependency — yields a session and auto-closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
