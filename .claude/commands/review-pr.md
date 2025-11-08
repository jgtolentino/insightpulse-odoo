---
description: Review a GitHub pull request for code quality and standards
---

# Review Pull Request

Perform a comprehensive code review on the specified PR:

1. **Ask for PR number** (e.g., `#123`)

2. **Fetch PR details:**
   ```bash
   gh pr view {pr_number} --json title,body,files,additions,deletions
   gh pr diff {pr_number}
   ```

3. **Check standards:**
   - [ ] Odoo 18 CE APIs used (NOT 19, NOT Enterprise)
   - [ ] License: AGPL-3 in all new files
   - [ ] Tests included (>80% coverage)
   - [ ] No hardcoded secrets/URLs
   - [ ] RLS rules for multi-company if applicable
   - [ ] BIR compliance (immutable accounting)
   - [ ] OpenAPI `x-atomic` and `x-role-scopes` for controllers
   - [ ] Docstrings and type hints
   - [ ] CHANGELOG.md updated

4. **Run automated checks:**
   ```bash
   black . --check
   flake8 .
   pylint addons/
   pytest odoo/tests -q
   ```

5. **Review output:**
   - Summarize changes
   - List potential issues
   - Suggest improvements
   - Approve or request changes

6. **Add PR comment with review results**

**Standards**: OCA-compliant, BIR-compliant, Odoo 18 CE only
