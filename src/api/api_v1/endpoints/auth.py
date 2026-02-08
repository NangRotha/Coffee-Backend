from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.database.session import get_db
from src.schemas.user import Token, UserCreate, UserInDB, GoogleAuth
from src.core.security import create_access_token, get_password_hash, get_current_user
from src.services.user_service import create_user, authenticate_user, get_user_by_email, create_or_update_google_user

router = APIRouter()

@router.post("/register", response_model=UserInDB)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Check if this is the first user (make admin)
    if user.email == settings.ADMIN_EMAIL and user.password == settings.ADMIN_PASSWORD:
        user.role = "admin"
    
    return create_user(db=db, user=user)

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/google", response_model=Token)
def google_auth(google_auth: GoogleAuth, db: Session = Depends(get_db)):
    """Authenticate or register user with Google"""
    user = create_or_update_google_user(db, google_auth)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/google-link", response_model=UserInDB)
def link_google_account(
    google_auth: GoogleAuth,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Link Google account to existing user"""
    if current_user.is_google_user:
        raise HTTPException(
            status_code=400,
            detail="Account is already linked to Google"
        )
    
    # Update user with Google info
    current_user.google_id = google_auth.google_id
    current_user.avatar_url = google_auth.avatar_url
    current_user.is_google_user = True
    if google_auth.full_name and not current_user.full_name:
        current_user.full_name = google_auth.full_name
    
    db.commit()
    db.refresh(current_user)
    return current_user