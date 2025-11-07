---
description: Check BIR compliance and immutable accounting rules
---

# Check BIR Compliance

Validate BIR compliance across the codebase:

1. **Check immutable accounting:**
   ```bash
   grep -r "write\|unlink" addons/custom/*/models/*account*.py
   ```
   - [ ] No direct writes to posted journal entries
   - [ ] All corrections via reversal entries
   - [ ] Audit trail via `mail.thread` inheritance

2. **Check BIR forms:**
   - [ ] 1601-C (withholding tax) - `ipai_finance/reports/bir_1601c.py`
   - [ ] 2550Q (quarterly VAT) - `ipai_finance/reports/bir_2550q.py`
   - [ ] 1702-RT (annual income tax) - `ipai_finance/reports/bir_1702rt.py`
   - [ ] 2307 (certificate of withholding) - `ipai_finance/reports/bir_2307.py`

3. **Validate audit trail:**
   ```bash
   grep -r "mail.thread" addons/custom/*/models/*.py
   ```
   - [ ] All financial models inherit `mail.thread`
   - [ ] State changes logged via chatter
   - [ ] Actor + timestamp captured

4. **Check multi-company isolation:**
   ```bash
   grep -r "company_id" addons/custom/*/security/*.xml
   ```
   - [ ] RLS rules enforce `company_id` isolation
   - [ ] No cross-company data leaks

5. **Run compliance tests:**
   ```bash
   pytest tests/test_bir_compliance.py -v
   ```

6. **Generate compliance report:**
   - List all violations
   - Suggest fixes
   - Update SECURITY.md

**Compliance**: BIR Philippines standards, immutable accounting
