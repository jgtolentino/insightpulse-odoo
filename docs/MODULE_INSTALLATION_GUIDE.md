# Odoo Module Installation Guide - InsightPulse AI

**Last Updated:** 2025-11-09
**Odoo Version:** **19.0 CE** (deployed from source)
**Environment:** Production (165.227.10.178 / erp.insightpulseai.net)

⚠️ **Version Notice:** This project deploys **Odoo 19.0 CE** (confirmed in Dockerfile), not 18.0 as stated in some documentation. See [Version Discrepancy](#version-discrepancy) section.

---

## Table of Contents

1. [Overview](#overview)
2. [Module Types](#module-types)
3. [Installation Methods](#installation-methods)
4. [OCA Module Installation](#oca-module-installation)
5. [IPAI Custom Module Installation](#ipai-custom-module-installation)
6. [Module Update Procedures](#module-update-procedures)
7. [Troubleshooting](#troubleshooting)
8. [Version Discrepancy](#version-discrepancy)

---

## Overview

InsightPulse AI uses three types of Odoo modules:

1. **Odoo CE Core Modules** - Bundled with Odoo 19.0 source
2. **OCA Community Modules** - Community-maintained modules from Odoo Community Association
3. **IPAI Custom Modules** - Custom modules developed for InsightPulse AI

All modules are managed via Odoo's module system and stored in addons paths.

### Module Locations

```
/opt/odoo-src/                           # Odoo 19.0 CE source
├── odoo/                                # Core Odoo modules
│   └── addons/                          # Standard Odoo modules
└── addons/                              # OCA modules bundled with Odoo

/mnt/extra-addons/                       # Custom modules (mounted volume)
├── custom_addons/                       # OCA modules (downloaded separately)
│   ├── account-financial-tools/
│   ├── account-invoicing/
│   ├── expense-management/
│   └── ...
└── ipai_modules/                        # IPAI custom modules
    ├── expense_mgmt/
    ├── bir_compliance/
    ├── vendor_portal/
    └── ...
```

### Addons Path Configuration

Odoo configuration (`/etc/odoo/odoo.conf`):

```ini
[options]
addons_path = /opt/odoo-src/odoo/addons,/opt/odoo-src/addons,/mnt/extra-addons/custom_addons,/mnt/extra-addons/ipai_modules
```

---

## Module Types

### 1. Odoo CE Core Modules

**Source:** https://github.com/odoo/odoo/tree/19.0/addons

**Examples:**
- `account` - Accounting
- `hr` - Human Resources
- `sale` - Sales Management
- `purchase` - Purchase Management
- `stock` - Inventory Management

**Installation:**
Bundled with Odoo source, available by default.

**Usage:**
```bash
# Enable via Odoo UI
Apps → Search "Accounting" → Install

# Or via CLI
/opt/odoo-src/odoo-bin -c /etc/odoo/odoo.conf -d postgres -i account --stop-after-init
```

### 2. OCA Community Modules

**Source:** https://github.com/OCA (Odoo Community Association)

**Key OCA Repositories for 19.0:**
- https://github.com/OCA/account-financial-tools (19.0 branch)
- https://github.com/OCA/account-invoicing (19.0 branch)
- https://github.com/OCA/hr-expense (19.0 branch)
- https://github.com/OCA/server-tools (19.0 branch)
- https://github.com/OCA/web (19.0 branch)

**Examples:**
- `account_move_batch_validate` - Batch invoice validation
- `hr_expense_sequence` - Expense report numbering
- `base_exception` - Exception handling framework
- `web_responsive` - Responsive UI improvements

### 3. IPAI Custom Modules

**Source:** `/mnt/extra-addons/ipai_modules/`

**Examples:**
- `expense_mgmt` - Multi-agency expense management
- `bir_compliance` - BIR Forms 2307, 2316, e-invoicing
- `vendor_portal` - Privacy-first vendor portals
- `scout_integration` - Scout transaction data integration

**License:** AGPL-3 (Odoo Community Association standard)

---

## Installation Methods

### Method 1: Via Odoo UI (Recommended for Production)

1. **Access Apps Menu:**
   ```
   Navigate to: https://erp.insightpulseai.net/web#action=
   Click: Apps
   ```

2. **Update Apps List:**
   ```
   Click: ⚙️ (gear icon in search bar)
   Select: "Update Apps List"
   Confirm: Update
   ```

3. **Search and Install:**
   ```
   Search: "expense" (example)
   Find module: "Expense Management"
   Click: Install
   Wait for installation to complete
   ```

4. **Verify Installation:**
   ```sql
   -- Check module state
   psql "$POSTGRES_URL" -c "
   SELECT name, state, latest_version
   FROM ir_module_module
   WHERE name = 'expense_mgmt';
   "
   ```

### Method 2: Via Command Line (For Automation/CI)

```bash
# SSH to droplet
ssh root@165.227.10.178

# Navigate to Odoo directory
cd /opt/odoo-src

# Install module
sudo -u odoo ./odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d postgres \
  -i expense_mgmt \
  --stop-after-init

# Restart Odoo service
systemctl restart odoo

# Verify installation
systemctl status odoo
```

### Method 3: Via SQL (Direct Database - Use with Caution)

```sql
-- Connect to Supabase
psql "postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres"

-- Mark module for installation
UPDATE ir_module_module
SET state = 'to install'
WHERE name = 'expense_mgmt' AND state = 'uninstalled';

-- Restart Odoo to apply changes
-- (Odoo will automatically install marked modules on restart)
```

**⚠️ Warning:** SQL method requires Odoo restart and doesn't run module dependencies automatically. Use UI or CLI methods for safety.

---

## OCA Module Installation

### Step-by-Step: Install OCA Modules

#### Step 1: Download OCA Repository

```bash
# SSH to droplet
ssh root@165.227.10.178

# Navigate to custom addons directory
cd /mnt/extra-addons/custom_addons

# Clone OCA repository (example: account-financial-tools)
git clone --depth 1 --branch 19.0 \
  https://github.com/OCA/account-financial-tools.git

# Verify modules available
ls -la account-financial-tools/
```

**Expected Output:**
```
account-financial-tools/
├── account_move_batch_validate/
├── account_netting/
├── account_template_active/
├── ...
└── README.md
```

#### Step 2: Update Odoo Addons Path

Edit `/etc/odoo/odoo.conf`:

```ini
[options]
addons_path = /opt/odoo-src/odoo/addons,/opt/odoo-src/addons,/mnt/extra-addons/custom_addons/account-financial-tools,/mnt/extra-addons/ipai_modules
```

**Or add to existing path:**
```bash
# Backup config
sudo cp /etc/odoo/odoo.conf /etc/odoo/odoo.conf.backup

# Append new path
sudo sed -i 's|addons_path = \(.*\)|addons_path = \1,/mnt/extra-addons/custom_addons/account-financial-tools|' /etc/odoo/odoo.conf

# Verify
grep addons_path /etc/odoo/odoo.conf
```

#### Step 3: Restart Odoo

```bash
sudo systemctl restart odoo

# Verify service started successfully
sudo systemctl status odoo

# Check logs for errors
sudo journalctl -u odoo -n 50 --no-pager
```

#### Step 4: Install Module via UI

1. Navigate to `Apps` menu
2. Click `Update Apps List`
3. Search for module (e.g., "account_move_batch_validate")
4. Click `Install`

#### Step 5: Verify Installation

```sql
-- Check module state
psql "$POSTGRES_URL" -c "
SELECT
  m.name,
  m.state,
  m.latest_version,
  m.author
FROM ir_module_module m
WHERE m.name LIKE 'account_move%'
ORDER BY m.name;
"
```

**Expected Output:**
```
       name               |  state    | latest_version |     author
--------------------------+-----------+----------------+----------------
 account_move_batch_validate | installed | 19.0.1.0.0 | Odoo Community Association (OCA)
```

### Popular OCA Modules for InsightPulse AI

| Module | Repository | Purpose |
|--------|------------|---------|
| `account_move_batch_validate` | account-financial-tools | Batch invoice validation |
| `hr_expense_sequence` | hr-expense | Expense report numbering |
| `base_exception` | server-tools | Exception handling framework |
| `web_responsive` | web | Mobile-friendly UI |
| `date_range` | server-tools | Date range picker widget |
| `account_financial_report` | account-financial-reporting | Financial reports |

---

## IPAI Custom Module Installation

### Step-by-Step: Install IPAI Custom Modules

#### Step 1: Verify Module Structure

```bash
# Check module directory exists
ls -la /mnt/extra-addons/ipai_modules/expense_mgmt/

# Verify required files
ls -la /mnt/extra-addons/ipai_modules/expense_mgmt/__manifest__.py
ls -la /mnt/extra-addons/ipai_modules/expense_mgmt/models/
ls -la /mnt/extra-addons/ipai_modules/expense_mgmt/views/
ls -la /mnt/extra-addons/ipai_modules/expense_mgmt/security/
```

**Required Files:**
```
expense_mgmt/
├── __init__.py
├── __manifest__.py          # Module metadata
├── models/
│   ├── __init__.py
│   └── expense_report.py    # Python models
├── views/
│   ├── expense_report_views.xml
│   └── menu.xml
├── security/
│   ├── ir.model.access.csv  # Access rights
│   └── expense_security.xml # Record rules
├── data/
│   └── expense_data.xml     # Demo/initial data
└── tests/
    └── test_expense_report.py
```

#### Step 2: Validate __manifest__.py

```bash
# Check manifest syntax
python3 -c "import ast; ast.parse(open('/mnt/extra-addons/ipai_modules/expense_mgmt/__manifest__.py').read())"

# View manifest content
cat /mnt/extra-addons/ipai_modules/expense_mgmt/__manifest__.py
```

**Expected Content:**
```python
{
    'name': 'Expense Management',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Multi-agency expense management with BIR compliance',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': ['account', 'hr', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/expense_security.xml',
        'views/expense_report_views.xml',
        'views/menu.xml',
        'data/expense_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

#### Step 3: Install via CLI

```bash
# Install module with dependency resolution
sudo -u odoo /opt/odoo-src/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d postgres \
  -i expense_mgmt \
  --stop-after-init \
  --log-level=info

# Check installation output
tail -n 100 /var/log/odoo/odoo.log | grep -E "expense_mgmt|ERROR|WARNING"
```

**Expected Output:**
```
INFO postgres odoo.modules.loading: loading 1 modules...
INFO postgres odoo.modules.loading: 1 modules loaded in 0.05s, 0 queries
INFO postgres odoo.modules.module: module expense_mgmt: creating or updating database tables
INFO postgres odoo.modules.loading: loading expense_mgmt/security/ir.model.access.csv
INFO postgres odoo.modules.loading: loading expense_mgmt/views/expense_report_views.xml
INFO postgres odoo.modules.loading: Module expense_mgmt installed
```

#### Step 4: Restart Odoo

```bash
sudo systemctl restart odoo
sudo systemctl status odoo
```

#### Step 5: Verify via UI

1. Navigate to `Apps` menu
2. Search "Expense Management"
3. Verify status shows "Installed"
4. Check main menu for "Expense" menu item

#### Step 6: Verify Database Tables

```sql
-- Check tables created
psql "$POSTGRES_URL" -c "
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename LIKE 'expense%'
ORDER BY tablename;
"
```

**Expected Output:**
```
       tablename
-----------------------
 expense_report
 expense_report_line
 expense_category
```

#### Step 7: Test Module Functionality

```sql
-- Create test expense report
INSERT INTO expense_report (name, employee_id, company_id, date_submitted)
VALUES ('Test Expense Report', 1, 1, NOW())
RETURNING id, name, state;

-- Verify creation
SELECT id, name, state, create_date
FROM expense_report
WHERE name = 'Test Expense Report';
```

---

## Module Update Procedures

### Updating OCA Modules

```bash
# SSH to droplet
ssh root@165.227.10.178

# Navigate to OCA repository
cd /mnt/extra-addons/custom_addons/account-financial-tools

# Pull latest changes
git fetch origin 19.0
git pull origin 19.0

# Check for module updates
git log --oneline -n 10

# Restart Odoo
sudo systemctl restart odoo

# Update module via CLI
sudo -u odoo /opt/odoo-src/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d postgres \
  -u account_move_batch_validate \
  --stop-after-init

# Restart Odoo again
sudo systemctl restart odoo
```

### Updating IPAI Custom Modules

```bash
# Navigate to module directory
cd /mnt/extra-addons/ipai_modules/expense_mgmt

# Edit files as needed
nano models/expense_report.py

# Increment version in __manifest__.py
nano __manifest__.py
# Change: 'version': '19.0.1.0.0' → '19.0.1.0.1'

# Update module via CLI
sudo -u odoo /opt/odoo-src/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d postgres \
  -u expense_mgmt \
  --stop-after-init

# Restart Odoo
sudo systemctl restart odoo
```

### Database Migration (Major Changes)

For schema changes (new fields, tables, constraints):

```bash
# Step 1: Create backup
pg_dump "$POSTGRES_URL" | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Step 2: Update module code
# (Edit Python models, XML views, etc.)

# Step 3: Update module with migration mode
sudo -u odoo /opt/odoo-src/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d postgres \
  -u expense_mgmt \
  --stop-after-init \
  --log-level=debug

# Step 4: Verify migration logs
tail -n 200 /var/log/odoo/odoo.log | grep -E "migration|ALTER TABLE|CREATE TABLE"

# Step 5: Test in UI
# Navigate to module and verify changes

# Step 6: If successful, restart Odoo
sudo systemctl restart odoo

# Step 7: If failed, restore backup
# gunzip -c backup_YYYYMMDD_HHMMSS.sql.gz | psql "$POSTGRES_URL"
```

---

## Troubleshooting

### Issue: Module Not Appearing in Apps List

**Symptoms:**
- Module directory exists
- Module not showing in Apps menu after "Update Apps List"

**Solutions:**

1. **Verify addons path:**
   ```bash
   grep addons_path /etc/odoo/odoo.conf
   # Ensure module directory is included
   ```

2. **Check file permissions:**
   ```bash
   ls -la /mnt/extra-addons/ipai_modules/expense_mgmt/
   # Should be owned by odoo:odoo
   sudo chown -R odoo:odoo /mnt/extra-addons/ipai_modules/
   ```

3. **Validate __manifest__.py:**
   ```bash
   python3 -c "import ast; ast.parse(open('/mnt/extra-addons/ipai_modules/expense_mgmt/__manifest__.py').read())"
   # Should return no errors
   ```

4. **Check Odoo logs:**
   ```bash
   sudo journalctl -u odoo -n 100 | grep -E "expense_mgmt|ERROR"
   ```

5. **Restart Odoo with verbose logging:**
   ```bash
   sudo systemctl stop odoo
   sudo -u odoo /opt/odoo-src/odoo-bin \
     -c /etc/odoo/odoo.conf \
     -d postgres \
     --log-level=debug
   # Watch for loading errors
   ```

### Issue: Module Installation Fails

**Symptoms:**
- Error message during installation
- Module state stuck on "To Install"

**Solutions:**

1. **Check dependency modules:**
   ```sql
   -- View module dependencies
   SELECT dep.name AS depends_on
   FROM ir_module_module_dependency dep
   JOIN ir_module_module m ON m.id = dep.module_id
   WHERE m.name = 'expense_mgmt';

   -- Install missing dependencies first
   ```

2. **Check database constraints:**
   ```bash
   # Look for constraint violations in logs
   sudo journalctl -u odoo -n 200 | grep -E "constraint|foreign key|unique"
   ```

3. **Try manual SQL installation:**
   ```sql
   -- Mark dependencies as installed
   UPDATE ir_module_module
   SET state = 'installed'
   WHERE name IN ('account', 'hr', 'mail');

   -- Then try module installation again
   ```

4. **Check for conflicting modules:**
   ```sql
   -- Find modules with similar names
   SELECT name, state FROM ir_module_module
   WHERE name LIKE '%expense%'
   ORDER BY name;
   ```

### Issue: Module Update Fails

**Symptoms:**
- Error during module update
- Old version still active after update

**Solutions:**

1. **Force module upgrade:**
   ```bash
   sudo -u odoo /opt/odoo-src/odoo-bin \
     -c /etc/odoo/odoo.conf \
     -d postgres \
     -u expense_mgmt \
     --stop-after-init \
     --log-level=debug \
     2>&1 | tee /tmp/upgrade.log
   ```

2. **Clear Odoo cache:**
   ```sql
   -- Clear view cache
   DELETE FROM ir_ui_view WHERE model LIKE 'expense%';

   -- Clear attachment cache
   DELETE FROM ir_attachment WHERE res_model LIKE 'expense%';

   -- Restart Odoo
   ```

3. **Check for view inheritance conflicts:**
   ```bash
   sudo journalctl -u odoo -n 200 | grep -E "view|xpath|inherit"
   ```

4. **Manually update module version:**
   ```sql
   UPDATE ir_module_module
   SET latest_version = '19.0.1.0.1',
       write_date = NOW()
   WHERE name = 'expense_mgmt';
   ```

### Issue: Access Denied After Module Installation

**Symptoms:**
- Users cannot access module features
- "Access Denied" errors in UI

**Solutions:**

1. **Verify access rights CSV:**
   ```bash
   cat /mnt/extra-addons/ipai_modules/expense_mgmt/security/ir.model.access.csv
   ```

   **Expected Format:**
   ```csv
   id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
   access_expense_report_user,expense.report.user,model_expense_report,base.group_user,1,1,1,0
   access_expense_report_manager,expense.report.manager,model_expense_report,account.group_account_manager,1,1,1,1
   ```

2. **Grant access to user groups:**
   ```sql
   -- Find group IDs
   SELECT id, name FROM res_groups WHERE name LIKE '%Accounting%';

   -- Check current access rights
   SELECT
     a.name,
     m.model,
     g.name AS group_name,
     a.perm_read,
     a.perm_write,
     a.perm_create,
     a.perm_unlink
   FROM ir_model_access a
   JOIN ir_model m ON m.id = a.model_id
   LEFT JOIN res_groups g ON g.id = a.group_id
   WHERE m.model LIKE 'expense%'
   ORDER BY m.model, g.name;
   ```

3. **Assign users to required groups:**
   ```sql
   -- Find user ID
   SELECT id, login, name FROM res_users WHERE login = 'jgtolentino_rn@yahoo.com';

   -- Find group ID
   SELECT id, name FROM res_groups WHERE name = 'Accounting / Billing';

   -- Assign user to group
   INSERT INTO res_groups_users_rel (gid, uid)
   VALUES (
     (SELECT id FROM res_groups WHERE name = 'Accounting / Billing'),
     (SELECT id FROM res_users WHERE login = 'jgtolentino_rn@yahoo.com')
   )
   ON CONFLICT DO NOTHING;
   ```

### Issue: Module Breaking Odoo After Installation

**Symptoms:**
- Odoo service fails to start
- White screen or 500 errors

**Solutions:**

1. **Uninstall problematic module:**
   ```sql
   -- Mark module for uninstallation
   UPDATE ir_module_module
   SET state = 'to remove'
   WHERE name = 'expense_mgmt';

   -- Restart Odoo to apply
   ```

2. **Restore from backup:**
   ```bash
   # Stop Odoo
   sudo systemctl stop odoo

   # Restore database
   gunzip -c backup_YYYYMMDD_HHMMSS.sql.gz | psql "$POSTGRES_URL"

   # Start Odoo
   sudo systemctl start odoo
   ```

3. **Check Python syntax errors:**
   ```bash
   python3 -m py_compile /mnt/extra-addons/ipai_modules/expense_mgmt/models/*.py
   python3 -m py_compile /mnt/extra-addons/ipai_modules/expense_mgmt/__init__.py
   ```

4. **Validate XML syntax:**
   ```bash
   xmllint --noout /mnt/extra-addons/ipai_modules/expense_mgmt/views/*.xml
   ```

---

## Version Discrepancy

⚠️ **Critical Notice:** Configuration Drift Detected

**Deployed Version:**
- **Dockerfile (line 57):** `git clone --branch 19.0 https://github.com/odoo/odoo.git`
- **Actual Deployment:** Odoo 19.0 CE

**Documented Version:**
- **claude.md:** States "Odoo 18 CE" throughout
- **API References:** Point to Odoo 18.0 documentation

### Impact Analysis

**What Works:**
- ✅ Odoo 19.0 deployment is successful (post-psycopg2 fix)
- ✅ OCA modules have 19.0 branches available
- ✅ Most Odoo 18 → 19 migrations are backward compatible

**What Needs Updating:**
- ❌ `claude.md` references to "18 CE" → should be "19 CE"
- ❌ API documentation links (odoo.com/documentation/18.0/ → 19.0/)
- ❌ OCA module branch references (18.0 → 19.0)

### Recommendation

**Option 1: Stay on Odoo 19.0 (Recommended)**
- Update all documentation to reflect 19.0 deployment
- Verify OCA modules available for 19.0
- Test compatibility with existing customizations

**Option 2: Downgrade to Odoo 18.0**
- Update Dockerfile to use 18.0 branch
- Redeploy with correct version
- Align with claude.md documentation

### Next Steps

1. **Confirm version strategy** with stakeholders
2. **Update claude.md** to match deployed version
3. **Test critical workflows** on actual version
4. **Document migration path** if downgrade needed

**Tracking Issue:** Create GitHub issue to track version alignment

---

## Reference Links

- **Odoo 19.0 Documentation:** https://www.odoo.com/documentation/19.0/
- **OCA GitHub:** https://github.com/OCA
- **Odoo Apps Store:** https://apps.odoo.com/apps/modules (filter by 19.0)
- **Odoo Developer Docs:** https://www.odoo.com/documentation/19.0/developer.html

---

**Maintainer:** InsightPulse AI Team
**Support:** jgtolentino_rn@yahoo.com
**Last Tested:** 2025-11-09 with Odoo 19.0 CE
**Document Version:** 1.0 (reflects actual deployed version)
