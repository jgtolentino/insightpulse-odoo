# Odoo CE & OCA Native Documentation Sources

## Official Documentation Hierarchy

### 🥇 PRIMARY SOURCES (Always Check First)

#### 1. **Odoo Official Documentation**
```
URL: https://www.odoo.com/documentation/19.0/

Structure:
├── developer/              # Developer reference
│   ├── reference/
│   │   ├── backend/       # ORM, Models, Views
│   │   ├── frontend/      # JavaScript, OWL
│   │   └── data/          # XML, CSV, Security
│   ├── tutorials/         # Step-by-step guides
│   └── howtos/            # Specific tasks
│
├── applications/          # Functional documentation
│   ├── finance/           # Accounting, Invoicing
│   ├── sales/             # CRM, Sales Orders
│   ├── inventory/         # Stock, Warehousing
│   └── studio/            # No-code customization
│
└── administration/        # Deployment, Setup
    ├── install/           # Installation guides
    ├── deployment/        # Production deployment
    └── upgrade/           # Version migration
```

**Key Pages to Bookmark:**

**Developer Reference:**
```
Core ORM:
https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html

Models & Fields:
https://www.odoo.com/documentation/19.0/developer/reference/backend/models.html

Views (XML):
https://www.odoo.com/documentation/19.0/developer/reference/backend/views.html

Security:
https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html

QWeb Reports:
https://www.odoo.com/documentation/19.0/developer/reference/frontend/qweb.html

JavaScript/OWL:
https://www.odoo.com/documentation/19.0/developer/reference/frontend/javascript_reference.html
```

**Application Guides:**
```
Accounting:
https://www.odoo.com/documentation/19.0/applications/finance/accounting.html

Invoicing:
https://www.odoo.com/documentation/19.0/applications/finance/accounting/customer_invoices.html

Studio:
https://www.odoo.com/documentation/19.0/applications/studio.html

Automated Actions:
https://www.odoo.com/documentation/19.0/applications/studio/automated_actions.html
```

#### 2. **OCA Official Documentation**

**Main OCA Website:**
```
URL: https://odoo-community.org/

Key Resources:
├── Documentation         # OCA guidelines
├── Module Browser       # Search modules
├── Contributing Guide   # How to contribute
└── Maintainer Tools     # Development tools
```

**OCA GitHub Organization:**
```
URL: https://github.com/OCA

Repository Categories:
├── account-*            # Accounting modules (14 repos)
├── hr-*                 # HR modules (10 repos)
├── project-*            # Project management (7 repos)
├── sale-*               # Sales modules (9 repos)
├── purchase-*           # Purchase modules (5 repos)
├── stock-*              # Inventory modules (6 repos)
├── server-tools         # Backend utilities
├── web                  # Frontend enhancements
└── reporting-engine     # Report generators
```

**Per-Repository Documentation Pattern:**

Every OCA repo follows this structure:
```
OCA/[repo-name]/
├── README.md                    # Repository overview
├── [module-name]/
│   ├── README.rst              # Module documentation
│   ├── __manifest__.py         # Module metadata
│   ├── models/                 # Python code
│   ├── views/                  # XML views
│   ├── security/               # Access rules
│   ├── data/                   # Master data
│   ├── demo/                   # Demo data
│   ├── tests/                  # Unit tests
│   └── static/
│       └── description/
│           ├── index.html      # Module description
│           └── icon.png        # Module icon
```

**Example: Reading OCA Module Docs**
```
Repository: OCA/hr-expense
Module: hr_expense_advance_clearing

Direct Links:
1. README: https://github.com/OCA/hr-expense/blob/19.0/hr_expense_advance_clearing/README.rst
2. Manifest: https://github.com/OCA/hr-expense/blob/19.0/hr_expense_advance_clearing/__manifest__.py
3. Models: https://github.com/OCA/hr-expense/tree/19.0/hr_expense_advance_clearing/models
4. Views: https://github.com/OCA/hr-expense/tree/19.0/hr_expense_advance_clearing/views
```

### 🥈 SECONDARY SOURCES (For Deep Dives)

#### 3. **Odoo Source Code (GitHub)**

**Official Odoo Repository:**
```
URL: https://github.com/odoo/odoo

Branch: 19.0 (always use your target version)
```

**Key Directories:**
```
odoo/
├── odoo/                       # Core framework
│   ├── models.py              # BaseModel class
│   ├── fields.py              # Field types
│   ├── api.py                 # API decorators
│   ├── exceptions.py          # Exception classes
│   └── http.py                # HTTP controllers
│
├── addons/                     # Standard modules
│   ├── base/                  # Base module (required)
│   ├── account/               # Accounting
│   ├── sale/                  # Sales
│   ├── purchase/              # Purchase
│   ├── hr/                    # Human Resources
│   └── project/               # Project Management
│
└── doc/                        # Internal documentation
```

**Reading Source Code Workflow:**

**Example 1: Understanding Many2one Field**
```python
# Step 1: Find field definition
File: odoo/odoo/fields.py
Class: Many2one
Line: ~2000

# Step 2: Read docstring
"""
    The attribute ``comodel_name`` is mandatory except in the case of related
    or extended fields.

    :param str comodel_name: name of the target model (string)
    :param domain: an optional domain to set on candidate values on the
        client side (domain or string)
    :param dict context: an optional context to use on the client side when
        handling that field
    :param str ondelete: what to do when the referred record is deleted;
        possible values are: ``'set null'``, ``'restrict'``, ``'cascade'``
"""

# Step 3: Find usage examples
Search in addons: grep -r "Many2one" odoo/addons/*/models/*.py
```

**Example 2: Understanding Automated Actions**
```python
# Step 1: Find base automation model
File: odoo/addons/base_automation/models/base_automation.py
Class: BaseAutomation

# Step 2: Read trigger types
def _check_trigger(self):
    if self.trigger == 'on_create':
        ...
    elif self.trigger == 'on_write':
        ...
    elif self.trigger == 'on_time':
        ...

# Step 3: Understand action execution
def _process(self, records):
    # Execute actions on filtered records
    ...
```

#### 4. **OCA Module Documentation (In Repo)**

**Direct Documentation Links:**

**Account Financial Tools:**
```
Repo: https://github.com/OCA/account-financial-tools/tree/19.0
Key Modules:
- account_move_name_sequence: Custom invoice numbering
- account_fiscal_year: Define fiscal year
- account_journal_lock_date: Lock journal entries
```

**Server Tools:**
```
Repo: https://github.com/OCA/server-tools/tree/19.0
Key Modules:
- base_technical_user: Technical admin user
- sentry: Error tracking integration
- mail_tracking: Email delivery tracking
- scheduler_error_mailer: Cron error notifications
```

**Reporting Engine:**
```
Repo: https://github.com/OCA/reporting-engine/tree/19.0
Key Modules:
- report_xlsx: Excel report generation
- report_qweb_pdf_watermark: PDF watermarks
- report_py3o: ODT/DOCX reports
- mis_builder: Management Information System reports
```

### 🥉 TERTIARY SOURCES (Community Knowledge)

#### 5. **Odoo Community Forum**
```
URL: https://www.odoo.com/forum

Sections:
├── Help               # Q&A for development issues
├── Feedback           # Feature requests
└── Tips & Tricks      # Best practices

Search Pattern:
"[module_name] [error_message] site:odoo.com/forum"

Example:
"account.move ValidationError site:odoo.com/forum"
```

#### 6. **OCA Runbot (Live Demos)**
```
URL: https://runbot.odoo-community.org/

Purpose:
- Test OCA modules live
- See module functionality
- Check compatibility
- Preview before installation
```

#### 7. **Stack Overflow**
```
URL: https://stackoverflow.com/questions/tagged/odoo

Tag: [odoo] + [python] + [postgresql]

Search Pattern:
"odoo 19.0 [your question]"

Best for:
- Common errors
- API usage examples
- Integration patterns
```

---

## Complete Documentation Workflow

### Scenario 1: Building a New Module

**Step 1: Understand Requirements**
```
Question: "Build expense approval workflow with 3 levels"
```

**Step 2: Check Odoo Official Docs**
```
Visit: https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101.html

Learn:
- Module structure
- Model definition
- View creation
- Security rules
```

**Step 3: Check OCA for Similar Modules**
```
Visit: https://github.com/OCA?q=expense&type=repositories

Found: OCA/hr-expense repository

Check modules:
- hr_expense_advance_clearing ✅ Has approval workflow
- hr_expense_sequence ✅ Has numbering
- hr_expense_invoice ✅ Has invoice integration
```

**Step 4: Read OCA Module Documentation**
```
Visit: https://github.com/OCA/hr-expense/blob/19.0/hr_expense_advance_clearing/README.rst

Learn:
- Advance payment process
- Approval states
- Clearing workflow
- Accounting integration
```

**Step 5: Read Source Code**
```
File: https://github.com/OCA/hr-expense/blob/19.0/hr_expense_advance_clearing/models/hr_expense.py

Understand:
- State field definition
- Approval methods
- Workflow transitions
- Computed fields
```

**Step 6: Decide Approach**
```
Decision: Extend hr_expense_advance_clearing + Add 3rd level approval

Module: ipai_expense_approval_extended
Depends: ['hr_expense', 'hr_expense_advance_clearing']
```

### Scenario 2: Debugging an Error

**Error Message:**
```
ValidationError: Invalid field 'partner_id' on model 'account.move'
```

**Step 1: Check Odoo Official Docs**
```
Visit: https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#fields

Search: "ValidationError"
Learn: Common causes (missing field, wrong type, constraint failure)
```

**Step 2: Check Source Code**
```
File: https://github.com/odoo/odoo/blob/19.0/addons/account/models/account_move.py

Search for: partner_id field definition
Check: Field type, required, domain, compute
```

**Step 3: Check Forum for Similar Issues**
```
Search: "account.move partner_id ValidationError site:odoo.com/forum"

Find: Common issues:
- Missing partner_id in data files
- Constraint violation (partner_id required for invoices)
- Wrong partner_id value (deleted partner)
```

**Step 4: Check Stack Overflow**
```
Search: "odoo 19.0 account.move partner_id validation"

Find: Code examples showing correct usage
```

**Step 5: Fix and Test**
```python
# In custom module:
class AccountMove(models.Model):
    _inherit = 'account.move'

    # Override to add custom validation
    @api.constrains('partner_id')
    def _check_partner_id(self):
        for move in self:
            if move.move_type in ('out_invoice', 'out_refund') and not move.partner_id:
                raise ValidationError('Customer is required for customer invoices')
```

### Scenario 3: Learning a New API

**Need:** "How to create automated actions programmatically?"

**Step 1: Check Official Docs**
```
Visit: https://www.odoo.com/documentation/19.0/applications/studio/automated_actions.html

Learn:
- Trigger types
- Action types
- Filter domains
- Python code execution
```

**Step 2: Check Source Code**
```
File: https://github.com/odoo/odoo/blob/19.0/odoo/addons/base_automation/models/base_automation.py

Study:
- Model: base.automation
- Fields: trigger, model_id, filter_domain, action_server_ids
- Methods: _process(), _check_trigger()
```

**Step 3: Find Usage Example in OCA**
```
Search GitHub: "base.automation create" in:file extension:py org:OCA

Found example in OCA/server-tools:
```python
automation = self.env['base.automation'].create({
    'name': 'Send Email on Invoice Validation',
    'model_id': self.env.ref('account.model_account_move').id,
    'trigger': 'on_write',
    'filter_domain': "[('state', '=', 'posted')]",
    'action_server_ids': [(6, 0, [action_send_email.id])],
})
```

**Step 4: Implement in Custom Module**
```python
# data/base_automation.xml
<record id="automation_invoice_validated" model="base.automation">
    <field name="name">Send Email on Invoice Validation</field>
    <field name="model_id" ref="account.model_account_move"/>
    <field name="trigger">on_write</field>
    <field name="filter_domain">[('state', '=', 'posted')]</field>
    <field name="code">
        for record in records:
            record.message_post(
                body='Invoice validated',
                subject='Invoice %s' % record.name
            )
    </field>
</record>
```

---

## Quick Reference: Where to Find What

### Models & ORM
```
Primary: https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html
Source: https://github.com/odoo/odoo/blob/19.0/odoo/models.py
Source: https://github.com/odoo/odoo/blob/19.0/odoo/fields.py
Example: OCA modules /models/ directory
```

### Views & UI
```
Primary: https://www.odoo.com/documentation/19.0/developer/reference/backend/views.html
Source: https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/views/
Example: OCA modules /views/ directory
QWeb: https://www.odoo.com/documentation/19.0/developer/reference/frontend/qweb.html
```

### Security
```
Primary: https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html
Source: https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/security/
Example: OCA modules /security/ directory
```

### Controllers & HTTP
```
Primary: https://www.odoo.com/documentation/19.0/developer/reference/backend/http.html
Source: https://github.com/odoo/odoo/blob/19.0/odoo/http.py
Example: https://github.com/OCA/server-tools search "controllers"
```

### JavaScript & OWL
```
Primary: https://www.odoo.com/documentation/19.0/developer/reference/frontend/javascript_reference.html
Source: https://github.com/odoo/odoo/tree/19.0/addons/web/static/src
Example: OCA/web modules
```

### Reports (PDF)
```
Primary: https://www.odoo.com/documentation/19.0/developer/reference/frontend/qweb.html#reporting
Source: https://github.com/odoo/odoo/tree/19.0/addons/web/report
Example: OCA/reporting-engine
```

### Testing
```
Primary: https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html
Source: https://github.com/odoo/odoo/blob/19.0/odoo/tests/
Example: OCA modules /tests/ directory
```

### Deployment
```
Primary: https://www.odoo.com/documentation/19.0/administration/deployment.html
Docker: https://github.com/Tecnativa/docker-odoo-base
Example: OCA/maintainer-tools deployment scripts
```

---

## Documentation Reading Priorities

### Week 1: Foundation
```
Day 1: Odoo Developer Tutorial
https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101.html

Day 2: ORM API Reference
https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html

Day 3: Models & Fields
https://www.odoo.com/documentation/19.0/developer/reference/backend/models.html

Day 4: Views Reference
https://www.odoo.com/documentation/19.0/developer/reference/backend/views.html

Day 5: Security
https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html
```

### Week 2: OCA Standards
```
Day 1: Browse OCA/account-financial-tools
https://github.com/OCA/account-financial-tools/tree/19.0

Day 2: Study OCA/server-tools
https://github.com/OCA/server-tools/tree/19.0

Day 3: Review OCA/reporting-engine
https://github.com/OCA/reporting-engine/tree/19.0

Day 4: OCA Contributing Guide
https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst

Day 5: OCA Module Template
https://github.com/OCA/oca-addons-repo-template
```

### Week 3: Deep Dive (Your Domain)
```
Day 1-2: Finance/Accounting modules
- Odoo account module source code
- OCA account-* repositories

Day 3-4: HR/Expense modules
- Odoo hr_expense module
- OCA hr-expense repository

Day 5: Integration patterns
- Webhook implementations
- External API integrations
```

---

## Tools for Efficient Documentation Usage

### 1. Browser Bookmarks Structure
```
📁 Odoo Docs
├── 📄 Developer Reference (official)
├── 📄 ORM API (official)
├── 📄 Views Reference (official)
├── 📄 Security (official)
└── 📄 Studio (official)

📁 Odoo Source
├── 📄 odoo/odoo (GitHub)
├── 📄 odoo/addons (GitHub)
└── 📄 odoo 19.0 branch (GitHub)

📁 OCA
├── 📄 OCA GitHub (organization)
├── 📄 account-financial-tools
├── 📄 server-tools
├── 📄 reporting-engine
├── 📄 hr-expense
└── 📄 OCA Runbot

📁 Community
├── 📄 Odoo Forum
├── 📄 Stack Overflow [odoo]
└── 📄 Odoo Apps Store
```

### 2. Local Documentation Clone
```bash
# Clone Odoo source for offline reference
git clone --depth 1 --branch 19.0 https://github.com/odoo/odoo.git ~/odoo-19.0-source

# Clone key OCA repositories
git clone --depth 1 --branch 19.0 https://github.com/OCA/account-financial-tools.git ~/oca/account-financial-tools
git clone --depth 1 --branch 19.0 https://github.com/OCA/server-tools.git ~/oca/server-tools
git clone --depth 1 --branch 19.0 https://github.com/OCA/hr-expense.git ~/oca/hr-expense

# Use grep/ripgrep for fast searching
rg "Many2one" ~/odoo-19.0-source/odoo/
rg "base.automation" ~/oca/server-tools/
```

### 3. VS Code Extensions
```json
{
  "recommendations": [
    "jigar-patel.OdooSnippets",        // Odoo code snippets
    "trinhanhngoc.odoo-development",   // Odoo syntax
    "ms-python.python",                 // Python support
    "redhat.vscode-xml",                // XML support
    "GitHub.copilot"                    // AI assistance
  ]
}
```

---

## Best Practices

### ✅ Documentation Reading Workflow

**1. Start Broad → Narrow Down**
```
Official Docs → Source Code → OCA Examples → Forum
```

**2. Use Multiple Sources**
```
Read official docs for concepts
Check source code for details
Find OCA examples for patterns
Search forum for issues
```

**3. Take Notes**
```
# Create docs/learning-notes/
- orm-patterns.md
- view-syntax.md
- security-rules.md
- oca-standards.md
```

**4. Build Examples**
```
# Create test modules while learning
test-modules/
├── test_orm/
├── test_views/
├── test_security/
└── test_automation/
```

### ❌ Common Mistakes

**Don't:**
- Rely only on tutorials (outdated quickly)
- Skip official docs (miss important details)
- Ignore OCA standards (code quality issues)
- Copy-paste without understanding (debugging nightmare)

**Do:**
- Read official docs first
- Check OCA for patterns
- Understand before implementing
- Document your learnings

---

## Quick Start Checklist

**Today:**
- [ ] Bookmark Odoo 19.0 developer docs
- [ ] Clone odoo/odoo repository (19.0 branch)
- [ ] Browse OCA GitHub organization
- [ ] Read: ORM API reference

**This Week:**
- [ ] Complete Odoo developer tutorial
- [ ] Study 5 OCA modules in your domain
- [ ] Clone key OCA repositories locally
- [ ] Create learning notes directory

**This Month:**
- [ ] Read all core API references
- [ ] Understand 20+ OCA modules
- [ ] Build 3 test modules
- [ ] Document patterns learned

---

**Start Here:** https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101.html

**Your next module starts with the right documentation!** 📚
