import qrcode
import io
import base64
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import hashlib

class KHQRService:
    """KHQR (Cambodian QR Code) payment service"""
    
    def __init__(self):
        # KHQR configuration - these would typically come from bank integration
        self.merchant_info = {
            "merchant_id": "1234567890",  # Replace with actual merchant ID
            "merchant_name": "ROTHA NANG",
            "merchant_city": "Phnom Penh",
            "country_code": "KH",  # Cambodia
            "currency_code": "USD",  # USD for Cambodia
            "account_number": "0123456789"  # Replace with actual account
        }
    
    def generate_khqr_data(self, amount: float, bill_number: Optional[str] = None) -> str:
        """
        Generate KHQR data string according to NBC (National Bank of Cambodia) specification
        """
        # Generate unique transaction ID
        transaction_id = str(uuid.uuid4()).replace('-', '')[:16]
        
        # KHQR payload structure (simplified version)
        # Format: [Field ID][Length][Value]
        payload_parts = []
        
        # Payload Format Indicator (00)
        payload_parts.append("0002")  # EMV Co format
        
        # Point of Initiation Method (01)
        payload_parts.append("01")  # Static QR
        
        # Merchant Account Information (26-45)
        # Globally Unique Identifier (00)
        payload_parts.append("0016khqr.bakong.gov.kh")
        
        # Merchant Account Information (01-99)
        # For Bakong system
        payload_parts.append(f"01{len(self.merchant_info['account_number']):02d}{self.merchant_info['account_number']}")
        
        # Merchant Category Code (52)
        payload_parts.append("5204")  # Retail
        
        # Transaction Currency (53)
        payload_parts.append("5303")  # USD (840)
        
        # Transaction Amount (54)
        amount_str = f"{amount:.2f}".replace('.', '')
        payload_parts.append(f"54{len(amount_str):02d}{amount_str}")
        
        # Tip or Convenience Fee Indicator (56)
        payload_parts.append("5602")  # Not applicable
        
        # Country Code (58)
        payload_parts.append("5802KH")
        
        # Merchant Name (59)
        merchant_name_bytes = self.merchant_info['merchant_name'].encode('utf-8')
        payload_parts.append(f"59{len(merchant_name_bytes):02d}{self.merchant_info['merchant_name']}")
        
        # Merchant City (60)
        city_bytes = self.merchant_info['merchant_city'].encode('utf-8')
        payload_parts.append(f"60{len(city_bytes):02d}{self.merchant_info['merchant_city']}")
        
        # Additional Data (62-63)
        # Bill Number (01)
        if bill_number:
            bill_bytes = bill_number.encode('utf-8')
            payload_parts.append(f"6201{len(bill_bytes):02d}{bill_bytes}")
        
        # Transaction ID (04)
        payload_parts.append(f"6204{len(transaction_id):02d}{transaction_id}")
        
        # CRC (63) - Calculate CRC16
        payload_data = ''.join(payload_parts)
        crc = self._calculate_crc16(payload_data)
        payload_parts.append(f"6304{crc}")
        
        return payload_data
    
    def _calculate_crc16(self, data: str) -> str:
        """Calculate CRC16 for KHQR data integrity"""
        # Simplified CRC16 calculation - in production, use proper CRC16 algorithm
        crc = 0xFFFF
        for byte in data.encode('utf-8'):
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0x1021
                else:
                    crc >>= 1
        return f"{crc:04X}"
    
    def generate_khqr_qr_code(self, amount: float, bill_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate KHQR QR code image
        """
        try:
            # Generate KHQR data
            khqr_data = self.generate_khqr_data(amount, bill_number)
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(khqr_data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 for web display
            img_buffer = io.BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "qr_code": f"data:image/png;base64,{img_base64}",
                "khqr_data": khqr_data,
                "amount": amount,
                "merchant_name": self.merchant_info['merchant_name'],
                "account_number": self.merchant_info['account_number']
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_khqr_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Verify KHQR payment status (this would integrate with bank API in production)
        """
        # Mock implementation - in production, integrate with Bakong or bank API
        # For demo purposes, we'll simulate payment verification
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "status": "completed",
            "verified_at": datetime.now().isoformat(),
            "amount": 0.00  # Would be retrieved from bank API
        }

# Global instance
khqr_service = KHQRService()
