# -*- coding: utf-8 -*-
from odoo import models, fields

class ProjectTask(models.Model):
    """Extend project.task to link to Finance PPM logframe and BIR schedule"""
    _inherit = "project.task"

    finance_logframe_id = fields.Many2one(
        "ipai.finance.logframe",
        string="Logframe Entry",
        help="Link to Finance Logical Framework objective"
    )

    bir_schedule_id = fields.Many2one(
        "ipai.finance.bir_schedule",
        string="BIR Form",
        help="Link to BIR Filing Schedule"
    )

    # Computed fields for dashboard visibility
    is_finance_ppm = fields.Boolean(
        compute="_compute_is_finance_ppm",
        store=True,
        string="Is Finance PPM Task"
    )

    def _compute_is_finance_ppm(self):
        for task in self:
            task.is_finance_ppm = bool(task.finance_logframe_id or task.bir_schedule_id)
