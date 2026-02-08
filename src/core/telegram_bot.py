import requests
import logging
from typing import Dict, Any
from src.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or settings.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, message: str, parse_mode: str = None) -> Dict[str, Any]:
        """Send message to Telegram chat with proper UTF-8 encoding"""
        # Telegram message length limit is 4096 characters
        if len(message) > 4096:
            logger.warning(f"Message too long ({len(message)} chars), truncating to 4096")
            message = message[:4093] + "..."
        
        url = f"{self.base_url}/sendMessage"
        
        # Prepare payload with proper encoding
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }
        
        # Only add parse_mode if it's a valid value and message contains HTML
        if parse_mode and self._contains_html(message):
            payload["parse_mode"] = parse_mode
        
        # Ensure proper headers for UTF-8
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json; charset=utf-8'
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Message sent to Telegram successfully")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            # Try to get more detailed error info
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"Telegram API error: {error_data}")
                except:
                    logger.error(f"Response content: {e.response.text}")
            return {"error": str(e)}
    
    def _contains_html(self, text: str) -> bool:
        """Check if text contains HTML tags"""
        import re
        html_tags = re.compile(r'<[^>]+>')
        return bool(html_tags.search(text))
    
    def _escape_markdown(self, text: str) -> str:
        """Escape special characters for MarkdownV2 format"""
        escape_chars = '_*[]()~`>#+-=|{}.!'
        return ''.join(f'\\{char}' if char in escape_chars else char for char in text)
    
    def send_order_notification(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send order notification to Telegram with Khmer language support"""
        items_text = ""
        if 'items' in order_data:
            items_text = "\n".join([
                f"• {item.get('product_name', 'Item')} "
                f"x{item.get('quantity', 1)} "
                f"- ${item.get('price', 0):.2f}"
                for item in order_data['items']
            ])
        
        # Get Khmer translations
        payment_method_kh = self._get_payment_method_khmer(order_data.get('payment_method', 'cash'))
        status_kh = self._get_status_description_khmer(order_data.get('status', 'pending'))
        
        # Create message with proper formatting for Khmer text
        message = f"""🔔 ការបញ្ជាទិញថ្មី / New Order!

លេខកូដការបញ្ជាទិញ: #{order_data.get('id', 'N/A')}
លេខការបញ្ជាទិញ: {order_data.get('order_number', 'N/A')}

ឈ្មោះអតិថិជន: {order_data.get('customer_name', 'N/A')}
លេខទូរស័ព្ទ: {order_data.get('customer_phone', 'N/A')}

របស់ដែលបានបញ្ជាទិញ:
{items_text}

សរុប: ${order_data.get('total_amount', 0):.2f}
វិធីទូទាត់: {payment_method_kh}
ស្ថានភាព: {status_kh}

អាសយដ្ឋាន: {order_data.get('delivery_address', 'Pickup')}
កំណត់សម្គាល់: {order_data.get('notes', 'No notes')}

ពេលវេលា: {order_data.get('created_at', 'N/A')}
        """.strip()
        
        # Send without parse_mode to ensure Khmer text displays correctly
        return self.send_message(message, parse_mode=None)
    
    def send_status_update(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send order status update to Telegram with Khmer language support"""
        # Get Khmer translations
        payment_method_kh = self._get_payment_method_khmer(order_data.get('payment_method', 'cash'))
        status_kh = self._get_status_description_khmer(order_data.get('status', 'pending'))
        
        # Create message with proper formatting for Khmer text
        message = f"""📊 ការអាប់ដេតស្ថានភាព / Status Update

ការបញ្ជាទិញ: {order_data.get('order_number', 'N/A')}
ស្ថានភាព: {status_kh}

អតិថិជន: {order_data.get('customer_name', 'N/A')}
លេខទូរស័ព្ទ: {order_data.get('customer_phone', 'N/A')}

សរុប: ${order_data.get('total_amount', 0):.2f}
វិធីទូទាត់: {payment_method_kh}
បានអាប់ដេត: {order_data.get('updated_at', 'N/A')}
        """.strip()
        
        # Send without parse_mode to ensure Khmer text displays correctly
        return self.send_message(message, parse_mode=None)
    
    def _get_payment_method_khmer(self, payment_method: str) -> str:
        """Get Khmer translation for payment method"""
        payment_methods = {
            'cash': 'សាច់ប្រាក់ / Cash',
            'khqr': 'KHQR',
            'card': 'កាតឥណទាន / Card',
            'paypal': 'PayPal',
            'apple_pay': 'Apple Pay',
            'google_pay': 'Google Pay'
        }
        return payment_methods.get(payment_method.lower(), payment_method)

    def _get_status_description_khmer(self, status: str) -> str:
        """Get Khmer description for order status"""
        status_descriptions = {
            'pending': '⏳ កំពុងរង់ចាំ / Pending',
            'confirmed': '✅ បានបញ្ជាក់ / Confirmed',
            'preparing': '👨‍🍳 កំពុងរៀបចំ / Preparing',
            'ready': '🎯 ួចរាល់ / Ready for Pickup',
            'delivered': '🚚 បានដឹកជញ្ជូន / Delivered',
            'cancelled': '❌ បានបដិសេធ / Cancelled'
        }
        return status_descriptions.get(status.lower(), status)

# Global instance
telegram_bot = TelegramBot()