from odoo import api, fields, models

class IpaiPurchaseReqLine(models.Model):
    _name = "ipai.purchase.req.line"
    _description = "IPAI Purchase Requisition Line"
    _order = "id"

    requisition_id = fields.Many2one("ipai.purchase.requisition", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Product")
    name = fields.Char(string="Description")
    qty = fields.Float(default=1.0)
    uom_id = fields.Many2one("uom.uom", string="UoM", related="product_id.uom_id", store=True, readonly=False)
    price_unit = fields.Monetary(currency_field="currency_id", default=0.0)
    currency_id = fields.Many2one("res.currency", related="requisition_id.currency_id", store=True)
    subtotal = fields.Monetary(currency_field="currency_id", compute="_compute_subtotal", store=True)
    target_date = fields.Date()

    @api.depends("qty","price_unit")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = (rec.qty or 0.0) * (rec.price_unit or 0.0)
