# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class RatePolicyLine(models.Model):
    _name = "rate.policy.line"
    _description = "Rate Policy Line"
    _order = "policy_id, role_id"

    policy_id = fields.Many2one(
        comodel_name="rate.policy",
        string="Policy",
        required=True,
        ondelete="cascade",
    )
    role_id = fields.Many2one(
        comodel_name="hr.job",
        string="Job Position",
        required=True,
    )
    p60_base_rate = fields.Float(
        string="P60 Base Rate",
        required=True,
        help="Base rate from P60 scale",
    )
    calculated_rate = fields.Float(
        string="Calculated Rate",
        compute="_compute_calculated_rate",
        store=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    notes = fields.Text(
        string="Notes",
    )

    @api.depends("p60_base_rate", "policy_id.markup_percentage")
    def _compute_calculated_rate(self):
        """Compute rate with markup."""
        for line in self:
            if line.policy_id and line.p60_base_rate:
                line.calculated_rate = line.policy_id.calculate_rate(line.p60_base_rate)
            else:
                line.calculated_rate = 0.0
