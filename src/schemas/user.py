from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    STAFF = "staff"

class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER

class UserCreate(UserBase):
    password: Optional[str] = None  # Optional for Google users
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    is_google_user: Optional[bool] = False

class UserUpdate(BaseModel):
    phone: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    is_google_user: Optional[bool] = False
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleAuth(BaseModel):
    google_id: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserInDB

class TokenData(BaseModel):
    email: Optional[str] = None