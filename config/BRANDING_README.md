# InsightPulseAI Unified Branding Guide

**Last Updated:** 2025-11-08
**Odoo Version:** 18.0 Community Edition
**Purpose:** Apply consistent visual branding across all InsightPulse services

---

## Overview

This directory contains the unified branding specification and implementation files for InsightPulseAI platform:

- **ERP:** Odoo 18 CE
- **Chat:** Mattermost
- **Analytics:** Apache Superset
- **Automation:** n8n

## Brand Colors

```
Primary:   #1455C7 (InsightPulse Blue)
Secondary: #111827 (Dark Gray)
Accent:    #F97316 (Orange)
```

---

## Files

### 1. branding_theme.json
**Purpose:** Master design token specification
**Usage:** Reference file for all applications
**Contains:** Colors, typography, spacing, shadows, breakpoints

### 2. mattermost_theme.json
**Purpose:** Mattermost custom theme configuration
**Usage:** Copy-paste into Mattermost settings
**Path:** User Menu → Preferences → Display → Custom Theme

### 3. odoo18_desired_state.json
**Purpose:** Declarative Odoo 18 configuration
**Usage:** Apply settings via Python RPC script
**Contains:** Apps, users, email, integrations, branding

---

## Installation Instructions

### Odoo 18 Custom Theme

**Step 1: Install the Custom Theme Module**

```bash
# Navigate to Odoo directory
cd /Users/tbwa/insightpulse-odoo

# Restart Odoo to detect new module
docker-compose restart odoo

# Or via Odoo CLI (if running directly)
./odoo-bin -d odoo19 -i custom_theme --stop-after-init
```

**Step 2: Activate via Web UI**

1. Login to Odoo at https://erp.insightpulseai.net
2. Navigate to **Apps** menu
3. Click **Update Apps List** (remove filters first)
4. Search for "InsightPulseAI Custom Theme"
5. Click **Install**

**Step 3: Verify Theme Applied**

- Check navbar is dark gray (#111827)
- Check primary buttons are blue (#1455C7)
- Check links are blue (#1455C7)

**Step 4: Configure Document Layout (Optional)**

Navigate to **Settings → General Settings → Companies → Document Layout**:

```
Primary Color:   #1455C7
Secondary Color: #111827
Logo:            Upload InsightPulseAI logo
Footer Text:     InsightPulseAI • Philippine Operations • VAT Registered
```

---

### Mattermost Custom Theme

**Step 1: Open Mattermost Settings**

1. Login to Mattermost at https://chat.insightpulseai.net
2. Click **User Menu** (top-right)
3. Select **Preferences**
4. Click **Display**
5. Scroll to **Theme**

**Step 2: Apply Custom Theme**

1. Click **Custom Theme**
2. Copy contents of `/config/mattermost_theme.json`
3. Paste into the **Custom Theme** text box
4. Click **Save**

**Verification:**
- Sidebar should be dark gray (#111827)
- Links should be blue (#1455C7)
- Online indicators should be green (#10B981)

---

### Apache Superset (Future)

**File Location:** `/superset/static/css/custom_theme.css`
**Status:** To be created
**Implementation:** CSS variables matching branding_theme.json

---

### n8n Workflow Automation (Future)

**File Location:** `/n8n/custom_theme.css`
**Status:** To be created
**Implementation:** CSS variables matching branding_theme.json

---

## Applying Configuration via RPC

**Script Location:** `/scripts/apply_odoo18_config.py` (to be created)

**Preview Script:**

```python
#!/usr/bin/env python3
import json
import xmlrpc.client

# Load desired state
with open('/Users/tbwa/insightpulse-odoo/config/odoo18_desired_state.json') as f:
    desired = json.load(f)

# Connect to Odoo 18
url = 'http://localhost:8069'
db = 'odoo19'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Example: Install apps
for app in desired['apps']['install']:
    module = models.execute_kw(db, uid, password, 'ir.module.module', 'search', [[('name', '=', app)]])
    if module:
        models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [module])
        print(f"✅ Installed: {app}")

# Example: Set company branding
company_id = models.execute_kw(db, uid, password, 'res.company', 'search', [[('name', '=', desired['company']['name'])]])[0]
models.execute_kw(db, uid, password, 'res.company', 'write', [company_id, {
    'primary_color': desired['document_layout']['primary_color'],
    'secondary_color': desired['document_layout']['secondary_color'],
    'paperformat_id': 1,  # Default paper format
}])
print(f"✅ Updated company branding")
```

---

## Maintenance

### Updating Colors

1. Edit `/config/branding_theme.json`
2. Update corresponding theme files:
   - Mattermost: `mattermost_theme.json`
   - Odoo: `odoo/addons/custom_theme/static/src/css/odoo_custom_theme.css`
3. Restart services or clear browser cache

### Version Compatibility

- **Odoo:** 18.0 only (not compatible with Odoo 19)
- **Mattermost:** 7.x and above
- **Superset:** 3.x and above
- **n8n:** 1.x and above

---

## Troubleshooting

### Odoo Theme Not Applying

**Problem:** Custom theme module not visible in Apps list

**Solution:**
```bash
# Update module list
docker exec insightpulse-odoo-odoo-1 odoo -d odoo19 --update-list --stop-after-init

# Or via web UI
Apps → Update Apps List (click gear icon first to remove filters)
```

**Problem:** CSS not loading after installation

**Solution:**
```bash
# Clear Odoo asset bundle cache
docker exec insightpulse-odoo-odoo-1 odoo -d odoo19 --dev=all
# Then regenerate assets in browser: Ctrl+Shift+R (force reload)
```

### Mattermost Theme Not Saving

**Problem:** Theme reverts to default after refresh

**Solution:**
- Ensure you're using Mattermost 7.0+
- Check browser console for errors
- Try incognito/private browsing mode
- Clear Mattermost cache: Settings → Advanced → Clear Cache and Reload

### Colors Look Different Across Services

**Problem:** Blue in Odoo doesn't match blue in Mattermost

**Solution:**
- Verify hex codes in all theme files match `branding_theme.json`
- Check for browser extensions that modify colors (Night Mode, Dark Reader)
- Ensure sRGB color profile in browser settings

---

## Support

**Documentation:** https://github.com/jgtolentino/insightpulse-odoo/docs
**Issues:** https://github.com/jgtolentino/insightpulse-odoo/issues
**Admin:** jgtolentino_rn@yahoo.com

---

**Generated:** 2025-11-08 via Claude Code
**Target:** Odoo 18.0 Community Edition
**Branding Spec Version:** 1.0.0
