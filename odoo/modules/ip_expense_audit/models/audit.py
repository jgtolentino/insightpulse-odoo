from odoo import models, fields

class ExpenseAudit(models.Model):
    _name = 'ip.expense.audit'
    _description = 'Expense Audit Trail'

    expense_id = fields.Many2one('hr.expense', required=True)
    audit_date = fields.Datetime(default=fields.Datetime.now)
    auditor_id = fields.Many2one('res.users')
    notes = fields.Text()
    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('review', 'Needs Review')
    ])
