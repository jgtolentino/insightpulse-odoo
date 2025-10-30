# -*- coding: utf-8 -*-
"""Extend project.task to integrate with GitHub."""

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    """Extend project tasks with GitHub integration."""

    _inherit = 'project.task'

    github_issue_number = fields.Integer('GitHub Issue #')
    github_issue_url = fields.Char('GitHub Issue URL')
    github_repository = fields.Char('GitHub Repository')
    github_synced = fields.Boolean('Synced to GitHub', default=False)

    def action_sync_to_github(self):
        """Create GitHub issue from Odoo task."""
        self.ensure_one()

        if self.github_synced:
            _logger.warning(f"Task {self.id} already synced to GitHub")
            return

        if not self.github_repository:
            _logger.error(f"Task {self.id} has no repository configured")
            return

        github_api = self.env['github.api']

        try:
            issue = github_api.create_issue(
                repo=self.github_repository,
                title=self.name,
                body=self.description or '',
                labels=['odoo-sync']
            )

            self.write({
                'github_issue_number': issue['number'],
                'github_issue_url': issue['html_url'],
                'github_synced': True,
            })

            _logger.info(f"Synced task {self.id} to GitHub issue #{issue['number']}")

        except Exception as e:
            _logger.error(f"Failed to sync task {self.id} to GitHub: {str(e)}")
            raise

    def action_view_github_issue(self):
        """Open GitHub issue in browser."""
        self.ensure_one()
        if self.github_issue_url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.github_issue_url,
                'target': 'new',
            }
