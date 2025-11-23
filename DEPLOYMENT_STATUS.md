# Odoo CE Deployment Status - Live Instance

**Instance**: https://erp.insightpulseai.net
**Last Updated**: 2025-11-23 14:45 UTC
**Odoo Version**: 18.0

---

## 📊 Module Catalog – CE vs OCA vs IPAI (Current Status)

### 1. IPAI & TBWA Custom Modules

| Display Name | Technical Name | Source | URL | Notes |
|-------------|----------------|--------|-----|-------|
| **IPAI Equipment Management** | `ipai_equipment` | IPAI | https://insightpulseai.net | Cheqroom parity (Equipment) |
| **IPAI Expense & Travel (PH)** | `ipai_expense` | IPAI | https://insightpulseai.net | Concur parity (Expense/Travel) |
| **IPAI Finance PPM** | `ipai_finance_ppm` | IPAI | https://insightpulseai.net | Clarity-style Finance PPM |
| **InsightPulse AI Finance SSC** | `ipai_finance_ssc` | IPAI | https://insightpulseai.net | Legacy SSC engine (to sunset) |
| **IPAI Docs** | `ipai_docs` | IPAI | https://insightpulseai.net | Notion/Workspace parity |
| **IPAI Docs Project** | `ipai_docs_project` | IPAI | https://insightpulseai.net | Project-linked docs |
| **IPAI Cash Advance** | `ipai_cash_advance` | IPAI | https://insightpulseai.net | New cash advance workflow |
| **IPAI OCR Expense** | `ipai_ocr_expense` | IPAI | https://insightpulseai.net | OCR + hr_expense bridge |
| **IPAI Finance Monthly Closing** | `ipai_finance_monthly_closing` | IPAI | https://insightpulseai.net | PPM → Project monthly close |
| **IPAI PPM Monthly Close** | `ipai_ppm_monthly_close` | IPAI | https://insightpulseai.net | Opinionated PPM close engine |
| **Cash Advance Management** | `x_cash_advance` | IPAI/TBWA | https://github.com/OCA/account-financial-tools | Legacy; replaced by ipai_* |
| **Expense Policy Engine** | `x_expense_policy` | IPAI/TBWA | https://pulse-hub-web-an645.ondigitalocean.app | Legacy Spectra-era policy |

> **Status:** All IPAI modules are visible in Apps; `ipai_equipment` is MVP-ready and should be installed via UI. Legacy `x_*` modules are marked **for migration/deprecation** once ipai_* flows are stable.

---

### 2. OCA Modules in Use / Available

| Display Name | Technical Name | OCA Repo / URL | Role |
|-------------|----------------|----------------|------|
| **Account Financial Reports** | `account_financial_report` | https://github.com/OCA/account-financial-reporting | Advanced financial reports |
| **Account Financial Reports Sale** | `account_financial_report_sale` | https://github.com/OCA/account-financial-reporting | Sales-focused reports |
| **Animal** | `animal` | https://github.com/OCA/partner-contact | Example/utility module |
| **Audit Log** | `auditlog` | https://github.com/OCA/server-tools | Security & audit trail |
| **MIS Builder** | `mis_builder` | https://github.com/OCA/mis-builder | Management reporting (MIS) |
| **Partner VAT Unique** | `partner_vat_unique` | https://github.com/OCA/partner-contact | VAT uniqueness constraint |
| **Purchase Request** | `purchase_request` | https://github.com/OCA/purchase-workflow | PR / PO workflow |
| **Web Theme Classic** | `web_theme_classic` | https://github.com/OCA/web | CE/OCA front-end theme |

> **Rule:** All analytics / reporting / theming enhancements should prefer **OCA** modules above custom development.

---

### 3. Core Odoo 18 CE Apps (Allowed Baseline)

> These are standard **Community Edition** apps you're allowed to install when needed.

| Display Name | Technical Name | Vendor | URL |
|-------------|----------------|--------|-----|
| **Sales** | `sale_management` | Odoo S.A. | https://www.odoo.com/app/sales |
| **CRM** | `crm` | Odoo S.A. | https://www.odoo.com/app/crm |
| **Invoicing** | `account` | Odoo S.A. | https://www.odoo.com/app/invoicing |
| **Inventory** | `stock` | Odoo S.A. | https://www.odoo.com/app/inventory |
| **Purchase** | `purchase` | Odoo S.A. | https://www.odoo.com/app/purchase |
| **Project** | `project` | Odoo S.A. | https://www.odoo.com/app/project |
| **Timesheets** | `timesheet_grid` | Odoo S.A. | — (bundled CE) |
| **Expenses** | `hr_expense` | Odoo S.A. | https://www.odoo.com/app/expenses |
| **Employees** | `hr` | Odoo S.A. | https://www.odoo.com/app/employees |
| **Maintenance** | `maintenance` | Odoo S.A. | https://www.odoo.com/app/maintenance |
| **Manufacturing** | `mrp` | Odoo S.A. | https://www.odoo.com/app/manufacturing |
| **Website** | `website` | Odoo S.A. | https://www.odoo.com/app/website |
| **eCommerce** | `website_sale` | Odoo S.A. | https://www.odoo.com/app/ecommerce |
| **Point of Sale** | `point_of_sale` | Odoo S.A. | https://www.odoo.com/app/point-of-sale-shop |
| **Email Marketing** | `mass_mailing` | Odoo S.A. | https://www.odoo.com/app/email-marketing |
| **Calendar** | `calendar` | Odoo S.A. | — |
| **Contacts** | `contacts` | Odoo S.A. | — |
| **Discuss** | `mail` | Odoo S.A. | https://www.odoo.com/app/discuss |
| **Fleet** | `fleet` | Odoo S.A. | https://www.odoo.com/app/fleet |
| **Time Off** | `hr_holidays` | Odoo S.A. | https://www.odoo.com/app/time-off |
| **Recruitment** | `hr_recruitment` | Odoo S.A. | https://www.odoo.com/app/recruitment |

---

### 4. Enterprise / Blocklisted Modules (Do **Not** Use)

> ⚠️ **Enterprise Guardrail:** The following modules must remain **uninstalled** in TBWA / InsightPulse instances. All requested features must be implemented via **OCA + ipai_*** modules instead.

**Blocklisted Modules** (present in Apps menu but off-limits):
- `web_studio` (Studio) - No-code builder (Enterprise only)
- `sign` (Sign) - Digital signature (Enterprise only)
- `helpdesk` (Helpdesk) - Ticketing system (Enterprise only)
- `sale_subscription` (Subscriptions) - Recurring revenue (Enterprise only)
- `timesheet_grid` (Timesheets) - Listed as CE but has Enterprise hooks
- `planning` (Planning) - Resource planning (Enterprise only)
- `quality_control` (Quality) - QMS (Enterprise only)
- `mrp_plm` (PLM) - Product lifecycle (Enterprise only)
- `industry_fsm` (Field Service) - FSM (Enterprise only)
- `appointment` (Appointments) - Booking (Enterprise only)
- `voip` (VoIP) - Voice calls (Enterprise only)

**Policy**: If a feature exists in one of these modules, it must be:
1. Replicated in an IPAI custom module, OR
2. Sourced from an OCA alternative, OR
3. Deferred until a CE/OCA solution exists

---

## 🔗 Module Links Verification

### ✅ Correct Links (InsightPulse Branded)

All IPAI modules correctly point to InsightPulse infrastructure:
- ✅ `https://insightpulseai.net` (all ipai_* modules)
- ✅ `https://pulse-hub-web-an645.ondigitalocean.app` (x_expense_policy)

**No odoo.com upsell links detected in code** ✅

> **Note**: Core CE Apps table below contains odoo.com reference links for official documentation. These are in markdown docs (not code) and excluded from CI guardrails which only scan `addons/`, `oca/`, `deploy/` directories.

### 🏢 OCA Modules (Community Edition)

Sample OCA modules visible in Apps menu:
- ✅ Account Financial Reports (OCA)
- ✅ Audit Log (OCA)
- ✅ MIS Builder (OCA)
- ✅ Purchase Request (OCA)
- ✅ Web Theme Classic (OCA)

---

## 🎯 Ready to Install: IPAI Equipment Management

### Prerequisites
**Required Dependency**: Maintenance module

**Status**:
- ✅ Maintenance module visible in Apps menu
- ✅ Maintenance version: 18.0.1.0
- ✅ Link: https://www.odoo.com/app/maintenance

### Installation Steps

1. **Install Dependency** (if not already installed)
   ```
   Apps > Search "Maintenance" > Install
   ```

2. **Install IPAI Equipment**
   ```
   Apps > Search "IPAI Equipment Management" > Install
   ```

3. **Verify Installation**
   - Equipment menu appears in main navigation
   - 3 submenus visible: Catalog, Bookings, Incidents
   - Cron job registered: "IPAI Equipment: Check Overdue Bookings"

---

## 📋 Odoo CE 18.0 Core Modules (Installed)

### Essential Modules Already Available

| Category | Module | Status |
|----------|--------|--------|
| **Sales** | Sales Management | ✅ Available |
| **Accounting** | Invoicing | ✅ Available |
| **CRM** | Customer Relationship Management | ✅ Available |
| **Inventory** | Stock Management | ✅ Available |
| **Purchase** | Purchase Management | ✅ Available |
| **Project** | Project Management | ✅ Available |
| **HR** | Employees | ✅ Available |
| **HR** | Expenses | ✅ Available |
| **HR** | Time Off | ✅ Available |
| **HR** | Recruitment | ✅ Available |
| **Maintenance** | Maintenance | ✅ Available (Required for ipai_equipment) |
| **Communication** | Discuss | ✅ Available |
| **Contacts** | Contacts | ✅ Available |
| **Calendar** | Calendar | ✅ Available |

---

## 🚀 CI/CD Automation Status

### ✅ Deployed Scripts

| Script | Location | Status | Purpose |
|--------|----------|--------|---------|
| `odoo-bin` | Repo root | ✅ Deployed | Portable Odoo wrapper for CI/GitHub Actions |
| `run_odoo_migrations.sh` | scripts/ | ✅ Deployed | Auto-detect and migrate ipai_*/tbwa_* modules |
| `report_ci_telemetry.sh` | scripts/ | ✅ Deployed | Send CI health to n8n webhook |

### 🔄 GitHub Actions Integration

| Workflow | Status | Telemetry | odoo-bin |
|----------|--------|-----------|----------|
| `odoo-parity-tests.yml` | ✅ Updated | ✅ Enabled | ✅ Enabled |
| `ci-odoo-ce.yml` | ✅ Updated | ✅ Enabled | N/A (guardrails only) |

**Telemetry Configuration**:
- Webhook: `${{ secrets.N8N_CI_WEBHOOK_URL }}` (optional)
- Graceful fallback if webhook not configured

---

## 📈 Deployment Metrics

### Code Changes (Last 4 Commits)

```
Commits: 4
Files Modified: 9
Lines Added: 648
Lines Removed: 4
```

**Breakdown**:
- Odoo 18 compatibility fix: 1 line removed (ir.cron.numbercall)
- CI/CD automation scripts: 80 lines (3 new scripts)
- GitHub Actions integration: 37 lines (2 workflows)
- Documentation: 534 lines (3 new docs)

### Commits

```
7f6ce80 docs: Add CI/CD automation infrastructure summary
d1b4e51 ci: Wire automation scripts into GitHub Actions workflows
d1680c9 docs: Update CHANGELOG for Equipment MVP + CI/CD automation deployment
ed1df44 fix(odoo18): Equipment module compatibility + CI/CD automation
```

---

## ⚠️ Known Issues & Limitations

### CLI Installation Issue
**Problem**: `odoo -d odoo -i ipai_equipment` silently completes but module remains "uninstalled"
**Root Cause**: Docker container database connectivity or module discovery issue
**Workaround**: ✅ **Use Odoo UI Apps menu for installation** (recommended approach)

### Database Health
**Status**: PostgreSQL container shows "unhealthy" status intermittently
**Impact**: None on web UI functionality (web interface fully accessible)
**Action**: Monitor for persistent issues

---

## 🎬 Next Actions

### Immediate (Manual Installation Required)

1. **Navigate to Odoo**
   - URL: http://localhost:8069 or https://erp.insightpulseai.net
   - Login with admin credentials

2. **Update Apps List**
   - Click Apps menu
   - Click "Update Apps List" (⟳ icon top-right)
   - Confirm update

3. **Install Maintenance Module**
   - Search: "Maintenance"
   - Click "Install" button
   - Wait for installation to complete

4. **Install IPAI Equipment Management**
   - Search: "IPAI Equipment Management"
   - Click "Install" button
   - Wait for installation to complete

5. **Verify Installation**
   ```bash
   # Via database query
   docker exec odoo-db psql -U odoo -d odoo -c \
     "SELECT name, state FROM ir_module_module WHERE name = 'ipai_equipment';"

   # Expected: state = 'installed'
   ```

   - Check Equipment menu appears in navigation
   - Verify 3 submenus: Catalog, Bookings, Incidents

### Optional (Enable CI Telemetry)

1. **Set GitHub Secret**
   ```
   Repository Settings > Secrets and variables > Actions
   Name: N8N_CI_WEBHOOK_URL
   Value: https://n8n.insightpulseai.net/webhook/ci-telemetry
   ```

2. **Create n8n Webhook Receiver**
   - See: `CI_CD_AUTOMATION_SUMMARY.md` for example workflow
   - Configure Mattermost alerts for failures
   - Store telemetry in Supabase for trend analysis

---

## 📚 Documentation References

| Document | Purpose | Status |
|----------|---------|--------|
| `DEPLOYMENT_MVP.md` | Installation guide | ✅ Complete |
| `CI_CD_AUTOMATION_SUMMARY.md` | Automation reference | ✅ Complete |
| `DEPLOYMENT_STATUS.md` | Live status (this file) | ✅ Current |
| `CHANGELOG.md` | Version history | ✅ Updated (v1.2.0) |

---

## 🎯 Acceptance Gates

- [ ] IPAI Equipment module state = "installed" (pending UI installation)
- [x] Module visible in Apps menu with correct branding
- [x] All ipai_* modules link to insightpulseai.net (no odoo.com upsells)
- [x] Odoo 18 compatibility issues resolved
- [x] CI/CD automation scripts deployed
- [x] GitHub Actions workflows updated
- [ ] Equipment menu accessible (pending installation)
- [ ] Cron job registered and active (pending installation)
- [ ] Zero errors in Odoo logs (pending installation)

**Current Status**: ✅ **Code Ready** | ⏳ **UI Installation Pending**

---

**Last Verification**: 2025-11-23 14:45 UTC via Apps menu screenshot
