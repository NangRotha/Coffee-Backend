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
    """Create admin user with simple credentials"""
    
    with Session(engine) as session:
        # Check if admin user already exists
        admin_exists = session.query(User).filter(
            User.email == "admin@coffee.com"
        ).first()
        
        if not admin_exists:
            print("Creating admin user...")
            # Create admin user with shorter password
            admin_user = User(
                email="admin@coffee.com",
                username="admin",
                full_name="Administrator",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                phone="+1234567890"
            )
            session.add(admin_user)
            session.commit()
            print("✅ Admin user created!")
            print("   Email: admin@coffee.com")
            print("   Password: admin123")
        else:
            print("✅ Admin user already exists")
            print("   Email: admin@coffee.com")
            print("   Password: admin123")

if __name__ == "__main__":
    create_admin()
