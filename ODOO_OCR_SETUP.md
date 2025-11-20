# InsightPulse OCR for Odoo Expenses - Service Definition

**Version**: v0.2.1-quality
**Status**: Production (Quality Baseline)
**Last Updated**: 2025-11-21

---

## Service Architecture

```
Odoo Expense Form
    ↓ OCR Button
OCR Adapter (FastAPI)
    ↓ HTTP POST
PaddleOCR-VL-900M + OpenAI gpt-4o-mini
    ↓ Response
Odoo `ocr.expense.log` Table
    ↓ Dashboard/Pivot
Quality Monitoring & n8n Alerts
```

### Components

- **Odoo Module**: `ipai_ocr_expense` (CE 18.0 compatible)
- **OCR Adapter**: FastAPI service at `https://ocr.insightpulseai.net`
- **OCR Backend**: PaddleOCR-VL-900M document understanding model
- **LLM Enhancement**: OpenAI gpt-4o-mini for post-processing
- **Observability**: `ocr.expense.log` model with UI dashboard
- **Quality Testing**: Test harness with ground truth validation

---

## Service Level Objectives (SLOs)

### 1. Success Rate

**Short-term Target**: ≥ 75% "success" (all fields extracted correctly)
**Medium-term Target**: ≥ 85% "success"
**Long-term Target**: ≥ 90% "success"

**Measurement**:
- Query `ocr.expense.log` for `status='success'` count vs total
- Review weekly via Odoo pivot or n8n daily summary
- Track by vendor to identify weak spots

**Definition of Success**:
- All 4 core fields extracted: vendor, date, total, currency
- Fields pass validation rules (date parseable, total numeric, vendor non-empty)

---

### 2. Processing Duration

**P50 Target**: < 5 seconds (UX feel target)
**P95 Target**: < 30 seconds (30,000ms)
**P99 Target**: < 60 seconds (60,000ms)

**Measurement**:
- Query `ocr.expense.log.duration_ms` field
- Calculate percentiles weekly via SQL or Odoo pivot
- Alert if P95 exceeds 30s in daily n8n summary

**Optimization Levers**:
- OCR backend model inference time (currently ~2-5s)
- LLM post-processing time (currently ~1-3s)
- Network latency (Odoo ↔ adapter ↔ OCR backend)

---

### 3. Field-wise Accuracy (via Test Harness)

Measured against ground truth CSV with real PH receipts.

**Date Accuracy**: ≥ 95%
- Accepts YYYY-MM-DD, DD/MM/YYYY, PH-style "15 Nov 2025"
- Normalized to YYYY-MM-DD in adapter

**Total Accuracy (±1 peso tolerance)**: ≥ 95%
- Exact match within 0.01 preferred
- ±1 peso tolerance for rounding issues (e.g., 345.50 vs 345.00)

**Vendor Accuracy**: ≥ 90%
- Case-insensitive match after normalization
- Common PH variants handled (SM Store → SM Supermarket, etc.)

**Currency Accuracy**: ≥ 95%
- Defaults to PHP for PH-local vendors
- Explicit currency symbols recognized (₱, PHP, Php)

---

### 4. Availability

**Uptime Target**: 99.0% (8.7 hours downtime/year)

**Measurement**:
- Health endpoint: `https://ocr.insightpulseai.net/health`
- Monitor via external uptime service (e.g., UptimeRobot, Pingdom)
- n8n can query health endpoint daily

**Failure Modes**:
- Adapter service down (FastAPI crash)
- OCR backend unavailable (PaddleOCR service down)
- Network issues (DNS, SSL, routing)

---

## Quality Monitoring

### Odoo Dashboard (Built-in)

**Menu**: Expenses → Configuration → OCR Logs

**Views**:
- **List View**: Recent OCR calls with status, duration, confidence
- **Pivot View**: Performance metrics by status, vendor, month
- **Filters**:
  - Failed (Last 7 Days)
  - Issues (Last 30 Days) – partial or failed
  - This Week / Today
- **Groupings**:
  - Status → Employee (who hits most failures)
  - Status → Vendor (which vendors/receipt types are weak)

**Usage**:
- Check weekly for trends
- Review failed logs to understand error patterns
- Identify vendors needing normalization rules

---

### Test Harness (External Validation)

**Location**: `/Users/tbwa/odoo-ce/ocr-adapter/scripts/test-harness.py`

**Usage**:
```bash
cd /Users/tbwa/odoo-ce/ocr-adapter

python3 scripts/test-harness.py \
  --images ./test_receipts \
  --ground-truth ./test_receipts/ground_truth.csv \
  --api-url https://ocr.insightpulseai.net/api/expense/ocr \
  --api-key 282e6543652de3e969d43293e934f6f84557ab767132bcd2fd37c76289ff703e
```

**Output**:
- Console report with field-wise accuracy percentages
- Per-vendor breakdown
- JSON report for tracking over time

**Frequency**:
- Run after each adapter normalization change
- Run weekly with expanded receipt set
- Store results in `docs/ocr_quality/` for historical tracking

---

### n8n Daily QA Workflow (Planned)

**Workflow Name**: "Daily OCR Quality Summary"

**Schedule**: Daily at 09:00 PH time

**Steps**:
1. Query Supabase/Postgres for yesterday's `ocr.expense.log` stats:
   - Total calls
   - Success / partial / failed counts
   - Top 5 vendors by failure count
   - P95 duration_ms
2. IF failure rate > 20% OR P95 duration > 30s:
   - Send Mattermost alert to ops channel
3. ELSE:
   - Log summary for review

**Alert Example**:
> OCR Daily Summary – 2025-11-21
> 34 scans, 4 failed (11.8%), avg 2.1s, P95 5.4s
> Top failing vendors: 7-Eleven (2), SM (1), Max's (1)

---

## Normalization Strategy

All quality improvements happen in the OCR adapter's `normalize_ocr_response()` function.
**No Odoo code changes needed** – adapter is the single lever for quality.

### Current Normalization Passes

**Pass 1: Vendor Normalization**
- Map common PH variants to canonical names
- Example: "SM Store" → "SM Supermarket", "7 Eleven" → "7-Eleven"
- Stored in `VENDOR_NORMALIZATION` dict in `main.py`

**Pass 2: Date Normalization**
- Accept YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, PH-style "15 Nov 2025"
- Convert all to YYYY-MM-DD for Odoo
- Uses `python-dateutil` for flexible parsing

**Pass 3: Total Tolerance**
- Keep raw vs normalized amounts
- Test harness allows ±1 peso tolerance
- Adapter returns exact float value

**Pass 4: Currency Defaulting**
- If no explicit currency, default to PHP for PH-local vendors
- Uses `PH_LOCAL_VENDORS` set for pattern matching

### Adding New Normalization Rules

**When to add**:
- Test harness shows repeated failures for specific vendor
- Odoo logs show consistent pattern (e.g., "SM Store" appears 5+ times)
- User reports specific receipt type failing

**How to add**:
1. Update `VENDOR_NORMALIZATION` dict in `main.py`
2. Or update `PH_LOCAL_VENDORS` set for currency defaulting
3. Or add new normalization pass function
4. Deploy adapter (no Odoo restart needed)
5. Re-run test harness to validate improvement

---

## Iteration Loop

```
1. Collect receipts → run test harness
2. Check harness + `ocr.expense.log` pivot in Odoo
3. Patch `normalize_ocr_response()` in adapter only
4. Redeploy adapter (DigitalOcean App Platform or local)
5. Re-run test harness to validate
6. Watch daily n8n summary for regressions
```

**Key Principle**: Infra is locked (v0.2.0-ocr baseline). From here, it's pure data and adapter edits.

---

## Deployment

### Adapter Deployment (DigitalOcean App Platform)

**App ID**: TBD (currently local dev)

**Deployment**:
```bash
# Update app spec if needed
doctl apps update <app-id> --spec infra/do/ocr-adapter.yaml

# Force rebuild and deploy
doctl apps create-deployment <app-id> --force-rebuild

# Monitor logs
doctl apps logs <app-id> --follow
```

**Environment Variables**:
- `UPSTREAM_OCR_URL`: PaddleOCR backend URL
- `IPAI_OCR_API_KEY`: API key for authentication
- `OCR_TIMEOUT`: Request timeout (default 60s)

---

### Odoo Module Deployment

**Module Location**: `/opt/odoo/custom-addons/ipai_ocr_expense/`

**Deployment**:
```bash
# Rsync updated files
rsync -avz /Users/tbwa/odoo-ce/addons/ipai_ocr_expense/ root@erp.insightpulseai.net:/opt/odoo/custom-addons/ipai_ocr_expense/

# Upgrade module
ssh root@erp.insightpulseai.net "docker exec odoo-odoo-1 odoo -d odoo -u ipai_ocr_expense --workers=0 --stop-after-init"

# Restart Odoo
ssh root@erp.insightpulseai.net "docker restart odoo-odoo-1"
```

---

## Troubleshooting

### High Failure Rate (> 20%)

**Diagnosis**:
1. Check Odoo logs: Expenses → Configuration → OCR Logs → Filter: Failed (Last 7 Days)
2. Group by: Status → Vendor to identify problem vendors
3. Check adapter logs for upstream errors

**Common Causes**:
- OCR backend service down
- New vendor/receipt type not normalized
- Poor quality receipt images (crumpled, low contrast)
- Network issues (adapter ↔ OCR backend)

**Resolution**:
- Add vendor normalization rule if pattern found
- Check OCR backend health endpoint
- Review receipt quality with users

---

### Slow Processing (P95 > 30s)

**Diagnosis**:
1. Query `ocr.expense.log` for high `duration_ms` values
2. Check adapter logs for slow upstream calls
3. Test OCR backend directly

**Common Causes**:
- OCR backend model inference slow (complex receipt)
- LLM post-processing timeout
- Network latency spikes

**Resolution**:
- Optimize OCR backend (increase compute, reduce queue)
- Adjust LLM timeout or model selection
- Check network routing and DNS

---

### Inaccurate Extractions

**Diagnosis**:
1. Run test harness to measure field-wise accuracy
2. Check specific failing receipts in Odoo logs
3. Review raw OCR output (if `raw_payload_path` saved)

**Common Causes**:
- Vendor name variant not normalized
- Date format not recognized
- Currency symbol ambiguous
- Total amount obscured or multi-line

**Resolution**:
- Add normalization rule for vendor/date format
- Improve OCR backend model training data
- Add fallback patterns in adapter

---

## Future Enhancements

### UX Guardrails (When Ready for Polish)

**Confidence Bar**:
- Show `confidence` score on expense form
- Warn if confidence < 0.8: "Low OCR confidence – please double-check values"

**View OCR Raw Data Smart Button**:
- Smart button on `hr.expense` form
- Opens linked `ocr.expense.log` record
- Users can see extracted fields, duration, error message

**Proposed Values Panel** (Iterative Workflow):
- Show OCR-extracted values as proposed
- User confirms or edits before saving
- Reduces auto-approval errors

---

## References

- **Test Harness Documentation**: `ocr-adapter/scripts/README.md`
- **Odoo Module**: `addons/ipai_ocr_expense/`
- **OCR Adapter Code**: `ocr-adapter/main.py`
- **Git Tags**: `v0.2.0-ocr` (infra baseline), `v0.2.1-quality` (quality layer baseline)

---

**Last Review**: 2025-11-21
**Next Review**: Weekly (check SLOs via pivot + test harness)
