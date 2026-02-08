from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.database.session import get_db
from src.core.security import get_current_admin
from src.services.order_service import get_orders
from src.services.product_service import get_products
from src.services.user_service import get_users
from src.database.models import OrderStatus, Order, User, Product

router = APIRouter()

@router.get("/public/recent-orders/")
async def get_public_recent_orders(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    orders = get_orders(db, skip=0, limit=limit)
    return orders

@router.get("/public/stats/")
async def get_public_stats(
    db: Session = Depends(get_db)
):
    # Get today's date
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    
    # Calculate different stats
    total_orders = db.query(Order).count()
    today_orders = db.query(Order).filter(Order.created_at >= start_of_day).count()
    total_users = db.query(User).count()
    total_products = db.query(Product).count()
    
    # Calculate revenue
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
    today_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= start_of_day,
        Order.payment_status == True
    ).scalar() or 0
    
    # Orders by status
    orders_by_status = {}
    for status in OrderStatus:
        count = db.query(Order).filter(Order.status == status).count()
        orders_by_status[status.value] = count
    
    return {
        "total_orders": total_orders,
        "today_orders": today_orders,
        "total_users": total_users,
        "total_products": total_products,
        "total_revenue": float(total_revenue),
        "today_revenue": float(today_revenue),
        "orders_by_status": orders_by_status
    }

@router.get("/stats/")
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    # Get today's date
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    
    # Calculate different stats
    total_orders = db.query(Order).count()
    today_orders = db.query(Order).filter(Order.created_at >= start_of_day).count()
    total_users = db.query(User).count()
    total_products = db.query(Product).count()
    
    # Calculate revenue
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
    today_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= start_of_day,
        Order.payment_status == True
    ).scalar() or 0
    
    # Orders by status
    orders_by_status = {}
    for status in OrderStatus:
        count = db.query(Order).filter(Order.status == status).count()
        orders_by_status[status.value] = count
    
    return {
        "total_orders": total_orders,
        "today_orders": today_orders,
        "total_users": total_users,
        "total_products": total_products,
        "total_revenue": float(total_revenue),
        "today_revenue": float(today_revenue),
        "orders_by_status": orders_by_status
    }

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    # Get today's date
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    
    # Calculate different stats
    total_orders = db.query(Order).count()
    today_orders = db.query(Order).filter(Order.created_at >= start_of_day).count()
    total_users = db.query(User).count()
    total_products = db.query(Product).count()
    
    # Calculate revenue
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
    today_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= start_of_day,
        Order.payment_status == True
    ).scalar() or 0
    
    # Orders by status
    orders_by_status = {}
    for status in OrderStatus:
        count = db.query(Order).filter(Order.status == status).count()
        orders_by_status[status.value] = count
    
    return {
        "total_orders": total_orders,
        "today_orders": today_orders,
        "total_users": total_users,
        "total_products": total_products,
        "total_revenue": float(total_revenue),
        "today_revenue": float(today_revenue),
        "orders_by_status": orders_by_status
    }

@router.get("/recent-orders")
async def get_recent_orders(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    orders = get_orders(db, skip=0, limit=limit)
    return orders

@router.get("/revenue-trend")
async def get_revenue_trend(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Query revenue by day
    revenue_by_day = db.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_amount).label('revenue'),
        func.count(Order.id).label('orders')
    ).filter(
        Order.created_at >= start_date,
        Order.payment_status == True
    ).group_by(
        func.date(Order.created_at)
    ).order_by('date').all()
    
    # Format response
    trend_data = []
    for row in revenue_by_day:
        trend_data.append({
            "date": row.date.isoformat() if row.date else None,
            "revenue": float(row.revenue or 0),
            "orders": row.orders or 0
        })
    
    return trend_data

@router.post("/telegram-test")
async def test_telegram_notification(
    message: str = "Test message from Coffee Shop Admin",
    current_user = Depends(get_current_admin)
):
    from src.core.telegram_bot import telegram_bot
    result = telegram_bot.send_message(message)
    return {"success": "error" not in result, "result": result}