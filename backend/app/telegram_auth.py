"""
Telegram WebApp authentication and user ID extraction.
"""
import json
import hmac
import hashlib
from urllib.parse import parse_qs
from typing import Optional, Dict
import structlog

logger = structlog.get_logger()


def validate_telegram_data(init_data: str, bot_token: str) -> bool:
    """
    Validate Telegram WebApp initData.
    
    Args:
        init_data: Telegram WebApp initData string
        bot_token: Bot token for validation
        
    Returns:
        True if data is valid, False otherwise
    """
    try:
        # Parse init_data
        parsed = parse_qs(init_data)
        
        # Get hash
        received_hash = parsed.get('hash', [''])[0]
        if not received_hash:
            return False
        
        # Remove hash from data
        data_check_string_parts = []
        for key, value in sorted(parsed.items()):
            if key != 'hash':
                data_check_string_parts.append(f"{key}={value[0]}")
        
        data_check_string = '\n'.join(data_check_string_parts)
        
        # Calculate expected hash
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        expected_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(received_hash, expected_hash)
        
    except Exception as e:
        logger.error("Error validating Telegram data", error=str(e))
        return False


def extract_user_id(init_data: str) -> Optional[str]:
    """
    Extract user ID from Telegram WebApp initData.
    
    Args:
        init_data: Telegram WebApp initData string
        
    Returns:
        User ID as string, or None if extraction fails
    """
    try:
        # Parse init_data
        parsed = parse_qs(init_data)
        
        # Try to get user data
        user_data = parsed.get('user', [''])[0]
        if user_data:
            user_json = json.loads(user_data)
            user_id = user_json.get('id')
            if user_id:
                logger.info("User ID extracted", user_id=user_id)
                return str(user_id)
        
        logger.warning("No user data in initData")
        return None
        
    except Exception as e:
        logger.error("Error extracting user ID", error=str(e))
        return None


def get_user_id_from_header(authorization: Optional[str]) -> Optional[str]:
    """
    Extract user ID from Authorization header.
    Expected format: "tma <initData>"
    
    Args:
        authorization: Authorization header value
        
    Returns:
        User ID as string, or None if extraction fails
    """
    if not authorization:
        return None
    
    try:
        # Check if it starts with "tma "
        if not authorization.startswith("tma "):
            return None
        
        init_data = authorization[4:]  # Remove "tma " prefix
        return extract_user_id(init_data)
        
    except Exception as e:
        logger.error("Error getting user ID from header", error=str(e))
        return None

