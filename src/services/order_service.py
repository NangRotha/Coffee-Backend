from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime
import random
import string

from src.database.models import Order, OrderItem, Product, OrderStatus
from src.schemas.order import OrderCreate, OrderUpdate
from src.services.product_service import get_product, update_product_stock

def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"ORD-{timestamp}-{random_str}"

def get_order(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()

def get_order_by_number(db: Session, order_number: str) -> Optional[Order]:
    return db.query(Order).filter(Order.order_number == order_number).first()

def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Order]:
    query = db.query(Order)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

def create_order(db: Session, order: OrderCreate, user_id: Optional[int] = None) -> Order:
    # Calculate total amount and validate products
    total_amount = 0
    order_items_data = []
    
    for item in order.items:
        product = get_product(db, item.product_id)
        if not product or not product.is_available:
            raise ValueError(f"Product {item.product_id} not available")
        if product.stock < item.quantity:
            raise ValueError(f"Insufficient stock for {product.name}")
        
        total_amount += product.price * item.quantity
        order_items_data.append({
            "product": product,
            "quantity": item.quantity,
            "price": product.price,
            "special_instructions": item.special_instructions
        })
    
    # Determine initial status based on payment method
    initial_status = OrderStatus.PENDING
    initial_payment_status = False
    
    # If KHQR payment is already confirmed, set status to confirmed
    if hasattr(order, 'payment_status') and order.payment_status:
        initial_status = OrderStatus.CONFIRMED
        initial_payment_status = True
    
    # Create order
    db_order = Order(
        user_id=user_id,
        order_number=generate_order_number(),
        total_amount=total_amount,
        status=initial_status,
        payment_method=order.payment_method,
        payment_status=initial_payment_status,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        delivery_address=order.delivery_address,
        notes=order.notes
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items and update stock
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            price=item_data["price"],
            special_instructions=item_data["special_instructions"]
        )
        db.add(order_item)
        
        # Update product stock
        update_product_stock(db, item_data["product"].id, -item_data["quantity"])
    
    db.commit()
    db.refresh(db_order)
    
    return db_order

def update_order(db: Session, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    db_order = get_order(db, order_id)
    if db_order:
        update_data = order_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_order, field, value)
        db.commit()
        db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: int) -> bool:
    db_order = get_order(db, order_id)
    if db_order:
        # Restore product stock
        for item in db_order.items:
            update_product_stock(db, item.product_id, item.quantity)
        
        db.delete(db_order)
        db.commit()
        return True
    return False

def get_orders_by_customer(
    db: Session,
    customer_phone: str,
    customer_email: Optional[str] = None
) -> List[Dict[str, Any]]:
    query = db.query(Order).filter(Order.customer_phone == customer_phone)
    
    if customer_email:
        # If email provided, also check user email
        from src.services.user_service import get_user_by_email
        user = get_user_by_email(db, customer_email)
        if user:
            query = query.filter(
                (Order.customer_phone == customer_phone) | (Order.user_id == user.id)
            )
    
    orders = query.order_by(Order.created_at.desc()).all()
    
    # Convert to dict with items
    orders_with_items = []
    for order in orders:
        order_dict = get_order_with_items(db, order.id)
        if order_dict:
            orders_with_items.append(order_dict)
    
    return orders_with_items

def get_orders_with_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    query = db.query(Order)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert each order to dict with items
    orders_with_items = []
    for order in orders:
        order_dict = get_order_with_items(db, order.id)
        if order_dict:
            orders_with_items.append(order_dict)
    
    return orders_with_items

def get_order_with_items(db: Session, order_id: int) -> Optional[Dict[str, Any]]:
    order = get_order(db, order_id)
    if not order:
        return None
    
    # Get order items with product names
    items = []
    for item in order.items:
        product = get_product(db, item.product_id)
        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": product.name if product else "Unknown",
            "quantity": item.quantity,
            "price": item.price,
            "special_instructions": item.special_instructions
        })
    
    return {
        "id": order.id,
        "user_id": order.user_id,
        "order_number": order.order_number,
        "total_amount": order.total_amount,
        "status": order.status,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "delivery_address": order.delivery_address,
        "notes": order.notes,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "items": items
    }