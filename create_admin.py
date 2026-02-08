#!/usr/bin/env python3
"""
Simple script to create admin user
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.session import engine
from src.database.models import User
from src.core.security import get_password_hash
from sqlalchemy.orm import Session

def create_admin():
    """Create admin user with environment-based credentials"""
    
    # Get admin credentials from environment variables or use defaults
    admin_email = os.getenv("ADMIN_EMAIL", "admin@coffee.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    with Session(engine) as session:
        # Check if admin user already exists
        admin_exists = session.query(User).filter(
            User.email == admin_email
        ).first()
        
        if not admin_exists:
            print("Creating admin user...")
            # Create admin user
            admin_user = User(
                email=admin_email,
                username="admin",
                full_name="Administrator",
                hashed_password=get_password_hash(admin_password),
                role="admin",
                phone="+1234567890"
            )
            session.add(admin_user)
            session.commit()
            print("✅ Admin user created!")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
        else:
            print("✅ Admin user already exists")
            print(f"   Email: {admin_email}")

if __name__ == "__main__":
    create_admin()
