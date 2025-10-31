# Odoo 19 Production Deployment Checklist - Wave 1-3

**Version**: 3.0.0
**Last Updated**: 2025-10-30
**Status**: Production Ready ✅
**Modules**: 10 enterprise modules
**Test Coverage**: 134 test methods, 2,771 lines of tests

## 🚀 Quick Start

```bash
# Clone with submodules (required for ipai_knowledge_ai)
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo
git submodule update --init --recursive

# Run full validation (recommended before deployment)
./scripts/deploy-check.sh --full

# Run quick validation (skip asset rebuild & module updates)
./scripts/deploy-check.sh --quick
```

## ✅ Pre-Deployment Validation

The `deploy-check.sh` script validates **13 critical areas**:

1. **Docker Daemon** - Ensures Docker is running
2. **Container Health** - Validates Odoo + PostgreSQL containers are healthy
3. **Odoo Version** - Confirms Odoo 19.x is installed
4. **Database Connectivity** - Tests PostgreSQL connection and Odoo → DB connectivity
5. **Odoo Configuration** - Validates `proxy_mode`, `workers`, memory limits, logging
6. **Addons Path** - Ensures all configured addon paths exist
7. **Python Dependencies** - Checks psycopg2, requests, werkzeug, lxml
8. **Environment Secrets** - Validates `.env` file and detects hardcoded secrets
9. **Asset Build** - Rebuilds assets in production mode (--full only)
10. **Module Update** - Tests module update functionality (--full only)
11. **Proxy Headers** - Checks HTTP accessibility and security headers
12. **Backup System** - Validates backup directory and permissions
13. **Log Rotation** - Checks Docker log configuration

## 📋 Manual Pre-Deployment Steps

### 1. Environment Configuration

Create/verify `.env` file:

```bash
# Database
POSTGRES_PASSWORD=<strong-password>
PGHOST=db
PGUSER=odoo
PGDATABASE=odoo

# Odoo workers & limits
ODOO_WORKERS=4
ODOO_LIMIT_TIME_CPU=120
ODOO_LIMIT_TIME_REAL=240
ODOO_LIMIT_MEMORY_HARD=2147483648  # 2GB
ODOO_LIMIT_MEMORY_SOFT=1610612736  # 1.5GB
```

### 2. Odoo Configuration

Ensure `config/odoo/odoo.conf` contains:

```ini
[options]
# Database
db_host = db
db_port = 5432
db_user = %(env:PGUSER)s
db_password = %(env:POSTGRES_PASSWORD)s
db_name = false

# Paths (Wave 1-3: All 10 enterprise modules)
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons/insightpulse,/mnt/extra-addons/custom,/mnt/extra-addons/oca,/mnt/extra-addons/bi_superset_agent,/mnt/extra-addons/knowledge_notion_clone

# Server (production)
proxy_mode = True
workers = %(env:ODOO_WORKERS)s
limit_time_cpu = %(env:ODOO_LIMIT_TIME_CPU)s
limit_time_real = %(env:ODOO_LIMIT_TIME_REAL)s
limit_memory_hard = %(env:ODOO_LIMIT_MEMORY_HARD)s
limit_memory_soft = %(env:ODOO_LIMIT_MEMORY_SOFT)s

# Logging
log_level = info
logfile = /var/log/odoo/odoo.log
```

### 3. Docker Compose Configuration

Add health checks to `docker-compose.yml`:

```yaml
services:
  odoo:
    image: your/odoo:19
    env_file: [.env]
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost:8069/web/health || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 10
    volumes:
      - ./config/odoo/odoo.conf:/etc/odoo/odoo.conf:ro
      - odoo-data:/var/lib/odoo

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: odoo
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER -d $POSTGRES_DB -q"]
      interval: 10s
      timeout: 5s
      retries: 10
    volumes:
      - pg-data:/var/lib/postgresql/data

volumes:
  odoo-data:
  pg-data:
```

### 4. Reverse Proxy Configuration

**Caddy Example** (recommended):

```caddy
your.domain.com {
  encode gzip
  reverse_proxy odoo:8069 {
    header_up X-Forwarded-Proto {scheme}
    header_up X-Forwarded-For {remote}
    header_up X-Forwarded-Host {host}
  }
}
```

**Nginx Example**:

```nginx
server {
    listen 443 ssl http2;
    server_name your.domain.com;

    location / {
        proxy_pass http://odoo:8069;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header Host $host;
    }
}
```

## 🔧 Smoke Tests (Manual)

Run these inside Odoo container to verify functionality:

```bash
# 1. Odoo version
docker compose exec odoo python odoo-bin --version

# 2. Database connectivity
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod --stop-after-init

# 3. Module update (test with base module)
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -u base --stop-after-init

# 4. Asset build (clean, non-dev)
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod --dev=none --stop-after-init
```

## 📦 Wave 1-3 Module Installation (10 Enterprise Modules)

### Installation Order

**IMPORTANT**: Install modules in dependency order to avoid errors.

#### Step 1: Foundation Module
```bash
# Install ipai_core first (required by all other modules)
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -i ipai_core --stop-after-init
```

#### Step 2: Finance Modules
```bash
# Install finance modules in order
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod \
  -i ipai_rate_policy,ipai_ppm,ipai_ppm_costsheet,ipai_subscriptions \
  --stop-after-init
```

#### Step 3: Operations Modules
```bash
# Install operations modules
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod \
  -i ipai_saas_ops,ipai_approvals,ipai_procure,ipai_expense \
  --stop-after-init
```

#### Step 4: Analytics & AI Modules
```bash
# Install analytics and AI modules
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod \
  -i superset_connector,ipai_knowledge_ai \
  --stop-after-init
```

### Post-Installation Configuration

#### AI Knowledge Workspace (ipai_knowledge_ai)
```bash
# 1. Enable pgVector extension in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;

# 2. Set environment variables
export OPENAI_API_KEY="sk-proj-your_key"
export POSTGRES_HOST="aws-0-us-east-1.pooler.supabase.com"
export POSTGRES_PORT="6543"
export POSTGRES_USER="postgres.your_project_ref"
export POSTGRES_PASSWORD="your_password"

# 3. Restart Odoo
docker compose restart odoo
```

#### OCR Expense Automation (ipai_expense)
```bash
# Configure OCR service endpoint in Odoo
# Settings → Technical → System Parameters
# Key: ocr.service.endpoint
# Value: https://ade-ocr-backend-d9dru.ondigitalocean.app/v1/parse
```

#### Apache Superset Integration (superset_connector)
```bash
# Install and configure Superset separately
docker run -d -p 8088:8088 apache/superset

# Configure in Odoo: BI → Superset → Settings
# Superset URL: http://localhost:8088
# API Token: [from Superset admin]
```

### Verify Installation

```bash
# Check all 10 modules are installed
docker compose exec db psql -U odoo -d odoo_prod -c "
  SELECT name, latest_version, state
  FROM ir_module_module
  WHERE name LIKE 'ipai_%' OR name IN ('superset_connector')
  ORDER BY name;
"

# Expected output: 10 modules with state='installed'
```

## 📱 Apps Page Truth Sync

**Problem**: Apps page shows incorrect "Install" or "Upgrade" badges that don't match actual deployment state.

**Solution**: Force-sync module registry with actual code state.

### Quick Fix (Automated)

```bash
# Sync everything (module list, versions, assets)
./scripts/apps-truth-sync.sh odoo_prod

# Then in Odoo UI:
# 1. Enable Developer Mode (⋮ menu → Developer Mode)
# 2. Go to Apps → Toggle filter from "Apps" to "All"
# 3. Click ⋮ → Update Apps List
# 4. Apply Scheduled Upgrades (if banner appears)
```

### Manual Steps (If Automated Script Fails)

```bash
# 1. Refresh module list from disk
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -i base --stop-after-init

# 2. Apply pending upgrades (sync DB versions with code)
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -u all --stop-after-init

# 3. Build production assets (clear stale UI badges)
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod --dev=none --stop-after-init
```

### Check Module Versions (Diagnostic)

```bash
# Compare DB versions with code (__manifest__.py)
./scripts/check-module-versions.sh odoo_prod

# List all installed modules with versions
docker compose exec db psql -U odoo -d odoo_prod -c "
  SELECT name, latest_version, state
  FROM ir_module_module
  WHERE state IN ('installed', 'to upgrade')
  ORDER BY name;
"
```

### Common "Upgrade" Badge Issues

**Cause**: Version in `__manifest__.py` > version in `ir_module_module` table.

**Fix Options**:

1. **Update specific module**:
   ```bash
   docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -u <module_name> --stop-after-init
   ```

2. **Update all modules**:
   ```bash
   ./scripts/apps-truth-sync.sh odoo_prod
   ```

3. **Rebuild container** (if code changes not reflected):
   ```bash
   docker compose up -d --build
   ```

### Verify addons_path Configuration

```bash
# Check configured paths
docker compose exec odoo grep addons_path /etc/odoo/odoo.conf

# Verify paths exist
docker compose exec odoo ls -la /usr/lib/python3/dist-packages/odoo/addons
docker compose exec odoo ls -la /mnt/extra-addons
```

**Common Gotchas**:
- Wrong database selected (check top-right → About)
- Stale container after code changes (`docker compose up -d --build`)
- Missing volume mount (check `docker-compose.yml` volumes)
- Filter set to "Apps" instead of "All"

## 🔧 Fixing Broken Modules & KeyNotFoundError

**Problem**: JavaScript error `KeyNotFoundError: <key> not found in registry` when clicking menus or loading pages.

**Root Cause**: Module's JavaScript action is missing from the frontend registry, typically caused by:
- Incomplete module installation
- Broken module upgrade
- Missing dependencies
- Corrupted web assets cache
- Module uninstalled but menus/actions remain in database

### Quick Fix (Automated)

```bash
# 1. Diagnose issues
./scripts/check-broken-modules.sh odoo_prod

# 2. Reinstall broken module
./scripts/odoo-reinstall-module.sh odoo_prod <module_name>

# Example: Fix knowledge_notion_clone
./scripts/odoo-reinstall-module.sh odoo_prod knowledge_notion_clone
```

### Manual Recovery Steps

If automated script fails, follow these steps:

#### Step 1: Identify Broken Module

Check browser console for the exact error:
```
KeyNotFoundError: "knowledge_notion_clone.app" not found in registry
                  ^^^^^^^^^^^^^^^^^^^^^^^^^ (this is your module name)
```

#### Step 2: Uninstall Module Cleanly

```bash
# Access Odoo Python shell
docker compose exec odoo python odoo-bin shell -c /etc/odoo/odoo.conf -d odoo_prod

# In Python shell:
env = odoo.api.Environment(odoo.registry('odoo_prod').cursor(), odoo.SUPERUSER_ID, {})
module = env['ir.module.module'].search([('name', '=', 'knowledge_notion_clone')])
if module:
    module.button_immediate_uninstall()
    env.cr.commit()
```

#### Step 3: Remove and Re-add Module Code

```bash
# For OCA modules
cd addons/oca
rm -rf knowledge
git clone https://github.com/OCA/knowledge.git --depth 1 -b 19.0

# For custom modules
# Update your module code as needed
```

#### Step 4: Reinstall Module

```bash
# Refresh module registry
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -i base --stop-after-init

# Install module
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -i knowledge_notion_clone --stop-after-init

# Update all modules (sync versions)
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -u all --stop-after-init
```

#### Step 5: Rebuild Assets and Purge Cache

```bash
# Build production assets
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod --dev=none --stop-after-init

# Purge web asset cache
docker compose exec odoo rm -rf /var/lib/odoo/.local/share/Odoo/filestore/*/web/assets/*

# Restart Odoo
docker compose restart odoo
```

#### Step 6: Clear Browser Cache

- Hard reload: **Ctrl+Shift+R** (Windows/Linux) or **Cmd+Shift+R** (Mac)
- Or visit: `https://insightpulseai.net/web?debug=assets`
- Check browser console to verify error is gone

### Reinstalling OCA Modules

For modules from OCA repositories:

```bash
# Example: Reinstall knowledge module from OCA
./scripts/odoo-reinstall-module.sh odoo_prod knowledge_notion_clone \
  "https://github.com/OCA/knowledge.git"

# With subdirectory
./scripts/odoo-reinstall-module.sh odoo_prod some_module \
  "https://github.com/OCA/repo-name.git" "subdirectory_path"
```

### Diagnostic Commands

```bash
# Check for broken modules
./scripts/check-broken-modules.sh odoo_prod

# List modules in error states
docker compose exec db psql -U odoo -d odoo_prod -c "
  SELECT name, state, latest_version
  FROM ir_module_module
  WHERE state IN ('to remove', 'uninstallable', 'to upgrade')
  ORDER BY state, name;
"

# Find menus with missing actions
docker compose exec db psql -U odoo -d odoo_prod -c "
  SELECT m.name AS menu_name, m.action
  FROM ir_ui_menu m
  WHERE m.action IS NOT NULL
    AND m.action NOT LIKE 'ir.actions.%';
"

# Check orphaned records
docker compose exec db psql -U odoo -d odoo_prod -c "
  SELECT model, COUNT(*) as count
  FROM ir_model_data
  WHERE res_id IS NOT NULL
  GROUP BY model
  ORDER BY count DESC;
"
```

### Prevention Best Practices

1. **Always use `apps-truth-sync.sh` after code changes**:
   ```bash
   ./scripts/apps-truth-sync.sh odoo_prod
   ```

2. **Test module installations in staging first**

3. **Keep module dependencies up to date**:
   ```bash
   # Update OCA modules
   python3 scripts/vendor_oca_enhanced.py --update
   ```

4. **Use proper uninstall process**:
   - Never delete module code while installed
   - Always uninstall via Odoo UI or `button_immediate_uninstall()`
   - Verify clean uninstall before removing code

5. **Rebuild assets after any module changes**:
   ```bash
   docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod --dev=none --stop-after-init
   ```

### Troubleshooting Matrix

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| KeyNotFoundError on page load | Missing JS action in registry | Reinstall module + rebuild assets |
| Module shows "Upgrade" badge | Version mismatch (DB < code) | `apps-truth-sync.sh` |
| Module shows "Install" but exists | Missing from addons_path | Check docker volume mounts |
| Menu appears but gives error | Orphaned menu record | Reinstall module or remove menu |
| Cannot uninstall module | Foreign key constraints | Force uninstall with Python |
| Assets not updating | Stale cache | Purge `/var/lib/odoo/.../web/assets/` |

### Emergency Recovery

If nothing works:

```bash
# Nuclear option: Full module registry reset
./scripts/odoo-reinstall-module.sh odoo_prod base
./scripts/apps-truth-sync.sh odoo_prod
docker compose restart odoo

# Then reinstall problematic module
./scripts/odoo-reinstall-module.sh odoo_prod <module_name>
```

## 🏢 Enterprise Parity Setup (100+ Modules)

**Goal**: Install 100+ modules (3 IPAI custom + ~97 OCA community modules) to achieve feature parity with Odoo Enterprise Edition.

### Quick Start

```bash
# 1. Sync OCA repositories (30+ repos)
./scripts/sync-oca-repos.sh

# 2. Install all modules (default: all categories)
./scripts/install-enterprise-parity.sh

# 3. Verify installation (100+ modules target)
./scripts/verify-enterprise-parity.sh

# 4. Audit module inventory
./scripts/audit-modules.sh --format table
```

### Module Categories (100+ modules total)

| Category | Count | Description |
|----------|-------|-------------|
| **IPAI Custom** | 3 | ipai_studio (configurator), ipai_sign (eSignature), ipai_knowledge (blocks) |
| **Accounting & Finance** | 12 | Financial reports, payment orders, reconciliation, budgeting, assets |
| **Sales & CRM** | 8 | Quotations, workflows, order types, product sets, invoicing |
| **Purchase & Procurement** | 7 | Purchase requests, approvals, work acceptance, price history |
| **Inventory & Logistics** | 8 | Stock requests, picking links, valuation, putaway, batch management |
| **Project Management** | 6 | Task dependencies, templates, timesheets, key tracking |
| **HR & Timesheets** | 7 | Timesheet sheets, expense sequences, service tracking, auto-close |
| **Helpdesk & Support** | 5 | Helpdesk management, ticketing, timesheet integration |
| **Field Service** | 4 | Field service management, agreements, stock integration |
| **Manufacturing** | 6 | BOM costing, production requests, workorder sequences, subcontracting |
| **Quality & Maintenance** | 5 | Quality control, maintenance equipment, preventive plans |
| **Contracts & Agreements** | 4 | Contract management, invoice integration, legal agreements |
| **Website & eCommerce** | 6 | Product suggestions, wishlists, stock display, branding |
| **eLearning & Knowledge** | 4 | Website slides, surveys, forums, knowledge base |
| **Reporting & BI** | 6 | XLSX reports, KPI dashboards, watermarks, py3o integration |
| **Server Tools & Utilities** | 8 | Import matching, user roles, technical users, auditing |
| **Web Enhancements** | 7 | Responsive UI, timeline widgets, advanced search, PWA |
| **Document Management** | 4 | DMS system, field integration, storage, attachments |
| **Queue & Background Jobs** | 3 | Job queue, cron integration, subscriptions |

**Total**: 100+ modules across 19 functional categories

### Installation Workflow

#### Step 1: Prepare Repository Structure

```bash
# Reorganize scattered OCA repos (if needed)
./scripts/reorganize-oca-addons.sh

# Sync/update OCA repositories
./scripts/sync-oca-repos.sh
```

This clones 30+ OCA repositories into `addons/oca/`:
- account-financial-tools, account-invoicing, account-reconcile
- sale-workflow, crm, purchase-workflow
- stock-logistics-workflow, stock-logistics-warehouse
- project, project-reporting, timesheet
- helpdesk, fieldservice
- manufacture, quality-control, maintenance
- contract, website, website-themes
- reporting-engine, server-tools, web, dms, queue
- ...and more

#### Step 2: Install Modules

**Option A: Install All Categories (Recommended)**

```bash
# Install all 100+ modules across all categories
./scripts/install-enterprise-parity.sh
```

**Option B: Install Specific Category**

```bash
# Install only accounting modules
./scripts/install-enterprise-parity.sh --category accounting

# Install only sales & CRM modules
./scripts/install-enterprise-parity.sh --category sales

# Available categories:
#   ipai, accounting, sales, purchase, inventory, project, hr,
#   helpdesk, fieldservice, manufacturing, quality, contracts,
#   website, elearning, reporting, tools, web, dms, queue
```

**Option C: Skip IPAI Modules**

```bash
# Install only OCA modules (skip IPAI custom modules)
./scripts/install-enterprise-parity.sh --skip-ipai
```

**Option D: Dry Run (Preview)**

```bash
# See what would be installed without making changes
./scripts/install-enterprise-parity.sh --dry-run
```

#### Step 3: Verify Installation

```bash
# Run full verification suite
./scripts/verify-enterprise-parity.sh

# Generate verification report
./scripts/verify-enterprise-parity.sh --report logs/verification-report.txt

# Strict mode (fail on any warnings)
./scripts/verify-enterprise-parity.sh --strict
```

**Verification Checks**:
- ✅ Module count ≥ 100
- ✅ All IPAI modules installed (ipai_studio, ipai_sign, ipai_knowledge)
- ✅ No broken modules (state = 'uninstallable')
- ✅ No modules pending upgrade
- ✅ Database integrity
- ✅ Client actions valid (no KeyNotFoundError)
- ✅ Category coverage (≥10 categories)
- ✅ OCA module count (≥80)
- ✅ Menu items present (≥100)

#### Step 4: Audit Module Inventory

```bash
# Compare filesystem vs database
./scripts/audit-modules.sh --format table

# Export to CSV for analysis
./scripts/audit-modules.sh --format csv --output logs/module-inventory.csv

# Export to JSON
./scripts/audit-modules.sh --format json --output logs/module-inventory.json
```

**Audit Output Includes**:
- Module technical name
- Display name
- Version
- Category
- Installation state
- Filesystem path
- Orphaned modules (DB only or FS only)

#### Step 5: Check Client Actions (Prevent Errors)

```bash
# Validate JavaScript action registry
./scripts/check-client-actions.sh

# CI mode (exit 1 if missing handlers found)
./scripts/check-client-actions.sh --ci
```

This prevents `KeyNotFoundError` by ensuring all client actions in database have corresponding JavaScript handlers in codebase.

### Troubleshooting

#### Installation Failures

**Symptom**: Some modules fail to install

**Solution**:
```bash
# Check installation log
cat logs/install-enterprise-parity-*.log

# Retry specific category
./scripts/install-enterprise-parity.sh --category <category_name>

# Manual module install
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -i <module_name> --stop-after-init
```

#### Module Count Below 100

**Symptom**: Verification reports < 100 modules

**Solution**:
```bash
# Check which categories were installed
./scripts/audit-modules.sh --format table

# Install missing categories
./scripts/install-enterprise-parity.sh --category <missing_category>

# Check for broken modules
./scripts/check-broken-modules.sh odoo_prod

# Fix broken modules
./scripts/odoo-reinstall-module.sh odoo_prod <module_name>
```

#### IPAI Modules Not Found

**Symptom**: ipai_studio, ipai_sign, or ipai_knowledge not detected

**Solution**:
```bash
# Regenerate IPAI modules
./scripts/generate-ipai-modules.sh

# Verify module files exist
ls -la insightpulse_odoo/addons/custom/ipai_*/

# Update addons_path in odoo.conf
docker compose exec odoo grep addons_path /etc/odoo/odoo.conf

# Refresh module list
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -i base --stop-after-init
```

#### OCA Repository Sync Issues

**Symptom**: sync-oca-repos.sh fails or hangs

**Solution**:
```bash
# Check Git access
git ls-remote https://github.com/OCA/account-financial-tools.git

# Sync with verbose output
./scripts/sync-oca-repos.sh 2>&1 | tee logs/sync-oca.log

# Manual clone problematic repo
cd addons/oca
git clone --depth 1 https://github.com/OCA/<repo-name>.git -b 19.0
```

#### Database Performance Issues

**Symptom**: Slow installation or timeouts

**Solution**:
```bash
# Increase timeout in install script
export ODOO_LIMIT_TIME_REAL=600  # 10 minutes

# Install in smaller batches
./scripts/install-enterprise-parity.sh --category accounting
./scripts/install-enterprise-parity.sh --category sales
# ... repeat for each category

# Check database connections
docker compose exec db psql -U odoo -d odoo_prod -c "SELECT count(*) FROM pg_stat_activity;"
```

#### Conflicting Module Dependencies

**Symptom**: Dependency errors during installation

**Solution**:
```bash
# Check module dependencies
docker compose exec db psql -U odoo -d odoo_prod -c "
  SELECT m.name, string_agg(d.name, ', ') AS dependencies
  FROM ir_module_module m
  JOIN ir_module_module_dependency d ON d.module_id = m.id
  WHERE m.name = '<module_name>'
  GROUP BY m.name;
"

# Install dependencies first
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -i <dependency> --stop-after-init

# Then install target module
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -i <module_name> --stop-after-init
```

### Rollback Procedures

#### Full Rollback (Before Installation)

```bash
# 1. Create database backup
docker compose exec db pg_dump -U odoo -d odoo_prod -Fc > backups/pre-enterprise-parity-$(date +%F_%H%M%S).dump

# 2. Backup filestore
docker compose exec odoo bash -lc 'tar -czf - /var/lib/odoo' > backups/filestore-pre-parity-$(date +%F_%H%M%S).tar.gz
```

#### Partial Rollback (After Installation)

```bash
# Uninstall specific category modules (example: helpdesk)
docker compose exec odoo python odoo-bin shell -c /etc/odoo/odoo.conf -d odoo_prod <<EOF
env = odoo.api.Environment(odoo.registry('odoo_prod').cursor(), odoo.SUPERUSER_ID, {})
modules = env['ir.module.module'].search([
    ('category', 'ilike', 'helpdesk'),
    ('state', '=', 'installed')
])
for module in modules:
    module.button_immediate_uninstall()
    env.cr.commit()
EOF
```

#### Emergency Recovery

```bash
# Restore from backup
docker compose exec -T db pg_restore -U odoo -d odoo_prod --clean --if-exists < backups/pre-enterprise-parity-*.dump

# Restore filestore
docker compose exec -T odoo bash -c 'tar -xzf - -C /' < backups/filestore-pre-parity-*.tar.gz

# Restart services
docker compose restart
```

### Post-Installation Best Practices

1. **Keep OCA Modules Updated**:
   ```bash
   # Weekly sync
   ./scripts/sync-oca-repos.sh
   ./scripts/install-enterprise-parity.sh  # Rerun to apply updates
   ```

2. **Monitor Module Health**:
   ```bash
   # Weekly audit
   ./scripts/audit-modules.sh --format table
   ./scripts/check-broken-modules.sh odoo_prod
   ./scripts/check-client-actions.sh
   ```

3. **Document Custom Configurations**:
   - Keep notes on which modules are configured
   - Document any custom workflows
   - Track integration points between modules

4. **Test Module Interactions**:
   - Verify workflows across module boundaries
   - Test data flow between integrated modules
   - Validate reporting and dashboards

5. **Backup Regularly**:
   ```bash
   # Daily backups after enterprise parity setup
   docker compose exec db pg_dump -U odoo -d odoo_prod -Fc > backups/daily-$(date +%F).dump
   ```

### Reference Documentation

For detailed module descriptions, feature comparisons, and installation guides, see:
- **docs/ENTERPRISE_PARITY.md** - Comprehensive feature matrix and module details
- **scripts/README.md** - Script usage documentation
- **insightpulse_odoo/addons/custom/*/README.md** - IPAI module documentation

## 🔧 Production Operations Hardening

### Worker Configuration

Optimize Odoo workers for production load:

```ini
# config/odoo/odoo.conf
[options]
workers = 9  # Formula: (CPU cores * 2) + 1
limit_time_cpu = 120
limit_time_real = 240
limit_memory_hard = 2147483648  # 2GB
limit_memory_soft = 1610612736  # 1.5GB
max_cron_threads = 2
```

**Guidelines**:
- **workers**: Start with `(CPU * 2) + 1`, adjust based on load
- **memory_hard**: 2GB per worker (adjust for available RAM)
- **memory_soft**: 75% of memory_hard
- **cron_threads**: 1-2 for background jobs

### Proxy Headers & Security

Ensure proper proxy configuration in `odoo.conf`:

```ini
[options]
proxy_mode = True
```

**Reverse Proxy Configuration**:

**Caddy (Recommended)**:
```caddy
your.domain.com {
  encode gzip
  reverse_proxy odoo:8069 {
    header_up X-Forwarded-Proto {scheme}
    header_up X-Forwarded-For {remote}
    header_up X-Forwarded-Host {host}
  }
  header {
    X-Frame-Options SAMEORIGIN
    X-Content-Type-Options nosniff
    X-XSS-Protection "1; mode=block"
    Strict-Transport-Security "max-age=31536000; includeSubDomains"
  }
}
```

**Nginx**:
```nginx
server {
    listen 443 ssl http2;
    server_name your.domain.com;

    # Security headers
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    location / {
        proxy_pass http://odoo:8069;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header Host $host;
    }
}
```

### Log Rotation

Configure Docker log rotation in `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "3"
  }
}
```

Apply configuration:
```bash
sudo systemctl restart docker
```

### Automated Backups

**Daily Database Backups**:
```bash
# Add to crontab: crontab -e
0 2 * * * docker compose exec db pg_dump -U odoo -d odoo_prod -Fc > /backups/daily-$(date +\%F).dump

# Retention: keep 7 days
0 3 * * * find /backups/daily-* -mtime +7 -delete
```

**Weekly Full Backups** (DB + Filestore):
```bash
# Add to crontab
0 3 * * 0 /path/to/insightpulse-odoo/scripts/backup-full.sh

# Retention: keep 4 weeks
0 4 * * 0 find /backups/weekly-* -mtime +28 -delete
```

**Monthly Test Restores**:
```bash
# Verify backup integrity monthly
0 5 1 * * /path/to/insightpulse-odoo/scripts/test-restore.sh
```

### Security Hardening

**Database Access Control**:
```ini
# config/odoo/odoo.conf
[options]
dbfilter = ^odoo_prod$  # Restrict to specific database
list_db = False          # Hide database list
admin_passwd = <strong-random-password>
```

**Block Database Management Routes**:

**Caddy**:
```caddy
your.domain.com {
  @database_routes {
    path /web/database/*
  }
  respond @database_routes 403
}
```

**Nginx**:
```nginx
location ~ ^/web/database/ {
    return 403;
}
```

**Freeze Base URL**:
```ini
# config/odoo/odoo.conf
[options]
web.base.url = https://your.domain.com
web.base.url.freeze = True
```

**SMTP Security**:
Configure outgoing mail with SPF, DMARC, and DKIM:

```ini
# config/odoo/odoo.conf
[options]
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_ssl = starttls
smtp_user = noreply@your.domain.com
smtp_password = <app-password>
email_from = noreply@your.domain.com
```

**DNS Records** (for `your.domain.com`):
```
SPF:   v=spf1 include:_spf.google.com ~all
DMARC: v=DMARC1; p=quarantine; rua=mailto:dmarc@your.domain.com
DKIM:  (Configure in Gmail/SMTP provider)
```

### Health Checks & Monitoring

**Add Health Check Endpoint**:

Odoo has a built-in health endpoint: `/web/health`

**Docker Compose Health Check**:
```yaml
services:
  odoo:
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost:8069/web/health || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 10
      start_period: 60s
```

**Uptime Monitoring**:

Configure external monitoring service (UptimeRobot, Pingdom, etc.):
- **Endpoint**: `https://your.domain.com/web/health`
- **Interval**: 5 minutes
- **Alert**: Email/SMS on 3 consecutive failures

**Alert on Failures**:
```bash
# scripts/healthcheck-alert.sh
#!/usr/bin/env bash
HEALTH_URL="https://your.domain.com/web/health"
ALERT_EMAIL="ops@your.domain.com"

if ! curl -fsS "$HEALTH_URL" > /dev/null 2>&1; then
  echo "Odoo health check FAILED" | mail -s "⚠️ Odoo Health Alert" "$ALERT_EMAIL"
fi
```

**Cron Job** (every 5 minutes):
```bash
*/5 * * * * /path/to/scripts/healthcheck-alert.sh
```

### OCA Sync Cadence

**Weekly OCA Updates**:
```bash
# Add to crontab: every Sunday at 3 AM
0 3 * * 0 cd /path/to/insightpulse-odoo && ./scripts/sync-oca-repos.sh
0 4 * * 0 cd /path/to/insightpulse-odoo && ./scripts/install-enterprise-parity.sh
0 5 * * 0 cd /path/to/insightpulse-odoo && ./scripts/verify-enterprise-parity.sh
```

**Manual Sync Workflow**:
```bash
# 1. Sync OCA repositories
./scripts/sync-oca-repos.sh

# 2. Test in staging
ODOO_DB=odoo_staging ./scripts/install-enterprise-parity.sh

# 3. Verify staging
ODOO_DB=odoo_staging ./scripts/verify-enterprise-parity.sh

# 4. Apply to production
./scripts/install-enterprise-parity.sh
./scripts/verify-enterprise-parity.sh
```

### Apps List Truth Refresh

**Operator Habit**:

After each deployment or module installation:

1. **Enable Developer Mode**: Settings → Activate Developer Mode (⋮ menu)
2. **Update Apps List**: Apps → ⋮ → Update Apps List
3. **Apply Scheduled Upgrades**: Click banner if present

**Automated Refresh** (included in installer script):
```bash
# Already part of install-enterprise-parity.sh
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -i base --stop-after-init
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -u all --stop-after-init
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod --dev=none --stop-after-init
```

### Smoke Test Checklist

**One-Shot Smoke Test**:
```bash
./scripts/parity-smoke.sh odoo_prod
```

**Manual Smoke Test Steps**:
1. ✅ Docker services running: `docker compose ps`
2. ✅ Odoo version: `docker compose exec odoo python odoo-bin --version`
3. ✅ Base module initialized: `-i base --stop-after-init`
4. ✅ All modules updated: `-u all --stop-after-init`
5. ✅ Production assets built: `--dev=none --stop-after-init`
6. ✅ Module count ≥ 100: Query `ir_module_module`
7. ✅ No broken modules: `state != 'uninstallable'`
8. ✅ No pending upgrades: `state != 'to upgrade'`

**Post-Deployment Verification**:
```bash
# Web interface
curl -fsS https://your.domain.com/web/health

# Login
curl -fsS https://your.domain.com/web/login

# SSL certificate
curl -vI https://your.domain.com 2>&1 | grep "SSL certificate verify ok"

# Performance
time curl -fsS https://your.domain.com > /dev/null  # Should be <3s
```

## 💾 Backup Procedures

### Create Backups

```bash
# Database backup (PostgreSQL custom format)
docker compose exec db pg_dump -U "$PGUSER" -d "$PGDATABASE" -Fc > backups/$(date +%F_%H%M%S).dump

# Filestore backup (attachments)
docker compose exec odoo bash -lc 'tar -czf - /var/lib/odoo' > backups/filestore_$(date +%F_%H%M%S).tar.gz
```

### Restore Backups

```bash
# Restore database
docker compose exec -T db pg_restore -U "$PGUSER" -d "$PGDATABASE" --clean --if-exists < backups/xxxx.dump

# Restore filestore
docker compose exec -T odoo bash -c 'tar -xzf - -C /' < backups/filestore_xxxx.tar.gz
```

## 🔄 Upgrade Procedure (Safe Sequence)

```bash
# 1. Create pre-upgrade backup
docker compose exec db pg_dump -U "$PGUSER" -d "$PGDATABASE" -Fc > backups/preupgrade_$(date +%F_%H%M%S).dump

# 2. Pull new images and rebuild
docker compose pull
docker compose build --no-cache odoo

# 3. Stop containers
docker compose down

# 4. Start with database upgrade
docker compose up -d db
sleep 10  # Wait for DB to be ready

# 5. Run Odoo database migration
docker compose run --rm odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -u all --stop-after-init

# 6. Start all services
docker compose up -d

# 7. Verify health
./scripts/deploy-check.sh --full
```

## 📊 Monitoring & Logs

### View Logs

```bash
# Odoo logs (real-time)
docker compose logs -f odoo

# PostgreSQL logs
docker compose logs -f db

# All services
docker compose logs -f

# Claudia utilities (if configured)
claudia-log | tail -50
claudia-status
```

### Log Rotation

Add to `/etc/docker/daemon.json` on host:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "3"
  }
}
```

Then restart Docker daemon:

```bash
sudo systemctl restart docker
```

## 🛡️ Security Hardening

### 1. Change Default Passwords

```bash
# Update admin password in .env
ADMIN_PASSWD=<strong-random-password>

# Update PostgreSQL password
POSTGRES_PASSWORD=<strong-random-password>
```

### 2. Enable HTTPS

Always use HTTPS in production. Configure SSL/TLS in your reverse proxy (Caddy/Nginx).

### 3. Restrict Database Access

In `odoo.conf`:

```ini
dbfilter = ^odoo_prod$  # Restrict to specific database
list_db = False          # Hide database list
```

### 4. Configure Security Headers

In reverse proxy, add:

```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## 🚨 Troubleshooting

### Container Won't Start

```bash
# Check container logs
docker compose logs odoo

# Check health status
docker compose ps

# Restart services
docker compose restart
```

### Database Connection Errors

```bash
# Verify PostgreSQL is running
docker compose exec db pg_isready -U odoo -d odoo

# Check connection from Odoo container
docker compose exec odoo psql -h db -U odoo -d odoo -c "SELECT version();"
```

### Asset Loading Issues

```bash
# Rebuild assets
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod --dev=none --stop-after-init

# Clear browser cache and test
```

### Performance Issues

1. Check worker configuration: `workers = 4` (adjust based on CPU cores)
2. Monitor memory usage: `docker stats`
3. Check database performance: Enable PostgreSQL slow query log
4. Review Odoo logs for bottlenecks

## 📞 Quick Reference Commands

```bash
# Deployment validation
./scripts/deploy-check.sh --full

# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# View logs
docker compose logs -f

# Enter Odoo container
docker compose exec odoo bash

# Enter PostgreSQL container
docker compose exec db psql -U odoo -d odoo

# Create backup
docker compose exec db pg_dump -U odoo -d odoo -Fc > backups/backup_$(date +%F).dump

# Update module
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -u <module_name> --stop-after-init
```

## ✨ Post-Deployment Verification

After deployment, verify:

1. **Web Interface**: `https://your.domain.com` loads correctly
2. **Login**: Admin credentials work
3. **Database**: No errors in Odoo logs
4. **Performance**: Pages load within acceptable time (<3s)
5. **SSL**: Certificate is valid and HTTPS works
6. **Health Check**: `curl https://your.domain.com/web/health` returns 200
7. **Backups**: Automated backup system is running

## 📚 Additional Resources

- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Caddy Documentation](https://caddyserver.com/docs/)

---

**Last Updated**: 2025-10-28
**Odoo Version**: 19.0
**Python Version**: 3.12.12
