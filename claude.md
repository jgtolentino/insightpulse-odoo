# Claude AI Assistant Context
**Last Updated:** 2025-11-07
**Purpose:** AI assistant instructions for code generation and architectural guidance
**Freshness:** Maximum 7 days (enforced by CI/CD)

> For operational tasks (installation, monitoring, troubleshooting), see [README.md](README.md).

---

## Section 0: Repository Overview

### Project Mission
InsightPulse Odoo is a **multi-tenant, BIR-compliant Finance Shared Service Center (SSC)** platform built on Odoo 18 CE, replacing expensive SaaS tools like SAP Ariba, Concur, and QuickBooks with 100% open-source alternatives.

### Core Principles
1. **Multi-Tenant First** - Legal entity isolation via `company_id`, not organizational routing
2. **BIR Compliance** - Immutable records, audit trails, e-invoicing ready
3. **Automation-First** - CI/CD, documentation, and deployment fully automated
4. **OCA Standards** - Follow Odoo Community Association conventions strictly
5. **Security by Default** - SQL injection prevention, XSS protection, CSRF tokens

### Key Technologies
- **ERP:** Odoo 18.0 Community Edition
- **Database:** PostgreSQL 15.6 with multi-tenant RLS
- **BI/Analytics:** Apache Superset (Tableau alternative)
- **Backend:** Supabase (auth, storage, edge functions)
- **OCR:** PaddleOCR with DeepSeek LLM validation
- **Infrastructure:** DigitalOcean (Docker, App Platform)

---

## Section 10: Code Generation Guidelines

### When Asked to Write Code

#### 1. Always Check Context First
```bash
# Check if module exists
ls -la odoo/addons/module_name/

# Check existing patterns
grep -r "class.*Model" odoo/addons/module_name/

# Review OCA conventions
cat .github/PLANNING.md
```

#### 2. Follow Odoo Conventions

**Model Structure:**
```python
# âœ… CORRECT: Multi-tenant model
from odoo import models, fields, api

class ExpenseReport(models.Model):
    _name = 'expense.report'
    _description = 'Expense Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_submitted desc'

    # Multi-tenant isolation (REQUIRED)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True
    )

    # BIR compliance fields
    bir_form_2307 = fields.Binary('BIR Form 2307 (Withholding Tax)')
    audit_trail = fields.Text('Audit Trail', readonly=True)

    @api.model
    def create(self, vals):
        # Log audit trail
        vals['audit_trail'] = f"Created by {self.env.user.name} at {fields.Datetime.now()}"
        return super().create(vals)
```

**❌ WRONG: Not multi-tenant**
```python
# Missing company_id
class ExpenseReport(models.Model):
    _name = 'expense.report'
    # Missing: company_id field
    # This violates multi-tenant requirement!
```

#### 3. Security Checklist

Before generating any code, ensure:

- [ ] **SQL Injection:** Use ORM methods, never raw SQL with user input
- [ ] **XSS Prevention:** Escape HTML in templates (`t-esc` not `t-raw`)
- [ ] **CSRF Protection:** Use Odoo's built-in CSRF tokens for forms
- [ ] **Access Rights:** Define `ir.model.access.csv` and record rules
- [ ] **Multi-Tenant Isolation:** Add `company_id` filter to all queries

**âœ… Safe SQL:**
```python
# Use ORM
self.env['expense.report'].search([('company_id', '=', self.env.company.id)])

# If raw SQL is unavoidable (rare), use parameterized queries
self.env.cr.execute("SELECT * FROM expense_report WHERE company_id = %s", (company_id,))
```

**❌ Unsafe SQL:**
```python
# NEVER do this - SQL injection vulnerability!
query = f"SELECT * FROM expense_report WHERE name = '{user_input}'"
self.env.cr.execute(query)
```

#### 4. BIR Compliance Patterns

**Immutable Records (Forms 2307, 2316):**
```python
class BIRForm2307(models.Model):
    _name = 'bir.form.2307'
    _description = 'BIR Form 2307 - Certificate of Creditable Tax Withheld at Source'
    _rec_name = 'certificate_number'

    # Immutable after submission
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True)

    # Prevent modification after submission
    @api.constrains('state')
    def _check_immutable(self):
        for record in self:
            if record.state == 'submitted' and self._origin.state == 'submitted':
                raise ValidationError("Cannot modify submitted BIR forms")
```

#### 5. Include Tests

Every module MUST have tests:

```python
# tests/__init__.py
from . import test_expense_report

# tests/test_expense_report.py
from odoo.tests import TransactionCase

class TestExpenseReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.expense_model = self.env['expense.report']

    def test_multi_tenant_isolation(self):
        """Test company_id isolation"""
        company1 = self.env['res.company'].create({'name': 'Company 1'})
        company2 = self.env['res.company'].create({'name': 'Company 2'})

        expense1 = self.expense_model.create({
            'name': 'Expense 1',
            'company_id': company1.id
        })

        # Switch to company2 context
        expense_search = self.expense_model.with_context(
            allowed_company_ids=[company2.id]
        ).search([('id', '=', expense1.id)])

        self.assertFalse(expense_search, "Should not find expense from another company")
```

#### 6. Document as You Go

Every module needs:

```markdown
# odoo/addons/expense_mgmt/README.md

# Expense Management Module

## Overview
Multi-tenant expense reporting with BIR compliance (Forms 2307, 2316).

## Features
- Multi-level approval workflows
- BIR withholding tax calculation
- OCR receipt scanning (PaddleOCR)
- Superset analytics integration

## Installation
See [INSTALLATION.md](../../docs/INSTALLATION.md)

## Configuration
1. Navigate to Settings > Expense Management
2. Configure approval levels per company
3. Upload BIR tax tables

## Usage
See [USER_GUIDE.md](docs/USER_GUIDE.md)

## API Reference
See [API.md](docs/API.md)

## Testing
```bash
./automate.sh test expense_mgmt
```

## BIR Compliance
- Form 2307: Automated generation
- Form 2316: Annual summary
- e-Invoicing: Ready for 2025 BIR rollout

## License
LGPL-3.0
```

---

## Section 11: Conditional Deployment Mode

### When to Auto-Deploy vs Just Advise

**Auto-Deploy Triggers (use automation):**
- Query mentions: "Odoo", "InsightPulse AI", "Finance SSC", "BIR compliance"
- Task type: "create module", "deploy", "add feature", "fix bug"
- User says: "automate this", "deploy now", "production ready"

**Just Advise (conversational mode):**
- General questions: "How does Odoo work?", "What is multi-tenancy?"
- Exploratory: "Should I use Odoo or NetSuite?"
- Learning: "Explain BIR Form 2307"

**Example Auto-Deploy:**
```
User: "Create a travel request module with multi-level approval"