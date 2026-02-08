from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from pathlib import Path

from src.database.session import get_db
from src.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from src.core.security import get_current_user
from src.services.product_service import (
    get_product, get_products, create_product, update_product, delete_product
)

router = APIRouter()

# Configure upload directory
UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file and return the URL"""
    # Generate unique filename
    file_extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = upload_file.file.read()
        buffer.write(content)
    
    # Return URL (you might want to configure this based on your serving setup)
    return f"/uploads/products/{unique_filename}"

@router.get("/", response_model=List[ProductResponse])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = Query(None),
    available_only: bool = True,
    db: Session = Depends(get_db)
):
    products = get_products(
        db, skip=skip, limit=limit,
        category=category, available_only=available_only
    )
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.post("/", response_model=ProductResponse)
async def create_new_product(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    category: str = Form(...),
    price: float = Form(...),
    stock: int = Form(0),
    is_available: bool = Form(True),
    image_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Handle image upload
    image_url = None
    if image_file:
        image_url = save_upload_file(image_file)
    
    # Create product data
    product_data = ProductCreate(
        name=name,
        description=description,
        category=category,
        price=price,
        stock=stock,
        image_url=image_url
    )
    
    return create_product(db=db, product=product_data)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_existing_product(
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    is_available: Optional[bool] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Handle image upload
    image_url = None
    if image_file:
        image_url = save_upload_file(image_file)
    
    # Create update data with only provided fields
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if category is not None:
        update_data["category"] = category
    if price is not None:
        update_data["price"] = price
    if stock is not None:
        update_data["stock"] = stock
    if is_available is not None:
        update_data["is_available"] = is_available
    if image_url is not None:
        update_data["image_url"] = image_url
    
    product_update = ProductUpdate(**update_data)
    
    db_product = update_product(db, product_id, product_update)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.delete("/{product_id}")
async def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    success = delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}