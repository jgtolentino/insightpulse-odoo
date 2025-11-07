from odoo import models, fields

class ExpensePolicy(models.Model):
    _name = 'ip.expense.policy'
    _description = 'Expense Policy'

    name = fields.Char(required=True)
    amount_limit = fields.Float()
    per_diem = fields.Float(help='Daily allowance')
