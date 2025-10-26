from odoo import fields, models

class IpaiRfqRound(models.Model):
    _name = "ipai.rfq.round"
    _description = "IPAI RFQ Round"
    _order = "round_no"

    requisition_id = fields.Many2one("ipai.purchase.requisition", required=True, ondelete="cascade")
    round_no = fields.Integer(default=1)
    deadline = fields.Datetime()
    vendor_ids = fields.Many2many("res.partner", string="Vendors", domain=[("supplier_rank", ">", 0)])
    state = fields.Selection([("draft","Draft"),("running","Running"),("closed","Closed")], default="draft")
