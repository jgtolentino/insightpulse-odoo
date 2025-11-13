# Travel & Expense OCR Integration - COMPLETE

**Date**: 2025-11-13
**Status**: ✅ Production Ready
**Infrastructure**: erp.insightpulseai.net (159.223.75.148)

---

## What Was Deployed

### Phase 1: T&E Configuration ✅
**Expense Settings Configured**:
- Email domain: `insightpulseai.com`
- Email-to-expense: `expenses@insightpulseai.com` (ready to configure)
- Default journal: **EXP - Expense (Purchase)** (ID: 8)
- Outstanding account: **Employee Advances (120500)** (ID: 52)
- Payment methods: All payment methods allowed

**T&E Products** (12 categories):
- Airfare
- Lodging
- Meals
- Ground Transport
- Car Rental
- Fuel
- Parking
- Tolls
- Communication
- Supplies
- Entertainment
- Other Expenses

**Accounts Created**:
- 120500 - Employee Advances (Asset - Current)
- 210500 - Company Credit Cards (Liability - Current)

**Journals Created**:
- EXP - Expenses (Purchase Journal)
- ADV - Employee Advances (Cash Journal)
- CARD - Company Cards (Bank Journal)

### Phase 2: Infrastructure Hardening ✅
**Caddy TLS** (HTTPS with Let's Encrypt):
- Domain: `https://erp.insightpulseai.net/`
- Security headers: HSTS, X-Content-Type-Options, X-Frame-Options, XSS-Protection
- Large file uploads: Max 25MB (for receipt images)
- Health endpoint: `/_health`

**PostgreSQL Backups**:
- Schedule: Daily at 04:15 UTC
- Retention: 14 days
- Format: Custom (pg_dump -Fc)
- Location: `/var/backups/pg/`
- Service: `pg-backup.timer` (systemd)

**Health Monitoring**:
- Frequency: Every 5 minutes
- Endpoints checked: HTTPS + localhost:8069
- Log: `/var/log/stack-health.log`
- Service: `stack-health.timer` (systemd)

**UFW Firewall**:
- Allowed: 22/tcp (SSH), 80/tcp (HTTP), 443/tcp (HTTPS)
- Default: Deny incoming, Allow outgoing
- Status: Active

### Phase 3: OCR Bridge Module ✅
**Module**: `ipai_ocr_bridge` v1.0.0
**Location**: `/mnt/extra-addons/insightpulse/ipai_ocr_bridge`

**Components**:
- **Webhook Endpoint**: `POST /ipai/ocr/inbound`
- **HMAC Signature Validation**: X-IPAI-Signature header
- **Automatic Expense Creation**: Maps OCR JSON to `hr.expense` records
- **Attachment Support**: Base64 image attachments
- **Product Matching**: Fuzzy match OCR categories to T&E products
- **Employee Matching**: Work email lookup with fallback

**Configuration Parameters**:
```bash
ipai_ocr.api_base         = https://ocr.insightpulseai.net
ipai_ocr.api_token        = CHANGE_ME_API_TOKEN
ipai_ocr.webhook_secret   = CHANGE_ME_WEBHOOK_SECRET
```

---

## How It Works

### OCR Service → Odoo Flow

1. **OCR Service** processes receipt (at `https://ocr.insightpulseai.net`)
2. **Webhook POST** to `https://erp.insightpulseai.net/ipai/ocr/inbound`:
   ```json
   {
     "source_id": "rec_uuid",
     "total": 245.70,
     "currency": "USD",
     "date": "2025-11-13",
     "vendor": "Hilton",
     "category": "Lodging",
     "description": "Hilton Boston 1 night",
     "employee_email": "admin@insightpulseai.com",
     "attachment": {
       "filename": "hilton.jpg",
       "content_base64": "BASE64_JPEG_DATA"
     }
   }
   ```
3. **HMAC Validation**: Verifies `X-IPAI-Signature` header
4. **Employee Lookup**: Finds employee by `work_email`
5. **Product Matching**: Fuzzy matches `category` to T&E products (e.g., "Lodging" → "Lodging")
6. **Expense Creation**: Creates `hr.expense` record with:
   - Employee, product, amount, date, currency
   - Attached receipt image
7. **Response**: `{"ok": true, "expense_id": 123}`

### Email-to-Expense Flow (Alternative)

1. **User emails** receipt to `expenses@insightpulseai.com`
2. **Odoo Mail Gateway** ingests email
3. **Creates Expense** with email body/attachments
4. **Manual categorization** by employee

---

## Testing

### Webhook Endpoint Test
```bash
curl -sS https://erp.insightpulseai.net/ipai/ocr/inbound \
  -H "Content-Type: application/json" \
  -H "X-IPAI-Signature: test" \
  -d '{
    "source_id": "test_001",
    "total": 125.50,
    "currency": "USD",
    "date": "2025-11-13",
    "vendor": "Test Vendor",
    "category": "Lodging",
    "description": "Test Hotel Expense",
    "employee_email": "admin@insightpulseai.com"
  }' | jq
```

**Expected Response** (with incorrect signature):
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "ok": false,
    "error": "bad_signature"
  }
}
```

### Verify Configuration
```bash
ssh root@159.223.75.148 "docker exec insightpulse-db psql -U odoo -d odoo -c \"
SELECT key, value
FROM ir_config_parameter
WHERE key LIKE 'ipai_ocr%' OR key LIKE 'hr_expense%' OR key = 'mail.catchall.domain'
ORDER BY key;
\""
```

### Check Recent Expenses
```bash
ssh root@159.223.75.148 "docker exec insightpulse-db psql -U odoo -d odoo -c \"
SELECT id, name, unit_amount, date, employee_id
FROM hr_expense
ORDER BY id DESC
LIMIT 5;
\""
```

---

## Next Steps

### 1. Configure OCR Service Webhook
In your OCR service (`ocr.insightpulseai.net`), configure:
- **Webhook URL**: `https://erp.insightpulseai.net/ipai/ocr/inbound`
- **Webhook Secret**: Generate strong secret, update `ipai_ocr.webhook_secret`
- **Signature Header**: `X-IPAI-Signature` (HMAC-SHA256 of request body)
- **Payload Format**: JSON matching schema above

### 2. Generate Webhook Secret
```bash
# Generate secure secret (32 bytes)
openssl rand -hex 32

# Set in Odoo
ssh root@159.223.75.148 "docker exec -i insightpulse-odoo odoo shell -d odoo" <<'PY'
secret = "YOUR_GENERATED_SECRET_HERE"
env['ir.config_parameter'].sudo().set_param('ipai_ocr.webhook_secret', secret)
env.cr.commit()
print(f"✓ Webhook secret set: {secret[:8]}...")
PY
```

### 3. Configure Email Alias (Optional)
**In Odoo UI** (Settings > Technical > Email > Aliases):
1. Create alias: `expenses@insightpulseai.com`
2. Alias Model: **Expense (hr.expense)**
3. Create Record: **Create a new expense**
4. Accept Emails From: **Everyone** (or **Authenticated Partners**)

**DNS Configuration** (in your domain provider):
```
MX  insightpulseai.com  10  erp.insightpulseai.net
```

### 4. Test End-to-End
1. Upload receipt to OCR service
2. OCR service processes and calls webhook
3. Check Odoo: **Expenses > My Expenses**
4. Verify expense created with correct:
   - Amount, date, vendor
   - Category/product
   - Attached receipt image

---

## Security Checklist

- ✅ HTTPS with HSTS enabled
- ✅ HMAC webhook signature validation
- ✅ Firewall rules (UFW) active
- ✅ PostgreSQL backups scheduled
- ⚠️ **TODO**: Update `ipai_ocr.webhook_secret` from `CHANGE_ME_WEBHOOK_SECRET`
- ⚠️ **TODO**: Update `ipai_ocr.api_token` from `CHANGE_ME_API_TOKEN` (if needed)
- ✅ Daily health monitoring
- ✅ Odoo Enterprise OCR disabled (using external OCR)

---

## Troubleshooting

### Webhook Returns `bad_signature`
**Cause**: HMAC signature mismatch
**Fix**: Verify OCR service is using correct `webhook_secret` and HMAC-SHA256 algorithm

### Expense Not Created
**Check webhook logs**:
```bash
ssh root@159.223.75.148 "docker logs insightpulse-odoo --tail 50 | grep OCR"
```

**Common issues**:
- Employee not found: Check `work_email` matches
- Product not found: Check `category` matches T&E product names (case-insensitive)
- Currency not found: Ensure `USD` exists in Odoo currencies

### Health Check Not Running
```bash
ssh root@159.223.75.148 "systemctl status stack-health.timer"
ssh root@159.223.75.148 "tail -f /var/log/stack-health.log"
```

### Backup Not Running
```bash
ssh root@159.223.75.148 "systemctl status pg-backup.timer"
ssh root@159.223.75.148 "ls -lh /var/backups/pg/"
```

---

## File Locations

**Module**: `/var/lib/docker/volumes/c39972a67c6ba1d27305ea007416aa5d50206decdeead0ed44f9c5ff8544f569/_data/insightpulse/ipai_ocr_bridge`
**Caddyfile**: `/opt/odoo/Caddyfile`
**Backups**: `/var/backups/pg/odoo-YYYYMMDD-HHMMSS.dump`
**Health Log**: `/var/log/stack-health.log`
**Scripts**:
- `/usr/local/bin/pg_backup.sh`
- `/usr/local/bin/health.sh`

---

## Success Criteria ✅

- [x] T&E products seeded (12 categories)
- [x] Accounts created (120500, 210500)
- [x] Journals created (EXP, ADV, CARD)
- [x] Expense settings configured
- [x] HTTPS TLS with Caddy
- [x] PostgreSQL backups scheduled
- [x] Health monitoring active
- [x] UFW firewall configured
- [x] OCR bridge module installed
- [x] Webhook endpoint accessible
- [x] Signature validation working
- [ ] **TODO**: Update webhook secret from default
- [ ] **TODO**: Configure OCR service webhook
- [ ] **TODO**: Test end-to-end OCR → Expense flow

---

## Contact

**Project**: InsightPulse AI - Finance SSC
**Repository**: https://github.com/jgtolentino/insightpulse-odoo
**ERP**: https://erp.insightpulseai.net/
**OCR**: https://ocr.insightpulseai.net/

**Maintainer**: Jake Tolentino
**Email**: jgtolentino_rn@yahoo.com
