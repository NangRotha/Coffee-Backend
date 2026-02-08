from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.database.session import get_db
from src.services.khqr_service import khqr_service

router = APIRouter()

@router.post("/generate")
async def generate_khqr(
    amount: float,
    bill_number: str = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate KHQR QR code for payment"""
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")
    
    if amount > 10000:  # Example limit
        raise HTTPException(status_code=400, detail="Amount exceeds maximum limit")
    
    try:
        result = khqr_service.generate_khqr_qr_code(amount, bill_number)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate KHQR: {str(e)}")

@router.post("/verify/{transaction_id}")
async def verify_khqr_payment(
    transaction_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Verify KHQR payment status"""
    
    if not transaction_id:
        raise HTTPException(status_code=400, detail="Transaction ID is required")
    
    try:
        result = khqr_service.verify_khqr_payment(transaction_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify KHQR payment: {str(e)}")

@router.get("/merchant-info")
async def get_merchant_info() -> Dict[str, Any]:
    """Get merchant KHQR information"""
    
    return {
        "merchant_name": khqr_service.merchant_info["merchant_name"],
        "merchant_city": khqr_service.merchant_info["merchant_city"],
        "country_code": khqr_service.merchant_info["country_code"],
        "currency_code": khqr_service.merchant_info["currency_code"],
        "supported_currencies": ["USD", "KHR"],
        "max_amount": 10000,
        "min_amount": 0.01
    }
