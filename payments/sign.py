import hashlib
import requests

# Payment ma'lumotlari
data = {
    "billing_id": "5152baae-2016-45c9-82f4-345ab782450c",
    "amount": "200.00",
    "currency": "USD",
    "status": "paid",
    "uuid": "INV-TEST-123"
}

# CRYPTOCLOUD_WEBHOOK_SECRET ni to‘g‘ri qo‘ying
secret = "O03nviF71W86SVdMhhfV2Tup1ntrEvKS9eOi"

# Sign generatsiya qilish (billing_id birinchi)
raw = (
    data["billing_id"]
    + data["amount"]
    + data["currency"]
    + data["status"]
    + data["uuid"]
    + secret
)
sign = hashlib.sha256(raw.encode()).hexdigest()
data["sign"] = sign

# Callback URL
url = "https://china-asic.com/payments/callback/"

# POST so‘rov yuborish
response = requests.post(url, json=data)
print("Status code:", response.status_code)
print("Response text:", response.text)
