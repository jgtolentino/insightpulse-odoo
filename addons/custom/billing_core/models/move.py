from odoo import models, fields
class AccountMove(models.Model):
    _inherit = "account.move"
    billing_kind = fields.Selection([
        ("subscription","Subscription"),("oneoff","One-off"),("usage","Usage-based")
    ], default="oneoff", string="Billing Kind")
