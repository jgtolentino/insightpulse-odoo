from odoo import api, fields, models
from datetime import date

class IpaiPurchaseRequisition(models.Model):
    _name = "ipai.purchase.requisition"
    _description = "IPAI Purchase Requisition"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(default=lambda s: s.env["ir.sequence"].next_by_code("ipai.pr") or "/", tracking=True)
    requester_id = fields.Many2one("res.users", required=True, default=lambda s: s.env.user, tracking=True)
    date_requested = fields.Date(default=date.today, tracking=True)
    state = fields.Selection([
        ("draft","Draft"),("submitted","Submitted"),("approved","Approved"),
        ("rfq","RFQ"),("po_created","PO Created"),("done","Done"),("cancel","Cancelled")
    ], default="draft", tracking=True)
    line_ids = fields.One2many("ipai.purchase.req.line","requisition_id","Lines")
    notes = fields.Text()

    amount_total = fields.Monetary(currency_field="currency_id", compute="_compute_amount_total", store=True)
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id.id)

    @api.depends("line_ids.subtotal")
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped("subtotal"))
