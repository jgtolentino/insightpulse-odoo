# Fix Odoo Apps Configuration - Custom Modules Not Visible

**Issue Date**: 2025-11-08
**Affected URL**: https://erp.insightpulseai.net/odoo/settings
**Status**: ⚠️ **CONFIGURATION ERROR DETECTED**

---

## 🔴 Problem

When accessing https://erp.insightpulseai.net/odoo/settings, you see:

**What's Showing:**
- ✅ Official Odoo 19.0 apps (Sales, CRM, Invoicing, etc.)
- ❌ Custom modules NOT visible:
  - `ip_expense_mvp` (InsightPulse Expense MVP)
  - `pulser_webhook` (GitHub integration)
  - `ipai_mattermost_bridge` (Mattermost webhook)

**Expected Behavior:**
- Should show custom InsightPulse modules in Apps list
- Custom modules should be installable from UI

---

## 🔍 Root Cause Analysis

### Issue 1: Incorrect URL Path
```
Current: https://erp.insightpulseai.net/odoo/settings
Correct: https://erp.insightpulseai.net/web#action=base.open_module_tree
```

The `/odoo/settings` route doesn't exist - you're seeing the default apps page at `/web/settings`.

### Issue 2: addons_path Not Configured
```python
# Current: docker-compose.yml
volumes:
  - ./custom_addons:/mnt/custom-addons:ro  # ✅ Mounted

# Problem: No odoo.conf to tell Odoo to load from /mnt/custom-addons
# Result: Odoo only loads from default path (/usr/lib/python3/dist-packages/odoo/addons)
```

### Issue 3: Modules Not in Database
Even if addons_path is configured, modules must be:
1. Scanned (update module list)
2. Installed (via UI or CLI)

---

## ✅ Solution

I've prepared a complete fix with 3 components:

### 1. **odoo.conf** (New File)
```ini
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/custom-addons
db_host = postgres
db_name = odoo
http_port = 8069
workers = 2
proxy_mode = True
session_cookie_domain = .insightpulseai.net
```

### 2. **docker-compose.yml** (Updated)
```yaml
odoo:
  image: odoo:19.0
  volumes:
    - ./custom_addons:/mnt/custom-addons:ro
    - ./odoo.conf:/etc/odoo/odoo.conf:ro  # ← NEW: Mount config
    - odoo_data:/var/lib/odoo              # ← NEW: Persistent data
```

### 3. **Deployment Script** (`scripts/fix-odoo-apps.sh`)
Automated deployment to production droplet

---

## 🚀 Quick Fix (Option A: Automated)

Run the automated fix script:

```bash
cd /home/user/insightpulse-odoo

# Make script executable
chmod +x scripts/fix-odoo-apps.sh

# Deploy fix to production
./scripts/fix-odoo-apps.sh
```

**What it does:**
1. Uploads `odoo.conf` and updated `docker-compose.yml`
2. Uploads `custom_addons/` directory
3. Restarts Odoo with new configuration
4. Updates module list
5. Verifies deployment

**Duration:** ~2 minutes
**Downtime:** ~30 seconds (Odoo restart)

---

## 🔧 Manual Fix (Option B: Step-by-Step)

If you prefer manual deployment:

### Step 1: Verify Files Locally
```bash
cd /home/user/insightpulse-odoo

# Check files exist
ls -la odoo.conf
ls -la docker-compose.yml
ls -la custom_addons/
```

### Step 2: Upload to Droplet
```bash
# Copy configuration
scp odoo.conf root@165.227.10.178:/opt/insightpulse-odoo/
scp docker-compose.yml root@165.227.10.178:/opt/insightpulse-odoo/
scp -r custom_addons root@165.227.10.178:/opt/insightpulse-odoo/
```

### Step 3: Deploy on Droplet
```bash
# SSH into droplet
ssh root@165.227.10.178

cd /opt/insightpulse-odoo

# Restart with new config
docker-compose down
docker-compose up -d

# Wait for startup
sleep 30

# Update module list
docker-compose exec odoo odoo-bin -d odoo --update=all --stop-after-init --no-http

# Restart normally
docker-compose restart odoo
```

### Step 4: Verify in UI
1. Go to: https://erp.insightpulseai.net/web#action=base.open_module_tree
2. Search for "InsightPulse"
3. Should see 3 custom modules
4. Install them one by one

---

## 📋 Post-Fix Verification

### Checklist

After running the fix, verify:

**1. Custom Modules Visible:**
```bash
# SSH to droplet
ssh root@165.227.10.178

# Check addons path
docker-compose exec odoo cat /etc/odoo/odoo.conf | grep addons_path

# Should output:
# addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/custom-addons

# Verify custom_addons mounted
docker-compose exec odoo ls -la /mnt/custom-addons

# Should show:
# ip_expense_mvp/
# pulser_webhook/
# ipai_mattermost_bridge/
```

**2. Modules in UI:**
- ✅ Go to: Apps → Remove filters → Search "InsightPulse"
- ✅ See: InsightPulse – Expense MVP
- ✅ See: Pulser Webhook
- ✅ See: IPAI Mattermost Bridge

**3. Install Modules:**
```
Click each module → Click "Install" → Wait for completion
```

**4. Verify Installation:**
```
Main Menu → Should see "InsightPulse T&E" menu item
```

---

## 🎯 Correct URLs to Use

| What You Want | Correct URL |
|---------------|-------------|
| **Apps List** | https://erp.insightpulseai.net/web#action=base.open_module_tree |
| **Settings** | https://erp.insightpulse ai.net/web/settings |
| **Expense MVP (after install)** | https://erp.insightpulseai.net/web#menu_id=XXX |
| **Mobile Receipt Capture** | https://erp.insightpulseai.net/ip/mobile/receipt |
| **Admin Dashboard** | https://erp.insightpulseai.net/web#menu_id=XXX |

---

## 🔧 Troubleshooting

### Issue: Modules still not visible after fix

**Solution 1: Force module list update**
```bash
ssh root@165.227.10.178
cd /opt/insightpulse-odoo
docker-compose exec odoo odoo-bin \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/custom-addons \
  -d odoo \
  --update=all \
  --stop-after-init

docker-compose restart odoo
```

**Solution 2: Check logs**
```bash
docker-compose logs odoo | grep -i "error\|exception"
docker-compose logs odoo | grep "custom_addons"
```

**Solution 3: Verify manifest files**
```bash
docker-compose exec odoo cat /mnt/custom-addons/ip_expense_mvp/__manifest__.py
```

### Issue: "Access Denied" when accessing /odoo/settings

**Reason:** Route doesn't exist or you're not logged in

**Solution:**
1. Login first: https://erp.insightpulseai.net/web/login
2. Use correct URL: https://erp.insightpulseai.net/web#action=base.open_module_tree

### Issue: Modules install but don't appear in menu

**Solution:** Clear browser cache and refresh
```bash
# Or force menu refresh in Odoo
Settings → Technical → Menu Items → Reload
```

---

## 📊 What Each Custom Module Does

### 1. **ip_expense_mvp** (v0.1.0)
- **Purpose:** Travel & Expense Management MVP
- **Features:**
  - Mobile receipt capture
  - OCR integration
  - Cash advance/liquidation
  - Admin dashboard
- **Menu:** InsightPulse T&E
- **Routes:**
  - `/ip/mobile/receipt` - Mobile capture
  - Admin dashboard view

### 2. **pulser_webhook** (v19.0.1.0.2)
- **Purpose:** GitHub git-ops integration
- **Features:**
  - Repository dispatch triggers
  - GitHub App authentication
  - Webhook HMAC validation
  - One-click git-ops from records
- **Bindings:** Project Task, Sale Order, Invoice, Expense, Purchase Order

### 3. **ipai_mattermost_bridge** (v1.0.0)
- **Purpose:** Webhook ingestion for external systems
- **Features:**
  - GitHub webhook handling
  - Jira integration
  - ServiceNow integration
- **Use Case:** External system notifications

---

## 🚦 Deployment Impact

**Downtime:** ~30 seconds (Odoo restart)
**Risk:** Low (read-only config changes)
**Rollback:** Simple (restore docker-compose.yml backup)

**Backup Created:**
```bash
docker-compose.yml.backup.20251108_HHMMSS
```

---

## ✅ Success Criteria

After deployment, you should:

1. ✅ See 3 custom modules in Apps list
2. ✅ Be able to install modules via UI
3. ✅ See "InsightPulse T&E" menu after install
4. ✅ Access mobile capture at `/ip/mobile/receipt`
5. ✅ See admin dashboard
6. ✅ All official Odoo apps still visible

---

## 📝 Next Steps

After fixing the apps configuration:

1. **Install Custom Modules** - via UI or CLI
2. **Configure Expense MVP:**
   - Settings → System Parameters
   - Set `ip_ai_inference_base_url`: http://ocr.insightpulseai.net
   - Set `ip_ai_inference_token`: (optional)
3. **Test Mobile Capture:**
   - Go to: https://erp.insightpulseai.net/ip/mobile/receipt
   - Upload test receipt
   - Verify OCR processing
4. **Set Up DMS** (if needed):
   - Follow DMS installation guide
   - Downgrade to Odoo 18.0 for full OCA/dms support

---

**Ready to deploy?** Run `./scripts/fix-odoo-apps.sh` or follow manual steps above.
