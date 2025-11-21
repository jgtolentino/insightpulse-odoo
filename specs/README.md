# InsightPulse ERP – Technical Specifications

This directory contains the complete technical specifications for the InsightPulse ERP platform, covering three product domains:

1. **SAP Concur-equivalent** - Expenses & Travel
2. **Cheqroom-equivalent** - Equipment Booking & Management
3. **Notion-equivalent** - Finance Workspace & BIR Calendar

---

## 📁 File Organization

### 1. [MODULE_SERVICE_MATRIX.md](./MODULE_SERVICE_MATRIX.md)
**Complete platform architecture matrix**

**Contents**:
- Odoo modules mapped to each product (Concur/Cheqroom/Notion)
- External services and infrastructure components
- Integration points and data flow
- Current status tracking (v0.2.1-quality baseline)

**Use this for**:
- Understanding which modules serve which products
- Planning infrastructure deployment
- Identifying integration requirements
- Validating completeness of the platform

---

### 2. [tasks.md](./tasks.md)
**v1 scope checklists by product**

**Contents**:
- **Section A**: SAP Concur-equivalent checklist
  - Odoo modules installation
  - OCR infrastructure setup
  - Expense workflows configuration
  - n8n automation deployment
  - Testing & validation steps

- **Section B**: Cheqroom-equivalent checklist
  - Equipment catalog setup
  - Booking system implementation
  - Incident logging configuration
  - Calendar integration

- **Section C**: Notion-equivalent checklist
  - Finance closing project templates
  - BIR workflow setup
  - Knowledge base creation
  - Task automation via n8n

- **Section D**: Cross-product integration tests
- **Section E**: Quality gates for v1 release
- **Section F**: Post-v1 enhancements roadmap

**Use this for**:
- Tracking v1 implementation progress
- Assigning tasks to team members
- Validating release readiness
- Planning future enhancements

---

### 3. [INSTALL_SEQUENCE.md](./INSTALL_SEQUENCE.md)
**Production module installation guide**

**Contents**:
- Pre-installation checklist
- Phase 1: Core CE modules verification
- Phase 2: Custom InsightPulse modules installation (exact order)
  1. `ipai_ce_cleaner` ✅ Installed
  2. `ipai_ocr_expense` ✅ Installed
  3. `ipai_expense` ⏳ Pending
  4. `ipai_equipment` ⏳ Pending
  5. `ipai_finance_monthly_closing` ⏳ Pending
- Phase 3: Post-installation verification
- Phase 4: External service configuration
- Phase 5: Data migration & setup
- Phase 6: Testing & validation
- Rollback procedures

**Use this for**:
- Deploying modules to production
- Troubleshooting installation issues
- Rolling back failed installations
- Planning deployment windows

---

### 4. [002-odoo-expense-equipment-mvp.prd.md](./002-odoo-expense-equipment-mvp.prd.md)
**Original PRD for expense & equipment MVP**

**Contents**:
- Product requirements for expense management
- Equipment booking requirements
- User stories and acceptance criteria
- Technical architecture

**Use this for**:
- Historical context for MVP scope
- Detailed feature requirements
- User experience specifications

---

## 🚀 Quick Start Guide

### For Platform Overview
1. Read [MODULE_SERVICE_MATRIX.md](./MODULE_SERVICE_MATRIX.md) to understand the complete architecture
2. Review current status section to see what's already deployed

### For Implementation Planning
1. Check [tasks.md](./tasks.md) for v1 scope checklists
2. Use checkboxes to track progress
3. Refer to quality gates before v1 release

### For Production Deployment
1. Follow [INSTALL_SEQUENCE.md](./INSTALL_SEQUENCE.md) step-by-step
2. Create backups before each phase
3. Run verification commands after each module installation
4. Execute rollback procedures if any step fails

---

## 📊 Current Platform Status (v0.2.1-quality)

### ✅ Completed
- Core Odoo CE 18 installation (169 modules)
- CE-only validation (0 Enterprise modules)
- odoo.com link cleanup (0 links remaining)
- `ipai_ce_cleaner` module (UI cleanup)
- `ipai_ocr_expense` module (OCR integration)
- OCR adapter at `ocr.insightpulseai.net`
- PH normalization in OCR response
- Enhanced OCR log views

### ⏳ In Progress
- `ipai_expense` module (PH expense/travel workflows)
- `ipai_equipment` module (equipment booking)
- `ipai_finance_monthly_closing` module (closing tasks + BIR)

### 📋 Planned (v1 Release)
- n8n workflow deployment
- Superset dashboard creation
- OCA addon integration
- Chat agent integration (Mattermost)

---

## 🔗 Related Documentation

### Internal Documentation
- `/addons/ipai_*/README.rst` - Module-specific documentation
- `/data/*.csv` - Import templates for tasks and equipment
- `/.github/workflows/` - CI/CD pipeline configuration

### External Resources
- Odoo CE 18 Documentation: https://www.odoo.com/documentation/18.0/
- OCA Guidelines: https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md
- n8n Documentation: https://docs.n8n.io/

### InsightPulse Infrastructure
- Production ERP: https://erp.insightpulseai.net
- OCR Service: https://ocr.insightpulseai.net
- n8n Automation: https://ipa.insightpulseai.net
- Superset BI: https://superset.insightpulseai.net

---

## 📝 Maintenance & Updates

### Updating This Documentation

When making changes to the platform:

1. **Update MODULE_SERVICE_MATRIX.md**:
   - Add new modules or services
   - Update status indicators (✅/⏳/📋)
   - Document integration points

2. **Update tasks.md**:
   - Check off completed tasks
   - Add new tasks as scope expands
   - Update quality gates if criteria change

3. **Update INSTALL_SEQUENCE.md**:
   - Add new module installation steps
   - Update verification commands
   - Document new external services

4. **Version Control**:
   - Commit changes with clear messages
   - Tag releases (e.g., `v1.0.0`, `v1.1.0`)
   - Update "Last Updated" dates in each file

---

## 🤝 Contributing

### For Developers

- Follow OCA coding standards for all custom modules
- Write comprehensive tests for new features
- Document all API changes in relevant spec files
- Run quality checks before committing

### For Project Managers

- Use tasks.md to track implementation progress
- Review MODULE_SERVICE_MATRIX.md before planning new features
- Ensure INSTALL_SEQUENCE.md is updated for new modules
- Maintain quality gate criteria in tasks.md

### For System Administrators

- Follow INSTALL_SEQUENCE.md for all production deployments
- Create backups before any installation or upgrade
- Verify all post-installation checks pass
- Document any deviations from standard procedures

---

**Maintained By**: InsightPulse AI - Finance SSC Team
**Last Updated**: 2025-11-21
**Baseline Version**: v0.2.1-quality
**Target v1 Release**: TBD

**Questions or Issues?**
- Create GitHub issue in `jgtolentino/odoo-ce` repo
- Tag with appropriate label: `documentation`, `installation`, `bug`, `enhancement`
