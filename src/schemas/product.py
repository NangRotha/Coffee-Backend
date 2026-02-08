from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class ProductCategory(str, Enum):
    COFFEE = "coffee"
    TEA = "tea"
    SMOOTHIE = "smoothie"
    PASTRY = "pastry"
    SANDWICH = "sandwich"

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: ProductCategory
    price: float
    image_url: Optional[str] = None
    stock: int = 0

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ProductCategory] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    stock: Optional[int] = None

class ProductInDB(ProductBase):
    id: int
    is_available: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductResponse(ProductInDB):
    pass