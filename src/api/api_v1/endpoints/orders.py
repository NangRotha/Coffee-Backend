from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from src.database.session import get_db
from src.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from src.core.security import get_current_user
from src.services.order_service import create_order, get_order_with_items, update_order, delete_order
from src.core.telegram_bot import telegram_bot
from src.api.api_v1.endpoints.notifications import notify_new_order

router = APIRouter()

def send_telegram_notification(order_data: dict):
    """Background task to send Telegram notification"""
    telegram_bot.send_order_notification(order_data)

@router.get("/", response_model=List[OrderResponse])
async def read_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = None
    if current_user.role == "customer":
        user_id = current_user.id
    
    orders = get_orders_with_items(db, skip=skip, limit=limit, user_id=user_id, status=status)
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    order = get_order_with_items(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    if current_user.role == "customer" and order["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return order

@router.get("/customer/", response_model=List[OrderResponse])
async def get_customer_orders(
    customer_phone: str,
    customer_email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get orders for a customer by phone (and optionally email)"""
    from src.services.order_service import get_orders_by_customer
    
    orders = get_orders_by_customer(db, customer_phone, customer_email)
    return orders

@router.post("/guest", response_model=OrderResponse)
async def create_guest_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        created_order = create_order(db, order, user_id=None)
        
        # Get order with items for response and notification
        order_data = get_order_with_items(db, created_order.id)
        
        # Send Telegram notification in background
        background_tasks.add_task(send_telegram_notification, order_data)
        
        return order_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=OrderResponse)
async def create_new_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = current_user.id if current_user.role == "customer" else None
    
    try:
        created_order = create_order(db, order, user_id)
        
        # Get order with items for notification
        order_data = get_order_with_items(db, created_order.id)
        
        # Send Telegram notification in background
        background_tasks.add_task(send_telegram_notification, order_data)
        
        # Send real-time notification
        background_tasks.add_task(notify_new_order, order_data)
        
        return created_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{order_id}", response_model=OrderResponse)
async def update_existing_order(
    order_id: int,
    order_update: OrderUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_order = update_order(db, order_id, order_update)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get order with items for notification
    order_data = get_order_with_items(db, db_order.id)
    
    # Send status update notification
    background_tasks.add_task(
        telegram_bot.send_status_update,
        order_data
    )
    
    return db_order

@router.delete("/{order_id}")
async def delete_existing_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    success = delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}