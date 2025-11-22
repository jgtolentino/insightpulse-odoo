# InsightPulse OCR Adapter for Odoo

FastAPI adapter service that bridges your existing OCR service with Odoo's expense OCR integration.

## Architecture

```
Odoo Expense Form
    ↓ POST multipart/form-data
https://ocr.insightpulseai.net/api/expense/ocr
    ↓ (This Adapter)
Your Existing OCR Service (PaddleOCR-VL + OpenAI)
    ↓ JSON response
Adapter normalizes → Odoo contract
    ↓
Odoo populates expense fields
```

## Odoo Contract

**Request:**
- Method: `POST`
- URL: `https://ocr.insightpulseai.net/api/expense/ocr`
- Auth: `X-API-Key: your-key` (optional)
- Body: `multipart/form-data` with `file` field

**Response JSON:**
```json
{
  "merchant_name": "Sample Store",
  "invoice_date": "2025-11-20",
  "currency": "PHP",
  "total_amount": 1234.56
}
```

## Quick Start

### 1. Configure Environment

Edit `docker-compose.yml`:

```yaml
environment:
  - UPSTREAM_OCR_URL=http://your-ocr-service:8000/ocr  # Your actual OCR endpoint
  - IPAI_OCR_API_KEY=your-secure-api-key-here           # Generate a strong key
  - OCR_TIMEOUT=60
```

### 2. Customize Response Mapping

Edit `main.py` function `normalize_ocr_response()` to match your OCR service's response format.

**Example mappings:**

```python
# If your OCR returns:
# {"merchant": "Store", "date": "2025-11-20", "total": 1234.56}

def normalize_ocr_response(raw: dict) -> dict:
    return {
        "merchant_name": raw.get("merchant", "Unknown"),
        "invoice_date": raw.get("date"),
        "currency": "PHP",
        "total_amount": float(raw.get("total", 0.0))
    }
```

### 3. Deploy on OCR Droplet

```bash
# On ocr.insightpulseai.net (188.166.237.231)
cd /opt
git clone <your-repo> ocr-adapter
cd ocr-adapter

# Build and start
docker-compose up -d --build

# Check logs
docker logs -f ocr-adapter

# Verify health
curl http://localhost:8001/health
```

### 4. Configure Nginx

```bash
# Copy nginx config
sudo cp nginx-site.conf /etc/nginx/sites-available/ocr-adapter.conf

# Enable site
sudo ln -s /etc/nginx/sites-available/ocr-adapter.conf /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 5. Test End-to-End

```bash
# From any machine
curl -v -F "file=@receipt.jpg" \
  -H "X-API-Key: your-api-key" \
  https://ocr.insightpulseai.net/api/expense/ocr

# Expected response:
# {
#   "merchant_name": "Sample Store",
#   "invoice_date": "2025-11-20",
#   "currency": "PHP",
#   "total_amount": 1234.56
# }
```

### 6. Configure Odoo

In Odoo web UI:

1. Navigate to: **Expenses → Configuration → InsightPulse OCR**
2. Enable: **☑ Enable InsightPulse OCR**
3. Set **OCR API URL**: `https://ocr.insightpulseai.net/api/expense/ocr`
4. Set **API Key**: `your-api-key` (same as in docker-compose.yml)
5. Click **Save**

### 7. Test in Odoo

1. Create new expense: **Expenses → My Expenses → Create**
2. Attach receipt image
3. Click **"Scan with InsightPulse OCR"** button
4. Watch fields populate:
   - `Name` ← merchant_name
   - `Date` ← invoice_date
   - `Total Amount` ← total_amount

## Response Normalization Patterns

### Pattern 1: Direct Fields (simplest)

```python
# Your OCR returns:
{"merchant": "Store", "date": "2025-11-20", "total": 123.45}

# Normalize:
{
    "merchant_name": raw["merchant"],
    "invoice_date": raw["date"],
    "currency": "PHP",
    "total_amount": float(raw["total"])
}
```

### Pattern 2: Nested Extraction

```python
# Your OCR returns:
{"extracted": {"merchant": "Store", "date": "2025-11-20", "total": 123.45}}

# Normalize:
ext = raw["extracted"]
{
    "merchant_name": ext["merchant"],
    "invoice_date": ext["date"],
    "currency": "PHP",
    "total_amount": float(ext["total"])
}
```

### Pattern 3: Azure Document Intelligence

```python
# Your OCR returns:
{"fields": {"MerchantName": {"value": "Store"}, "Total": {"value": 123.45}}}

# Normalize:
fields = raw["fields"]
{
    "merchant_name": fields["MerchantName"]["value"],
    "invoice_date": fields.get("TransactionDate", {}).get("value"),
    "currency": "PHP",
    "total_amount": float(fields["Total"]["value"])
}
```

## Troubleshooting

### Check Adapter Logs

```bash
docker logs -f ocr-adapter
```

### Test Upstream OCR

```bash
# From ocr-adapter container
docker exec ocr-adapter curl -F "file=@/tmp/test.jpg" http://localhost:8000/ocr
```

### Test Adapter Directly

```bash
curl -X POST http://localhost:8001/api/expense/ocr \
  -F "file=@receipt.jpg" \
  -H "X-API-Key: your-key"
```

### Check Nginx Proxy

```bash
sudo tail -f /var/log/nginx/ocr-adapter.error.log
```

### Odoo Logs

```bash
# On erp.insightpulseai.net
docker logs -f odoo-odoo-1 | grep -i "InsightPulse OCR"
```

## Security Checklist

- [ ] Change `IPAI_OCR_API_KEY` from default
- [ ] Configure firewall: only allow port 443 (HTTPS)
- [ ] Set up SSL with Let's Encrypt (Certbot)
- [ ] Review nginx security headers
- [ ] Monitor adapter logs for suspicious activity
- [ ] Rotate API keys regularly

## Production Deployment

```bash
# 1. Clone repository
cd /opt
git clone <repo> ocr-adapter
cd ocr-adapter

# 2. Generate secure API key
openssl rand -hex 32

# 3. Update docker-compose.yml with:
#    - UPSTREAM_OCR_URL (your actual OCR service)
#    - IPAI_OCR_API_KEY (generated key above)

# 4. Build and deploy
docker-compose up -d --build

# 5. Configure nginx
sudo cp nginx-site.conf /etc/nginx/sites-available/ocr-adapter.conf
sudo ln -s /etc/nginx/sites-available/ocr-adapter.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 6. Verify SSL certificate exists or generate with Certbot
sudo certbot --nginx -d ocr.insightpulseai.net

# 7. Test end-to-end
curl -F "file=@sample-receipt.jpg" \
  -H "X-API-Key: your-generated-key" \
  https://ocr.insightpulseai.net/api/expense/ocr

# 8. Configure Odoo settings with same API key
```

## Monitoring

### Health Check

```bash
# Adapter health
curl https://ocr.insightpulseai.net/health

# Expected:
# {
#   "status": "ok",
#   "service": "ocr-adapter",
#   "upstream": "http://...",
#   "timestamp": "2025-11-20T10:00:00"
# }
```

### Metrics

Add Prometheus metrics endpoint:

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Log Aggregation

Configure docker logging driver to send to your log aggregation service.

## License

AGPL-3.0 (matches Odoo CE licensing)
