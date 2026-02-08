from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    special_instructions: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: float
    special_instructions: Optional[str] = None
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_name: str
    customer_phone: str
    delivery_address: Optional[str] = None
    payment_method: str = "cash"
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    payment_status: Optional[bool] = False

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[bool] = None

class OrderInDB(OrderBase):
    id: int
    user_id: Optional[int]
    order_number: str
    total_amount: float
    status: OrderStatus
    payment_status: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderResponse(OrderInDB):
    items: List[OrderItemResponse]