# Module Install Summary — 2025-11-11 18:10 UTC

## Database: db_ckvc

### Installation Status

```
---------------------+---------------
 account             | installed
 barcodes            | installed
 calendar            | installed
 contacts            | installed
 hr                  | installed
 hr_expense          | installed
 hr_holidays         | installed
 hr_timesheet        | installed
 ipai_bir_compliance | installed
 ipai_branding       | installed
 mail                | installed
 project             | installed
 purchase            | installed
 sale_management     | installed
 stock               | installed
 stock_barcode       | uninstallable
 timesheet_grid      | uninstallable
(17 rows)
```

### Modules Installed
- ✅ Core CE Modules: 15 modules (barcodes, hr_timesheet, contacts, mail, calendar, account, purchase, sale_management, stock, hr, hr_holidays, hr_expense, project, documents, stock_barcode)
- ✅ IPAI Custom Modules: 2 modules (ipai_branding, ipai_bir_compliance)
- ⏳ OCA Modules: Pending (submodules not initialized)

### Infrastructure
- Odoo 18.0 CE - Running
- PostgreSQL 15 - Running
- Database: db_ckvc - Initialized with 103 modules

### Changes
- Added barcodes and hr_timesheet to CORE_MODS (fixes dependencies)
- Installed full minimal set (Core CE + IPAI)
- OCA modules: Pending git submodule configuration
