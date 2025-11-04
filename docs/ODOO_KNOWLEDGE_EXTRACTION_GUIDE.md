# Odoo Knowledge Extraction Guide

## How to Build Skills, Capabilities, and Knowledge from Odoo Documentation

This guide shows how to systematically extract knowledge from the [Odoo 19.0 Developer Reference](https://www.odoo.com/documentation/19.0/developer/reference.html) and transform it into reusable Claude skills.

---

## Overview: Documentation → Skills Pipeline

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Map Documentation Structure                    │
│ → Identify major topics and capabilities               │
└───────────────┬─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────┐
│ Step 2: Extract Concrete Examples                      │
│ → Find code samples, patterns, use cases               │
└───────────────┬─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────┐
│ Step 3: Identify Reusable Components                   │
│ → Scripts, references, assets, templates               │
└───────────────┬─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────┐
│ Step 4: Create Skill Structure                         │
│ → Use skill-creator pattern, organize resources        │
└───────────────┬─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────┐
│ Step 5: Package and Test                               │
│ → Validate, package, iterate                           │
└─────────────────────────────────────────────────────────┘
```

---

## Step 1: Map Documentation Structure

The Odoo 19.0 Developer Reference covers these major areas:

### Core Framework Areas

1. **ORM (Object-Relational Mapping)**
   - Model definitions and fields
   - Recordsets and operations
   - CRUD operations
   - Computed fields and onchanges
   - Inheritance patterns

2. **Views & UI**
   - Form, Tree, Kanban, Graph, Pivot, Calendar views
   - QWeb templating engine
   - JavaScript/OWL framework
   - Client actions and widgets

3. **Data Files**
   - XML data files
   - CSV imports
   - External IDs
   - Demo and initialization data

4. **Security**
   - Access rights (ir.model.access.csv)
   - Record rules (ir.rule)
   - Groups and users
   - Field-level security

5. **Controllers & HTTP**
   - HTTP routes (JSON/HTTP)
   - Request/response handling
   - Authentication methods
   - File uploads/downloads

6. **Workflows & Automation**
   - Scheduled actions (cron)
   - Server actions
   - Automated actions
   - Workflow states

7. **Reports**
   - QWeb PDF reports
   - Excel/CSV exports
   - Report actions
   - Custom templates

8. **Testing**
   - Unit tests
   - Form and flow tests
   - Test classes and fixtures

9. **Deployment**
   - Configuration files
   - Command-line interface
   - Database management
   - Module installation

10. **Web Services**
    - XML-RPC API
    - JSON-RPC API
    - External API integration

---

## Step 2: Extract Concrete Examples

For each documentation area, extract:

### Code Patterns
Extract reusable code patterns from the docs:

**Example: ORM Model Definition**
```python
# Pattern: Basic model with computed field
from odoo import models, fields, api

class ExpenseClaim(models.Model):
    _name = 'expense.claim'
    _description = 'Expense Claim'

    name = fields.Char(required=True)
    amount = fields.Float()
    tax_amount = fields.Float(compute='_compute_tax')
    total = fields.Float(compute='_compute_total')

    @api.depends('amount')
    def _compute_tax(self):
        for rec in self:
            rec.tax_amount = rec.amount * 0.12

    @api.depends('amount', 'tax_amount')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.amount + rec.tax_amount
```

### Common Use Cases
Document typical scenarios developers face:

- "Create a model with approval workflow"
- "Add computed fields with dependencies"
- "Build a Kanban view with drag-and-drop"
- "Generate PDF report from QWeb template"
- "Create scheduled action for daily tasks"
- "Implement Many2one relationship"

### Anti-Patterns & Gotchas
Capture common mistakes from documentation notes:

- ❌ Don't use `browse()` in loops - use recordsets directly
- ❌ Don't modify recordsets in computed fields
- ❌ Don't forget `@api.depends()` on computed fields
- ✅ Always use `ensure_one()` when accessing single records
- ✅ Use `sudo()` carefully - security implications
- ✅ Prefer `mapped()`, `filtered()` over Python loops

---

## Step 3: Identify Reusable Components

For each topic, determine what resources would help:

### Scripts Directory (`scripts/`)

**Example: Generate boilerplate code**

```python
# scripts/scaffold_model.py
"""
Generate Odoo model boilerplate from simple specification.

Usage:
    python scripts/scaffold_model.py expense.claim \
        --fields "name:char,amount:float,date:date" \
        --compute "total=amount+tax"
"""
```

**Example: Validate module structure**
```python
# scripts/validate_module.py
"""
Validate Odoo module structure against OCA standards.

Checks:
- __manifest__.py format
- License headers
- Access rights files
- README.rst format
"""
```

### References Directory (`references/`)

**Example: ORM Quick Reference**
```markdown
# references/orm-api.md

## Recordset Operations

### Search
- `search([domain])` - Find records
- `search_count([domain])` - Count matches
- `search_read([domain], fields)` - Search + read in one call

### CRUD
- `create(vals_list)` - Create records
- `write(vals)` - Update records
- `unlink()` - Delete records

### Recordset Operations
- `mapped('field')` - Extract field values
- `filtered(lambda r: r.active)` - Filter records
- `sorted(key=lambda r: r.name)` - Sort records
```

**Example: Field Types Reference**
```markdown
# references/field-types.md

## Basic Fields
- `Char(string, size=None, required=False)`
- `Text(string)`
- `Integer(string)`
- `Float(string, digits=None)`
- `Boolean(string)`

## Relational Fields
- `Many2one(comodel, string, ondelete='set null')`
- `One2many(comodel, inverse, string)`
- `Many2many(comodel, relation=None, column1=None, column2=None)`

## Date/Time
- `Date(string)`
- `Datetime(string)`

## Special Fields
- `Selection(selection, string)` - Dropdown
- `Binary(string)` - File storage
- `Html(string)` - Rich text
```

### Assets Directory (`assets/`)

**Example: Module template**
```
assets/module-template/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── model_template.py
├── views/
│   └── views_template.xml
├── security/
│   └── ir.model.access.csv
└── README.rst
```

**Example: View templates**
```xml
<!-- assets/view-templates/form-view.xml -->
<record id="view_model_form" model="ir.ui.view">
    <field name="name">model.form</field>
    <field name="model">your.model</field>
    <field name="arch" type="xml">
        <form string="Your Model">
            <sheet>
                <group>
                    <field name="name"/>
                </group>
            </sheet>
        </form>
    </field>
</record>
```

---

## Step 4: Create Skill Structure

### Skill Planning Matrix

Use this matrix to decide what skills to create:

| Documentation Section | Skill Name | Scripts | References | Assets | Priority |
|----------------------|------------|---------|-----------|---------|----------|
| ORM API | `odoo-orm-expert` | ✅ Model scaffolder | ✅ API reference | ✅ Templates | HIGH |
| Views & QWeb | `odoo-view-builder` | ✅ View generator | ✅ View types | ✅ View templates | HIGH |
| Security | `odoo-security-config` | ✅ Security validator | ✅ Security guide | ✅ Security templates | MEDIUM |
| Reports | `odoo-report-generator` | ✅ Report scaffolder | ✅ QWeb reference | ✅ Report templates | MEDIUM |
| Controllers | `odoo-api-builder` | ✅ Route generator | ✅ HTTP guide | ✅ Controller templates | MEDIUM |
| Testing | `odoo-test-writer` | ✅ Test generator | ✅ Testing patterns | ✅ Test templates | LOW |

### Example Skill: ORM Expert

```markdown
# .claude/skills/odoo-orm-expert/SKILL.md

---
name: odoo-orm-expert
description: Expert guidance for Odoo ORM operations including model definitions, recordsets, computed fields, and CRUD operations. Use when working with Odoo models, fields, or database operations.
---

# Odoo ORM Expert

Transform Claude into an Odoo ORM expert that helps with model definitions, recordset operations, and database interactions.

## When to Use This Skill

- Creating new Odoo models with fields
- Working with recordsets and CRUD operations
- Implementing computed fields and onchanges
- Defining model inheritance patterns
- Optimizing database queries

## Quick Start Patterns

### Pattern 1: Create Basic Model
```python
# Use scripts/scaffold_model.py for boilerplate
python scripts/scaffold_model.py your.model \\
    --fields "name:char:required,amount:float,date:date" \\
    --description "Your Model Description"
```

### Pattern 2: Add Computed Field
See [references/computed-fields.md](references/computed-fields.md) for patterns.

### Pattern 3: Optimize Recordset Operations
See [references/recordset-optimization.md](references/recordset-optimization.md) for best practices.

## Resources Available

- **scripts/scaffold_model.py** - Generate model boilerplate
- **scripts/validate_fields.py** - Check field definitions
- **references/orm-api.md** - Complete ORM API reference
- **references/field-types.md** - All field types with examples
- **references/computed-fields.md** - Computed field patterns
- **references/recordset-optimization.md** - Performance tips
- **assets/model-templates/** - Common model patterns

## Common Workflows

### Create Model with Relationships
[workflow details...]

### Add Approval Workflow
[workflow details...]

### Implement Multi-Company Support
[workflow details...]
```

---

## Step 5: Practical Implementation

### Phase 1: Start with High-Value Skills (Week 1-2)

1. **odoo-orm-expert** - Most frequently used
2. **odoo-view-builder** - UI is critical
3. **odoo-security-config** - Security is essential

### Phase 2: Expand Coverage (Week 3-4)

4. **odoo-report-generator** - Common requirement
5. **odoo-api-builder** - External integrations
6. **odoo-workflow-designer** - Business logic

### Phase 3: Advanced Skills (Month 2)

7. **odoo-test-writer** - Quality assurance
8. **odoo-performance-optimizer** - Scaling
9. **odoo-deployment-expert** - Production operations

---

## Extraction Workflow Example

Let's extract knowledge from "ORM API" documentation section:

### Step 1: Read Documentation
```bash
# Fetch the ORM API documentation
curl https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html \\
    > docs/odoo-orm-reference.html
```

### Step 2: Identify Patterns
Extract these patterns from the docs:
- Model definition syntax
- Field type declarations
- Computed field decorators
- Recordset operation methods
- Inheritance patterns

### Step 3: Create Scripts
```python
# scripts/scaffold_model.py
import sys

def generate_model(model_name, fields, description):
    """Generate Odoo model boilerplate."""
    template = '''from odoo import models, fields, api

class {class_name}(models.Model):
    _name = '{model_name}'
    _description = '{description}'

{fields}
'''
    # Implementation...
    return template
```

### Step 4: Create References
```markdown
# references/orm-api.md

# Odoo ORM API Reference

## Model Methods

### Search Methods
- `search(domain, offset=0, limit=None, order=None)` - Returns recordset
- `search_count(domain)` - Returns integer count
- `search_read(domain, fields, offset=0, limit=None, order=None)` - Returns list of dicts

[Continue with full API...]
```

### Step 5: Create Assets
```
assets/model-templates/
├── basic_model.py
├── transient_model.py
├── inherited_model.py
└── abstract_mixin.py
```

### Step 6: Package Skill
```bash
python scripts/package_skill.py .claude/skills/odoo-orm-expert
```

---

## Automation: Bulk Skill Generation

Create a script to automate the process:

```python
# scripts/extract_odoo_docs.py
"""
Automate extraction of Odoo documentation into skill structure.

Usage:
    python scripts/extract_odoo_docs.py \\
        --section orm \\
        --output .claude/skills/odoo-orm-expert
"""

import requests
from bs4 import BeautifulSoup

def extract_code_examples(html):
    """Extract code blocks from documentation."""
    soup = BeautifulSoup(html, 'html.parser')
    examples = []
    for code in soup.find_all('pre'):
        examples.append(code.text)
    return examples

def generate_references(examples):
    """Convert code examples to reference documentation."""
    # Implementation...
    pass

def generate_skill_structure(section_name, references, scripts, assets):
    """Create complete skill directory."""
    # Implementation...
    pass
```

---

## Success Metrics

After completing knowledge extraction, you should have:

✅ **10+ specialized Odoo skills** covering major documentation areas
✅ **50+ reusable scripts** for code generation and validation
✅ **100+ reference pages** with API documentation and patterns
✅ **200+ code templates** for common use cases
✅ **Zero context switching** - All knowledge embedded in skills
✅ **Faster development** - 10x speed improvement on common tasks

---

## Next Steps

1. **Prioritize skills** - Start with what you use most
2. **Extract incrementally** - One skill per day
3. **Test immediately** - Use skill on real projects
4. **Iterate based on usage** - Improve after each use
5. **Share with team** - Package and distribute skills

---

## Resources

- [Skill Creator Guide](.claude/skills/skill-creator/SKILL.md)
- [Odoo 19.0 Developer Reference](https://www.odoo.com/documentation/19.0/developer/reference.html)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)

---

**Ready to build your Odoo knowledge library? Start with one skill today!**
