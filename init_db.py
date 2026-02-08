#!/usr/bin/env python3
"""
Database initialization script for Coffee Shop Project
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.session import engine
from src.database.base import Base
from src.database.models import User, Product, Order, OrderItem
from src.core.security import get_password_hash
from src.config.settings import settings

def init_database():
    """Initialize database tables and seed with initial data"""
    
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Create a session to add initial data
    from sqlalchemy.orm import Session
    from sqlalchemy import text
    
    with Session(engine) as session:
        # Check if admin user already exists
        admin_exists = session.query(User).filter(
            User.email == settings.ADMIN_EMAIL
        ).first()
        
        if not admin_exists:
            print("Creating admin user...")
            # Create admin user
            admin_user = User(
                email=settings.ADMIN_EMAIL,
                username="admin",
                full_name="Administrator",
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                role="admin"
            )
            session.add(admin_user)
            session.commit()
            print("✅ Admin user created!")
            print(f"   Email: {settings.ADMIN_EMAIL}")
            print(f"   Password: {settings.ADMIN_PASSWORD}")
        else:
            print("✅ Admin user already exists")
        
        # Check if products exist
        products_exist = session.query(Product).first()
        if not products_exist:
            print("Adding sample products...")
            
            # Sample coffee products
            sample_products = [
                Product(
                    name="Espresso",
                    description="Strong and concentrated coffee",
                    category="coffee",
                    price=2.50,
                    stock=100,
                    image_url="/images/espresso.jpg"
                ),
                Product(
                    name="Cappuccino",
                    description="Espresso with steamed milk foam",
                    category="coffee",
                    price=3.50,
                    stock=80,
                    image_url="/images/cappuccino.jpg"
                ),
                Product(
                    name="Latte",
                    description="Espresso with steamed milk",
                    category="coffee",
                    price=4.00,
                    stock=70,
                    image_url="/images/latte.jpg"
                ),
                Product(
                    name="Americano",
                    description="Espresso with hot water",
                    category="coffee",
                    price=3.00,
                    stock=90,
                    image_url="/images/americano.jpg"
                ),
                Product(
                    name="Mocha",
                    description="Chocolate flavored latte",
                    category="coffee",
                    price=4.50,
                    stock=60,
                    image_url="/images/mocha.jpg"
                ),
                Product(
                    name="Green Tea",
                    description="Fresh green tea",
                    category="tea",
                    price=2.00,
                    stock=50,
                    image_url="/images/green-tea.jpg"
                ),
                Product(
                    name="Black Tea",
                    description="Classic black tea",
                    category="tea",
                    price=2.00,
                    stock=50,
                    image_url="/images/black-tea.jpg"
                ),
                Product(
                    name="Croissant",
                    description="Freshly baked butter croissant",
                    category="pastry",
                    price=2.50,
                    stock=40,
                    image_url="/images/croissant.jpg"
                ),
                Product(
                    name="Chocolate Cake",
                    description="Rich chocolate cake slice",
                    category="pastry",
                    price=4.50,
                    stock=30,
                    image_url="/images/chocolate-cake.jpg"
                ),
                Product(
                    name="Blueberry Smoothie",
                    description="Fresh blueberry smoothie",
                    category="smoothie",
                    price=5.00,
                    stock=25,
                    image_url="/images/smoothie.jpg"
                )
            ]
            
            for product in sample_products:
                session.add(product)
            
            session.commit()
            print(f"✅ {len(sample_products)} sample products added!")
        
        print("\n" + "="*50)
        print("Database initialization complete!")
        print("="*50)
        print("\nYou can now:")
        print("1. Run the backend server: uvicorn src.main:app --reload")
        print("2. Access the API docs at: http://localhost:8000/docs")
        print("3. Login with admin credentials:")
        print(f"   Email: {settings.ADMIN_EMAIL}")
        print(f"   Password: {settings.ADMIN_PASSWORD}")

if __name__ == "__main__":
    init_database()