from odoo import api, fields, models


class IpaiSubscription(models.Model):
    _name = "ipai.subscription"
    _description = "Subscription"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    
    name = fields.Char(required=True, index=True)
    partner_id = fields.Many2one("res.partner", required=True)
    contract_id = fields.Many2one("contract.contract", string="Contract")
    start_date = fields.Date(required=True)
    next_invoice_date = fields.Date()
    state = fields.Selection([
        ("active", "Active"), ("suspended", "Suspended"),
        ("cancelled", "Cancelled")
    ], default="active", tracking=True)
    line_ids = fields.One2many(
        "ipai.subscription.line", "subscription_id", "Lines"
    )
    mrr = fields.Monetary(
        compute="_compute_mrr", currency_field="currency_id", store=True
    )
    currency_id = fields.Many2one(
        "res.currency", default=lambda s: s.env.company.currency_id.id
    )

    @api.depends("line_ids.monthly_price")
    def _compute_mrr(self):
        for rec in self:
            rec.mrr = sum(rec.line_ids.mapped("monthly_price"))

    def _cron_generate_invoices(self):
        today = fields.Date.today()
        for sub in self.search([('state', '=', 'active')]):
            # compute usage, create account.move draft, post if policy says so
            pass
