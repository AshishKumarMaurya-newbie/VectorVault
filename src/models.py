from sqlalchemy import Column, Integer, String, Boolean
from database import Base  # <-- Fixed import

class User(Base):
    """SQLAlchemy model for the User table."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # We will add relationships to KnowledgeBases later