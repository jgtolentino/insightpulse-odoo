# Odoo Model Context

## Model Types

### models.Model (Persistent)
Stored in database permanently. Use for master data.

```python
class AccountTrialBalance(models.Model):
    _name = 'account.trial.balance'
    _description = 'Trial Balance Report'
```

### models.TransientModel (Temporary)
Stored temporarily (auto-deleted). Use for wizards, reports.

```python
class TrialBalanceWizard(models.TransientModel):
    _name = 'account.trial.balance.wizard'
    _description = 'Trial Balance Wizard'
```

### models.AbstractModel (No Storage)
Not stored. Use as mixin for inheritance.

```python
class ReportAbstract(models.AbstractModel):
    _name = 'report.module.template'
```

## Common Field Types

```python
# Basic Types
name = fields.Char(string='Name', required=True)
description = fields.Text(string='Description')
active = fields.Boolean(string='Active', default=True)
sequence = fields.Integer(string='Sequence', default=10)
amount = fields.Float(string='Amount', digits=(16, 2))
amount_total = fields.Monetary(string='Total', currency_field='currency_id')

# Date/Time
date = fields.Date(string='Date', default=fields.Date.today)
datetime = fields.Datetime(string='DateTime', default=fields.Datetime.now)

# Selection
state = fields.Selection([
    ('draft', 'Draft'),
    ('posted', 'Posted'),
    ('cancel', 'Cancelled')
], string='Status', default='draft')

# Relational
partner_id = fields.Many2one('res.partner', string='Partner')
line_ids = fields.One2many('model.line', 'parent_id', string='Lines')
tag_ids = fields.Many2many('model.tag', string='Tags')

# Computed
total = fields.Float(compute='_compute_total', store=True)

# Related
partner_country_id = fields.Many2one(
    related='partner_id.country_id',
    string='Partner Country',
    store=True
)
```

## Odoo 19 Specific Features

- Python 3.10+ with type hints
- Enhanced OWL components
- Improved performance
- Better multi-company support
