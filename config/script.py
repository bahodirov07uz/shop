import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import csv
from datetime import datetime
import os

# ===================== SOZLAMALAR =====================
IMAP_SERVER = 'imap.beget.com'
EMAIL       = 'info@china-asic.com'
PASSWORD    = 'asic-China2025?'          # ← BU YERNI O‘ZGARTIRING!

COUNT       = 20                            # oxirgi nechta xabar
OUTPUT_DIR  = "email_export"
CSV_FILE    = os.path.join(OUTPUT_DIR, f"inbox_last_{COUNT}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")

# ===================== YORDAMCHI FUNKSİYALAR =====================

def decode_text(text):
    if not text:
        return ""
    decoded = decode_header(text)[0][0]
    if isinstance(decoded, bytes):
        try:
            return decoded.decode('utf-8')
        except:
            return decoded.decode('iso-8859-1', errors='replace')
    return decoded


def get_plain_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                charset = part.get_content_charset() or 'utf-8'
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(charset, errors='replace')
                break
    else:
        charset = msg.get_content_charset() or 'utf-8'
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(charset, errors='replace')
    
    return body[:1500].replace('\n', ' ').replace('\r', ' ').strip()  # juda uzun bo‘lmasin


# ===================== ASOSIY KOD =====================

try:
    # ulanish
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
    mail.login(EMAIL, PASSWORD)
    print("Login muvaffaqiyatli")

    # INBOX ni ochamiz
    mail.select("INBOX", readonly=True)
    print("INBOX ochildi")

    # barcha xabar ID larini olamiz
    status, data = mail.search(None, 'ALL')
    if status != 'OK' or not data[0]:
        print("INBOX da xabar topilmadi")
        mail.logout()
        exit()

    msg_ids = data[0].split()
    print(f"Jami xabarlar: {len(msg_ids)} ta")

    # oxirgi 20 ta (eng yangi xabarlar)
    last_ids = msg_ids[-COUNT:]
    print(f"O‘qilmoqda: {len(last_ids)} ta xabar")

    rows = []
    rows.append(["ID", "Sana", "Kimdan", "Mavzu", "Matn (qisqa)"])

    for num in reversed(last_ids):  # yangidan → eskiga tartibda
        _, msg_data = mail.fetch(num, "(RFC822)")
        if not msg_data or not isinstance(msg_data[0], tuple):
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = decode_text(msg["Subject"]) or "(mavzu yo‘q)"
        from_   = decode_text(msg["From"]) or "?"
        date_str = msg["Date"] or "?"

        # sanani chiroyli formatlash
        try:
            dt = parsedate_to_datetime(date_str)
            date_formatted = dt.strftime("%Y-%m-%d %H:%M")
        except:
            date_formatted = date_str[:25]

        body_short = get_plain_body(msg)

        rows.append([
            num.decode(),
            date_formatted,
            from_,
            subject,
            body_short
        ])

    # CSV ga saqlash
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:  # utf-8-sig → Excelda to‘g‘ri ochiladi
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"\nSaqlandi: {CSV_FILE}")
    print(f"Jami yozilgan qatorlar: {len(rows)-1} ta")

    mail.logout()

except imaplib.IMAP4.error as e:
    print("IMAP xatosi (parol yoki login noto‘g‘ri bo‘lishi mumkin):")
    print(e)
except Exception as e:
    print("Xato yuz berdi:")
    print(type(e).__name__, str(e))
    
    
import requests
import json
from decouple import config

API_KEY = config("CRYPTOCLOUD_API_KEY")

url = "https://api.cryptocloud.plus/v2/merchant/wallet/balance/all"

headers = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (API Client)"
}

response = requests.post(url, headers=headers, timeout=30)

print("STATUS:", response.status_code)
print(response.text)

if response.ok:
    data = response.json()
    print("✅ Balans ma'lumotlari:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print("❌ Xato:", response.status_code)
