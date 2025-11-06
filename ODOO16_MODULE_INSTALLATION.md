# Odoo 16 — Tier-3 SaaS Parity Install (CE + OCA)

## Quick Start

```bash
DB=odoo16 STRICT=0 USE_DOCKER=auto ./scripts/install-all-odoo16-modules.sh
```

* `STRICT=0` skips modules not found on disk (e.g., `helpdesk` on some CE builds).
* `USE_DOCKER=auto` runs inside docker if `docker-compose.odoo16.yml` exists; otherwise uses local `odoo/odoo-bin`.
* Config file: `config/odoo16.conf` (must contain a valid `addons_path` list).

## Stages

1. **Foundation** — UI/Dev tooling, queue/job, REST, OAuth/TOTP
2. **Core** — CRM, Sales, Purchase, Stock, Accounting, Project, HR, Website/Portal
3. **Accounting OCA** — Bank imports, fiscal year, petty cash, MIS & financial reports
4. **Ops** — Sale→Stock glue, delivery, barcode, landed costs, fleet
5. **Services** — Project timesheets, Helpdesk (if present), OCA Field Service suite
6. **MRP/PLM/Quality** — Manufacturing flow, PLM, Quality control, Maintenance
7. **HR & OCR** — Contracts, Timesheets, Leave, Attendance, Recruitment, Skills, `ip_expense_mvp`
8. **Web/Pay/Marketing/BI** — eCom, appointments, payments, mailing, marketing, reporting XLSX

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB` | `odoo16` | Database name |
| `CONF` | `config/odoo16.conf` | Path to Odoo config file |
| `STRICT` | `0` | `1` = fail on missing module, `0` = skip missing |
| `USE_DOCKER` | `auto` | `auto` = detect, `yes` = force docker, `no` = local |
| `DC_FILE` | `docker-compose.odoo16.yml` | Docker Compose file path |
| `ODOO_SERVICE` | `odoo` | Docker service name |

### Examples

**Local installation (no Docker):**
```bash
USE_DOCKER=no DB=production CONF=/etc/odoo/odoo.conf ./scripts/install-all-odoo16-modules.sh
```

**Force Docker with strict mode:**
```bash
USE_DOCKER=yes STRICT=1 ./scripts/install-all-odoo16-modules.sh
```

**Custom database and service:**
```bash
DB=mydb ODOO_SERVICE=odoo16_app ./scripts/install-all-odoo16-modules.sh
```

## Detailed Module List (~50 modules)

### Stage 1: Foundation (8 modules)
Technical infrastructure and UI enhancements:
- `web_responsive` - Mobile-responsive UI
- `web_environment_ribbon` - Environment indicator ribbon
- `base_automation` - Automated actions
- `base_rest` - REST API framework
- `component` - Component architecture
- `queue_job` - Background job queue
- `server_environment` - Environment-based configuration
- `auth_oauth` - OAuth authentication
- `auth_totp` - Two-factor authentication

### Stage 2: Core (11 modules)
Essential business applications:
- `contacts` - Contact management
- `crm` - Customer relationship management
- `sale_management` - Sales orders
- `purchase` - Purchase orders
- `stock` - Inventory management
- `account` - Accounting
- `account_accountant` - Accounting features
- `project` - Project management
- `hr` - Human resources
- `hr_expense` - Expense management
- `website` - Website builder
- `portal` - Customer portal
- `calendar` - Calendar/scheduling

### Stage 3: Accounting OCA (13 modules)
Advanced accounting features (OCA):
- `l10n_generic_coa` - Generic chart of accounts
- `account_bank_statement_import` - Bank statement import framework
- `account_bank_statement_import_csv` - CSV bank imports
- `account_bank_statement_import_ofx` - OFX bank imports
- `account_bank_statement_import_qif` - QIF bank imports
- `account_bank_statement_import_camt` - CAMT bank imports
- `account_move_base_import` - Journal entry import
- `account_invoice_import` - Invoice import
- `account_fiscal_year` - Fiscal year management
- `account_payment_order` - Payment orders
- `account_petty_cash` - Petty cash management
- `account_financial_report` - Financial reports
- `account_tax_balance` - Tax balance reports
- `mis_builder` - Management information system builder

### Stage 4: Ops & Fulfillment (7 modules)
Operations and delivery:
- `sale_stock` - Sales-inventory integration
- `delivery` - Delivery methods
- `barcode` - Barcode scanning
- `stock_account` - Inventory accounting
- `stock_picking_batch` - Batch picking
- `stock_landed_costs` - Landed costs
- `fleet` - Fleet management

### Stage 5: Services (7 modules)
Project services and field operations:
- `project` - Project management (already in core)
- `sale_timesheet` - Timesheet billing
- `helpdesk` - Helpdesk ticketing (CE variant if available)
- `fieldservice` - Field service management (OCA)
- `fieldservice_sale` - Field service sales integration
- `fieldservice_account` - Field service accounting
- `fieldservice_stock` - Field service inventory

### Stage 6: MRP/PLM/Quality (7 modules)
Manufacturing and quality:
- `mrp` - Manufacturing resource planning
- `mrp_workorder` - Work orders
- `mrp_subcontracting` - Subcontracting
- `plm` - Product lifecycle management
- `quality` - Quality management
- `quality_control` - Quality control
- `maintenance` - Equipment maintenance

### Stage 7: HR & OCR (8 modules)
Human resources suite + custom OCR:
- `hr_contract` - Employment contracts
- `hr_timesheet` - Timesheets
- `hr_holidays` - Leave management
- `hr_attendance` - Attendance tracking
- `hr_recruitment` - Recruitment
- `hr_skills` - Skills management
- `ip_expense_mvp` - **Custom OCR expense module**

### Stage 8: Web/Payments/Marketing/BI (13 modules)
E-commerce, payments, marketing:
- `website` - Website (already in core)
- `website_sale` - E-commerce
- `website_form` - Website forms
- `website_livechat` - Live chat
- `appointment` - Online appointments
- `payment` - Payment framework
- `payment_stripe` - Stripe payments
- `payment_paypal` - PayPal payments
- `mass_mailing` - Email marketing
- `marketing_automation` - Marketing automation
- `sms` - SMS messaging
- `social` - Social media integration
- `board` - Dashboards
- `report_xlsx` - Excel reports (OCA)

**Total: ~50 modules** (exact count depends on CE variant and OCA availability)

## Upgrades & Rollback

### Upgrade Specific Modules

```bash
# Docker
docker compose -f docker-compose.odoo16.yml exec -T odoo odoo \
  -c config/odoo16.conf -d odoo16 -u module1,module2 --stop-after-init

# Local
odoo -c config/odoo16.conf -d odoo16 -u module1,module2 --stop-after-init
```

### Uninstall Modules

Use the Apps UI (recommended) to ensure dependency-safe removal:
1. Navigate to **Apps** menu
2. Remove any search filters
3. Find the module
4. Click **Uninstall**
5. Confirm dependency removal

**Note:** Uninstalling base modules (e.g., `account`, `sale`) can break your installation. Always test in a staging environment first.

## Common Issues

### Module Missing Error

**Symptom:** `ERROR: missing module on disk: module_name`

**Solution:**
1. Check if module exists in any `addons_path` directory
2. If missing, clone the required OCA repository or install the module
3. Or set `STRICT=0` to skip missing modules gracefully

### Accounting Initialization Errors

**Symptom:** `ValidationError: No chart of accounts found`

**Solution:**
1. Install base `account` module first (Stage 2)
2. Install a chart of accounts: `l10n_generic_coa` or country-specific (e.g., `l10n_ph` for Philippines)
3. Then proceed with OCA accounting modules (Stage 3)

### Docker Service Not Found

**Symptom:** `ERROR: service 'odoo' not found`

**Solution:**
1. Check your docker-compose file service name
2. Set `ODOO_SERVICE` to match your service name:
   ```bash
   ODOO_SERVICE=odoo16_app ./scripts/install-all-odoo16-modules.sh
   ```

### Config File Not Found

**Symptom:** `ERROR: Config file not found: config/odoo16.conf`

**Solution:**
1. Ensure `config/odoo16.conf` exists
2. Or specify custom path:
   ```bash
   CONF=/path/to/odoo.conf ./scripts/install-all-odoo16-modules.sh
   ```

### Database Connection Error

**Symptom:** `FATAL: database "odoo16" does not exist`

**Solution:**
1. Create database first:
   ```bash
   odoo -c config/odoo16.conf -d odoo16 -i base --stop-after-init
   ```
2. Or let the script create it (Stage 1 creates DB if not exists)

## Post-Install Checks

### 1. Verify Module Installation

```bash
# Docker
docker compose -f docker-compose.odoo16.yml exec -T postgres \
  psql -U odoo16 -d odoo16 -c \
  "SELECT name, state FROM ir_module_module WHERE state = 'installed' ORDER BY name;"

# Local
psql -U odoo16 -d odoo16 -c \
  "SELECT name, state FROM ir_module_module WHERE state = 'installed' ORDER BY name;"
```

### 2. Configure Users & Roles

1. Navigate to **Settings → Users & Companies → Users**
2. Create user accounts for your team
3. Assign appropriate access rights (Accounting, Sales, HR, etc.)
4. Set up approval workflows

### 3. Configure Company & Localization

1. **Settings → General Settings → Companies**
   - Company name, address, logo
   - Currency, timezone
   - Fiscal year dates
2. **Accounting → Configuration → Chart of Accounts**
   - Import or create accounts
   - Configure tax rates
3. **Accounting → Configuration → Fiscal Positions**
   - Tax mapping for different regions

### 4. Configure Payment Providers

1. **Website → Configuration → Payment Providers**
2. Enable Stripe/PayPal/others
3. Enter API credentials (use sandbox for testing)
4. Test payment flow

### 5. Configure OCR Integration

1. **Settings → Technical → System Parameters**
2. Set `ip_expense.ocr_api_url` = `https://ocr.insightpulseai.net/api/v1/extract`
3. Verify OCR service is running
4. Test receipt upload in Expense module

### 6. Verify Supabase Sync

Check that analytics data flows to Supabase:
```sql
-- Connect to Supabase PostgreSQL
SELECT COUNT(*) FROM analytics.ip_ocr_receipts;
```

### 7. Test Critical Workflows

- [ ] Create sales order → generate invoice → record payment
- [ ] Create purchase order → receive products → validate invoice
- [ ] Submit expense with OCR receipt → manager approval → accounting post
- [ ] Create project → log timesheets → invoice time
- [ ] Create manufacturing order → produce → deliver

## OCA Repositories Required

To support all Tier-3 modules, ensure these OCA repositories are cloned:

| Repository | Modules Used |
|------------|--------------|
| `web` | web_responsive, web_environment_ribbon |
| `server-tools` | base_automation, queue_job, server_environment |
| `rest-framework` | base_rest, component |
| `server-auth` | auth_oauth, auth_totp |
| `account-financial-tools` | account_fiscal_year, account_petty_cash, account_tax_balance |
| `account-financial-reporting` | account_financial_report, mis_builder |
| `bank-statement-import` | account_bank_statement_import_* |
| `account-invoicing` | account_invoice_import |
| `account-payment` | account_payment_order |
| `account-reconcile` | (reconciliation modules) |
| `field-service` | fieldservice* |
| `reporting-engine` | report_xlsx |
| `manufacture` | (MRP extras if needed) |
| `project` | (project extras) |

Clone OCA repos to `vendor/oca/` and add to `addons_path` in config.

## Troubleshooting Commands

### Check Container Status
```bash
docker compose -f docker-compose.odoo16.yml ps
```

### View Odoo Logs
```bash
docker logs odoo16_app --tail 100 -f
```

### View PostgreSQL Logs
```bash
docker logs odoo16_postgres --tail 100 -f
```

### Access Odoo Shell
```bash
# Docker
docker compose -f docker-compose.odoo16.yml exec odoo odoo shell -d odoo16

# Local
odoo shell -d odoo16
```

### Access PostgreSQL Directly
```bash
# Docker
docker compose -f docker-compose.odoo16.yml exec postgres psql -U odoo16 -d odoo16

# Local
psql -U odoo16 -d odoo16
```

### Restart Services
```bash
docker compose -f docker-compose.odoo16.yml restart
```

### View Addons Path
```bash
grep addons_path config/odoo16.conf
```

### Check Module Availability
```bash
# List all available modules
find /path/to/addons -maxdepth 2 -name "__manifest__.py" | xargs dirname | xargs basename -a | sort
```

## Installation Timeline

| Stage | Estimated Time | Notes |
|-------|---------------|-------|
| Stage 1: Foundation | 2-3 min | Fast (few dependencies) |
| Stage 2: Core | 5-8 min | Larger modules, more dependencies |
| Stage 3: Accounting OCA | 3-5 min | Bank imports, reporting |
| Stage 4: Ops | 2-3 min | Stock/sales integration |
| Stage 5: Services | 2-4 min | Field service suite |
| Stage 6: MRP/PLM | 3-5 min | Manufacturing flow |
| Stage 7: HR & OCR | 2-3 min | HR suite + custom module |
| Stage 8: Web/Pay/BI | 3-5 min | E-commerce, payments, marketing |
| **Total** | **25-40 minutes** | Depends on hardware and module availability |

**Hardware recommendations:**
- CPU: 4+ cores recommended
- RAM: 8GB minimum, 16GB+ recommended
- Disk: SSD highly recommended
- Network: Stable connection for pulling dependencies

## Next Steps After Installation

1. **Complete OCA Repository Cloning**
   - Clone remaining 15 OCA repositories from the list above
   - Add them to `addons_path` in config

2. **Data Migration** (if applicable)
   - Import customers, vendors, products
   - Import chart of accounts
   - Import opening balances

3. **Integration Setup**
   - Connect to email server (SMTP/IMAP)
   - Connect to payment gateways
   - Connect to Supabase for analytics
   - Connect to OCR service

4. **User Training**
   - Train users on core workflows
   - Document custom processes
   - Set up support channels

5. **Performance Tuning**
   - Enable worker processes
   - Configure caching
   - Optimize database
   - Set up monitoring

6. **Backup & Disaster Recovery**
   - Set up automated backups
   - Test restore procedures
   - Document recovery plan

7. **Security Hardening**
   - Enable HTTPS
   - Configure firewall
   - Set up fail2ban
   - Enable audit logging

## Support & Resources

- **Odoo Documentation:** https://www.odoo.com/documentation/16.0/
- **OCA Documentation:** https://github.com/OCA
- **InsightPulse Repository:** https://github.com/jgtolentino/insightpulse-odoo
- **Issue Tracker:** Create issues in the repository for bugs/features

## License

This installation script and documentation are part of the InsightPulse Odoo project.
See LICENSE file for details.
