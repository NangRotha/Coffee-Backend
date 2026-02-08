from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from src.database.models import User
from src.schemas.user import UserCreate, UserUpdate, GoogleAuth
from src.core.security import get_password_hash
from src.core.security import verify_password

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    return db.query(User).filter(User.google_id == google_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    # Handle password for Google users
    hashed_password = None
    if user.password:
        hashed_password = get_password_hash(user.password)
    
    db_user = User(
        email=user.email,
        phone=user.phone,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role,
        google_id=user.google_id,
        avatar_url=user.avatar_url,
        is_google_user=user.is_google_user or False
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("User with this email, username, or Google ID already exists")

def create_or_update_google_user(db: Session, google_auth: GoogleAuth) -> User:
    """Create or update user from Google authentication"""
    # Check if user exists by Google ID
    user = get_user_by_google_id(db, google_auth.google_id)
    
    if user:
        # Update existing Google user
        user.full_name = google_auth.full_name
        user.avatar_url = google_auth.avatar_url
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user
    
    # Check if user exists by email (link Google account)
    user = get_user_by_email(db, google_auth.email)
    if user:
        # Link Google account to existing user
        user.google_id = google_auth.google_id
        user.avatar_url = google_auth.avatar_url
        user.is_google_user = True
        if google_auth.full_name and not user.full_name:
            user.full_name = google_auth.full_name
        db.commit()
        db.refresh(user)
        return user
    
    # Create new Google user
    user_data = UserCreate(
        email=google_auth.email,
        full_name=google_auth.full_name,
        google_id=google_auth.google_id,
        avatar_url=google_auth.avatar_url,
        is_google_user=True,
        password=None  # No password for Google users
    )
    return create_user(db, user_data)

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    # Google users cannot authenticate with password
    if user.is_google_user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user