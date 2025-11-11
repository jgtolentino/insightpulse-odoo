# InsightPulse BIR Compliance Module

**Version**: 18.0.1.0.0
**Status**: 🚧 M0 Foundation (Module Skeleton)
**License**: LGPL-3

---

## Overview

Philippine Bureau of Internal Revenue (BIR) tax forms automation module for Odoo 18.0 CE.

Designed for Finance Shared Service Centers managing multiple Philippine legal entities (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB).

---

## Features (Roadmap)

### ✅ M0 - Foundation (Current)
- [x] Module structure scaffolded
- [x] BIR Form 1601-C model created
- [x] Basic views and menu structure
- [x] Security rules (ir.model.access.csv)
- [x] Unit test framework setup

### 🚧 M1 - BIR Compliance Core (Weeks 5-8)
- [ ] BIR 1601-C full implementation
  - [ ] GL transaction query logic
  - [ ] PDF generation (QWeb report)
  - [ ] XML export (eBIRForms schema v8.0)
  - [ ] Validation engine
- [ ] BIR 2550Q quarterly form
- [ ] 98% validation accuracy on 100 historical months
- [ ] Comprehensive unit tests

### 🔜 M2 - Advanced Forms (Weeks 9-12)
- [ ] BIR 1702-RT annual return
- [ ] BIR 2307 certificates
- [ ] Multi-org consolidation
- [ ] Audit trail export

### 📅 M3 - Future Enhancements
- [ ] E-filing API integration (eBIRForms direct upload)
- [ ] Auto-reminders for deadlines
- [ ] BIR form archiving (10-year retention)
- [ ] Digital signatures

---

## Supported BIR Forms

| Form | Name | Frequency | Deadline | Status |
|------|------|-----------|----------|--------|
| **1601-C** | Monthly Withholding Tax | Monthly | 10th of following month | 🚧 In Progress |
| **2550Q** | Quarterly VAT Return | Quarterly | 25th day after quarter end | ⏳ Planned (M1) |
| **1702-RT** | Annual Income Tax Return | Annual | April 15 | ⏳ Planned (M2) |
| **2307** | Certificate of Tax Withheld | As needed | 20th day | ⏳ Planned (M2) |

---

## Installation

### Prerequisites
- Odoo 18.0 Community Edition
- PostgreSQL 15+
- Python 3.10+
- Philippine localization module (`l10n_ph`)
- OCA modules:
  - `account_financial_reporting`
  - `account_financial_tools`

### Install Steps

1. **Copy module to addons path**
   ```bash
   cp -r ipai_bir_compliance /path/to/odoo/addons/
   ```

2. **Update apps list**
   ```bash
   # In Odoo UI: Apps > Update Apps List
   # Or via command line:
   odoo -d your_database -u all
   ```

3. **Install module**
   ```bash
   # In Odoo UI: Apps > Search "BIR Compliance" > Install
   # Or via command line:
   odoo -d your_database -i ipai_bir_compliance
   ```

4. **Verify installation**
   - Check menu: BIR Compliance > Tax Forms
   - Create test form: 1601-C (Monthly Withholding)

---

## Configuration

### Company Setup

Ensure your company has Philippine tax configuration:

1. **Go to**: Settings > Companies > Your Company
2. **Set**:
   - Country: Philippines
   - Currency: PHP (Philippine Peso)
   - TIN: XXX-XXX-XXX-000 (valid format)

### Chart of Accounts

BIR module expects these account codes:

| Account Code | Name | Type |
|--------------|------|------|
| **2151xx** | Withholding Tax Payable - Compensation | Liability |
| **2152xx** | Withholding Tax Payable - Expanded | Liability |
| **2153xx** | VAT Payable | Liability |

If using different codes, configure in: BIR Compliance > Configuration > Tax Codes

---

## Usage

### Creating BIR Form 1601-C

1. **Navigate**: BIR Compliance > Tax Forms > 1601-C (Monthly Withholding)
2. **Click**: Create
3. **Fill**:
   - Company: Select from dropdown
   - Month: 1-12
   - Year: Current or past year
4. **Click**: Save

### Workflow

```
Draft → Generate XML → Validate → Generate PDF → Mark as Filed
```

**Steps**:

1. **Draft**: Form created, tax amounts computed from GL
2. **Generate XML**: Creates eBIRForms XML for upload
3. **Validate**: Checks against BIR rules (TIN, amounts, etc.)
4. **Generate PDF**: Creates printable form
5. **Mark as Filed**: After uploading to eBIRForms portal

### Validation Rules

Form must pass these checks:

- ✅ TIN format: XXX-XXX-XXX-000
- ✅ Tax withheld >= 0
- ✅ Period in the past or current month
- ✅ Company registered in Philippines
- ✅ No duplicate form for same period
- ✅ XML conforms to BIR schema v8.0

---

## Development

### Running Tests

```bash
# Run all BIR compliance tests
odoo -d test_db -i ipai_bir_compliance --test-tags bir_compliance --stop-after-init

# Run specific test
odoo -d test_db --test-tags test_bir_1601c
```

### Code Coverage

Target: >80% for custom modules

```bash
pytest --cov=ipai_bir_compliance --cov-report=html
```

### Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

---

## Troubleshooting

### Issue: "Module not found"
**Solution**: Ensure module is in `addons_path` in `odoo.conf`

### Issue: "TIN validation failing"
**Solution**: TIN must be format `XXX-XXX-XXX-000` (12 digits with dashes)

### Issue: "Tax amounts showing zero"
**Solution**:
- Check GL transactions exist for the period
- Verify account codes match (2151xx, 2152xx)
- Ensure transactions are posted (not draft)

### Issue: "PDF generation error"
**Solution**: Check QWeb template: `ipai_bir_compliance.report_bir_1601c_document`

---

## References

### BIR Official Resources
- [BIR eBIRForms](https://efps.bir.gov.ph/)
- [BIR Form Downloads](https://www.bir.gov.ph/index.php/downloadable-forms.html)
- [BIR Revenue Regulations](https://www.bir.gov.ph/index.php/revenue-regulations.html)

### Technical Documentation
- [Odoo 18.0 Developer Docs](https://www.odoo.com/documentation/18.0/developer.html)
- [OCA Guidelines](https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md)
- [InsightPulse PRD](../../docs/PRD_IMPLEMENTATION_ROADMAP.md)

---

## Support

- **GitHub Issues**: https://github.com/jgtolentino/insightpulse-odoo/issues
- **Email**: jgtolentino_rn@yahoo.com
- **Documentation**: `/docs/BIR_COMPLIANCE.md`

---

## Changelog

### Version 18.0.1.0.0 (2025-11-11)
- Initial module scaffold (M0 Foundation)
- BIR Form 1601-C model created
- Basic views and menu
- Unit test framework setup

---

**Developed by**: InsightPulse AI
**License**: LGPL-3
**Odoo Version**: 18.0
**Last Updated**: 2025-11-11
