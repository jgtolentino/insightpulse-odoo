# -*- coding: utf-8 -*-
from odoo import api, fields, models

class IpCashAdvance(models.Model):
    _name = "ip.cash.advance"
    _description = "Cash Advance"

    name = fields.Char(required=True, default=lambda self: self.env["ir.sequence"].next_by_code("ip.cash.advance") or "Cash Advance")
    employee_id = fields.Many2one("hr.employee", required=True)
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id.id)
    purpose = fields.Char()
    state = fields.Selection([("draft","Draft"),("approved","Approved"),("released","Released"),("liquidated","Liquidated")], default="draft", tracking=True)
    related_expense_ids = fields.One2many("hr.expense", "cash_advance_id", string="Linked Expenses")

# link field on expense (created lazily to avoid inherit duplication)
from odoo import models as _models, fields as _fields
class HrExpenseCA(_models.Model):
    _inherit = "hr.expense"
    cash_advance_id = _fields.Many2one("ip.cash.advance", string="Cash Advance")
