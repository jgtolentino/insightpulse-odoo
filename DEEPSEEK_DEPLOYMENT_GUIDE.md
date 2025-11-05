# DeepSeek Infrastructure Deployment Guide

**Last Updated:** 2025-11-04
**Status:** Ready for Execution
**Estimated Time:** 30-45 minutes
**Cost Impact:** +$50-100/month for GPU droplet

---

## Overview

This guide implements the approved two-part DeepSeek deployment plan:

1. **DeepSeek-R1 7B LLM** - New GPU droplet at `llm.insightpulseai.net`
2. **DeepSeek-OCR** - Experimental endpoint at `ocr.insightpulseai.net/dsocr/`

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   InsightPulse AI Stack                     │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │ GPU Droplet  │ │ OCR Droplet  │ │ ERP Droplet  │
        │ (NEW)        │ │ (EXISTING)   │ │ (EXISTING)   │
        ├──────────────┤ ├──────────────┤ ├──────────────┤
        │ DeepSeek-R1  │ │ PaddleOCR    │ │ Odoo ERP     │
        │ 7B LLM       │ │ DeepSeek-OCR │ │ @ipai-bot    │
        │              │ │              │ │              │
        │ Port: 8000   │ │ Ports: 8000, │ │ Ports: 8069, │
        │              │ │ 7010         │ │ 8072         │
        ├──────────────┤ ├──────────────┤ ├──────────────┤
        │ llm.         │ │ ocr.         │ │ erp.         │
        │ insightpulse │ │ insightpulse │ │ insightpulse │
        │ ai.net       │ │ ai.net       │ │ ai.net       │
        └──────────────┘ └──────────────┘ └──────────────┘
             │                 │                  │
             │                 │                  │
             ▼                 ▼                  ▼
        /v1/models       /paddle/         /web/login
        /v1/chat/        /dsocr/
        completions      (NEW)
```

## Deployment Scripts

### 1. `scripts/deploy-deepseek-llm.sh` (6.5KB)

**Purpose:** Create new GPU droplet with DeepSeek-R1 7B LLM

**What It Does:**
- Creates GPU droplet using DigitalOcean Marketplace image
- Configures Nginx reverse proxy for port 8000
- Obtains Let's Encrypt TLS certificate
- Configures UFW firewall (SSH, HTTP, HTTPS only)
- Sets up automatic security updates
- Provides DNS configuration guidance

**Prerequisites:**
- `doctl` CLI authenticated with `$DO_ACCESS_TOKEN`
- Squarespace DNS access for adding `llm` A record

**Usage:**
```bash
# Execute deployment
./scripts/deploy-deepseek-llm.sh

# Script will:
# 1. Create GPU droplet in SGP1
# 2. Wait for SSH ready (30s)
# 3. Prompt for DNS configuration
# 4. Configure Nginx + TLS
# 5. Setup firewall
# 6. Verify service
```

**Expected Output:**
```
✅ DeepSeek-R1 7B LLM Deployment Complete!

Domain: https://llm.insightpulseai.net
Droplet ID: 123456789
IP Address: xxx.xxx.xxx.xxx
Region: sgp1
```

---

### 2. `scripts/deploy-deepseek-ocr.sh` (9.2KB)

**Purpose:** Add DeepSeek-OCR service to existing OCR droplet

**What It Does:**
- Creates Python venv at `~/dsocr` on OCR droplet
- Deploys FastAPI placeholder service (port 7010)
- Creates systemd service for auto-start
- Updates Nginx configuration for `/dsocr/` route
- Provides path for actual model integration

**Prerequisites:**
- SSH access to `root@188.166.237.231` (OCR droplet)
- OCR droplet already has Nginx and PaddleOCR running

**Usage:**
```bash
# Execute deployment
./scripts/deploy-deepseek-ocr.sh

# Script will:
# 1. Setup Python environment
# 2. Create FastAPI service
# 3. Configure systemd
# 4. Update Nginx routes
# 5. Verify service
```

**Expected Output:**
```
✅ DeepSeek-OCR Service Deployment Complete!

Domain: https://ocr.insightpulseai.net/dsocr/
Local Port: 7010
Service: deepseek-ocr.service
Status: Placeholder (ready for model integration)
```

---

### 3. `scripts/health-check-all-services.sh` (8.8KB)

**Purpose:** Comprehensive validation of all InsightPulse services

**What It Does:**
- DNS resolution checks for all 6 subdomains
- HTTPS connectivity validation
- TLS certificate verification
- Service-specific endpoint tests
- Droplet SSH connectivity
- Supabase database connection
- Color-coded output with success rate

**Prerequisites:**
- `dig`, `curl`, `openssl`, `jq`, `psql` installed
- SSH access to both droplets
- `$POSTGRES_URL` environment variable (optional)

**Usage:**
```bash
# Execute comprehensive health check
./scripts/health-check-all-services.sh

# Exit codes:
# 0 - All systems operational
# 1 - Critical issues detected
```

**Expected Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Health Check Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Checks: 27
✅ Passed: 25
❌ Failed: 0
⚠️ Warnings: 2

Success Rate: 92%
```

---

## Deployment Sequence

### Phase 1: Deploy DeepSeek-R1 LLM (30 minutes)

1. **Authenticate with DigitalOcean:**
   ```bash
   export DO_ACCESS_TOKEN="your_token_here"
   doctl auth init --access-token $DO_ACCESS_TOKEN
   ```

2. **Run LLM deployment script:**
   ```bash
   ./scripts/deploy-deepseek-llm.sh
   ```

3. **Add DNS record in Squarespace:**
   ```
   Host: llm
   Type: A
   Data: <GPU-droplet-IP from script output>
   TTL: 1 hour
   ```

4. **Wait for DNS propagation (5 minutes):**
   ```bash
   dig +short llm.insightpulseai.net A
   ```

5. **Verify LLM service:**
   ```bash
   # Test models endpoint
   curl -s https://llm.insightpulseai.net/v1/models | jq

   # Test chat completion
   curl -s https://llm.insightpulseai.net/v1/chat/completions \
     -H 'Content-Type: application/json' \
     -d '{"model": "deepseek-r1-distill-qwen-7b", "messages": [{"role": "user", "content": "Hello"}]}' | jq
   ```

### Phase 2: Deploy DeepSeek-OCR Service (15 minutes)

1. **Run OCR deployment script:**
   ```bash
   ./scripts/deploy-deepseek-ocr.sh
   ```

2. **Verify DeepSeek-OCR service:**
   ```bash
   # Health check
   curl -s http://ocr.insightpulseai.net/dsocr/health | jq

   # List models
   curl -s http://ocr.insightpulseai.net/dsocr/models | jq

   # Test OCR (placeholder)
   curl -s -F file=@sample.jpg http://ocr.insightpulseai.net/dsocr/ocr | jq
   ```

3. **Verify systemd service:**
   ```bash
   ssh root@188.166.237.231 'systemctl status deepseek-ocr.service'
   ```

### Phase 3: Comprehensive Validation (5 minutes)

1. **Run health check script:**
   ```bash
   ./scripts/health-check-all-services.sh
   ```

2. **Verify all 6 subdomains:**
   - ✅ `erp.insightpulseai.net` - Odoo ERP
   - ✅ `agent.insightpulseai.net` - AI Agent API (after DNS fix)
   - ✅ `mcp.insightpulseai.net` - Pulse Hub Web UI
   - ✅ `ocr.insightpulseai.net` - OCR services
   - ✅ `superset.insightpulseai.net` - BI Dashboard
   - ✅ `llm.insightpulseai.net` - DeepSeek-R1 LLM (NEW)

---

## Service Endpoints

### DeepSeek-R1 7B LLM
```
Base URL: https://llm.insightpulseai.net
Authentication: None (internal use only, firewall protected)

GET /v1/models
  Returns: Available model list

POST /v1/chat/completions
  Body: {"model": "deepseek-r1-distill-qwen-7b", "messages": [...]}
  Returns: Chat completion response
```

### DeepSeek-OCR
```
Base URL: https://ocr.insightpulseai.net/dsocr
Authentication: None (internal use only, firewall protected)

GET /health
  Returns: Service health status

GET /models
  Returns: Available OCR models

POST /ocr
  Body: multipart/form-data with file
  Returns: {"text": "...", "confidence": 0.99, "fields": {...}, "metadata": {...}}
```

---

## Integration with Existing Services

### Odoo ERP Integration

**@ipai-bot Commands:**
```
@ipai-bot analyze receipt using deepseek-ocr
@ipai-bot summarize document with deepseek-r1
```

**Implementation:** Update `ipai_agent` addon to support DeepSeek endpoints:
```python
# addons/custom/ipai_agent/models/ocr_integration.py

def extract_text_deepseek(self, file_data):
    """Extract text using DeepSeek-OCR endpoint"""
    url = "http://ocr.insightpulseai.net/dsocr/ocr"
    response = requests.post(url, files={'file': file_data})
    return response.json()

def query_llm_deepseek(self, prompt):
    """Query DeepSeek-R1 7B LLM"""
    url = "http://llm.insightpulseai.net/v1/chat/completions"
    payload = {
        "model": "deepseek-r1-distill-qwen-7b",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, json=payload)
    return response.json()
```

### Pulse Hub Web UI Integration

**Update Skill Hub:** Add DeepSeek endpoints to one-click deployment options

```javascript
// services/mcp-hub/src/components/ServiceGrid.tsx

const services = [
  // ... existing services
  {
    name: "DeepSeek-R1 LLM",
    endpoint: "https://llm.insightpulseai.net/v1/models",
    status: "operational"
  },
  {
    name: "DeepSeek-OCR",
    endpoint: "https://ocr.insightpulseai.net/dsocr/health",
    status: "experimental"
  }
]
```

---

## Cost Analysis

### Current Infrastructure ($68/month)
- ocr-service-droplet: $24/month
- ipai-odoo-erp: $24/month
- superset App Platform: $5/month
- mcp App Platform: $5/month
- odoobo-backup volume: $10/month

### After DeepSeek Deployment ($118-168/month)
- **GPU droplet:** $50-100/month (depending on GPU tier)
- **Total:** $118-168/month (+73-147% increase)

### Cost Optimization Options
1. **Use CPU-only droplet for LLM:** $24/month (slower inference)
2. **Share GPU droplet with OCR:** Migrate PaddleOCR to GPU droplet
3. **Use DeepSeek API:** Pay-per-use instead of dedicated droplet

---

## Rollback Procedures

### Rollback LLM Deployment
```bash
# Destroy GPU droplet
doctl compute droplet delete <droplet-id> --force

# Remove DNS record
# Squarespace → DNS Settings → Delete llm A record
```

### Rollback OCR Deployment
```bash
ssh root@188.166.237.231 <<'ROLLBACK'
# Stop and disable service
systemctl stop deepseek-ocr.service
systemctl disable deepseek-ocr.service

# Restore Nginx config from backup
cp /etc/nginx/sites-available/ocr.insightpulseai.net.conf.backup \
   /etc/nginx/sites-available/ocr.insightpulseai.net.conf
nginx -t && systemctl reload nginx

# Remove service files
rm /etc/systemd/system/deepseek-ocr.service
rm -rf ~/dsocr

systemctl daemon-reload
echo "✅ DeepSeek-OCR rollback complete"
ROLLBACK
```

---

## Troubleshooting

### Issue: GPU Droplet Creation Failed
**Symptoms:** `doctl` returns error creating droplet

**Solutions:**
1. Check DO account has GPU quota: `doctl compute quota list`
2. Try different region: Change `REGION="sgp1"` to `"nyc3"` or `"sfo2"`
3. Verify Marketplace image slug: `doctl compute image list-marketplace`

### Issue: TLS Certificate Failed
**Symptoms:** certbot returns error obtaining certificate

**Solutions:**
1. Verify DNS propagation: `dig +short llm.insightpulseai.net A`
2. Check port 80 accessible: `curl -I http://llm.insightpulseai.net`
3. Check certbot logs: `sudo tail -f /var/log/letsencrypt/letsencrypt.log`
4. Retry with debug: `certbot --nginx -d llm.insightpulseai.net --debug`

### Issue: DeepSeek-OCR Service Not Starting
**Symptoms:** `systemctl status deepseek-ocr.service` shows failed

**Solutions:**
1. Check service logs: `journalctl -u deepseek-ocr.service -n 50`
2. Verify Python dependencies: `source ~/dsocr/venv/bin/activate && pip list`
3. Test manual start: `cd ~/dsocr && source venv/bin/activate && python main.py`
4. Check port availability: `netstat -tuln | grep 7010`

### Issue: Nginx Route Not Working
**Symptoms:** 404 or 502 error on `/dsocr/` route

**Solutions:**
1. Check service listening: `curl http://localhost:7010/health`
2. Test Nginx config: `sudo nginx -t`
3. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
4. Verify rewrite rule: `sudo cat /etc/nginx/sites-available/ocr.insightpulseai.net.conf`

---

## Next Steps After Deployment

### 1. Integrate Actual DeepSeek-OCR Model (Priority: High)

**Current State:** Placeholder FastAPI service returns mock OCR results

**Implementation Path:**
```bash
ssh root@188.166.237.231
cd ~/dsocr

# Install DeepSeek-OCR dependencies
source venv/bin/activate
pip install transformers torch torchvision

# Download model (7GB)
python -c "from transformers import AutoModel; AutoModel.from_pretrained('deepseek-ai/deepseek-ocr-7b')"

# Update main.py to use actual model
# Replace placeholder in @app.post("/ocr") with real inference

# Restart service
systemctl restart deepseek-ocr.service
```

**Reference:** https://github.com/deepseek-ai/DeepSeek-OCR

### 2. Update Pulse Hub Web UI (Priority: Medium)

Add DeepSeek endpoints to one-click deployment dashboard:
- Deploy button for LLM endpoint
- Deploy button for OCR endpoint
- Real-time status monitoring
- Cost calculator for GPU droplet

### 3. Add Monitoring & Alerts (Priority: Medium)

```bash
# Setup Prometheus metrics scraping
# Setup Grafana dashboards for GPU utilization
# Configure alerting for service downtime
```

### 4. Performance Testing (Priority: Low)

```bash
# Benchmark LLM inference speed
# Compare DeepSeek-OCR vs PaddleOCR accuracy
# Measure cost-per-request for both services
```

---

## Validation Checklist

After completing deployment, verify:

- [ ] GPU droplet created successfully in SGP1
- [ ] DNS record `llm.insightpulseai.net` resolves to GPU droplet IP
- [ ] HTTPS certificate valid for `llm.insightpulseai.net`
- [ ] `/v1/models` endpoint returns DeepSeek-R1 model
- [ ] Chat completion endpoint responds correctly
- [ ] DeepSeek-OCR service running on OCR droplet
- [ ] `/dsocr/health` endpoint returns `{"status":"ok"}`
- [ ] Nginx routes both `/paddle/` and `/dsocr/` correctly
- [ ] Firewall configured (SSH, HTTP, HTTPS only)
- [ ] Systemd services enabled for auto-start
- [ ] Health check script shows 100% success rate

---

## References

- **Scripts:**
  - `scripts/deploy-deepseek-llm.sh`
  - `scripts/deploy-deepseek-ocr.sh`
  - `scripts/health-check-all-services.sh`

- **Documentation:**
  - `DNS_MAPPING.md` - DNS configuration
  - `DIGITALOCEAN_INVENTORY.md` - Infrastructure inventory
  - `DEEPSEEK_OCR_DEPLOYMENT.md` - OCR service details
  - `AUTOMATION_MODES.md` - 4-mode architecture

- **External:**
  - DeepSeek-R1 Model: https://github.com/deepseek-ai/DeepSeek-R1
  - DeepSeek-OCR Model: https://github.com/deepseek-ai/DeepSeek-OCR
  - DigitalOcean GPU Droplets: https://www.digitalocean.com/products/gpu-droplets

---

**Maintained by:** Jake Tolentino
**Email:** jgtolentino_rn@yahoo.com
**Last Tested:** 2025-11-04
**Status:** Ready for Production Deployment
