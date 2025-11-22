# InsightPulse ERP – Production Module Installation Sequence

**Target Server**: `erp.insightpulseai.net` (odoo-erp-prod droplet)
**Odoo Version**: 18.0-20251106
**Database**: `odoo`
**Baseline**: v0.2.1-quality (CE-only, 0 Enterprise modules)

---

## Pre-Installation Checklist

### 1. Verify Current State
```bash
# SSH to production server
ssh root@erp.insightpulseai.net

# Check installed modules count
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT license, COUNT(*) FROM ir_module_module WHERE state = 'installed' GROUP BY license;"

# Expected output:
# AGPL-3: 15 (OCA modules)
# LGPL-3: 154 (Odoo CE core)
# Total: 169 modules
```

### 2. Create Database Backup
```bash
# Create timestamped backup
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
docker exec odoo-db-1 pg_dump -U odoo odoo > \
  /var/backups/odoo_pre_v1_install_${BACKUP_DATE}.sql

# Verify backup size (should be ~38MB+)
ls -lh /var/backups/odoo_pre_v1_install_*.sql | tail -1
```

### 3. Stop Odoo Service
```bash
# Stop Odoo container (if needed for module installation)
docker stop odoo-odoo-1
```

---

## Phase 1: Verify Core CE Modules (Already Installed)

These modules are part of the base Odoo CE 18 installation. **No action needed**, just verification.

```bash
# Verify core modules are installed
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, state FROM ir_module_module WHERE name IN (
    'base', 'web', 'mail', 'contacts', 'calendar',
    'hr', 'hr_expense', 'hr_holidays',
    'account', 'account_accountant',
    'project', 'stock', 'stock_account',
    'maintenance', 'knowledge'
  ) ORDER BY name;"

# All should show state = 'installed'
```

**Expected Modules (Core CE)**:
- ✅ `base` - Core framework
- ✅ `web` - Web UI
- ✅ `mail` - Messaging and activities
- ✅ `contacts` - Contacts/partners
- ✅ `calendar` - Calendar and events
- ✅ `hr` - Human Resources
- ✅ `hr_expense` - Expense management
- ✅ `hr_holidays` - Time Off
- ✅ `account` - Accounting
- ✅ `account_accountant` - Accounting features
- ✅ `project` - Project management
- ✅ `stock` - Inventory management
- ✅ `stock_account` - Inventory accounting
- ✅ `maintenance` - Maintenance management
- ✅ `knowledge` - Knowledge base / wiki

---

## Phase 2: Install Custom InsightPulse Modules

### Module Installation Order (CRITICAL - Follow Sequence)

**Install in this exact order due to dependencies:**

1. `ipai_ce_cleaner` ✅ **INSTALLED**
2. `ipai_ocr_expense` ✅ **INSTALLED**
3. `ipai_expense` ⏳ **PENDING**
4. `ipai_equipment` ⏳ **PENDING**
5. `ipai_finance_monthly_closing` ⏳ **PENDING**

### 1. ipai_ce_cleaner (ALREADY INSTALLED)

**Status**: ✅ Installed and active

**Verification**:
```bash
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, state, license FROM ir_module_module WHERE name = 'ipai_ce_cleaner';"

# Expected: ipai_ce_cleaner | installed | AGPL-3
```

**Rollback** (if needed):
```bash
ssh root@erp.insightpulseai.net \
  "docker exec odoo-odoo-1 odoo -d odoo -u ipai_ce_cleaner --workers=0 --stop-after-init"
```

---

### 2. ipai_ocr_expense (ALREADY INSTALLED)

**Status**: ✅ Installed and active

**Verification**:
```bash
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, state, license FROM ir_module_module WHERE name = 'ipai_ocr_expense';"

# Expected: ipai_ocr_expense | installed | AGPL-3
```

**Check OCR Log Model**:
```bash
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT COUNT(*) FROM ocr_expense_log;"

# Should return count (may be 0 if no scans yet)
```

---

### 3. ipai_expense (TO INSTALL)

**Purpose**: PH-focused expense and travel workflows

**Dependencies**: `hr_expense`, `account`, `project`, `ipai_ocr_expense`

**Pre-Installation Check**:
```bash
# Verify module directory exists
ssh root@erp.insightpulseai.net "ls -la /opt/odoo-ce/addons/ipai_expense/"

# Verify __manifest__.py is valid
ssh root@erp.insightpulseai.net "python3 -m py_compile /opt/odoo-ce/addons/ipai_expense/__manifest__.py"
```

**Installation Command**:
```bash
ssh root@erp.insightpulseai.net \
  "docker exec odoo-odoo-1 odoo -d odoo -i ipai_expense --workers=0 --stop-after-init 2>&1 | tail -50"
```

**Post-Installation Verification**:
```bash
# Check module installed
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, state, license FROM ir_module_module WHERE name = 'ipai_expense';"

# Check travel request model created
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'travel_request';"
# Should return 1 if model exists
```

**Restart Odoo**:
```bash
ssh root@erp.insightpulseai.net "docker restart odoo-odoo-1"

# Wait 10 seconds for startup
sleep 10

# Check logs
ssh root@erp.insightpulseai.net "docker logs odoo-odoo-1 --tail 30"
```

---

### 4. ipai_equipment (TO INSTALL)

**Purpose**: Equipment catalog, booking, and incident management

**Dependencies**: `stock`, `maintenance`, `project`, `calendar`

**Pre-Installation Check**:
```bash
# Verify module directory exists
ssh root@erp.insightpulseai.net "ls -la /opt/odoo-ce/addons/ipai_equipment/"

# Verify __manifest__.py is valid
ssh root@erp.insightpulseai.net "python3 -m py_compile /opt/odoo-ce/addons/ipai_equipment/__manifest__.py"
```

**Installation Command**:
```bash
ssh root@erp.insightpulseai.net \
  "docker exec odoo-odoo-1 odoo -d odoo -i ipai_equipment --workers=0 --stop-after-init 2>&1 | tail -50"
```

**Post-Installation Verification**:
```bash
# Check module installed
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, state, license FROM ir_module_module WHERE name = 'ipai_equipment';"

# Check equipment models created
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT table_name FROM information_schema.tables
   WHERE table_name IN ('equipment_asset', 'equipment_booking', 'equipment_incident');"
# Should return 3 tables
```

**Restart Odoo**:
```bash
ssh root@erp.insightpulseai.net "docker restart odoo-odoo-1 && sleep 10"
ssh root@erp.insightpulseai.net "docker logs odoo-odoo-1 --tail 30"
```

---

### 5. ipai_finance_monthly_closing (TO INSTALL)

**Purpose**: Finance closing tasks with BIR workflows

**Dependencies**: `project`, `account`, `knowledge`, `mail`

**Pre-Installation Check**:
```bash
# Verify module directory exists
ssh root@erp.insightpulseai.net "ls -la /opt/odoo-ce/addons/ipai_finance_monthly_closing/"

# Verify __manifest__.py is valid
ssh root@erp.insightpulseai.net \
  "python3 -m py_compile /opt/odoo-ce/addons/ipai_finance_monthly_closing/__manifest__.py"
```

**Installation Command**:
```bash
ssh root@erp.insightpulseai.net \
  "docker exec odoo-odoo-1 odoo -d odoo -i ipai_finance_monthly_closing --workers=0 --stop-after-init 2>&1 | tail -50"
```

**Post-Installation Verification**:
```bash
# Check module installed
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, state, license FROM ir_module_module WHERE name = 'ipai_finance_monthly_closing';"

# Check project.task has new fields
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT column_name FROM information_schema.columns
   WHERE table_name = 'project_task'
   AND column_name IN ('cluster', 'relative_due', 'owner_code', 'bir_form', 'bir_deadline');"
# Should return 5 columns
```

**Restart Odoo**:
```bash
ssh root@erp.insightpulseai.net "docker restart odoo-odoo-1 && sleep 10"
ssh root@erp.insightpulseai.net "docker logs odoo-odoo-1 --tail 30"
```

---

## Phase 3: Post-Installation Tasks

### 1. Verify All Custom Modules Installed
```bash
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, state, license FROM ir_module_module
   WHERE name LIKE 'ipai_%' ORDER BY name;"

# Expected output (5 modules):
# ipai_ce_cleaner          | installed | AGPL-3
# ipai_equipment           | installed | AGPL-3
# ipai_expense             | installed | AGPL-3
# ipai_finance_monthly_closing | installed | AGPL-3
# ipai_ocr_expense         | installed | AGPL-3
```

### 2. Verify License Compliance (CE-Only)
```bash
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT license, COUNT(*) FROM ir_module_module
   WHERE state = 'installed' GROUP BY license ORDER BY license;"

# Expected output:
# AGPL-3: ~20 (OCA + InsightPulse custom)
# LGPL-3: ~154 (Odoo CE core)
# Total: ~174 modules
# Enterprise licenses (OPL-1/OEEL-1): 0
```

### 3. Verify odoo.com Links Cleaned
```bash
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT COUNT(*) as odoo_links FROM ir_module_module WHERE website LIKE '%odoo.com%';"

# Expected: 0
```

### 4. Create Post-Installation Backup
```bash
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
docker exec odoo-db-1 pg_dump -U odoo odoo > \
  /var/backups/odoo_post_v1_install_${BACKUP_DATE}.sql

ls -lh /var/backups/odoo_post_v1_install_*.sql | tail -1
```

### 5. Restart Odoo with Full Workers
```bash
# Start Odoo normally (not stop-after-init mode)
docker restart odoo-odoo-1

# Wait for startup
sleep 15

# Verify all workers alive
docker logs odoo-odoo-1 --tail 50 | grep "Worker.*alive"

# Should see:
# Worker WorkerHTTP (33) alive
# Worker WorkerHTTP (34) alive
# Worker WorkerHTTP (36) alive
# Worker WorkerHTTP (38) alive
# Worker WorkerCron (41) alive
```

---

## Phase 4: External Service Configuration

### 1. OCR Adapter Configuration (ALREADY DONE)

**Status**: ✅ Complete

**Verification**:
```bash
# Test OCR adapter endpoint
curl -s https://ocr.insightpulseai.net/health | jq

# Test Odoo System Parameter
ssh root@erp.insightpulseai.net \
  "docker exec odoo-db-1 psql -U odoo -d odoo -c \
   \"SELECT key, value FROM ir_config_parameter WHERE key LIKE '%ocr%';\""
```

### 2. n8n Workflows (TO DEPLOY)

**Workflows to Deploy**:
1. Daily pending expenses reminder
2. Ready to Post → closing task sync
3. BIR deadline alerts (7 days before)
4. Equipment booking → calendar sync

**Deployment Location**: n8n at `https://ipa.insightpulseai.net`

**Deployment Commands**:
```bash
# Export workflows from n8n UI or CLI
# Import to production n8n instance
# Activate workflows
```

### 3. Superset Dashboards (OPTIONAL)

**Dashboards to Create**:
1. Expense analytics
2. Equipment utilization
3. Closing SLA performance

**Connection**: Direct PostgreSQL read-only user

---

## Phase 5: Data Migration & Setup

### 1. Import Month-end Closing Template

**Template Project**: "Month-end Closing – Template"

**CSV Import** (from `data/finance_closing_template.csv`):
```bash
# Upload CSV via Odoo UI: Project > Import
# Or use RPC script to import programmatically
```

### 2. Create Active Closing Project

**Project Name**: "Month-end Closing – Nov 2025" (example)

**Tasks Import**:
- Import from template or CSV
- Calculate due dates from relative_due + current month
- Assign owners, reviewers, approvers

### 3. Create Knowledge Pages

**Workspace**: "Finance SSC Documentation"

**Pages to Create**:
- Closing SOP – Cluster A (General Ledger)
- Closing SOP – Cluster B (Accounts Payable)
- Closing SOP – Cluster C (Accounts Receivable)
- Closing SOP – Cluster D (Payroll & HR)
- BIR Calendar – 2025
- BIR Form Guides (1601-C, 1602, 2550Q)

### 4. Equipment Catalog Setup (If Deploying Cheqroom-equivalent)

**Categories to Create**:
- Cameras
- Lenses
- Audio
- Lighting
- Grip

**Assets to Create**:
- Import from spreadsheet or manual entry
- Include asset ID, serial number, location, value

---

## Phase 6: Testing & Validation

### 1. Smoke Tests

**OCR Expense Test**:
```bash
# Upload sample receipt via Odoo UI
# Click "Scan with InsightPulse OCR"
# Verify fields auto-populated
# Check ocr.expense.log created
```

**Equipment Booking Test**:
```bash
# Create equipment booking
# Verify conflict detection
# Check-out equipment
# Check-in equipment with notes
```

**Closing Task Test**:
```bash
# Create monthly closing project
# Import tasks from template
# Move task through stages
# Verify notifications sent
```

### 2. Performance Tests

**Response Time**:
```bash
# List view load time should be < 2s
# Form view load time should be < 1s
```

**OCR Processing**:
```bash
# P95 should be < 30s per receipt
```

### 3. Security Tests

**CE-Only Validation**:
```bash
# Run license compliance check (should show 0 Enterprise)
# Verify no odoo.com links in UI
# Check ipai_ce_cleaner CSS rules active
```

---

## Rollback Procedures

### If Module Installation Fails

1. **Stop Odoo**:
```bash
docker stop odoo-odoo-1
```

2. **Restore from Backup**:
```bash
# Find latest pre-install backup
ls -lh /var/backups/odoo_pre_v1_install_*.sql

# Restore
docker exec -i odoo-db-1 psql -U odoo -d odoo < /var/backups/odoo_pre_v1_install_YYYYMMDD_HHMMSS.sql
```

3. **Restart Odoo**:
```bash
docker start odoo-odoo-1
```

4. **Verify Restoration**:
```bash
docker exec odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT COUNT(*) FROM ir_module_module WHERE state = 'installed';"
# Should match pre-install count (169 modules)
```

---

## Post-Installation Checklist

- [ ] All custom modules installed and active
- [ ] License compliance verified (CE-only, 0 Enterprise)
- [ ] odoo.com links cleaned (0 remaining)
- [ ] OCR adapter accessible and configured
- [ ] Database backups created (pre and post installation)
- [ ] Odoo restarted with all workers alive
- [ ] Smoke tests passed for all products
- [ ] Performance metrics within acceptable range
- [ ] Security validation passed
- [ ] User documentation updated
- [ ] Admin team notified of new features

---

**Last Updated**: 2025-11-21
**Baseline Version**: v0.2.1-quality → v1.0.0 (target)
**Installation Time Estimate**: 2-3 hours (including testing)
