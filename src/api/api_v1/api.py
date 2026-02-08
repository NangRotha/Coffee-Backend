from fastapi import APIRouter
from src.api.api_v1.endpoints import auth, users, products, orders, admin, khqr, notifications

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(khqr.router, prefix="/khqr", tags=["khqr"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])