---
description: Run automated tests for a specific module
---
1. Run Odoo in test mode for the specified module.
```bash
cd deploy && docker compose exec odoo odoo -d odoo --test-enable --stop-after-init -u MODULE_NAME
```
