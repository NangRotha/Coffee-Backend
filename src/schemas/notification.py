from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    title: str
    message: str
    type: str
    timestamp: datetime
    read: bool = False

class NotificationCreate(NotificationBase):
    user_id: Optional[int] = None

class NotificationUpdate(BaseModel):
    read: Optional[bool] = None

class NotificationResponse(NotificationBase):
    id: int
    user_id: Optional[int]
    
    class Config:
        from_attributes = True

class NotificationSettings(BaseModel):
    enableRealTime: bool = True
    enableSound: bool = True
    enableDesktop: bool = False
    orderNotifications: bool = True
    stockNotifications: bool = True
    customerNotifications: bool = True
    systemNotifications: bool = True

class NotificationSettingsUpdate(BaseModel):
    enableRealTime: Optional[bool] = None
    enableSound: Optional[bool] = None
    enableDesktop: Optional[bool] = None
    orderNotifications: Optional[bool] = None
    stockNotifications: Optional[bool] = None
    customerNotifications: Optional[bool] = None
    systemNotifications: Optional[bool] = None
