import os
import requests
import pytest

OCR = f"https://{os.getenv('OCR_HOST', 'ocr.insightpulseai.net')}"

def test_ocr_health():
    """Test OCR service health endpoint"""
    j = requests.get(f"{OCR}/health", timeout=10).json()
    # API returns {'status': 'ok', 'models': {...}, 'ts': ...}
    assert j.get('status') == 'ok'
    assert 'models' in j
    assert 'ts' in j

@pytest.mark.skip(reason="Classify endpoint not yet deployed (404)")
def test_classify_endpoint_minimal():
    """Test expense classification endpoint (when deployed)"""
    r = requests.post(
        f"{OCR}/classify/expense",
        json={"text": "Restaurant dinner 45.20 USD"},
        timeout=20
    )
    j = r.json()
    assert 'category' in j and 'conf' in j and 0 <= j['conf'] <= 1
