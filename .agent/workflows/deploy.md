---
description: Deploy and update all custom IPAI modules
---
1. Restart the Odoo container to load Python changes.
```bash
cd deploy && docker compose restart odoo
```
// turbo
2. Update all custom modules via CLI.
```bash
cd deploy && docker compose exec odoo odoo -u ipai_docs,ipai_docs_project,ipai_cash_advance,ipai_expense,ipai_equipment,ipai_ce_cleaner,ipai_ocr_expense,ipai_finance_monthly_closing,tbwa_spectra_integration -d odoo --stop-after-init
```
