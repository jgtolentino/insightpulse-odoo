---
description: Run tests for a specific Odoo module
---

# Test Odoo Module

Run tests for the specified Odoo module:

1. **Ask for module name** (e.g., `ipai_approvals`, `ipai_expense`)

2. **Run tests:**
   ```bash
   pytest odoo/tests/test_{module_name}.py -v
   ```

3. **Check coverage:**
   ```bash
   pytest odoo/tests/test_{module_name}.py --cov=addons/custom/{module_name} --cov-report=term-missing
   ```

4. **Validate results:**
   - All tests pass (green)
   - Coverage >80%
   - No security warnings

5. **If tests fail:**
   - Show detailed error output
   - Suggest fixes based on error messages
   - Offer to fix and re-run

6. **Run linters:**
   ```bash
   black addons/custom/{module_name}/ --check
   flake8 addons/custom/{module_name}/
   pylint addons/custom/{module_name}/
   ```

**Target**: >80% test coverage, all linters pass
