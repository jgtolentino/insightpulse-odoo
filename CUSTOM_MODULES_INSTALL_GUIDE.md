# Custom Modules Installation Guide

**Date**: 2025-11-08
**Status**: ❌ **MODULES NOT VISIBLE - FIX REQUIRED**
**Production URL**: https://erp.insightpulseai.net/odoo/apps

---

## 🚨 Current Problem

### What You See Now
At https://erp.insightpulseai.net/odoo/apps?view_type=list:
- ✅ 54 official Odoo S.A. apps (Sales, CRM, Invoicing, etc.)
- ❌ **NO InsightPulse custom modules**
- ❌ **Cannot install** ip_expense_mvp, pulser_webhook, ipai_mattermost_bridge

### What You Should See
After fix:
- ✅ 54 official Odoo apps
- ✅ **3 InsightPulse custom modules**:
  - InsightPulse – Expense MVP (Mobile + Dashboard)
  - Pulser Webhook (GitHub integration)
  - IPAI Mattermost Bridge (Webhook ingestion)

---

## ✅ **SOLUTION - Deploy Fix Now**

### Step 1: Deploy Configuration Fix

**Run this command** (from your local machine):

```bash
cd /home/user/insightpulse-odoo

# Deploy odoo.conf and restart Odoo
./scripts/fix-odoo-apps.sh
```

**What this does**:
1. ✅ Uploads `odoo.conf` with `addons_path` configuration
2. ✅ Uploads updated `docker-compose.yml` with volume mounts
3. ✅ Uploads `custom_addons/` directory
4. ✅ Restarts Odoo containers
5. ✅ Updates module list
6. ✅ Makes custom modules visible

**Downtime**: ~30 seconds
**Duration**: ~2 minutes

---

### Step 2: Verify Modules Visible

After running the fix script:

**1. Refresh Apps Page**:
```
URL: https://erp.insightpulseai.net/odoo/apps
Action: Clear search filters (click X on any active filters)
Expected: See 57 apps total (54 official + 3 custom)
```

**2. Search for InsightPulse**:
```
Search box: Type "InsightPulse"
Expected results:
  - InsightPulse – Expense MVP (Mobile + Dashboard)
  - Pulser Webhook
  - IPAI Mattermost Bridge
```

**3. Alternative URL**:
```
Direct link: https://erp.insightpulseai.net/web#action=base.open_module_tree
```

---

### Step 3: Install Custom Modules

Once modules are visible, install them:

#### **A. Install ip_expense_mvp**

**Purpose**: Travel & Expense Management with OCR

**Installation**:
1. Go to Apps: https://erp.insightpulseai.net/odoo/apps
2. Search: "expense mvp" or "InsightPulse"
3. Find: **InsightPulse – Expense MVP (Mobile + Dashboard)**
4. Click: **Install** button
5. Wait: ~30 seconds for installation

**After Installation**:
- ✅ New menu appears: **InsightPulse T&E**
- ✅ Mobile capture: https://erp.insightpulseai.net/ip/mobile/receipt
- ✅ Admin dashboard available
- ✅ OCR integration ready

**Required Configuration**:
```
Settings → System Parameters → Set:
- ip_ai_inference_base_url = https://ocr.insightpulseai.net
- ip_ai_inference_token = (optional, leave empty for now)
```

---

#### **B. Install pulser_webhook**

**Purpose**: GitHub git-ops integration

**Installation**:
1. Apps → Search: "pulser"
2. Find: **Pulser Webhook**
3. Click: **Install**

**After Installation**:
- ✅ Server Action: "Trigger Git-Ops" available on records
- ✅ Bindings: Project Task, Sale Order, Invoice, Expense, Purchase Order

**Required Configuration**:
```
Environment variables (on production server):
- PULSER_WEBHOOK_SECRET
- GITHUB_APP_ID
- GITHUB_INSTALLATION_ID
- GITHUB_REPO_OWNER=jgtolentino
- GITHUB_REPO_NAME=insightpulse-odoo
- GITHUB_APP_PRIVATE_KEY_BASE64
```

---

#### **C. Install ipai_mattermost_bridge**

**Purpose**: Webhook ingestion for external systems

**Installation**:
1. Apps → Search: "mattermost"
2. Find: **IPAI Mattermost Bridge**
3. Click: **Install**

**After Installation**:
- ✅ Webhook endpoint: `/ipai/webhook/github`
- ✅ Handles: GitHub, Jira, ServiceNow webhooks

---

## 🔧 **Troubleshooting**

### Issue 1: Modules Still Not Visible After Fix

**Solution**:
```bash
# SSH to production droplet
ssh root@165.227.10.178

# Verify odoo.conf is mounted
docker exec insightpulse-odoo-odoo-1 cat /etc/odoo/odoo.conf | grep addons_path

# Should output:
# addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/custom-addons

# Verify custom_addons mounted
docker exec insightpulse-odoo-odoo-1 ls -la /mnt/custom-addons

# Should list:
# ip_expense_mvp/
# pulser_webhook/
# ipai_mattermost_bridge/

# Force module list update
docker exec insightpulse-odoo-odoo-1 odoo-bin \
  -d odoo \
  --update=all \
  --stop-after-init \
  --no-http

# Restart Odoo
docker restart insightpulse-odoo-odoo-1
```

---

### Issue 2: "Module not found" Error During Install

**Cause**: Manifest file issue or dependencies missing

**Solution**:
```bash
# Check manifest file
docker exec insightpulse-odoo-odoo-1 cat /mnt/custom-addons/ip_expense_mvp/__manifest__.py

# Verify dependencies exist
docker exec insightpulse-odoo-odoo-1 python3 -c "
import sys
sys.path.append('/usr/lib/python3/dist-packages/odoo')
from odoo import api
"
```

---

### Issue 3: Modules Visible But Won't Install

**Cause**: Dependency issues

**Solution**:
1. Install dependencies first:
   - `hr` (Employees)
   - `hr_expense` (Expenses)
   - `base` (always installed)
2. Then retry custom module installation

---

## 📋 **Post-Installation Checklist**

After installing all modules:

### Verify Expense MVP
```
[ ] Main menu shows "InsightPulse T&E"
[ ] Can create new expense: HR → Expenses → New
[ ] Mobile capture works: /ip/mobile/receipt
[ ] Admin dashboard accessible
[ ] OCR button appears on expense form
```

### Verify Pulser Webhook
```
[ ] Server Action "Trigger Git-Ops" appears
[ ] Can trigger from Project Task
[ ] GitHub webhook configured
```

### Verify Mattermost Bridge
```
[ ] Webhook endpoint responds: /ipai/webhook/github
[ ] Can receive test webhook
```

---

## 🎯 **Complete Installation URLs**

### Primary Apps Page
```
Main: https://erp.insightpulseai.net/odoo/apps
Alternative: https://erp.insightpulseai.net/web#action=base.open_module_tree
```

### Direct Module Links (after installation)
```
Expense MVP:
- Main menu: InsightPulse T&E
- Mobile: https://erp.insightpulseai.net/ip/mobile/receipt
- Dashboard: (via menu)

Settings:
- System Parameters: https://erp.insightpulseai.net/web#menu_id=base.menu_ir_config
```

---

## 🚀 **Quick Start After Installation**

### 1. Configure Expense MVP

**Step 1: Set OCR Endpoint**
```
Settings → Technical → System Parameters → Create New
Key: ip_ai_inference_base_url
Value: https://ocr.insightpulseai.net
```

**Step 2: Test Mobile Capture**
```
1. Visit: https://erp.insightpulseai.net/ip/mobile/receipt
2. Upload test receipt image
3. Click "Submit"
4. Verify expense created
```

**Step 3: Configure Payment Methods**
```bash
# Run payment methods configuration
./scripts/configure-payment-methods.sh
```

---

### 2. Test GitHub Integration

**Pulser Webhook Test**:
```
1. Go to: Project → Tasks → Create test task
2. Click: Action → Trigger Git-Ops
3. Check: GitHub Actions triggered
```

---

### 3. Test Mattermost Bridge

**Webhook Test**:
```bash
# Send test webhook
curl -X POST https://erp.insightpulseai.net/ipai/webhook/github \
  -H "Content-Type: application/json" \
  -d '{"action":"test","repository":"insightpulse-odoo"}'
```

---

## ⚡ **Next Steps After Installation**

1. **Phase 2: Configure Payment Methods**
   ```bash
   ./scripts/configure-payment-methods.sh
   ```

2. **Phase 3A: Enhance Expense MVP**
   - Add BIR compliance features
   - Integrate payment methods
   - Enhanced OCR validation

3. **Phase 3B: Full Solution**
   - Multi-level approvals
   - Email-to-expense
   - BIR forms automation

---

## 📊 **Module Dependencies**

### ip_expense_mvp
```python
"depends": ["base", "web", "hr", "hr_expense"]
```
**Install first**: hr, hr_expense

### pulser_webhook
```python
"depends": [
    "base",
    "project",
    "sale_management",
    "account",
    "hr_expense",
    "purchase",
]
```
**Install first**: project, sale_management, account, hr_expense, purchase

### ipai_mattermost_bridge
```python
"depends": ["base"]
```
**No additional dependencies**

---

## 🔐 **Security Notes**

### Production Credentials
- ❌ **NEVER** commit credentials to git
- ✅ **ALWAYS** use environment variables
- ✅ **ALWAYS** use Odoo System Parameters for API keys

### OAuth Configuration
- Google OAuth Client ID: `813089342312-sgk0lv3chvdcsaqb5o5hj2jv2jco1gai.apps.googleusercontent.com`
- Stored in: Database (secure)
- Not in: Git repository ✅

---

## 📞 **Support**

**If modules still not visible after fix**:
1. Check logs: `docker logs insightpulse-odoo-odoo-1`
2. Review: `DEPLOYMENT_VALIDATION.md`
3. Contact: jake@insightpulseai.net

**GitHub Issues**:
https://github.com/jgtolentino/insightpulse-odoo/issues

---

## ✅ **Success Criteria**

After completing this guide:

- [x] Ran `./scripts/fix-odoo-apps.sh`
- [ ] 3 custom modules visible at: https://erp.insightpulseai.net/odoo/apps
- [ ] Installed ip_expense_mvp
- [ ] Installed pulser_webhook
- [ ] Installed ipai_mattermost_bridge
- [ ] "InsightPulse T&E" menu appears
- [ ] Mobile capture works
- [ ] Payment methods configured
- [ ] Ready for Phase 3A (BIR compliance)

---

**Start here**: `./scripts/fix-odoo-apps.sh` 🚀
