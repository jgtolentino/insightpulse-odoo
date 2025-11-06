# Odoo 16 Module Installation Guide

## Quick Start

Run the automated script on your local machine:

```bash
./scripts/install-all-odoo16-modules.sh
```

Or follow the manual steps below.

---

## Manual Installation Steps

### Step 1: Initialize Database with Base Modules

```bash
docker exec -it odoo16_app odoo \
  -d odoo16 \
  --without-demo=all \
  --load-language=en_US \
  -i base \
  --stop-after-init
```

**Expected outcome:** Creates the `odoo16` database with base Odoo modules (no demo data)

---

### Step 2: Install Core Odoo Modules

```bash
docker exec -it odoo16_app odoo \
  -d odoo16 \
  -i web,account,hr_expense,stock,sale,purchase,project,website \
  --stop-after-init
```

**Modules installed:**
- `web` - Web interface
- `account` - Accounting
- `hr_expense` - Employee expenses
- `stock` - Inventory management
- `sale` - Sales management
- `purchase` - Purchase management
- `project` - Project management
- `website` - Website builder

---

### Step 3: Install Custom IP Expense MVP Module

```bash
docker exec -it odoo16_app odoo \
  -d odoo16 \
  -i ip_expense_mvp \
  --stop-after-init
```

**Expected outcome:** Installs your custom InsightPulse Expense MVP module with OCR integration

---

### Step 4: Configure System Parameters

```bash
docker exec -it odoo16_postgres psql -U odoo16 -d odoo16 << 'EOF'
INSERT INTO ir_config_parameter (key, value, create_date, write_date)
VALUES (
  'ip_expense.ocr_api_url',
  'https://ocr.insightpulseai.net/api/v1/extract',
  NOW(),
  NOW()
)
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();
EOF
```

**Expected outcome:** Sets the OCR API URL for receipt scanning

---

### Step 5: Upgrade All Modules

```bash
docker exec -it odoo16_app odoo \
  -d odoo16 \
  -u all \
  --stop-after-init
```

**Expected outcome:** Updates all installed modules to latest version

---

### Step 6: Verify Installation

```bash
docker exec -it odoo16_postgres psql -U odoo16 -d odoo16 -c \
  "SELECT name, state FROM ir_module_module WHERE state = 'installed' ORDER BY name;"
```

**Expected outcome:** Lists all installed modules

---

### Step 7: Restart Odoo

```bash
docker compose -f docker-compose.odoo16.yml restart odoo16_app
```

**Expected outcome:** Odoo runs in normal mode (not `--stop-after-init`)

---

## Access Information

- **URL:** http://localhost:8069
- **Database:** odoo16
- **Email:** admin@example.com
- **Password:** admin123
- **Master Password:** admin123

---

## OCA Modules (Optional)

You have 4 OCA repositories cloned:
1. `account-financial-tools`
2. `account-invoice-reporting`
3. `account-reconcile`
4. `project`

To use OCA modules, install them like:

```bash
docker exec -it odoo16_app odoo \
  -d odoo16 \
  -i account_fiscal_year,account_invoice_triple_discount \
  --stop-after-init
```

---

## Troubleshooting

### Check container status
```bash
docker compose -f docker-compose.odoo16.yml ps
```

### View Odoo logs
```bash
docker logs odoo16_app --tail 100
```

### View PostgreSQL logs
```bash
docker logs odoo16_postgres --tail 100
```

### Access Odoo shell
```bash
docker exec -it odoo16_app odoo shell -d odoo16
```

### Access PostgreSQL directly
```bash
docker exec -it odoo16_postgres psql -U odoo16 -d odoo16
```

---

## Next Steps After Installation

1. **Complete OCA clone** (15 more repositories from the original list)
2. **Configure email settings** (for expense notifications)
3. **Set up users and permissions**
4. **Import chart of accounts** (Philippines BIR-compliant)
5. **Configure company details**

---

## Installation Timeline

Estimated time for complete installation: **10-15 minutes**

- Step 1: ~2 minutes (database creation)
- Step 2: ~3-5 minutes (core modules)
- Step 3: ~1-2 minutes (custom module)
- Step 4: ~10 seconds (configuration)
- Step 5: ~2-3 minutes (upgrade all)
- Step 6: ~5 seconds (verification)
- Step 7: ~30 seconds (restart)
