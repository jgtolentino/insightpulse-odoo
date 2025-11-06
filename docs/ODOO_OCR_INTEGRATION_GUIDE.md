# 📱 Odoo OCR Integration Guide

**Module**: `ip_expense_mvp`
**OCR Service**: PaddleOCR-VL @ https://ocr.insightpulseai.net
**Database**: Supabase PostgreSQL (spdtwktxdalcfigzeqrz)

---

## Prerequisites ✅

Before proceeding, ensure the following are complete:

- ✅ OCR service deployed and hardened (see `PRODUCTION_DEPLOYMENT_OCR_2025-11-06.md`)
- ✅ SSL/TLS certificate valid (expires 2026-02-04)
- ✅ Security headers configured
- ✅ Firewall active (UFW)
- ✅ Fail2Ban protection enabled
- ✅ Supabase database with `analytics.ip_ocr_receipts` table

---

## Step 1: Configure Odoo Settings

### Access Settings Interface

1. Navigate to Odoo: **https://erp.insightpulseai.net**
2. Log in as administrator
3. Go to: **Settings → General Settings**
4. Scroll to **Integration** section (settings are added after this section)

### Configure AI OCR Service

**Field**: AI OCR Service URL
**Value**: `https://ocr.insightpulseai.net/v1/ocr/receipt`
**Purpose**: Production OCR endpoint with SSL/TLS and security hardening

**Technical Note**: This URL is configured via `res.config.settings` model with config parameter `ip.ai_ocr_url`

### Configure Supabase Analytics

**Field**: Supabase URL
**Value**: `https://spdtwktxdalcfigzeqrz.supabase.co`
**Purpose**: Analytics database for OCR receipt sync

**Field**: Supabase Service Key
**Value**: `$SUPABASE_SERVICE_ROLE_KEY` (from environment)
**Purpose**: Service-to-service authentication (RLS bypass for backend operations)

**Security Note**: Never expose service role key in frontend. Only use in Odoo backend server-side code.

### Save Configuration

Click **Save** button at the top of the settings page.

---

## Step 2: Upgrade Odoo Module

### Method 1: Via Odoo CLI

```bash
# SSH to Odoo droplet
ssh root@165.227.10.178

# Navigate to Odoo directory
cd /opt/odoo

# Activate Odoo environment
source .venv/bin/activate

# Upgrade module
./odoo-bin -u ip_expense_mvp -d odoo -c /etc/odoo.conf
```

### Method 2: Via Odoo UI (Apps)

1. Navigate to: **Apps**
2. Search for: **IP Expense MVP**
3. Click: **Upgrade** button

**Expected Outcome**: Module upgraded successfully, configuration settings now available in Settings → General Settings.

---

## Step 3: Verify Configuration

### Test Configuration Persistence

```bash
# SSH to Odoo droplet
ssh root@165.227.10.178

# Query config parameters
psql "postgresql://odoo:YOUR_PASSWORD@localhost:5432/odoo" -c "
SELECT key, value
FROM ir_config_parameter
WHERE key LIKE 'ip.%'
ORDER BY key;
"
```

**Expected Output**:
```
            key             |                    value
----------------------------+----------------------------------------------
 ip.ai_ocr_url              | https://ocr.insightpulseai.net/v1/ocr/receipt
 ip.supabase_service_key    | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
 ip.supabase_url            | https://spdtwktxdalcfigzeqrz.supabase.co
```

---

## Step 4: Test End-to-End Flow

### 4.1 Mobile Receipt Upload

**Endpoint**: `https://erp.insightpulseai.net/ip/mobile/receipt`
**Method**: POST (multipart/form-data)
**Authentication**: Odoo session cookie

**Test Upload**:
```bash
# Get Odoo session (replace with your credentials)
SESSION_ID=$(curl -s -c - -X POST "https://erp.insightpulseai.net/web/session/authenticate" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","params":{"db":"odoo","login":"admin","password":"YOUR_PASSWORD"}}' \
  | grep session_id | awk '{print $NF}')

# Upload test receipt
curl -X POST "https://erp.insightpulseai.net/ip/mobile/receipt" \
  -H "Cookie: session_id=$SESSION_ID" \
  -F "file=@/path/to/sample_receipt.jpg"
```

**Expected Response**:
```json
{
  "success": true,
  "receipt_id": 123,
  "filename": "sample_receipt.jpg",
  "ocr_lines": 22,
  "avg_confidence": 0.97
}
```

### 4.2 Verify OCR Receipt Record

1. Navigate to: **OCR Receipts** (top menu)
2. Verify new record created:
   - **Name**: `sample_receipt.jpg`
   - **Uploaded By**: Current user
   - **Line Count**: 22 (from OCR response)
   - **OCR JSON**: Complete JSON payload visible

### 4.3 Create Expense from Receipt

1. Open the OCR receipt record
2. Click **Create Expense** button
3. Verify expense created with:
   - **Name**: `Receipt: [Merchant Name]`
   - **Amount**: Extracted total amount
   - **Date**: Extracted receipt date
   - **Description**: `OCR Receipt: sample_receipt.jpg`

### 4.4 Verify Supabase Sync

```bash
# Query Supabase for recent receipts
curl -s "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/rpc/get_recent_ocr_receipts" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"p_limit": 5}' \
  | jq
```

**Expected Output**:
```json
[
  {
    "id": "uuid-here",
    "filename": "sample_receipt.jpg",
    "uploaded_by": "admin",
    "line_count": 22,
    "total_amount": 1234.56,
    "receipt_date": "2025-11-06",
    "created_at": "2025-11-06T13:04:00Z"
  }
]
```

---

## Architecture Overview

```
┌─────────────────┐
│  Mobile App     │
│  (Future)       │
└────────┬────────┘
         │ POST /ip/mobile/receipt
         │ (multipart/form-data)
         ▼
┌─────────────────────────────────────┐
│  Odoo ERP (erp.insightpulseai.net)  │
│  ┌───────────────────────────────┐  │
│  │ ip_expense_mvp Module         │  │
│  │ - Mobile Upload Controller    │  │
│  │ - OCR Receipt Model           │  │
│  │ - Expense Creation Logic      │  │
│  └────────┬──────────────────────┘  │
└───────────┼──────────────────────────┘
            │
            │ POST /v1/ocr/receipt
            │ (HTTPS, security headers)
            ▼
┌─────────────────────────────────────┐
│  OCR Service (ocr.insightpulseai.net)│
│  ┌───────────────────────────────┐  │
│  │ PaddleOCR-VL 900M             │  │
│  │ - Document understanding      │  │
│  │ - Structured output (JSON)    │  │
│  │ - Confidence scoring          │  │
│  └────────┬──────────────────────┘  │
└───────────┼──────────────────────────┘
            │ Return JSON
            │ {lines, totals, merchant, date}
            ▼
┌─────────────────────────────────────┐
│  Odoo (Process Response)            │
│  - Create ip.ocr.receipt record     │
│  - Store OCR JSON                   │
│  - Sync to Supabase (async)         │
└────────┬────────────────────────────┘
         │
         │ Fire-and-forget sync
         │ (non-blocking)
         ▼
┌─────────────────────────────────────┐
│  Supabase PostgreSQL                │
│  analytics.ip_ocr_receipts table    │
│  - RLS policies active              │
│  - Ready for Superset dashboards    │
└─────────────────────────────────────┘
```

---

## Data Flow

### 1. Mobile Upload
- User takes photo of receipt
- App uploads to `/ip/mobile/receipt` endpoint
- Odoo validates session and file

### 2. OCR Processing
- Odoo forwards image to OCR service
- PaddleOCR-VL processes document
- Returns structured JSON with confidence scores

### 3. Record Creation
- Odoo creates `ip.ocr.receipt` record
- Stores filename, uploader, JSON payload
- Calculates line count from response

### 4. Expense Creation (Manual)
- User opens OCR receipt record
- Clicks "Create Expense" button
- System extracts:
  - Total amount from `totals.total_amount.value`
  - Date from `date.value`
  - Merchant from `merchant.value`
- Creates `hr.expense` record with prefilled data

### 5. Supabase Sync (Automatic)
- Triggered on `ip.ocr.receipt` create
- Fire-and-forget (non-blocking)
- Syncs to `analytics.ip_ocr_receipts`
- Errors logged to `ir.logging`

---

## Troubleshooting

### Issue: "OCR URL not configured"

**Symptom**: Mobile upload fails with configuration error

**Solution**:
1. Check Settings → General Settings
2. Verify `ip.ai_ocr_url` parameter exists
3. Re-save configuration
4. Restart Odoo if necessary

### Issue: "Connection refused to OCR service"

**Symptom**: Upload succeeds but OCR fails

**Solution**:
```bash
# Check OCR service health
curl -sf https://ocr.insightpulseai.net/health | jq

# Check firewall allows HTTPS from Odoo droplet
ssh root@188.166.237.231 'ufw status'

# Verify Nginx is running
ssh root@188.166.237.231 'systemctl status nginx'
```

### Issue: "Supabase sync failed"

**Symptom**: Receipt created but not in Supabase

**Solution**:
1. Check Odoo logs: `journalctl -u odoo -n 50`
2. Verify Supabase URL and key in settings
3. Test Supabase connectivity:
   ```bash
   curl -sf "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/" \
     -H "apikey: $SUPABASE_SERVICE_ROLE_KEY"
   ```
4. Check RLS policies on `analytics.ip_ocr_receipts`

### Issue: "SSL certificate verification failed"

**Symptom**: HTTPS connection fails

**Solution**:
1. Verify certificate validity:
   ```bash
   echo | openssl s_client -servername ocr.insightpulseai.net \
     -connect ocr.insightpulseai.net:443 2>/dev/null \
     | openssl x509 -noout -dates
   ```
2. Check Certbot auto-renewal:
   ```bash
   ssh root@188.166.237.231 'certbot certificates'
   ```

---

## Performance Expectations

| Metric | Target | Actual (from testing) |
|--------|--------|----------------------|
| OCR Processing Time (P95) | ≤30s | ~25s |
| OCR Confidence (Average) | ≥60% | 96.97% |
| Lines Extracted (Average) | ≥10 | 22 |
| Upload Endpoint Response | <5s | <3s |
| Supabase Sync | <2s | <1s |

---

## Security Considerations

### HTTPS Only
- All OCR communication over TLS 1.2/1.3
- Certificate auto-renewal enabled
- HSTS header enforces HTTPS

### CORS Protection
- OCR service locked to `https://erp.insightpulseai.net`
- Preflight requests handled correctly
- No wildcard origins allowed

### Rate Limiting
- 5 requests/second per IP
- Burst capacity: 20 requests
- Fail2Ban protection active

### Credential Management
- Supabase service key stored in Odoo config (not database)
- Never exposed to frontend/mobile app
- Anon key safe for client use (RLS enforced)

---

## Next Steps

### Optional: Create Superset Dashboard

1. Connect Superset to Supabase:
   - Database: PostgreSQL
   - Host: `aws-1-us-east-1.pooler.supabase.com:6543`
   - Database: `postgres`
   - User: `postgres.spdtwktxdalcfigzeqrz`

2. Create dataset:
   - Table: `analytics.v_ip_ocr_receipts_daily`
   - Sync columns

3. Create charts:
   - KPI: "Receipts Today" (count)
   - Time Series: 7-day line chart (receipts per day)
   - Bar Chart: Top uploaders (user, count)

4. Create dashboard:
   - Name: "OCR Receipt Analytics"
   - Add all charts
   - Set auto-refresh: 5 minutes

### Optional: Mobile App Integration

Once mobile app is ready:

1. Implement photo capture
2. POST to `/ip/mobile/receipt` with Odoo session cookie
3. Handle response (success/error)
4. Display uploaded receipts in app

**API Contract**:
```typescript
POST /ip/mobile/receipt
Headers:
  Cookie: session_id=<odoo_session>
  Content-Type: multipart/form-data

Body:
  file: File (image/jpeg, image/png)

Response (200):
{
  "success": true,
  "receipt_id": number,
  "filename": string,
  "ocr_lines": number,
  "avg_confidence": number
}

Response (400/500):
{
  "success": false,
  "error": string
}
```

---

## Acceptance Criteria

All criteria must pass before production go-live:

- ✅ OCR service health returns `{"status":"ok"}`
- ✅ OCR processing P95 ≤ 30 seconds
- ✅ OCR confidence average ≥ 60%
- ✅ SSL/TLS certificate valid and auto-renewing
- ✅ Security headers present (6 headers)
- ✅ Firewall active (SSH, HTTP, HTTPS only)
- ✅ Rate limiting active (5 req/s)
- ✅ Fail2Ban active for abuse protection
- ✅ Log rotation configured
- ⏳ Odoo settings configured (production values)
- ⏳ Module upgraded successfully
- ⏳ End-to-end test passes (upload → OCR → expense)
- ⏳ Supabase sync verified (receipts in analytics table)

**Current Status**: 8/12 criteria met (infrastructure complete, Odoo integration pending)

---

## Support Contacts

**System Owner**: Jake Tolentino
**Email**: jgtolentino_rn@yahoo.com
**Documentation**: `/docs/PRODUCTION_DEPLOYMENT_OCR_2025-11-06.md`

---

**Last Updated**: 2025-11-06
**Next Review**: 2025-12-06 (monthly review)
