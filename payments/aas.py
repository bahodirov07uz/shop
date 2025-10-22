import hashlib
import json

SECRET = "O03nviF71W86SVdMhhfV2Tup1ntrEvKS9eOi"  # test uchun qo‘lda

def generate_signature(data: dict) -> str:
    raw = (
        data.get("billing_id", "") +
        data.get("amount", "") +
        data.get("currency", "") +
        data.get("status", "") +
        data.get("uuid", "") +
        SECRET
    )
    return hashlib.sha256(raw.encode()).hexdigest()


# 🔹 Test ma'lumotlar
data = {
    "billing_id": "33895b23-dc37-4cb5-bcf5-fa8ab1587422",
    "status": "paid",
    "uuid": "INV-123",
    "amount": "100.00",
    "currency": "USDT"
}

# 🔹 Sign hosil qilish
sign = generate_signature(data)
data["sign"] = sign

print("✅ Callback JSON:")
print(json.dumps(data, indent=2))

print("\n🚀 CURL komandasi (kopiyalab test qil):")
print(f'curl -X POST https://china-asic.com/payments/callback/ \\')
print('  -H "Content-Type: application/json" \\')
print(f'  -d \'{json.dumps(data)}\'')
