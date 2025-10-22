# payments/utils.py
import hashlib
import hmac
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def verify_signature(data):
    """
    Cryptocloud webhook signature ni tekshirish
    """
    try:
        secret = settings.CRYPTOCLOUD_WEBHOOK_SECRET
        
        # Variant 1: Standart formula
        raw_string = (
            str(data.get("billing_id", "")) +
            str(data.get("amount", "")) +
            str(data.get("currency", "")) +
            str(data.get("status", "")) +
            str(data.get("uuid", "")) +
            secret
        )
        
        calculated_signature = hashlib.sha256(raw_string.encode()).hexdigest()
        received_signature = data.get("sign", "")
        
        logger.info(f"🔐 Signature check: calculated={calculated_signature}, received={received_signature}")
        
        return calculated_signature == received_signature
        
    except Exception as e:
        logger.error(f"❌ Signature verification error: {e}")
        return False

def verify_signature_hmac(data):
    """
    HMAC yordamida signature tekshirish (agar SHA256 ishlamasa)
    """
    try:
        secret = settings.CRYPTOCLOUD_WEBHOOK_SECRET.encode()
        
        message = (
            str(data.get("billing_id", "")) +
            str(data.get("amount", "")) +
            str(data.get("currency", "")) +
            str(data.get("status", "")) +
            str(data.get("uuid", ""))
        ).encode()
        
        calculated_signature = hmac.new(secret, message, hashlib.sha256).hexdigest()
        received_signature = data.get("sign", "")
        
        logger.info(f"🔐 HMAC Signature: calculated={calculated_signature}, received={received_signature}")
        
        return hmac.compare_digest(calculated_signature, received_signature)
        
    except Exception as e:
        logger.error(f"❌ HMAC signature error: {e}")
        return False
