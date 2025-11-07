# Odoo 18 CE Module Installation Waves

> **Structured, wave-based installation guide for Odoo 18 Community Edition + OCA modules**

This directory contains carefully ordered module installation waves to ensure proper dependency resolution and smooth deployment of your Odoo 18 CE instance.

---

## 🌊 Installation Waves Overview

| Wave | File | Description | Modules | Dependencies |
|:---|:---|:---|---:|:---|
| **0** | `00_base.txt` | Base system modules | 12 | None |
| **1** | `10_web_ux.txt` | Web & UX enhancements | 4 | Wave 0 |
| **2** | `20_sales_inventory.txt` | Sales & inventory | 5 | Wave 1 |
| **2.5** | `25_localization.txt` | Chart of accounts | 1+ | Wave 2 |
| **3** | `30_accounting.txt` | Accounting & finance | 9+ | Wave 2.5 |
| **4** | `40_hr_project.txt` | HR & projects | 6 | Wave 3 |
| **9** | `90_optional.txt` | Optional features | 8 | Wave 4 |

---

## 🚀 Quick Start

### Prerequisites

1. **Odoo 18 CE installed**
   ```bash
   # Verify Odoo version
   docker exec -it odoo odoo-bin --version
   ```

2. **OCA modules cloned**
   ```bash
   # Clone all necessary OCA repositories
   ./scripts/clone-oca-18.sh ./oca
   ```

3. **Database created**
   ```bash
   # Create database
   docker exec -it odoo odoo-bin -d mydb --stop-after-init
   ```

### Installation Steps

```bash
# Navigate to install-waves directory
cd /path/to/insightpulse-odoo/install-waves

# Install Wave 0: Base (REQUIRED)
docker exec -it odoo odoo-bin -d mydb -i $(cat 00_base.txt | grep -v '^#' | tr '\n' ',' | sed 's/,$//')

# Install Wave 1: Web & UX
docker exec -it odoo odoo-bin -d mydb -i $(cat 10_web_ux.txt | grep -v '^#' | tr '\n' ',' | sed 's/,$//')

# Install Wave 2: Sales & Inventory
docker exec -it odoo odoo-bin -d mydb -i $(cat 20_sales_inventory.txt | grep -v '^#' | tr '\n' ',' | sed 's/,$//')

# Install Wave 2.5: Localization
docker exec -it odoo odoo-bin -d mydb -i $(cat 25_localization.txt | grep -v '^#' | tr '\n' ',' | sed 's/,$//')

# Install Wave 3: Accounting
docker exec -it odoo odoo-bin -d mydb -i $(cat 30_accounting.txt | grep -v '^#' | tr '\n' ',' | sed 's/,$//')

# Install Wave 4: HR & Projects
docker exec -it odoo odoo-bin -d mydb -i $(cat 40_hr_project.txt | grep -v '^#' | tr '\n' ',' | sed 's/,$//')

# Install Wave 9: Optional (as needed)
docker exec -it odoo odoo-bin -d mydb -i $(cat 90_optional.txt | grep -v '^#' | tr '\n' ',' | sed 's/,$//')
```

---

## 📋 Wave Details

### Wave 0: Base System Modules (`00_base.txt`)

**Core Odoo 18 CE modules** - These are foundational and must be installed first.

```
analytic, base, base_import, base_setup, bus, iap,
im_livechat, mail_bot, portal, web, web_editor, website
```

**Installation:**
```bash
docker exec -it odoo odoo-bin -d mydb -i analytic,base,base_import,base_setup,bus,iap,im_livechat,mail_bot,portal,web,web_editor,website
```

---

### Wave 1: Web & UX Improvements (`10_web_ux.txt`)

**Core automation + OCA enhancements** for better user experience.

**Modules:**
- `base_automation` - Core Odoo automated actions
- `server_environment` - OCA environment configuration
- `web_dashboard` - Core dashboard framework
- `web_responsive` - OCA responsive UI (mobile-friendly)

**Installation:**
```bash
docker exec -it odoo odoo-bin -d mydb -i base_automation,server_environment,web_dashboard,web_responsive
```

**Note:** `web_studio` (Enterprise only) has been excluded from CE.

---

### Wave 2: Sales & Inventory (`20_sales_inventory.txt`)

**Core sales, purchase, and inventory management.**

**Modules:**
- `purchase` - Purchase orders
- `sale` - Sales orders
- `sale_management` - Sales management
- `stock` - Inventory management
- `stock_account` - Inventory/Accounting integration

**Installation:**
```bash
docker exec -it odoo odoo-bin -d mydb -i purchase,sale,sale_management,stock,stock_account
```

---

### Wave 2.5: Localization (`25_localization.txt`)

**Chart of accounts** based on your country.

**Default:**
- `l10n_generic_coa` - Generic chart of accounts

**Country-Specific (uncomment in file as needed):**
- `l10n_in` - India
- `l10n_mx` - Mexico
- `l10n_nl` - Netherlands
- `l10n_pe` - Peru
- `l10n_us` - United States

**Installation:**
```bash
docker exec -it odoo odoo-bin -d mydb -i l10n_generic_coa
# OR for specific country:
docker exec -it odoo odoo-bin -d mydb -i l10n_us
```

---

### Wave 3: Accounting & Finance (`30_accounting.txt`)

**Core accounting with OCA enhancements.**

**Core Modules:**
- `account` - Base accounting
- `account_accountant` - Advanced accounting
- `account_asset` - Asset management
- `account_budget` - Budget management
- `account_check_printing` - Check printing
- `account_reports_followup` - Payment follow-up
- `currency_rate_live` - Live currency rates

**OCA Modules:**
- `account_invoice_refund` - Advanced refunds
- `mis_builder` - Management Information System reports

**Optional (commented in file):**
- `account_bank_statement_import_camt` - CAMT bank imports
- `account_bank_statement_import_csv` - CSV bank imports
- `account_bank_statement_import_ofx` - OFX bank imports
- `account_bank_statement_import_qif` - QIF bank imports

**Installation:**
```bash
docker exec -it odoo odoo-bin -d mydb -i account,account_accountant,account_asset,account_budget,account_check_printing,account_invoice_refund,account_reports_followup,currency_rate_live,mis_builder
```

---

### Wave 4: HR & Project Management (`40_hr_project.txt`)

**Core HR and project modules.**

**Modules:**
- `hr` - Base HR
- `hr_attendance` - Attendance tracking
- `hr_contract` - HR contracts
- `hr_expense` - Expense management
- `hr_timesheet` - Timesheet tracking
- `project` - Project management

**Installation:**
```bash
docker exec -it odoo odoo-bin -d mydb -i hr,hr_attendance,hr_contract,hr_expense,hr_timesheet,project
```

**Note:** `hr_org_chart` (Enterprise only) has been excluded from CE.

---

### Wave 9: Optional Modules (`90_optional.txt`)

**CRM, reporting, and other optional features.**

**Modules:**
- `crm` - Customer relationship management
- `event_social` - Social marketing
- `ir_attachment_url` - External attachment URLs
- `link_tracker` - Link tracking
- `product_email_template` - Product email templates
- `report_xlsx` - OCA XLSX report engine
- `social_push_notifications` - Push notifications
- `stock_logistics_reporting` - OCA stock reporting

**Installation:**
```bash
docker exec -it odoo odoo-bin -d mydb -i crm,event_social,ir_attachment_url,link_tracker,product_email_template,report_xlsx,social_push_notifications,stock_logistics_reporting
```

---

## 🔧 Automated Installation Script

For convenience, use the provided automation script:

```bash
#!/bin/bash
# install-all-waves.sh

DB_NAME="mydb"

for wave in install-waves/*.txt; do
    echo "Installing wave: $wave"
    MODULES=$(cat "$wave" | grep -v '^#' | tr '\n' ',' | sed 's/,$//')
    docker exec -it odoo odoo-bin -d "$DB_NAME" -i "$MODULES"
    echo "Wave completed: $wave"
    echo ""
done

echo "All waves installed successfully!"
```

---

## ⚠️ Important Notes

### Excluded Enterprise Modules

These modules are **Odoo Enterprise only** and have been excluded:

- `web_studio` - Visual UI customization tool
- `hr_org_chart` - Interactive org chart
- Various advanced reporting modules

### OCA Repository Mapping

| Module | OCA Repository | Branch |
|:---|:---|:---:|
| `web_responsive` | `OCA/web` | 18.0 |
| `server_environment` | `OCA/server-tools` | 18.0 |
| `mis_builder` | `OCA/mis-builder` | 18.0 |
| `account_invoice_refund` | `OCA/account-invoicing` | 18.0 |
| `report_xlsx` | `OCA/reporting-engine` | 18.0 |
| `stock_logistics_reporting` | `OCA/stock-logistics-reporting` | 18.0 |
| Bank imports | `OCA/bank-statement-import` | 18.0 |

### Troubleshooting

**Problem:** Module not found
```bash
# Update apps list
docker exec -it odoo odoo-bin -d mydb --update=base --stop-after-init

# Or via UI: Apps → Update Apps List
```

**Problem:** Dependency error
- Ensure you install waves in order (0 → 1 → 2 → 2.5 → 3 → 4 → 9)
- Check that OCA modules are in your addons_path

**Problem:** Import error
```bash
# Check logs
docker logs odoo --tail 100

# Verify module is in addons_path
docker exec -it odoo grep addons_path /etc/odoo/odoo.conf
```

---

## 📊 Module Statistics

| Source | Count | Percentage |
|:---|---:|:---:|
| **Odoo Core CE** | 36 | 80% |
| **OCA** | 9 | 20% |
| **Total** | 45 | 100% |

---

## 🎯 Next Steps

After installing all waves:

1. **Configure Odoo**
   - Set up company information
   - Configure chart of accounts
   - Set up users and permissions

2. **Install Additional OCA Modules**
   - Browse `OCA/` directories for more modules
   - Check compatibility with 18.0 branch

3. **Customize**
   - Create custom modules in `custom_addons/`
   - Follow OCA development guidelines

---

## 📚 Additional Resources

- [Odoo 18 Documentation](https://www.odoo.com/documentation/18.0/)
- [OCA GitHub](https://github.com/OCA)
- [OCA Guidelines](https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md)
- [InsightPulse AI Odoo Guide](../docs/ODOO_SAAS_PARITY.md)

---

**Last Updated:** 2025-11-07
**Odoo Version:** 18.0 Community Edition
**OCA Branch:** 18.0
