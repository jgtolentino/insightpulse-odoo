import os
import requests

OCR = f"https://{os.getenv('OCR_HOST', 'ocr.insightpulseai.net')}"

def test_ocr_health():
    j = requests.get(f"{OCR}/health", timeout=10).json()
    assert j.get('ok') is True

def test_classify_endpoint_minimal():
    r = requests.post(
        f"{OCR}/classify/expense",
        json={"text": "Restaurant dinner 45.20 USD"},
        timeout=20
    )
    j = r.json()
    assert 'category' in j and 'conf' in j and 0 <= j['conf'] <= 1
