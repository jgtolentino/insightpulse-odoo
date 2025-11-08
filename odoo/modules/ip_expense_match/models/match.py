from odoo import models, fields, api

class ExpenseMatch(models.Model):
    _name = 'ip.expense.match'
    _description = 'Expense Matching'

    expense_id = fields.Many2one('hr.expense', required=True)
    invoice_id = fields.Many2one('account.move')
    match_score = fields.Float(help='Matching confidence score')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('matched', 'Matched'),
        ('rejected', 'Rejected')
    ], default='pending')
