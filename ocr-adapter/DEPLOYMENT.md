# InsightPulse OCR Adapter - Production Deployment Guide

## Overview

This guide deploys the OCR adapter on `ocr.insightpulseai.net` (188.166.237.231) to bridge your existing OCR service with Odoo's expense integration.

**Current State:**
- ✅ Odoo modules installed (`ipai_ce_cleaner`, `ipai_ocr_expense`)
- ✅ OCR service running at `ocr.insightpulseai.net` with SSL
- ✅ Health endpoint working: `/health`
- ⏳ Need to deploy adapter at `/api/expense/ocr`

---

## Pre-Deployment Checklist

### 1. Identify Your Existing OCR Service

First, find where your current OCR service is running:

```bash
# SSH to OCR droplet
ssh root@ocr.insightpulseai.net

# Check running services
docker ps | grep -E "ocr|paddle"
# OR
ps aux | grep -E "python|fastapi|uvicorn" | grep -v grep

# Check listening ports
sudo netstat -tulpn | grep LISTEN
# OR
sudo ss -tulpn | grep LISTEN
```

**Document:**
- Service endpoint: `http://localhost:XXXX/path`
- Response format: What JSON structure does it return?

### 2. Update Adapter Configuration

Edit `docker-compose.yml`:

```yaml
environment:
  # Point to your existing OCR service
  - UPSTREAM_OCR_URL=http://localhost:8000/ocr  # ← Update this

  # Generate secure API key
  - IPAI_OCR_API_KEY=CHANGE_ME_TO_SECURE_KEY    # ← Generate new key

  # Adjust timeout if needed
  - OCR_TIMEOUT=60
```

**Generate secure API key:**
```bash
openssl rand -hex 32
```

### 3. Customize Response Mapping

Edit `main.py` function `normalize_ocr_response()` to match YOUR OCR service's response.

**Example: If your OCR returns:**
```json
{
  "merchant": "Sample Store",
  "date": "2025-11-20",
  "total": 1234.56,
  "currency": "PHP"
}
```

**Update normalize_ocr_response():**
```python
def normalize_ocr_response(raw: dict) -> dict:
    return {
        "merchant_name": raw.get("merchant", "Unknown Merchant"),
        "invoice_date": raw.get("date"),
        "currency": raw.get("currency", "PHP"),
        "total_amount": float(raw.get("total", 0.0))
    }
```

---

## Deployment Steps

### Step 1: Transfer Files to OCR Droplet

```bash
# From local machine
cd /Users/tbwa/odoo-ce
rsync -avz --delete ocr-adapter/ root@ocr.insightpulseai.net:/opt/ocr-adapter/
```

### Step 2: Deploy Adapter Container

```bash
# SSH to OCR droplet
ssh root@ocr.insightpulseai.net

# Navigate to deployment directory
cd /opt/ocr-adapter

# Review and update configuration
nano docker-compose.yml
# Update UPSTREAM_OCR_URL and IPAI_OCR_API_KEY

# Build and start adapter
docker-compose up -d --build

# Check logs
docker logs -f ocr-adapter

# Verify health check
curl http://localhost:8001/health
```

**Expected health response:**
```json
{
  "status": "ok",
  "service": "ocr-adapter",
  "upstream": "http://localhost:8000/ocr",
  "timestamp": "2025-11-20T10:00:00"
}
```

### Step 3: Configure Nginx Reverse Proxy

```bash
# Copy nginx configuration
sudo cp /opt/ocr-adapter/nginx-site.conf /etc/nginx/sites-available/ocr-adapter.conf

# Review and adjust if needed
sudo nano /etc/nginx/sites-available/ocr-adapter.conf

# Enable site
sudo ln -s /etc/nginx/sites-available/ocr-adapter.conf /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# If SSL certificates exist, reload nginx
sudo systemctl reload nginx
```

### Step 4: SSL Certificate Setup (if not already configured)

```bash
# Install Certbot if not present
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d ocr.insightpulseai.net

# Follow prompts to complete setup
# Certbot will automatically configure nginx for SSL
```

### Step 5: Test End-to-End

```bash
# Test adapter directly (local)
curl -X POST http://localhost:8001/api/expense/ocr \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@sample-receipt.jpg"

# Test through nginx (SSL)
curl -X POST https://ocr.insightpulseai.net/api/expense/ocr \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@sample-receipt.jpg"

# Expected response:
# {
#   "merchant_name": "Sample Store",
#   "invoice_date": "2025-11-20",
#   "currency": "PHP",
#   "total_amount": 1234.56
# }
```

**Use test script:**
```bash
cd /opt/ocr-adapter
./test-ocr.sh sample-receipt.jpg
```

---

## Odoo Configuration

### Step 1: Enable OCR in Odoo Settings

1. Login to Odoo: `https://erp.insightpulseai.net`
2. Navigate to: **Expenses → Configuration → InsightPulse OCR**
3. Configure:
   - ☑ **Enable InsightPulse OCR**
   - **OCR API URL**: `https://ocr.insightpulseai.net/api/expense/ocr`
   - **API Key**: `YOUR_SECURE_API_KEY` (same as in docker-compose.yml)
4. Click **Save**

### Step 2: Test in Odoo

1. Go to **Expenses → My Expenses → Create**
2. Fill in basic details (Employee, etc.)
3. Click **Attachments** icon (📎)
4. Upload a receipt image (JPG, PNG)
5. Click **"Scan with InsightPulse OCR"** button in header
6. Watch the magic:
   - `ocr_status` changes: none → pending → done
   - Fields auto-populate:
     - **Description** ← merchant_name
     - **Date** ← invoice_date
     - **Total Amount** ← total_amount

### Step 3: Monitor Logs

```bash
# Adapter logs
ssh root@ocr.insightpulseai.net "docker logs -f ocr-adapter"

# Odoo logs (from ERP droplet)
ssh root@erp.insightpulseai.net "docker logs -f odoo-odoo-1 | grep -i 'InsightPulse OCR'"

# Nginx access logs
ssh root@ocr.insightpulseai.net "sudo tail -f /var/log/nginx/ocr-adapter.access.log"
```

---

## Troubleshooting

### Issue: "Could not connect to OCR service"

**Symptoms:**
- Odoo shows error: "OCR failed: Could not connect to OCR service"
- Adapter logs: `Upstream OCR connection error`

**Solution:**
1. Verify `UPSTREAM_OCR_URL` in docker-compose.yml points to correct service
2. Check if upstream OCR service is running:
   ```bash
   docker ps | grep ocr
   curl http://localhost:8000/health  # Adjust port
   ```
3. Test connectivity from adapter container:
   ```bash
   docker exec ocr-adapter curl http://localhost:8000/ocr
   ```

### Issue: "Invalid API key"

**Symptoms:**
- Odoo shows error: "OCR failed: 401"
- Adapter logs: `Invalid API key attempt`

**Solution:**
1. Verify API key in Odoo settings matches docker-compose.yml:
   ```bash
   docker exec ocr-adapter printenv | grep IPAI_OCR_API_KEY
   ```
2. Update Odoo settings if mismatch
3. Restart adapter if key was changed:
   ```bash
   docker-compose restart ocr-adapter
   ```

### Issue: "Upstream OCR service error: 502"

**Symptoms:**
- Adapter logs: `Upstream OCR HTTP error: 502`
- Upstream service might be down or returning errors

**Solution:**
1. Check upstream service logs
2. Verify upstream service endpoint responds:
   ```bash
   curl -F "file=@test.jpg" http://localhost:8000/ocr
   ```
3. Check docker network connectivity:
   ```bash
   docker network inspect bridge
   ```

### Issue: Fields not populating in Odoo

**Symptoms:**
- OCR completes successfully (status → done)
- But fields remain empty

**Solution:**
1. Check adapter response structure matches Odoo contract:
   ```bash
   curl -F "file=@receipt.jpg" \
     -H "X-API-Key: KEY" \
     https://ocr.insightpulseai.net/api/expense/ocr | jq
   ```
2. Verify response includes required fields:
   - `merchant_name`
   - `invoice_date`
   - `total_amount`
3. Check `normalize_ocr_response()` function maps your OCR response correctly
4. Review Odoo logs for mapping errors:
   ```bash
   docker logs odoo-odoo-1 | grep -i "ocr" | tail -50
   ```

---

## Security Hardening

### 1. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Verify rules
sudo ufw status
```

### 2. API Key Rotation

```bash
# Generate new key
NEW_KEY=$(openssl rand -hex 32)

# Update docker-compose.yml
nano /opt/ocr-adapter/docker-compose.yml
# Change IPAI_OCR_API_KEY=...

# Restart adapter
cd /opt/ocr-adapter
docker-compose restart ocr-adapter

# Update Odoo settings immediately
# Otherwise OCR will fail with 401 errors
```

### 3. Rate Limiting (Nginx)

Add to nginx configuration:

```nginx
# Limit requests to 10 per minute per IP
limit_req_zone $binary_remote_addr zone=ocr_limit:10m rate=10r/m;

server {
    ...
    location /api/expense/ocr {
        limit_req zone=ocr_limit burst=5 nodelay;
        proxy_pass http://ocr_adapter;
        ...
    }
}
```

### 4. Log Monitoring

Set up log rotation:

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/ocr-adapter

# Add:
/var/log/nginx/ocr-adapter.*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Adapter health
curl https://ocr.insightpulseai.net/health

# SSL certificate expiry
echo | openssl s_client -connect ocr.insightpulseai.net:443 2>/dev/null | \
  openssl x509 -noout -dates
```

### Automated Monitoring Script

Create `/opt/ocr-adapter/monitor.sh`:

```bash
#!/bin/bash
HEALTH_URL="https://ocr.insightpulseai.net/health"
ALERT_EMAIL="admin@insightpulseai.net"

if ! curl -sf "$HEALTH_URL" > /dev/null; then
    echo "OCR Adapter health check failed!" | \
      mail -s "ALERT: OCR Service Down" "$ALERT_EMAIL"
fi
```

Add to crontab:
```bash
# Check every 5 minutes
*/5 * * * * /opt/ocr-adapter/monitor.sh
```

### Performance Metrics

Add Prometheus metrics (optional):

```python
# In main.py
from prometheus_fastapi_instrumentator import Instrumentator

@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app)
```

Metrics available at: `https://ocr.insightpulseai.net/metrics`

---

## Rollback Procedure

If deployment fails, rollback to service-less state:

```bash
# Stop adapter
cd /opt/ocr-adapter
docker-compose down

# Disable nginx site
sudo rm /etc/nginx/sites-enabled/ocr-adapter.conf
sudo nginx -t && sudo systemctl reload nginx

# Disable OCR in Odoo
# Login → Expenses → Configuration → InsightPulse OCR
# Uncheck "Enable InsightPulse OCR" → Save
```

---

## Success Criteria

Deployment is successful when:

- [ ] Health check responds: `curl https://ocr.insightpulseai.net/health`
- [ ] OCR endpoint accessible: `curl -F "file=@receipt.jpg" -H "X-API-Key: KEY" https://ocr.insightpulseai.net/api/expense/ocr`
- [ ] Response matches Odoo contract (merchant_name, invoice_date, total_amount)
- [ ] SSL certificate valid and not expired
- [ ] Odoo settings configured with correct URL and API key
- [ ] Test expense in Odoo successfully scans receipt and populates fields
- [ ] Logs show no errors during OCR processing

---

## Support Contacts

- **Adapter Issues**: Check logs at `/opt/ocr-adapter/`
- **Odoo Issues**: Check logs on `erp.insightpulseai.net`
- **Nginx Issues**: Check `/var/log/nginx/ocr-adapter.*.log`

## Next Steps After Deployment

1. **Monitor for 24 hours** - Watch logs and check health endpoint regularly
2. **Test with real receipts** - Create 5-10 test expenses with various receipt types
3. **Document edge cases** - Note any receipt formats that fail OCR
4. **Optimize normalization** - Adjust `normalize_ocr_response()` based on real data
5. **Set up monitoring** - Configure automated health checks and alerts
6. **Plan for scale** - Monitor response times and adjust adapter workers if needed
