from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, func
)
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Database is optional - only needed for prediction logging
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://meduser:medpass123@localhost:5432/medical_db")

Base = declarative_base()

class MedicalText(Base):
    __tablename__ = 'medical_texts'
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False, unique=True)  # Added unique constraint
    answer = Column(Text, nullable=False)
    source = Column(String(32))
    focusarea = Column(String(256))
    focusgroup = Column(String(64))
    created_at = Column(DateTime, default=func.now())

# Try to create engine, but don't fail if database is not available
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)
    logger.info("Database connection configured (optional)")
except Exception as e:
    logger.warning(f"Database not available (optional): {e}")
    engine = None
    SessionLocal = None

def get_db():
    """Dependency to get database session."""
    if SessionLocal is None:
        raise RuntimeError("Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    if engine is None:
        raise RuntimeError("Database not configured")
    Base.metadata.create_all(engine)