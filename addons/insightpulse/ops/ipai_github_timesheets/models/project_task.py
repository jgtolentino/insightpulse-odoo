# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models, fields


class ProjectTask(models.Model):
    """Extend project.task with GitHub fields"""

    _inherit = "project.task"

    github_pr_id = fields.Many2one(
        "github.pull.request",
        string="GitHub PR",
        ondelete="set null",
        help="Linked GitHub Pull Request",
    )

    github_issue_id = fields.Many2one(
        "github.issue",
        string="GitHub Issue",
        ondelete="set null",
        help="Linked GitHub Issue",
    )

    github_project_id = fields.Many2one(
        "github.project",
        string="GitHub Project",
        help="GitHub Project this task belongs to",
    )

    github_url = fields.Char(
        string="GitHub URL",
        compute="_compute_github_url",
        store=True,
    )

    is_github_synced = fields.Boolean(
        string="GitHub Synced",
        compute="_compute_is_github_synced",
        store=True,
    )

    def _compute_github_url(self):
        """Get GitHub URL from PR or Issue"""
        for record in self:
            if record.github_pr_id:
                record.github_url = record.github_pr_id.github_url
            elif record.github_issue_id:
                record.github_url = record.github_issue_id.github_url
            else:
                record.github_url = False

    def _compute_is_github_synced(self):
        """Check if task is synced with GitHub"""
        for record in self:
            record.is_github_synced = bool(
                record.github_pr_id or record.github_issue_id
            )
