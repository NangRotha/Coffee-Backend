from sqlalchemy.orm import Session
from typing import Optional, List
from src.database.models import Product, ProductCategory
from src.schemas.product import ProductCreate, ProductUpdate

def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    available_only: bool = False
) -> List[Product]:
    query = db.query(Product)
    
    if category:
        query = query.filter(Product.category == category)
    
    if available_only:
        query = query.filter(Product.is_available == True)
    
    return query.offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(
        name=product.name,
        description=product.description,
        category=product.category,
        price=product.price,
        image_url=product.image_url,
        stock=product.stock
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False

def update_product_stock(db: Session, product_id: int, quantity: int) -> Optional[Product]:
    db_product = get_product(db, product_id)
    if db_product:
        db_product.stock += quantity
        if db_product.stock < 0:
            db_product.stock = 0
        db.commit()
        db.refresh(db_product)
    return db_product