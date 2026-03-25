# src/database/database_setup.py
from sqlalchemy import create_engine
from src.database.models import Base
from src.utils.config import Config
from sqlalchemy.orm import sessionmaker  

def setup_database():
    """Initialize database"""
    engine = create_engine(Config.DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Database setup completed!")
    return engine

def get_session():
    """Get database session"""
    engine = create_engine(Config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()