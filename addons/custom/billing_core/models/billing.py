from odoo import models, fields
class BillingProfile(models.Model):
    _name = "billing.profile"
    _description = "Billing Profile"
    name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", required=True, ondelete="cascade")
    journal_id = fields.Many2one("account.journal", domain=[("type","=","sale")], required=True)
    payment_term_id = fields.Many2one("account.payment.term")
    auto_post = fields.Boolean(default=True)
    active = fields.Boolean(default=True)
