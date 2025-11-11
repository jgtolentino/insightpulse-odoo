# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class GitHubIssue(models.Model):
    """GitHub Issue (simplified - similar to PR model)"""

    _name = "github.issue"
    _description = "GitHub Issue"
    _rec_name = "title"
    _order = "github_updated_at desc"

    github_issue_number = fields.Integer(string="Issue Number", required=True, index=True)
    github_issue_id = fields.Integer(string="GitHub Issue ID", required=True, index=True)
    title = fields.Char(string="Title", required=True)
    description = fields.Html(string="Description")
    github_url = fields.Char(string="GitHub URL")
    github_state = fields.Selection([("open", "Open"), ("closed", "Closed")], default="open")
    github_author = fields.Char(string="Author")
    github_created_at = fields.Datetime(string="Created at")
    github_updated_at = fields.Datetime(string="Updated at")
    github_closed_at = fields.Datetime(string="Closed at")

    task_id = fields.Many2one("project.task", string="Linked Task", ondelete="set null")
    github_project_id = fields.Many2one("github.project", string="GitHub Project")
    employee_id = fields.Many2one("hr.employee", string="Assigned Employee")
    config_id = fields.Many2one("github.config", string="GitHub Config", required=True,
                                  default=lambda self: self.env["github.config"].search([], limit=1))
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def _sync_from_github(self, config):
        """Sync issues from GitHub (implementation similar to PRs)"""
        _logger.info("GitHub issues sync - implement as needed")
        pass
