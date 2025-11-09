# Odoo Module Visibility Guide

**Last Updated:** 2025-11-09
**Purpose:** Troubleshooting guide for custom module visibility in Odoo Apps

---

## Overview

Custom Odoo modules must meet specific requirements to appear in the Apps list. This guide explains the module visibility process and common issues.

---

## Module Discovery Process

### 1. Module Scanning (addons_path)

Odoo scans directories listed in `addons_path` on startup:

```ini
# odoo.conf
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
```

**Docker Volume Mapping:**
```yaml
# docker-compose.yml
volumes:
  - ./custom_addons:/mnt/extra-addons:ro
```

### 2. Module Loading Requirements

For a module to be discovered, it must have:

✅ **Valid directory structure:**
```
module_name/
├── __init__.py          # Module initialization
├__ __manifest__.py      # Module metadata
├── models/              # Optional: Business logic
├── views/               # Optional: UI definitions
└── security/            # Optional: Access rights
```

✅ **Valid __manifest__.py:**
```python
{
    "name": "Module Name",
    "version": "18.0.1.0.0",  # Match Odoo version
    "author": "Your Company",
    "license": "LGPL-3",
    "depends": ["base"],      # All dependencies must exist
    "installable": True,      # Must be True
    "application": False,     # True for top-level apps
    "data": [                 # Optional
        "security/ir.model.access.csv",
        "views/module_views.xml",
    ],
}
```

✅ **All dependencies installed or available:**
- If a module depends on an uninstalled module, it won't appear
- Use only dependencies that exist in your Odoo installation

### 3. Module List Update

After adding new modules, you must update the Apps list:

**Option 1: Via Odoo CLI (Recommended)**
```bash
docker exec insightpulse-odoo-odoo-1 \
  odoo -d odoo19 --update=base --stop-after-init --no-http
```

**Option 2: Via UI (Developer Mode)**
1. Enable Developer Mode: Settings → Activate the developer mode
2. Go to Apps
3. Click "Update Apps List" (gear icon)
4. Search for your module

**Option 3: Automated Script (see scripts/update-odoo-modules.sh)**

---

## Common Issues

### Issue 1: Module Not Appearing in Apps List

**Symptoms:**
- Module exists in `custom_addons/` directory
- Module doesn't appear in Apps search

**Possible Causes:**

#### A. Dependencies Not Installed

```python
# __manifest__.py
"depends": ["project", "sale_management", "purchase"],
```

**Check dependency status:**
```bash
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 -c "
SELECT name, state
FROM ir_module_module
WHERE name IN ('project', 'sale_management', 'purchase');
"
```

**Solution:**
1. Install missing dependencies first
2. OR make dependencies optional
3. OR remove unneeded dependencies

#### B. Module Not in addons_path

**Check mounted volumes:**
```bash
docker inspect insightpulse-odoo-odoo-1 | grep -A 10 Mounts
```

**Verify addons_path:**
```bash
docker exec insightpulse-odoo-odoo-1 cat /etc/odoo/odoo.conf | grep addons_path
```

**Solution:** Ensure volume is mounted correctly in docker-compose.yml

#### C. installable = False

**Check manifest:**
```python
"installable": True,  # Must be True!
```

**Solution:** Set `installable: True` in __manifest__.py

#### D. Module List Not Updated

**Check if module is in database:**
```bash
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 -c "
SELECT name, shortdesc::json->>'en_US', state
FROM ir_module_module
WHERE name = 'your_module_name';
"
```

**Solution:** Run module list update (see Section 3 above)

### Issue 2: Module Shows as "Not Installable"

**Symptoms:**
- Module appears in database query
- Module skipped during load with warning: `module xxx: not installable, skipped`

**Check Odoo logs:**
```bash
docker logs insightpulse-odoo-odoo-1 2>&1 | grep "not installable"
```

**Common Causes:**
- Python syntax errors in module files
- Missing or malformed `__init__.py`
- Version mismatch (e.g., module marked for Odoo 19 but running Odoo 18)

**Solution:**
1. Validate Python syntax: `python3 -m py_compile __manifest__.py`
2. Check version field matches Odoo version
3. Review Odoo logs for detailed errors

### Issue 3: Module Installed but Not Visible

**Symptoms:**
- Module state shows as "installed" in database
- Module doesn't appear in Apps or menu

**Check module state:**
```bash
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 -c "
SELECT name, shortdesc::json->>'en_US', state, application
FROM ir_module_module
WHERE name = 'your_module_name';
"
```

**Solution:**
- If `application = false`, module won't show as a top-level app
- Check module's menu items are properly defined in views
- Restart Odoo container to reload menu items

---

## InsightPulse AI Custom Modules

### Successfully Loaded Modules (Odoo 18)

| Module | State | Application | Notes |
|--------|-------|-------------|-------|
| **ip_expense_mvp** | uninstalled | Yes | InsightPulse Expense MVP - Ready to install |
| **ipai_mattermost_bridge** | uninstalled | No | IPAI Mattermost Bridge - Ready to install |
| **ip_superset_integration** | uninstalled | No | Superset Integration - Ready to install |
| **ipai_auth_fix** | to upgrade | No | Auth fix module - Needs upgrade |

### Blocked Modules

| Module | Issue | Solution |
|--------|-------|----------|
| **pulser_webhook** | Missing dependencies: project, sale_management, purchase | Install dependencies or make them optional |

---

## Verification Checklist

Before seeking help, verify:

- [ ] Module exists in `custom_addons/` directory
- [ ] `__manifest__.py` is valid Python (no syntax errors)
- [ ] `installable: True` in manifest
- [ ] Version matches Odoo version (18.0.x.x.x for Odoo 18)
- [ ] All dependencies are installed or available
- [ ] addons_path includes the custom_addons directory
- [ ] Docker volume is properly mounted
- [ ] Module list has been updated (`--update=base`)
- [ ] Odoo container has been restarted
- [ ] No errors in Odoo logs: `docker logs insightpulse-odoo-odoo-1`

---

## Manual Module Installation

If a module appears in Apps but won't install via UI, try CLI:

```bash
# Install specific module
docker exec insightpulse-odoo-odoo-1 \
  odoo -d odoo19 -i module_name --stop-after-init --no-http

# Restart Odoo
docker restart insightpulse-odoo-odoo-1
```

---

## Automated Workflow

See `.github/workflows/odoo-module-update.yml` for automated module discovery and installation in CI/CD.

---

## Support

**Project:** InsightPulse AI
**Repository:** https://github.com/jgtolentino/insightpulse-odoo
**Maintainer:** InsightPulse AI Team
**Odoo Version:** 18.0 Community Edition

