from odoo import api, fields, models


class IpaiSubscriptionLine(models.Model):
    _name = "ipai.subscription.line"
    _description = "Subscription Line"

    subscription_id = fields.Many2one(
        "ipai.subscription", required=True, ondelete="cascade"
    )
    product_id = fields.Many2one("product.product", required=True)
    qty = fields.Float(default=1.0)
    price_unit = fields.Monetary()
    currency_id = fields.Many2one(
        "res.currency", related="subscription_id.currency_id", store=True
    )
    billing_period = fields.Selection(
        [("month", "Month"), ("year", "Year")], default="month"
    )
    monthly_price = fields.Monetary(
        compute="_compute_monthly", currency_field="currency_id", store=True
    )

    @api.depends("price_unit", "billing_period")
    def _compute_monthly(self):
        for rec in self:
            if rec.billing_period == "month":
                rec.monthly_price = rec.price_unit or 0.0
            else:
                rec.monthly_price = (rec.price_unit or 0.0) / 12.0
