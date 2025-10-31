# SaaS Replication Playbook: SAP → Odoo CE + OCA

Systematic methodology for replicating any SAP or SaaS application using Odoo Community Edition, OCA modules, and custom development.

---

## 🎯 Overview

This playbook provides a **6-phase systematic approach** to analyze, design, build, and deploy SaaS applications on Odoo.

### Philosophy
- **80/20 Rule**: Use OCA modules for 80% of features, build custom for 20%
- **API-First**: Design for integration from day one
- **Modular**: Each feature = separate addon
- **Data-Driven**: Map data models before coding
- **Automated**: CI/CD for everything

---

## 📋 Phase 1: Feature Analysis & Mapping

### Step 1.1: Document Target Application

Create a **Feature Inventory** document:

```bash
# Use the automation script
./scripts/analyze-saas-app.sh --app "SAP SuccessFactors" --output analysis/
```

**Manual template:**
```markdown
# SaaS Application Analysis: [APP NAME]

## Core Modules
1. Module Name
   - Primary Features
   - Secondary Features
   - Data Models
   - Integrations
   - User Roles

## User Flows
1. Flow Name
   - Steps
   - Decision Points
   - Data Inputs/Outputs
```

### Step 1.2: Categorize Features

Use this classification:

| Category | Examples | Likely Solution |
|----------|----------|-----------------|
| **Core ERP** | Accounting, Sales, Inventory | Odoo CE modules |
| **Industry Standard** | CRM, Project Management | OCA modules |
| **Domain Specific** | Expense approval workflows | Custom modules |
| **Integrations** | API, webhooks, SSO | Custom connectors |
| **UI/UX Custom** | Dashboards, reports | Custom views/reports |

### Step 1.3: Search OCA for Existing Modules

```bash
# Automated OCA search
./scripts/search-oca-modules.sh --feature "expense management"
```

**Manual process:**
1. Go to: https://github.com/OCA
2. Search repositories for keywords
3. Check module maturity:
   - ✅ `installable: True` in manifest
   - ✅ Version matches Odoo 19.0
   - ✅ Active maintenance (commits in last 6 months)
   - ✅ Tests present
   - ✅ Good documentation

### Step 1.4: Gap Analysis

Create a **Feature-to-Module Matrix**:

```bash
# Generate matrix
./scripts/generate-feature-matrix.sh --input analysis/features.yaml
```

**Output example:**
```
Feature                    | Odoo CE | OCA Module              | Custom | Priority
---------------------------|---------|-------------------------|--------|----------
Employee Management        | ✅      | -                       | -      | High
Expense Tracking           | ⚠️      | hr_expense_advance      | ✅     | High
Approval Workflows         | -       | base_tier_validation    | ✅     | High
Mobile App                 | -       | -                       | ✅     | Medium
SSO Integration            | -       | auth_saml               | ⚠️     | High
Advanced Reporting         | ⚠️      | -                       | ✅     | Medium
```

**Legend:**
- ✅ = Available and sufficient
- ⚠️ = Available but needs extension
- ❌ = Not available, must build

---

## 📐 Phase 2: Architecture Design

### Step 2.1: Data Model Design

**Use Odoo's model inheritance pattern:**

```python
# Base model (if extending OCA/CE)
class HRExpense(models.Model):
    _inherit = 'hr.expense'

    # Add custom fields
    approval_level = fields.Integer()
    expense_category_id = fields.Many2one('expense.category')

# New model (if creating from scratch)
class ExpenseCategory(models.Model):
    _name = 'expense.category'
    _description = 'Expense Category'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    limit_amount = fields.Float()
    approval_required = fields.Boolean(default=True)
```

**Create ERD:**
```bash
# Auto-generate ERD from models
./scripts/generate-erd.sh --addon expense_management
```

### Step 2.2: Module Architecture

**Organize by domain:**
```
addons/
├── custom/
│   ├── expense_management/          # Core domain
│   │   ├── models/
│   │   │   ├── expense.py
│   │   │   ├── expense_category.py
│   │   │   └── expense_report.py
│   │   ├── views/
│   │   ├── security/
│   │   ├── data/
│   │   └── __manifest__.py
│   │
│   ├── expense_approval/            # Workflow domain
│   ├── expense_mobile/              # Channel domain
│   └── expense_sap_integration/     # Integration domain
```

**Dependencies tree:**
```mermaid
expense_management (base)
  ├── expense_approval (extends approval logic)
  ├── expense_mobile (adds mobile views)
  └── expense_sap_integration (sync with SAP)
```

### Step 2.3: Integration Architecture

**API-First Design:**
```python
# REST API (using OCA rest_framework)
class ExpenseAPI(restapi.Endpoint):
    _name = 'expense.api'

    @restapi.method([(["/expenses"], "GET")])
    def get_expenses(self, **params):
        """GET /api/expenses"""
        return self._get_expenses(**params)

    @restapi.method([(["/expenses"], "POST")])
    def create_expense(self, **params):
        """POST /api/expenses"""
        return self._create_expense(**params)
```

**Webhook Architecture:**
```python
# Outgoing webhooks
class ExpenseWebhook(models.Model):
    _name = 'expense.webhook'

    def _trigger_webhook(self, event, data):
        """Send webhook on expense events"""
        webhook_url = self.env['ir.config_parameter'].get_param('expense.webhook_url')
        requests.post(webhook_url, json={
            'event': event,
            'data': data,
            'timestamp': fields.Datetime.now()
        })
```

---

## 🛠️ Phase 3: Automated Module Scaffolding

### Step 3.1: Use Module Generator

```bash
# Generate base module structure
./scripts/scaffold-odoo-module.sh \
  --name expense_management \
  --category "Human Resources" \
  --author "InsightPulse" \
  --depends hr,account \
  --models expense,expense_category,expense_report
```

**What it creates:**
```
expense_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── expense.py
│   ├── expense_category.py
│   └── expense_report.py
├── views/
│   ├── expense_views.xml
│   ├── expense_category_views.xml
│   └── expense_report_views.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── expense_category_data.xml
├── tests/
│   ├── __init__.py
│   └── test_expense.py
└── README.rst
```

### Step 3.2: Generate Model Boilerplate

```bash
# Generate model from template
./scripts/generate-model.sh \
  --module expense_management \
  --model expense.category \
  --fields name:char,code:char,limit_amount:float \
  --security expense_user,expense_manager
```

**Generated code:**
```python
from odoo import models, fields, api

class ExpenseCategory(models.Model):
    _name = 'expense.category'
    _description = 'Expense Category'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
    )
    code = fields.Char(
        string='Code',
        required=True
    )
    limit_amount = fields.Float(
        string='Limit Amount',
        digits='Product Price'
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Code must be unique!')
    ]
```

### Step 3.3: Generate Views Automatically

```bash
# Generate tree, form, search views
./scripts/generate-views.sh \
  --module expense_management \
  --model expense.category \
  --views tree,form,search,pivot,graph
```

**Generated XML:**
```xml
<odoo>
    <!-- Tree View -->
    <record id="expense_category_view_tree" model="ir.ui.view">
        <field name="name">expense.category.tree</field>
        <field name="model">expense.category</field>
        <field name="arch" type="xml">
            <tree string="Expense Categories">
                <field name="name"/>
                <field name="code"/>
                <field name="limit_amount"/>
            </tree>
        </field>
    </record>

    <!-- Form View -->
    <record id="expense_category_view_form" model="ir.ui.view">
        <field name="name">expense.category.form</field>
        <field name="model">expense.category</field>
        <field name="arch" type="xml">
            <form string="Expense Category">
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="code"/>
                        <field name="limit_amount"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Action -->
    <record id="expense_category_action" model="ir.actions.act_window">
        <field name="name">Expense Categories</field>
        <field name="res_model">expense.category</field>
        <field name="view_mode">tree,form</field>
    </record>

    <!-- Menu -->
    <menuitem id="expense_category_menu"
              name="Expense Categories"
              parent="hr_expense.menu_hr_expense"
              action="expense_category_action"
              sequence="10"/>
</odoo>
```

---

## 👨‍💻 Phase 4: Development Workflow

### Step 4.1: Development Environment

```bash
# Setup dev environment
./scripts/setup-dev-env.sh --module expense_management

# What it does:
# 1. Creates Python venv
# 2. Installs Odoo + dependencies
# 3. Sets up test database
# 4. Configures VSCode
# 5. Installs pre-commit hooks
```

### Step 4.2: Live Development with Watch Mode

```bash
# Start Odoo with auto-reload
docker compose -f docker-compose.dev.yml watch

# What happens:
# - File changes in addons/ sync instantly
# - Odoo restarts automatically
# - Browser auto-refreshes
```

### Step 4.3: Test-Driven Development

```bash
# Generate test scaffolding
./scripts/generate-tests.sh \
  --module expense_management \
  --model expense.category \
  --test-types unit,integration,access
```

**Generated test:**
```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestExpenseCategory(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ExpenseCategory = self.env['expense.category']

    def test_01_create_category(self):
        """Test creating expense category"""
        category = self.ExpenseCategory.create({
            'name': 'Travel',
            'code': 'TRV',
            'limit_amount': 5000.00
        })
        self.assertEqual(category.name, 'Travel')
        self.assertEqual(category.code, 'TRV')

    def test_02_code_unique(self):
        """Test code uniqueness constraint"""
        self.ExpenseCategory.create({
            'name': 'Travel',
            'code': 'TRV',
        })
        with self.assertRaises(ValidationError):
            self.ExpenseCategory.create({
                'name': 'Transport',
                'code': 'TRV',  # Duplicate!
            })

    def test_03_access_rights(self):
        """Test user access rights"""
        user = self.env.ref('expense_management.expense_user')
        category = self.ExpenseCategory.with_user(user).create({
            'name': 'Meals',
            'code': 'MEAL'
        })
        self.assertTrue(category.id)
```

**Run tests:**
```bash
# Run specific module tests
pytest addons/custom/expense_management/tests/

# Run with coverage
pytest --cov=addons/custom/expense_management

# Run in CI
docker compose exec odoo odoo-bin -d test_db -u expense_management --test-enable --stop-after-init
```

---

## 🔄 Phase 5: Integration & Data Migration

### Step 5.1: API Integration Template

```python
# addons/custom/expense_sap_integration/models/sap_connector.py

class SAPConnector(models.Model):
    _name = 'sap.connector'

    def sync_expenses_to_sap(self):
        """Sync Odoo expenses to SAP"""
        expenses = self.env['hr.expense'].search([
            ('state', '=', 'approved'),
            ('sap_synced', '=', False)
        ])

        for expense in expenses:
            sap_data = self._prepare_sap_data(expense)
            response = self._post_to_sap(sap_data)

            if response.status_code == 200:
                expense.sap_id = response.json()['id']
                expense.sap_synced = True

    def _prepare_sap_data(self, expense):
        """Transform Odoo expense to SAP format"""
        return {
            'employeeId': expense.employee_id.sap_employee_id,
            'expenseType': expense.category_id.sap_code,
            'amount': expense.total_amount,
            'date': expense.date.isoformat(),
            'description': expense.name
        }

    def _post_to_sap(self, data):
        """POST to SAP API"""
        sap_url = self.env['ir.config_parameter'].get_param('sap.api_url')
        sap_token = self.env['ir.config_parameter'].get_param('sap.api_token')

        return requests.post(
            f'{sap_url}/expenses',
            json=data,
            headers={'Authorization': f'Bearer {sap_token}'}
        )
```

### Step 5.2: Data Migration Scripts

```python
# addons/custom/expense_management/migrations/19.0.1.0.0/post-migration.py

def migrate(cr, version):
    """Migrate data from old system"""

    # Example: Import expenses from CSV
    import csv
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    with open('/tmp/legacy_expenses.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Map legacy data to Odoo
            employee = env['hr.employee'].search([
                ('employee_id', '=', row['employee_id'])
            ], limit=1)

            category = env['expense.category'].search([
                ('code', '=', row['category_code'])
            ], limit=1)

            # Create expense
            env['hr.expense'].create({
                'employee_id': employee.id,
                'category_id': category.id,
                'name': row['description'],
                'total_amount': float(row['amount']),
                'date': row['expense_date']
            })
```

### Step 5.3: Webhook Handlers

```python
# addons/custom/expense_webhooks/controllers/webhook.py

from odoo import http
from odoo.http import request
import hmac
import hashlib

class ExpenseWebhook(http.Controller):

    @http.route('/webhook/expense', type='json', auth='public', csrf=False)
    def expense_webhook(self, **kwargs):
        """Receive webhooks from external systems"""

        # Verify signature
        signature = request.httprequest.headers.get('X-Webhook-Signature')
        if not self._verify_signature(signature, request.jsonrequest):
            return {'error': 'Invalid signature'}, 401

        # Process webhook
        data = request.jsonrequest
        event_type = data.get('event_type')

        if event_type == 'expense.approved':
            self._handle_expense_approved(data)
        elif event_type == 'expense.rejected':
            self._handle_expense_rejected(data)

        return {'status': 'success'}

    def _verify_signature(self, signature, payload):
        """Verify webhook signature"""
        secret = request.env['ir.config_parameter'].sudo().get_param('webhook.secret')
        computed = hmac.new(
            secret.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, computed)
```

---

## 🧪 Phase 6: Testing & Deployment

### Step 6.1: Automated Testing Pipeline

```yaml
# .github/workflows/test-modules.yml

name: Test Custom Modules

on:
  push:
    paths:
      - 'addons/custom/**'

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-odoo coverage

      - name: Run tests
        run: |
          # Test each custom module
          for module in addons/custom/*/; do
            module_name=$(basename $module)
            echo "Testing $module_name..."

            odoo-bin -d test_db \
              --addons-path=addons/custom,addons/oca \
              -i $module_name \
              --test-enable \
              --stop-after-init \
              --log-level=test
          done

      - name: Check coverage
        run: |
          coverage run --source=addons/custom -m pytest
          coverage report --fail-under=75
```

### Step 6.2: Deployment Checklist

```bash
# Automated deployment checklist
./scripts/deploy-module.sh --module expense_management --env production

# What it checks:
# ✓ All tests pass
# ✓ Security rules defined
# ✓ Access rights configured
# ✓ Demo data present
# ✓ README.rst exists
# ✓ __manifest__.py valid
# ✓ Dependencies available
# ✓ Migrations present (if needed)
# ✓ Translations complete
# ✓ No pylint errors
```

### Step 6.3: Gradual Rollout

```python
# Feature flags for gradual rollout
class ExpenseFeatureFlags(models.Model):
    _inherit = 'res.company'

    enable_advanced_approval = fields.Boolean(
        default=False,
        help="Enable multi-level approval workflow"
    )

    enable_sap_sync = fields.Boolean(
        default=False,
        help="Enable SAP integration"
    )

# Use in code
if self.company_id.enable_advanced_approval:
    # Use new approval logic
    self._advanced_approval_workflow()
else:
    # Use legacy logic
    self._simple_approval()
```

---

## 📊 Automation Scripts Reference

All scripts are in `scripts/` directory:

### Analysis Scripts
```bash
./scripts/analyze-saas-app.sh
./scripts/search-oca-modules.sh
./scripts/generate-feature-matrix.sh
```

### Scaffolding Scripts
```bash
./scripts/scaffold-odoo-module.sh
./scripts/generate-model.sh
./scripts/generate-views.sh
./scripts/generate-tests.sh
./scripts/generate-erd.sh
```

### Development Scripts
```bash
./scripts/setup-dev-env.sh
./scripts/run-tests.sh
./scripts/check-quality.sh
```

### Deployment Scripts
```bash
./scripts/deploy-module.sh
./scripts/migrate-data.sh
./scripts/rollback-module.sh
```

---

## 🎓 Best Practices

### DO:
- ✅ **One feature per module** - Keep modules focused
- ✅ **Inherit, don't modify** - Use `_inherit` to extend OCA/CE
- ✅ **API-first** - Design REST APIs from day one
- ✅ **Test everything** - Aim for 80%+ coverage
- ✅ **Document everything** - README.rst + docstrings
- ✅ **Use OCA tools** - maintainer-quality-tools, oca-gen-addon-readme
- ✅ **Follow OCA conventions** - model naming, file structure
- ✅ **Version semantically** - 19.0.1.0.0 format

### DON'T:
- ❌ **Modify core files** - Always inherit
- ❌ **Hardcode values** - Use ir.config_parameter
- ❌ **Skip security** - Always define access rules
- ❌ **Forget migrations** - Provide upgrade paths
- ❌ **Ignore performance** - Index database fields
- ❌ **Mix concerns** - Separate business logic from UI
- ❌ **Use sudo() carelessly** - Can bypass security
- ❌ **Commit without testing** - Pre-commit hooks save time

---

## 📈 Success Metrics

Track these KPIs for each replication project:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Feature Coverage** | >90% | Features implemented / Total features |
| **OCA Usage** | >60% | OCA modules used / Total modules |
| **Code Quality** | A+ | pylint-odoo score |
| **Test Coverage** | >75% | pytest-cov report |
| **Time to MVP** | <4 weeks | First deployable version |
| **Bug Density** | <5/module | Bugs found in first month |
| **Performance** | <2s page load | Odoo profiler |
| **User Adoption** | >80% | Active users / Total users |

---

## 🗂️ Project Structure Template

```
project-name/
├── addons/
│   ├── custom/
│   │   ├── base_module/              # Core domain logic
│   │   ├── workflow_module/          # Business workflows
│   │   ├── integration_module/       # External integrations
│   │   └── reporting_module/         # Analytics & reports
│   └── oca/                           # OCA modules
│
├── analysis/
│   ├── features.yaml                 # Feature inventory
│   ├── feature-matrix.xlsx           # Gap analysis
│   ├── data-model.mmd                # ERD (Mermaid)
│   └── api-spec.yaml                 # OpenAPI specification
│
├── migrations/
│   ├── legacy-data-export.sql
│   └── data-transformation.py
│
├── scripts/
│   ├── analyze-saas-app.sh
│   ├── scaffold-odoo-module.sh
│   ├── generate-model.sh
│   ├── generate-views.sh
│   ├── generate-tests.sh
│   ├── deploy-module.sh
│   └── README.md
│
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start Example

Let's replicate **SAP SuccessFactors Expense Management**:

### Step 1: Analyze
```bash
./scripts/analyze-saas-app.sh \
  --app "SAP SuccessFactors" \
  --module "Expense Management" \
  --output analysis/sap-expense/
```

### Step 2: Search OCA
```bash
./scripts/search-oca-modules.sh \
  --keywords "expense,approval,travel" \
  --version 19.0
```

**Found OCA modules:**
- `hr_expense` (Odoo CE - built-in)
- `hr_expense_advance` (OCA)
- `hr_expense_tier_validation` (OCA)
- `hr_expense_sequence` (OCA)

### Step 3: Identify Gaps

**Need to build custom:**
- Mobile receipt capture
- SAP integration
- Custom approval rules
- Advanced analytics

### Step 4: Scaffold Custom Modules
```bash
# Core expense extensions
./scripts/scaffold-odoo-module.sh \
  --name expense_insightpulse \
  --depends hr_expense,hr_expense_advance

# Mobile app
./scripts/scaffold-odoo-module.sh \
  --name expense_mobile \
  --depends expense_insightpulse

# SAP integration
./scripts/scaffold-odoo-module.sh \
  --name expense_sap_connector \
  --depends expense_insightpulse
```

### Step 5: Develop
```bash
# Start dev environment
docker compose -f docker-compose.dev.yml up -d

# Install modules
docker compose exec odoo odoo-bin \
  -d dev_db \
  -i expense_insightpulse,expense_mobile,expense_sap_connector \
  --dev=all
```

### Step 6: Test & Deploy
```bash
# Run tests
./scripts/run-tests.sh --module expense_insightpulse

# Deploy to staging
./scripts/deploy-module.sh \
  --module expense_insightpulse \
  --env staging

# Deploy to production (after validation)
./scripts/deploy-module.sh \
  --module expense_insightpulse \
  --env production
```

**Total time:** 2-4 weeks for MVP

---

## 🔗 Resources

### Odoo Official
- [Developer Documentation](https://www.odoo.com/documentation/19.0/developer.html)
- [Odoo Apps Store](https://apps.odoo.com/)
- [Odoo GitHub](https://github.com/odoo/odoo)

### OCA (Odoo Community Association)
- [OCA GitHub](https://github.com/OCA)
- [OCA Guidelines](https://github.com/OCA/maintainer-tools)
- [Module Categories](https://github.com/OCA?q=&type=all&language=&sort=)

### Tools
- [pylint-odoo](https://github.com/OCA/pylint-odoo) - Odoo linting
- [oca-gen-addon-readme](https://github.com/OCA/maintainer-tools) - Generate READMEs
- [click-odoo](https://github.com/acsone/click-odoo) - CLI tools
- [pytest-odoo](https://github.com/camptocamp/pytest-odoo) - Testing

### Communities
- [Odoo Community Forum](https://www.odoo.com/forum)
- [OCA Discussions](https://github.com/OCA/maintainer-tools/discussions)
- [r/Odoo on Reddit](https://reddit.com/r/Odoo)

---

## 📞 Next Steps

1. **Review** this playbook
2. **Choose** a SaaS app to replicate
3. **Run** the analysis scripts
4. **Start** with scaffolding
5. **Deploy** your first custom module

**Questions?** Open an issue or check the automation scripts in `scripts/`

---

**Status:** ✅ Playbook ready for use
**Automation:** Scripts available in `scripts/` directory
**Next:** Create first automation scripts
