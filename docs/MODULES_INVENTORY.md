# Odoo 18 CE Module Inventory

**Generated**: 2025-11-10
**Instance**: https://erp.insightpulseai.net
**Database**: odoo19
**Total Installed**: 63 modules

---

## Module Distribution by Source

| Source | Count | Percentage |
|--------|-------|------------|
| **Core** (Odoo S.A.) | 52 | 82.5% |
| **OCA** (Community) | 8 | 12.7% |
| **Custom** (InsightPulse AI) | 3 | 4.8% |

---

## Installed Applications (application=True)

### Core Applications (9 apps)

1. **Invoicing** (`account`)
   - Summary: Invoices, Payments, Follow-ups & Bank Synchronization
   - License: LGPL-3
   - Dependencies: base_setup, onboarding, product, analytic, portal, digest

2. **Employees** (`hr`)
   - Summary: Centralize employee information
   - License: LGPL-3
   - Dependencies: base_setup, mail, resource, web

3. **Contracts** (`hr_contract`)
   - Summary: Employee contracts management
   - License: LGPL-3
   - Dependencies: hr, mail

4. **Expenses** (`hr_expense`)
   - Summary: Submit, validate and reinvoice employee expenses
   - License: LGPL-3
   - Dependencies: hr, account, product

5. **Skills Management** (`hr_skills`)
   - Summary: Manage skills, knowledge and resume of your employees
   - License: LGPL-3
   - Dependencies: hr, web_hierarchy

6. **Discuss** (`mail`)
   - Summary: Chat, mail gateway and private channels
   - License: LGPL-3
   - Dependencies: base, web, bus

7. **Accounting & Finance Reports** (`account_financial_report`)
   - Summary: OCA Financial Reports
   - Author: OCA
   - License: AGPL-3
   - Dependencies: account, date_range, report_xlsx

8. **Audit Log** (`auditlog`)
   - Summary: Track all changes for BIR compliance
   - Author: OCA
   - License: AGPL-3
   - Dependencies: base

9. **MIS Builder** (`mis_builder`)
   - Summary: Build Management Information System Reports and Dashboards
   - Author: OCA
   - License: AGPL-3
   - Dependencies: date_range, report_xlsx

---

## OCA Modules (8 modules)

| Module | Purpose | License |
|--------|---------|---------|
| `account_financial_report` | Financial reports (General Ledger, Trial Balance, etc.) | AGPL-3 |
| `account_multicompany_easy_creation` | Multi-company setup wizard | AGPL-3 |
| `auditlog` | Track all database changes (BIR compliance) | AGPL-3 |
| `date_range` | Date range management | AGPL-3 |
| `date_range_account` | Date range for accounting | AGPL-3 |
| `hr_expense_advance_clearing` | Expense advance clearing | AGPL-3 |
| `mis_builder` | Management Information System builder | AGPL-3 |
| `report_xlsx` | Excel report export | AGPL-3 |

---

## Custom Modules (3 modules)

| Module | Purpose | Status |
|--------|---------|--------|
| `auth_supabase` | Supabase authentication integration | Installed |
| `hr_offboarding_clearance` | Employee offboarding clearance workflow | Installed ✅ |
| `ipai_auth_fix` | InsightPulse AI authentication fixes | Installed |

---

## Core Supporting Modules (52 modules)

### Authentication & Security
- `auth_oauth` - OAuth authentication
- `auth_signup` - User signup
- `auth_totp` - Two-factor authentication
- `auth_totp_mail` - 2FA via email
- `auth_totp_portal` - 2FA for portal users

### Communication
- `mail` - Email and messaging
- `mail_bot` - Odoobot assistant
- `mail_bot_hr` - HR-specific Odoobot
- `google_gmail` - Gmail integration
- `sms` - SMS messaging
- `snailmail` - Postal mail
- `snailmail_account` - Snailmail for invoices

### Human Resources
- `hr` - Employee management
- `hr_contract` - Employment contracts
- `hr_expense` - Expense management
- `hr_org_chart` - Organization chart
- `hr_skills` - Skills management
- `resource` - Resource management
- `resource_mail` - Resource mail integration

### Accounting & Finance
- `account` - Accounting core
- `account_edi_ubl_cii` - E-invoicing standards
- `account_payment` - Payment management
- `analytic` - Analytic accounting
- `product` - Product catalog
- `uom` - Units of measure
- `payment` - Payment acquirer

### Spreadsheets & Dashboards
- `spreadsheet` - Spreadsheet engine
- `spreadsheet_account` - Accounting spreadsheets
- `spreadsheet_dashboard` - Dashboard builder
- `spreadsheet_dashboard_account` - Accounting dashboards

### Web & UI
- `web` - Web client
- `web_editor` - WYSIWYG editor
- `web_hierarchy` - Hierarchical views
- `web_tour` - Guided tours
- `web_unsplash` - Unsplash image integration
- `html_editor` - HTML editor
- `http_routing` - HTTP routing

### Infrastructure
- `base` - Base module
- `base_setup` - Base setup wizard
- `base_import` - Import framework
- `base_import_module` - Module import
- `base_install_request` - Install request tracking
- `board` - Dashboard framework
- `bus` - Message bus
- `digest` - Digest emails
- `onboarding` - Onboarding wizard
- `portal` - Customer portal
- `privacy_lookup` - Privacy tools

### Utilities
- `iap` - In-App Purchases
- `iap_mail` - IAP for mail
- `partner_autocomplete` - Partner autocomplete
- `phone_validation` - Phone number validation

---

## Project Structure Recommendation

```
insightpulse-odoo/
├── odoo/
│   └── addons/                    # Core Odoo modules (52)
│       ├── account/
│       ├── hr/
│       └── ...
├── oca-addons/                    # OCA modules (8)
│   ├── account_financial_report/
│   ├── auditlog/
│   ├── mis_builder/
│   └── ...
├── custom_addons/                 # Custom modules (3)
│   ├── auth_supabase/
│   ├── hr_offboarding_clearance/
│   └── ipai_auth_fix/
├── config/
│   └── odoo.conf                  # Updated addons_path
└── docs/
    ├── modules_manifest.json      # Full module data
    └── MODULES_INVENTORY.md       # This file
```

### Updated odoo.conf

```ini
[options]
# Addons path - include all three sources
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/oca-addons,/mnt/custom-addons

# Database
db_host = postgres
db_port = 5432
db_user = odoo
db_password = odoo

# Multi-tenant & SSO
session_cookie_domain = .insightpulseai.net
session_cookie_secure = True
session_cookie_httponly = True
session_cookie_samesite = Lax
proxy_mode = True
```

---

## Making Modules Visible in Apps Grid

To make custom modules appear in the Apps interface, edit their `__manifest__.py`:

```python
{
    'name': 'HR Offboarding Clearance',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Employee offboarding clearance workflow',
    'author': 'InsightPulse AI',
    'license': 'LGPL-3',
    'depends': ['hr', 'hr_contract', 'mail', 'portal'],
    'application': True,  # Add this line
    'installable': True,
    'auto_install': False,
}
```

Then update the module:

```bash
docker exec insightpulse-odoo-odoo-1 odoo -u hr_offboarding_clearance -d odoo19 --stop-after-init
docker restart insightpulse-odoo-odoo-1
```

---

## BIR Compliance Stack

### Installed Modules for Philippine BIR Compliance:

1. **Audit Log** (`auditlog`) - Immutable change tracking
2. **Accounting** (`account`) - Financial records
3. **Date Range** (`date_range`) - Period management
4. **Financial Reports** (`account_financial_report`) - BIR-required reports
5. **HR Offboarding** (`hr_offboarding_clearance`) - Form 2316 generation
6. **Expense Management** (`hr_expense`, `hr_expense_advance_clearing`) - Form 2307 preparation

### Required Forms Support:

- ✅ **Form 2307** (Withholding Tax) - Via `hr_expense` + Supabase scout.transactions
- ✅ **Form 2316** (Annual Tax) - Via `hr_offboarding_clearance.final_pay_id`
- ✅ **Audit Trail** - Via `auditlog` module
- ⏸️ **Form 1601-C** (Monthly Remittance) - Pending custom module
- ⏸️ **Form 1702-RT** (Annual Return) - Pending integration

---

## Next Steps

1. ✅ **Reorganize directory structure** (core/oca/custom separation)
2. ✅ **Update odoo.conf** with new addons_path
3. ✅ **Set application=True** for custom modules
4. ⏸️ **Install additional OCA modules** for BIR compliance
5. ⏸️ **Create Superset dashboards** for analytics

---

**Full module data**: See `modules_manifest.json` for complete JSON export with dependencies.
