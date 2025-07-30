import hashlib
from django.conf import settings

def verify_signature(data):
    secret = settings.CRYPTOCLOUD_WEBHOOK_SECRET
    raw = data.get("amount", "") + data.get("currency", "") + data.get("status", "") + \
          data.get("order_id", "") + data.get("uuid", "") + secret
    signature = hashlib.sha256(raw.encode()).hexdigest()
    return signature == data.get("sign")
