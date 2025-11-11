# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)


class GitHubConfig(models.Model):
    """GitHub API Configuration"""

    _name = "github.config"
    _description = "GitHub API Configuration"
    _rec_name = "name"

    name = fields.Char(
        string="Configuration Name",
        required=True,
        default="GitHub API Config",
    )

    github_token = fields.Char(
        string="GitHub Personal Access Token",
        required=True,
        help="Generate at: https://github.com/settings/tokens\n"
        "Required scopes: repo, project, read:org, read:user",
    )

    github_org = fields.Char(
        string="GitHub Organization",
        required=True,
        default="jgtolentino",
        help="Your GitHub organization or username",
    )

    github_repo = fields.Char(
        string="Default Repository",
        required=True,
        default="insightpulse-odoo",
        help="Default repository for syncing",
    )

    webhook_secret = fields.Char(
        string="Webhook Secret",
        help="Secret for validating GitHub webhook signatures",
    )

    api_base_url = fields.Char(
        string="GitHub API Base URL",
        default="https://api.github.com",
        required=True,
    )

    sync_pull_requests = fields.Boolean(
        string="Sync Pull Requests",
        default=True,
        help="Automatically sync PRs to Odoo tasks",
    )

    sync_issues = fields.Boolean(
        string="Sync Issues",
        default=True,
        help="Automatically sync issues to Odoo tasks",
    )

    sync_projects = fields.Boolean(
        string="Sync GitHub Projects",
        default=True,
        help="Sync GitHub Projects (Org-level) with budget tracking",
    )

    auto_create_tasks = fields.Boolean(
        string="Auto-Create Tasks",
        default=True,
        help="Automatically create Odoo tasks for PRs/Issues",
    )

    prompt_timesheet_on_merge = fields.Boolean(
        string="Prompt Timesheet on PR Merge",
        default=True,
        help="Post GitHub comment prompting timesheet entry when PR is merged",
    )

    sync_costs_to_github = fields.Boolean(
        string="Sync Costs to GitHub",
        default=True,
        help="Update GitHub Projects with actual spend from Odoo timesheets",
    )

    default_project_id = fields.Many2one(
        "project.project",
        string="Default Odoo Project",
        help="Default project for GitHub tasks (if not mapped)",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    last_sync_date = fields.Datetime(
        string="Last Sync",
        readonly=True,
    )

    sync_status = fields.Selection(
        [
            ("idle", "Idle"),
            ("syncing", "Syncing"),
            ("error", "Error"),
        ],
        string="Sync Status",
        default="idle",
        readonly=True,
    )

    sync_error_message = fields.Text(
        string="Last Error",
        readonly=True,
    )

    @api.constrains("github_token")
    def _check_github_token(self):
        """Validate GitHub token format"""
        for record in self:
            if record.github_token:
                if not (
                    record.github_token.startswith("ghp_")
                    or record.github_token.startswith("github_pat_")
                ):
                    raise ValidationError(
                        _(
                            "GitHub token should start with 'ghp_' (classic) "
                            "or 'github_pat_' (fine-grained)"
                        )
                    )

    def test_connection(self):
        """Test GitHub API connection"""
        self.ensure_one()
        try:
            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }

            # Test user endpoint
            response = requests.get(
                f"{self.api_base_url}/user",
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()

            user_data = response.json()

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Connection Successful"),
                    "message": _(
                        "Connected to GitHub as: %s\n"
                        "Rate limit: %s/%s"
                    )
                    % (
                        user_data.get("login", "Unknown"),
                        response.headers.get("X-RateLimit-Remaining", "?"),
                        response.headers.get("X-RateLimit-Limit", "?"),
                    ),
                    "type": "success",
                    "sticky": False,
                },
            }

        except requests.exceptions.RequestException as e:
            _logger.error("GitHub API connection test failed: %s", str(e))
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Connection Failed"),
                    "message": _("Error: %s") % str(e),
                    "type": "danger",
                    "sticky": True,
                },
            }

    def get_github_headers(self):
        """Get GitHub API headers with authentication"""
        self.ensure_one()
        return {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def action_sync_now(self):
        """Manual sync trigger"""
        self.ensure_one()

        if self.sync_status == "syncing":
            raise ValidationError(_("Sync already in progress"))

        self.write({
            "sync_status": "syncing",
            "sync_error_message": False,
        })

        try:
            # Sync GitHub Projects
            if self.sync_projects:
                self.env["github.project"]._sync_from_github(self)

            # Sync PRs
            if self.sync_pull_requests:
                self.env["github.pull.request"]._sync_from_github(self)

            # Sync Issues
            if self.sync_issues:
                self.env["github.issue"]._sync_from_github(self)

            self.write({
                "sync_status": "idle",
                "last_sync_date": fields.Datetime.now(),
            })

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Sync Complete"),
                    "message": _("GitHub data synced successfully"),
                    "type": "success",
                },
            }

        except Exception as e:
            _logger.error("GitHub sync failed: %s", str(e))
            self.write({
                "sync_status": "error",
                "sync_error_message": str(e),
            })
            raise ValidationError(_("Sync failed: %s") % str(e))
