from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from src.database.session import get_db
from src.core.security import get_current_user, get_current_admin
from src.database.models import Order, User, Product
from src.schemas.order import OrderResponse
from src.schemas.user import UserInDB
from src.schemas.notification import NotificationResponse, NotificationSettings, NotificationSettingsUpdate

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: Optional[int] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: Optional[int] = None):
        self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await connection.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Store notifications in memory (in production, use database)
notifications_store = []

# Initialize with some sample notifications
def initialize_sample_notifications():
    """Initialize with sample notifications"""
    if not notifications_store:
        notifications_store.extend([
            {
                "id": 1,
                "title": "New order received",
                "message": "Order #12349 from Sarah Wilson",
                "type": "order",
                "timestamp": datetime.now() - timedelta(minutes=2),
                "read": False,
                "user_id": None
            },
            {
                "id": 2,
                "title": "Low stock alert",
                "message": "Coffee beans running low (5 units left)",
                "type": "inventory",
                "timestamp": datetime.now() - timedelta(minutes=15),
                "read": False,
                "user_id": None
            },
            {
                "id": 3,
                "title": "Customer review",
                "message": "5-star review from John Davis",
                "type": "review",
                "timestamp": datetime.now() - timedelta(hours=1),
                "read": True,
                "user_id": None
            },
            {
                "id": 4,
                "title": "System update",
                "message": "System maintenance scheduled for tonight",
                "type": "system",
                "timestamp": datetime.now() - timedelta(hours=3),
                "read": True,
                "user_id": None
            }
        ])

# Initialize sample notifications when module is imported
initialize_sample_notifications()

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all notifications for the current user"""
    user_notifications = [
        n for n in notifications_store 
        if n.get('user_id') is None or n.get('user_id') == current_user.id
    ]
    
    # Sort by timestamp (newest first)
    user_notifications.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Apply pagination
    paginated = user_notifications[skip:skip + limit]
    
    return [
        NotificationResponse(
            id=n['id'],
            title=n['title'],
            message=n['message'],
            type=n['type'],
            timestamp=n['timestamp'],
            read=n['read'],
            user_id=n.get('user_id')
        ) for n in paginated
    ]

@router.get("/unread/", response_model=List[NotificationResponse])
async def get_unread_notifications(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get unread notifications for the current user"""
    user_notifications = [
        n for n in notifications_store 
        if (n.get('user_id') is None or n.get('user_id') == current_user.id) 
        and not n.get('read', False)
    ]
    
    # Sort by timestamp (newest first)
    user_notifications.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return [
        NotificationResponse(
            id=n['id'],
            title=n['title'],
            message=n['message'],
            type=n['type'],
            timestamp=n['timestamp'],
            read=n['read'],
            user_id=n.get('user_id')
        ) for n in user_notifications
    ]

@router.post("/{notification_id}/read/")
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark a notification as read"""
    for notification in notifications_store:
        if notification['id'] == notification_id:
            notification['read'] = True
            break
    
    return {"message": "Notification marked as read"}

@router.post("/mark-all-read/")
async def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark all notifications as read for the current user"""
    for notification in notifications_store:
        if notification.get('user_id') is None or notification.get('user_id') == current_user.id:
            notification['read'] = True
    
    return {"message": "All notifications marked as read"}

@router.delete("/")
async def clear_all_notifications(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Clear all notifications for the current user"""
    global notifications_store
    notifications_store = [
        n for n in notifications_store 
        if n.get('user_id') is not None and n.get('user_id') != current_user.id
    ]
    
    return {"message": "All notifications cleared"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a specific notification"""
    global notifications_store
    notifications_store = [
        n for n in notifications_store 
        if n['id'] != notification_id or 
        (n.get('user_id') is not None and n.get('user_id') != current_user.id)
    ]
    
    return {"message": "Notification deleted"}

@router.get("/settings/", response_model=NotificationSettings)
async def get_notification_settings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get notification settings for the current user"""
    # In a real implementation, this would come from a database
    return NotificationSettings()

@router.put("/settings/", response_model=NotificationSettings)
async def update_notification_settings(
    settings: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update notification settings for the current user"""
    # In a real implementation, this would be saved to a database
    current_settings = NotificationSettings()
    
    # Update only the fields that are provided
    update_data = settings.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(current_settings, field):
            setattr(current_settings, field, value)
    
    return current_settings

# WebSocket endpoint for real-time notifications
@router.websocket("/ws/")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = None
):
    """WebSocket endpoint for real-time notifications"""
    user_id = None
    try:
        # Verify token if provided
        if token and token != "null":
            from src.core.security import get_current_user
            from src.database.session import SessionLocal
            
            # Create a database session for token validation
            db = SessionLocal()
            
            # Manually verify JWT token (similar to get_current_user but for WebSocket)
            from jose import JWTError, jwt
            from src.config.settings import settings
            
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                email: str = payload.get("sub")
                if email:
                    from src.services.user_service import get_user_by_email
                    user = get_user_by_email(db, email=email)
                    if user:
                        user_id = user.id
            except JWTError:
                pass
            finally:
                db.close()
        
        # Accept connection (with or without authentication for now)
        await manager.connect(websocket, user_id)
        
    except Exception as e:
        await websocket.close(code=1008, reason="Authentication failed")
        return

    try:
        while True:
            # Wait for messages (could be used for bidirectional communication)
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

# Helper functions to create notifications
def create_notification(title: str, message: str, type: str, user_id: Optional[int] = None) -> Dict[str, Any]:
    """Create a new notification"""
    notification = {
        "id": len(notifications_store) + 1,
        "title": title,
        "message": message,
        "type": type,
        "timestamp": datetime.now(),
        "read": False,
        "user_id": user_id
    }
    
    notifications_store.append(notification)
    return notification

async def broadcast_notification(notification: Dict[str, Any]):
    """Broadcast a notification to all connected clients"""
    message = json.dumps(notification)
    await manager.broadcast(message)

async def send_notification_to_user(notification: Dict[str, Any], user_id: int):
    """Send a notification to a specific user"""
    message = json.dumps(notification)
    await manager.send_personal_message(message, user_id)

# Notification creation functions for different events
async def notify_new_order(order: OrderResponse):
    """Create notification for new order"""
    notification = create_notification(
        title="New Order Received",
        message=f"Order #{order.id} from {order.customer_name}",
        type="order"
    )
    await broadcast_notification(notification)

async def notify_low_stock(product: Product, current_stock: int):
    """Create notification for low stock"""
    notification = create_notification(
        title="Low Stock Alert",
        message=f"{product.name} running low ({current_stock} units left)",
        type="inventory"
    )
    await broadcast_notification(notification)

async def notify_customer_review(customer_name: str, rating: int):
    """Create notification for customer review"""
    notification = create_notification(
        title="Customer Review",
        message=f"{rating}-star review from {customer_name}",
        type="review"
    )
    await broadcast_notification(notification)

async def notify_system_message(title: str, message: str):
    """Create system notification"""
    notification = create_notification(
        title=title,
        message=message,
        type="system"
    )
    await broadcast_notification(notification)
