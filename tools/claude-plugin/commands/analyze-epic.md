---
description: Analyze an epic from the PRD and generate implementation plan
---

# Analyze Epic

Analyze an epic from the PRD and create a detailed implementation plan:

1. **Ask for epic number** (1-10) or name

2. **Read PRD:**
   ```bash
   cat docs/PRD_ENTERPRISE_SAAS_PARITY.md | grep -A 20 "Epic {number}"
   ```

3. **Extract key information:**
   - Goal
   - Base modules (Odoo/OCA dependencies)
   - Acceptance criteria
   - Module name
   - Sprint assignment

4. **Generate implementation plan:**
   - [ ] List required models
   - [ ] List required views (form, tree, search, kanban)
   - [ ] List required controllers/API endpoints
   - [ ] List security rules (RLS, ACL)
   - [ ] List tests (unit, integration, E2E)
   - [ ] Estimate effort (story points)

5. **Check dependencies:**
   - [ ] OCA modules available for Odoo 18?
   - [ ] Any conflicting modules?
   - [ ] Database migrations needed?

6. **Create tasks in TASKS.md:**
   - Add epic tasks to appropriate sprint
   - Link to PRD epic
   - Set priority level

7. **Output implementation checklist**

**Reference**: `docs/PRD_ENTERPRISE_SAAS_PARITY.md` (Epics 1-10)
