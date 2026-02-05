---
description: Scaffold a new Odoo 18 CE module following OCA standards
---

# Scaffold New Odoo Module

Create a new Odoo 18 CE module with the following structure:

1. **Ask for module details:**
   - Module name (snake_case with `ipai_` prefix)
   - Module description (one-line summary)
   - Dependencies (default: `['base']`)
   - Category (e.g., 'Finance', 'Project Management', 'Procurement')

2. **Generate module structure:**
   ```
   addons/custom/{module_name}/
   ├── __init__.py
   ├── __manifest__.py        # AGPL-3, Odoo 18.0 compatible
   ├── models/
   │   └── __init__.py
   ├── views/
   ├── security/
   │   ├── ir.model.access.csv
   │   └── {module_name}_security.xml
   ├── tests/
   │   ├── __init__.py
   │   └── test_basic.py
   └── README.md
   ```

3. **Key requirements:**
   - License: AGPL-3
   - Version: 18.0.1.0.0
   - Category: As specified by user
   - Dependencies: Include all required Odoo/OCA modules
   - Maintainers: InsightPulse AI Team

4. **Add basic test:**
   - TransactionCase for model creation
   - Test module installation

5. **Update documentation:**
   - Add module to `MODULES.md`
   - Update `CHANGELOG.md`

**Odoo Version**: 18 CE (NOT 19, NOT Enterprise)
