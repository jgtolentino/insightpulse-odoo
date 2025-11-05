# -*- coding: utf-8 -*-
from odoo import fields, models

class IpLiquidation(models.Model):
    _name = "ip.liquidation"
    _description = "Liquidation"

    name = fields.Char(required=True)
    cash_advance_id = fields.Many2one("ip.cash.advance", required=True)
    total_spent = fields.Monetary()
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id.id)
    submitted_on = fields.Date()
    state = fields.Selection([("draft","Draft"),("submitted","Submitted"),("approved","Approved"),("reconciled","Reconciled")], default="draft")
