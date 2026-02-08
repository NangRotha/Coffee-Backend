#!/usr/bin/env python3
"""
Test authentication manually
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.session import engine
from src.database.models import User
from src.core.security import verify_password
from sqlalchemy.orm import Session

def test_authentication():
    """Test authentication manually"""
    
    with Session(engine) as session:
        # Get admin user
        admin_user = session.query(User).filter(
            User.email == "admin@coffee.com"
        ).first()
        
        if admin_user:
            print("Testing password verification...")
            print(f"   Email: {admin_user.email}")
            print(f"   Hashed Password: {admin_user.hashed_password}")
            
            # Test password
            test_password = "admin123"
            is_valid = verify_password(test_password, admin_user.hashed_password)
            
            print(f"   Test Password: {test_password}")
            print(f"   Password Valid: {is_valid}")
            
            if is_valid:
                print("✅ Authentication should work!")
            else:
                print("❌ Password verification failed")
        else:
            print("❌ Admin user not found")

if __name__ == "__main__":
    test_authentication()
