from sqlalchemy.orm import Session
import models, schemas, security  # <-- Fixed import

def get_user(db: Session, user_id: int):
    """Get a single user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """Get a single user by username."""
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Create a new user and store in the database."""
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        username=user.username, 
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user