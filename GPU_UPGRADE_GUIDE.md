# GPU Droplet Upgrade Guide

## Current Setup (CPU-Only)

**OCR Provider:** Tesseract (CPU-based)
**Cost:** $24/month (4GB/2vCPU)
**Performance:** ~2-5 seconds per receipt

## GPU Upgrade Option

### DigitalOcean GPU Droplets

**Available Options:**

| Type | GPU | RAM | vCPUs | Storage | Cost/Month |
|------|-----|-----|-------|---------|------------|
| GPU Basic | NVIDIA V100 (16GB) | 30GB | 8 | 200GB | $600 |
| GPU Pro | NVIDIA V100 (16GB) | 60GB | 16 | 400GB | $1,200 |

**Note:** GPU droplets are significantly more expensive.

### When to Upgrade

✅ **Consider GPU if:**
- Processing >1000 receipts/day
- Need <1 second OCR response time
- Want advanced AI features (sentiment analysis, entity extraction)
- Batch processing large document volumes

❌ **Don't need GPU if:**
- Processing <100 receipts/day (current Tesseract is fine)
- Using external OCR APIs (Google Vision, Azure)
- Cost is a primary concern

## Alternative: External GPU Services

### Option 1: Google Vision API
**Cost:** $1.50 per 1000 images
**Setup:**
```bash
# Update .env
OCR_PROVIDER=google
GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'

# Restart
docker compose restart ocr-api
```

### Option 2: Azure Document Intelligence
**Cost:** $1.00 per 1000 pages (first 1000 free)
**Setup:**
```bash
# Update .env
OCR_PROVIDER=azure
AZURE_ENDPOINT=https://YOUR_RESOURCE.cognitiveservices.azure.com/
AZURE_KEY=your_azure_key

# Restart
docker compose restart ocr-api
```

### Option 3: PaddleOCR on CPU
**Cost:** $0 (open source)
**Performance:** 3-8 seconds per receipt (CPU)
**Setup:**
```bash
# Update OCR service
cd services/ocr-api
cat > requirements.txt <<EOF
paddleocr==2.7.0
paddlepaddle==2.6.0
fastapi==0.115.0
uvicorn==0.30.6
EOF

# Update main.py
# (Implementation provided below)

# Rebuild
docker compose build ocr-api
docker compose restart ocr-api
```

## Recommendation

**For insightpulseai.net:**

**Start with:** Regular CPU droplet ($24/month)
**OCR Strategy:**
1. Start with Tesseract (free, CPU)
2. If volume increases, switch to Google Vision ($1.50/1000)
3. Only consider GPU if processing >10,000 documents/day

**Cost Comparison:**

| Solution | Fixed Cost | Variable Cost | Break-even |
|----------|------------|---------------|------------|
| CPU + Tesseract | $24/mo | $0 | Always |
| CPU + Google Vision | $24/mo | $1.50/1000 | <384,000 images/mo |
| GPU Droplet | $600/mo | $0 | >384,000 images/mo |

**Conclusion:** GPU droplet only makes sense at **massive scale** (>384k images/month).

## PaddleOCR Implementation (CPU)

If you want better OCR than Tesseract without GPU:

```python
# services/ocr-api/main.py
from fastapi import FastAPI, UploadFile, File
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
import io

app = FastAPI()
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

@app.post("/parse")
async def parse(file: UploadFile = File(...)):
    content = await file.read()
    img = Image.open(io.BytesIO(content))
    img_array = np.array(img)

    result = ocr.ocr(img_array, cls=True)

    # Extract text
    text_lines = []
    for line in result[0]:
        text_lines.append(line[1][0])

    # Parse receipt data
    vendor = text_lines[0] if text_lines else "Unknown"
    amount = extract_amount(text_lines)
    date = extract_date(text_lines)

    return {
        "ok": True,
        "data": {
            "vendor": vendor,
            "amount": amount,
            "currency": "PHP",
            "date": date,
            "raw": "\n".join(text_lines)
        }
    }

def extract_amount(lines):
    import re
    for line in reversed(lines):
        m = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', line)
        if m:
            return float(m.group(1).replace(',', ''))
    return None

def extract_date(lines):
    from dateutil import parser as dtp
    for line in lines:
        try:
            return dtp.parse(line, fuzzy=True).date().isoformat()
        except:
            pass
    return None
```

**Benefits:**
- 2-3x better accuracy than Tesseract
- Still runs on CPU
- No additional cost
- Handles rotated/skewed images

**Drawbacks:**
- 2-3x slower than Tesseract (still <10s)
- Larger Docker image (~500MB vs 100MB)

## Final Recommendation

**For Your Use Case:**
```
Platform: Regular CPU Droplet
RAM: 4GB
Cost: $24/month
OCR: Start with Tesseract → Upgrade to PaddleOCR if needed
External API: Use Google Vision for high-priority documents
GPU: Not needed unless processing >10K documents/day
```

---

**Bottom Line:** Save $576/month by using CPU + external APIs instead of GPU droplet.
