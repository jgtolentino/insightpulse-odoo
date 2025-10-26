from odoo import fields, models


class IpaiExpensePolicy(models.Model):
    _name = "ipai.expense.policy"
    _description = "IPAI Expense Policy"

    name = fields.Char(required=True)
    daily_limit = fields.Monetary()
    currency_id = fields.Many2one(
        "res.currency", default=lambda s: s.env.company.currency_id.id
    )
    require_receipt = fields.Boolean(default=True)
    notes = fields.Text()
