# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class RateCalculationLog(models.Model):
    _name = "rate.calculation.log"
    _description = "Rate Calculation Log"
    _order = "create_date desc"

    policy_id = fields.Many2one(
        comodel_name="rate.policy",
        string="Policy",
        required=True,
        ondelete="cascade",
    )
    policy_line_id = fields.Many2one(
        comodel_name="rate.policy.line",
        string="Policy Line",
        ondelete="cascade",
    )
    role_id = fields.Many2one(
        comodel_name="hr.job",
        string="Job Position",
        required=True,
    )
    p60_rate = fields.Float(
        string="P60 Base Rate",
        required=True,
    )
    markup_percentage = fields.Float(
        string="Markup Applied %",
        required=True,
    )
    calculated_rate = fields.Float(
        string="Calculated Rate",
        required=True,
    )
    calculation_date = fields.Datetime(
        string="Calculation Date",
        required=True,
        default=fields.Datetime.now,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Calculated By",
        default=lambda self: self.env.user,
    )
    notes = fields.Text(
        string="Notes",
    )
