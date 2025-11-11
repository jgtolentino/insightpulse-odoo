# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models, fields


class GitHubSyncLog(models.Model):
    """Log of GitHub sync operations"""

    _name = "github.sync.log"
    _description = "GitHub Sync Log"
    _order = "create_date desc"
    _rec_name = "sync_type"

    sync_type = fields.Selection([
        ("pr", "Pull Request"),
        ("issue", "Issue"),
        ("project", "Project"),
        ("manual", "Manual Sync"),
    ], string="Sync Type", required=True)

    status = fields.Selection([
        ("success", "Success"),
        ("partial", "Partial Success"),
        ("failed", "Failed"),
    ], string="Status", required=True)

    records_synced = fields.Integer(string="Records Synced")
    error_message = fields.Text(string="Error Message")
    config_id = fields.Many2one("github.config", string="GitHub Config")
    sync_duration = fields.Float(string="Duration (seconds)")
