# Odoo Custom Modules

This directory contains custom Odoo modules for InsightPulse AI Finance Shared Service Center.

## Directory Structure

```
odoo/modules/
├── README.md (this file)
├── ip_expense_mvp/          # Expense Management MVP
├── ip_expense_automation/   # Automated expense processing
├── ip_expense_ocr/          # OCR integration for receipts
└── ip_expense_analytics/    # Expense analytics and reporting
```

## Module Standards

All modules in this directory follow:

- **Odoo 18.0 CE** compatibility
- **OCA Guidelines** for structure and naming
- **AGPL-3.0** license
- **BIR Compliance** for Philippine tax requirements
- **Multi-tenant** design with `company_id` isolation

## Module Structure

Each module should contain:

```
module_name/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── *.py
├── views/
│   └── *.xml
├── security/
│   ├── ir.model.access.csv
│   └── ir.rule.xml
├── data/
│   └── *.xml
├── tests/
│   ├── __init__.py
│   └── test_*.py
└── README.md
```

## Creating New Modules

### Via Makefile
```bash
make create-module NAME=my_new_module
```

### Via Script
```bash
./scripts/development/create-module.sh my_new_module
```

### Manual Creation
1. Create module directory: `mkdir -p odoo/modules/module_name`
2. Add `__init__.py` and `__manifest__.py`
3. Follow OCA structure guidelines
4. Add tests in `tests/` directory
5. Document in module's README.md

## Testing Modules

### Run All Module Tests
```bash
make test
```

### Test Specific Module
```bash
pytest odoo/modules/my_module/tests/ -v
```

### Lint Module Code
```bash
flake8 odoo/modules/my_module/
pylint odoo/modules/my_module/
```

## Module Installation

### Development Environment
1. Add module to `odoo.conf` addons_path
2. Restart Odoo: `make restart`
3. Update Apps List in Odoo UI
4. Install module

### Production Deployment
Modules are auto-deployed via CI/CD:
- Push to `main` branch
- CI runs tests and validation
- CD deploys to production droplet
- Odoo auto-discovers new modules

## OCA Guidelines

Follow OCA conventions:
- Use `_inherit` for extending models
- Prefix custom fields with `x_`
- Add proper dependencies in `__manifest__.py`
- Include comprehensive tests
- Document all public APIs

## BIR Compliance

All financial modules must:
- Support Philippine tax codes (2307, 2316, 1701, 2550Q)
- Maintain immutable audit trails
- Generate BIR-compliant reports
- Support multi-company/multi-agency isolation

## Documentation

- **Architecture**: See `/docs/architecture/odoo-modules.md`
- **API Reference**: Each module has its own README.md
- **Development Guide**: See `/docs/guides/odoo-addons-structure.md`

## Support

- **Issues**: https://github.com/jgtolentino/insightpulse-odoo/issues
- **OCA Standards**: https://github.com/OCA
- **Odoo Docs**: https://www.odoo.com/documentation/18.0/

---

**Last Updated**: 2025-11-09
**Maintainer**: InsightPulse AI Team
