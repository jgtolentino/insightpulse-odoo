# Odoo Development Automation Scripts

Collection of scripts to automate Odoo module development following OCA conventions.

## 📋 Available Scripts

### Module Scaffolding

#### `scaffold-odoo-module.sh`
Generate complete Odoo module structure.

**Usage:**
```bash
./scripts/scaffold-odoo-module.sh \
  --name expense_management \
  --category "Human Resources" \
  --depends hr,account \
  --models expense,expense_category,expense_report
```

**What it creates:**
- Complete module structure (models, views, security, tests)
- OCA-compliant file organization
- Boilerplate code with best practices
- Security rules (ir.model.access.csv)
- Test scaffolding
- README.rst template

**Options:**
- `--name` - Module name (required)
- `--category` - Module category
- `--author` - Author name (default: InsightPulse)
- `--depends` - Comma-separated dependencies
- `--models` - Comma-separated model names
- `--license` - License (default: LGPL-3)
- `--output` - Output directory (default: addons/custom)

---

#### `search-oca-modules.sh`
Search OCA repositories for existing modules.

**Usage:**
```bash
./scripts/search-oca-modules.sh \
  --keywords "expense,approval,travel" \
  --version 19.0 \
  --format table
```

**Output formats:**
- `table` - Human-readable table (default)
- `json` - JSON format for automation
- `csv` - CSV format for spreadsheets

---

### Coming Soon

#### `generate-model.sh`
Generate individual model with fields.

```bash
./scripts/generate-model.sh \
  --module expense_management \
  --model expense.category \
  --fields name:char,code:char,limit:float
```

#### `generate-views.sh`
Generate view XML files.

```bash
./scripts/generate-views.sh \
  --module expense_management \
  --model expense.category \
  --views tree,form,search,pivot
```

#### `generate-tests.sh`
Generate test scaffolding.

```bash
./scripts/generate-tests.sh \
  --module expense_management \
  --model expense.category \
  --test-types unit,integration,access
```

#### `deploy-module.sh`
Validate and deploy module.

```bash
./scripts/deploy-module.sh \
  --module expense_management \
  --env production \
  --validate
```

#### `analyze-saas-app.sh`
Analyze SaaS application features.

```bash
./scripts/analyze-saas-app.sh \
  --app "SAP SuccessFactors" \
  --module "Expense Management" \
  --output analysis/
```

---

## 🚀 Quick Start Examples

### Example 1: Create HR Expense Module

```bash
# Scaffold module
./scripts/scaffold-odoo-module.sh \
  --name hr_expense_insightpulse \
  --category "Human Resources" \
  --depends hr,hr_expense,account \
  --models expense_policy,expense_category

# Search for related OCA modules
./scripts/search-oca-modules.sh \
  --keywords "expense,approval" \
  --format table

# Install and test
cd addons/custom/hr_expense_insightpulse
docker compose exec odoo odoo-bin -d dev_db -i hr_expense_insightpulse --test-enable
```

### Example 2: Replicate SAP Module

```bash
# Search what's already available
./scripts/search-oca-modules.sh --keywords "sap,integration"

# Create base module
./scripts/scaffold-odoo-module.sh \
  --name sap_connector \
  --category "Integration" \
  --depends base,web

# Create data sync module
./scripts/scaffold-odoo-module.sh \
  --name sap_expense_sync \
  --category "Integration" \
  --depends sap_connector,hr_expense
```

---

## 📚 Development Workflow

### 1. Analyze Target Application
```bash
# Document features manually or use script (coming soon)
./scripts/analyze-saas-app.sh --app "Your SaaS App"
```

### 2. Search OCA
```bash
# Find existing modules
./scripts/search-oca-modules.sh --keywords "your,keywords"
```

### 3. Scaffold Custom Modules
```bash
# Create what doesn't exist
./scripts/scaffold-odoo-module.sh --name your_module --models model1,model2
```

### 4. Develop
```bash
# Start dev environment
docker compose -f docker-compose.dev.yml up -d

# Install module
docker compose exec odoo odoo-bin -d dev_db -i your_module --dev=all
```

### 5. Test
```bash
# Run tests
pytest addons/custom/your_module/tests/

# Check coverage
pytest --cov=addons/custom/your_module --cov-report=term
```

### 6. Deploy
```bash
# Validate
./scripts/deploy-module.sh --module your_module --validate

# Deploy
./scripts/deploy-module.sh --module your_module --env production
```

---

## 🎯 Best Practices

### Module Naming
- Use lowercase with underscores: `expense_management`
- Prefix with domain: `hr_expense_mobile`, `account_sap_sync`
- Keep it descriptive but concise

### File Organization
```
your_module/
├── __init__.py
├── __manifest__.py
├── models/           # Business logic
├── views/            # XML views
├── security/         # Access rules
├── data/             # Master data
├── tests/            # Unit tests
├── static/           # Assets
└── README.rst        # Documentation
```

### OCA Conventions
- Follow [OCA guidelines](https://github.com/OCA/maintainer-tools)
- Use `pylint-odoo` for linting
- Add comprehensive tests
- Document everything

---

## 🔧 Troubleshooting

### Script Permission Denied
```bash
chmod +x scripts/*.sh
```

### Module Not Found After Scaffolding
```bash
# Update addons path
docker compose exec odoo odoo-bin -d dev_db --addons-path=/mnt/extra-addons/custom -u all
```

### OCA Search Returns No Results
- Check internet connection
- Try different keywords
- Verify OCA has modules for Odoo 19.0

---

## 📖 Resources

- [Odoo Developer Docs](https://www.odoo.com/documentation/19.0/developer.html)
- [OCA Guidelines](https://github.com/OCA/maintainer-tools)
- [SaaS Replication Playbook](../SAAS_REPLICATION_PLAYBOOK.md)

---

## 🤝 Contributing

Want to add more scripts? Follow this template:

```bash
#!/bin/bash
# Script Name - Brief Description

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Your script logic here

echo -e "${GREEN}✅ Success!${NC}"
```

---

**Status:** ✅ Core scripts available
**Next:** Add more automation scripts as needed
