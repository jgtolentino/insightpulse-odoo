from odoo import api, fields, models


class IpaiVendorScore(models.Model):
    _name = "ipai.vendor.score"
    _description = "IPAI Vendor Scorecard"

    vendor_id = fields.Many2one(
        "res.partner",
        required=True,
        domain=[("supplier_rank", ">", 0)],
        ondelete="cascade",
    )
    score_quality = fields.Integer(string="Quality", default=0)
    score_on_time = fields.Integer(string="On-time", default=0)
    score_cost = fields.Integer(string="Cost", default=0)
    score_avg = fields.Float(compute="_compute_avg", store=True)

    @api.depends("score_quality", "score_on_time", "score_cost")
    def _compute_avg(self):
        for rec in self:
            rec.score_avg = (
                (rec.score_quality + rec.score_on_time + rec.score_cost) / 3.0
                if any([rec.score_quality, rec.score_on_time, rec.score_cost])
                else 0.0
            )
