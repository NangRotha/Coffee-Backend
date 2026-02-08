from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./coffee_shop.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = "8400403295:AAGt9yXWxg7a_sRWxu1swv1dQmaEBv_Rdtw"
    TELEGRAM_CHAT_ID: str = "1422320012"
    
    # Admin
    ADMIN_EMAIL: str = "admin@coffee.com"
    ADMIN_PASSWORD: str = "admin123"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # App
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()