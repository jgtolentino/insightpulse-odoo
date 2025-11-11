# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models, fields, api


class AccountAnalyticLine(models.Model):
    """Extend account.analytic.line (timesheets) with GitHub fields"""

    _inherit = "account.analytic.line"

    github_pr_id = fields.Many2one(
        "github.pull.request",
        string="GitHub PR",
        ondelete="set null",
        help="GitHub PR this timesheet entry is for",
    )

    github_project_id = fields.Many2one(
        "github.project",
        string="GitHub Project",
        help="GitHub Project for CapEx/OpEx classification",
    )

    expense_type = fields.Selection(
        related="github_project_id.expense_type",
        string="Expense Type",
        store=True,
        readonly=True,
        help="CapEx vs OpEx classification from GitHub Project",
    )

    @api.onchange("task_id")
    def _onchange_task_id_github(self):
        """Auto-populate GitHub fields from task"""
        if self.task_id:
            self.github_pr_id = self.task_id.github_pr_id
            self.github_project_id = self.task_id.github_project_id
