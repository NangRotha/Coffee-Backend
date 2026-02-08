#!/usr/bin/env python3
"""
Check if admin user exists in database
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.session import engine
from src.database.models import User
from sqlalchemy.orm import Session

def check_admin_user():
    """Check if admin user exists"""
    
    with Session(engine) as session:
        # Check if admin user exists
        admin_user = session.query(User).filter(
            User.email == "admin@coffee.com"
        ).first()
        
        if admin_user:
            print("✅ Admin user found:")
            print(f"   ID: {admin_user.id}")
            print(f"   Email: {admin_user.email}")
            print(f"   Username: {admin_user.username}")
            print(f"   Full Name: {admin_user.full_name}")
            print(f"   Role: {admin_user.role}")
            print(f"   Hashed Password: {admin_user.hashed_password[:50]}...")
        else:
            print("❌ Admin user not found")
            
        # Check all users
        all_users = session.query(User).all()
        print(f"\nTotal users in database: {len(all_users)}")
        for user in all_users:
            print(f"   - {user.email} ({user.role})")

if __name__ == "__main__":
    check_admin_user()
