# Finance PPM CLI Tool

**Quick Reference Card** for completing Finance PPM deployment

---

## ✅ Current Status (Run First)

```bash
finance-cli.sh status
```

**Expected Output**:
- ✅ Odoo containers: odoo-ce (Up), odoo-db (Up)
- ✅ Module state: ipai_finance_ppm (installed)
- ⚠️ BIR count: 1 (should be 129)

---

## 🔧 Complete Deployment (5 Steps)

### Step 1: Fix BIR Schedules

```bash
finance-cli.sh seed-bir-orm
```

**What it does**: Inserts 128 BIR schedule records via Python ORM (bypasses `noupdate="1"` restriction)

**Verify**:
```bash
finance-cli.sh status | grep "BIR schedule count"
# Expected: count = 129 (1 seed + 128 generated)
```

---

### Step 2: Import n8n Workflow

**Prerequisites**:
1. Change n8n password: http://localhost:5678 → Settings → Change password
2. Generate API key: http://localhost:5678 → Settings → API Keys → Create
3. Export key to environment:
   ```bash
   export N8N_API_KEY="your-real-api-key-here"
   ```

**Import workflow**:
```bash
finance-cli.sh import-n8n
```

**Verify**: Open http://localhost:5678 → Workflows → Should see "Finance Compliance Engine"

---

### Step 3: Configure Mattermost Webhook

**Manual Steps** (one-time):
1. Login to Mattermost
2. Navigate to: **Main Menu (☰)** → **Integrations** → **Incoming Webhooks**
3. Click: **Add Incoming Webhook**
4. Configure:
   - Title: "n8n Finance Alerts"
   - Channel: #finance-alerts
5. Copy webhook URL

**Test webhook**:
```bash
export MM_WEBHOOK_URL="https://mattermost.insightpulseai.net/hooks/YOUR_WEBHOOK_ID"
curl -X POST "$MM_WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d '{"text":"✅ TBWA Finance PPM alerts online"}'
```

**Add to n8n workflow**:
1. Open workflow in n8n
2. Find "Send Mattermost Alert" node
3. Update Webhook URL field
4. Save workflow

---

### Step 4: Test Cron Job

```bash
finance-cli.sh test-cron
```

**What it does**: Manually triggers BIR Task Sync cron job

**Verify**:
- Check Odoo UI: Finance PPM → Tasks
- Check Mattermost: #finance-alerts channel for notifications

---

### Step 5: Final Verification

```bash
finance-cli.sh status
```

**Expected Final State**:
- ✅ ipai_finance_ppm: installed
- ✅ BIR schedules: 129 records
- ✅ Cron job: Active (Next run: Tomorrow 8:00 AM)
- ✅ n8n: Workflow active
- ✅ Mattermost: Webhook configured

---

## 🎯 Quick Commands Reference

| Command | Purpose |
|---------|---------|
| `finance-cli.sh status` | Check Odoo, modules, BIR count |
| `finance-cli.sh seed-bir-orm` | Fix BIR schedules (insert 128 records) |
| `finance-cli.sh gen-2026-calendar` | Generate 2026 Finance calendar |
| `finance-cli.sh import-n8n` | Import n8n workflow via API |
| `finance-cli.sh test-cron` | Manually trigger BIR Task Sync |
| `finance-cli.sh` | Show help and available commands |

---

## 🔐 Security Checklist

- [ ] Change n8n password from default (admin/insightpulse2024)
- [ ] Generate n8n API key (never use default credentials)
- [ ] Store API key in environment variable (not in code)
- [ ] Verify Mattermost webhook is not public
- [ ] Confirm Odoo is not exposed to internet without authentication

---

## 📊 Deployment Status

**Session 1** (Database + Module Structure):
- ✅ Supabase schema migrations
- ✅ Odoo module scaffold
- ✅ Dashboard route + ECharts

**Session 2** (Automation + Integration):
- ✅ Finance PPM Dashboard accessibility
- ✅ BIR Task Sync cron job (Odoo 18 migration)
- ✅ n8n server running
- ⚠️ BIR schedules issue (workaround: `seed-bir-orm`)
- ⏳ n8n workflow import (manual)
- ⏳ Mattermost configuration (manual)

---

## 🆘 Troubleshooting

### BIR count still 1 after seed-bir-orm
**Issue**: Odoo shell script failed to insert records

**Fix**: Use Option A from DEPLOYMENT_SUMMARY.md (remove `noupdate="1"` flag)

### n8n workflow import fails
**Issue**: API authentication or workflow format error

**Fix**:
1. Verify API key: `echo $N8N_API_KEY`
2. Check workflow file exists: `ls ~/n8n/workflows/finance_compliance_engine.json`
3. Import manually via UI: http://localhost:5678 → Import from File

### Cron job not triggering
**Issue**: Cron configuration error

**Fix**:
```bash
docker exec odoo-db psql -U odoo -d odoo -c \
  "SELECT * FROM ir_cron WHERE cron_name LIKE '%Finance PPM%';"
# Verify: active=true, nextcall is set
```

---

## 📚 Documentation

- **Full Deployment Guide**: `/Users/tbwa/DEPLOYMENT_SUMMARY.md`
- **Odoo 18 Cron Docs**: https://www.odoo.com/documentation/18.0/developer/reference/backend/actions.html
- **n8n Workflow Docs**: https://docs.n8n.io/workflows/
- **Mattermost Webhooks**: https://developers.mattermost.com/integrate/webhooks/incoming/

---

**Last Updated**: 2025-11-23
**CLI Version**: 1.0.0
**Author**: InsightPulse AI Team
