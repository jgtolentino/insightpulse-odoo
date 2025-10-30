# -*- coding: utf-8 -*-
"""GitHub webhook event log model."""

from odoo import models, fields


class GitHubWebhookEvent(models.Model):
    """Log GitHub webhook events for debugging."""

    _name = 'github.webhook.event'
    _description = 'GitHub Webhook Event'
    _order = 'create_date desc'

    name = fields.Char('Name', compute='_compute_name', store=True)
    event_type = fields.Char('Event Type', required=True)
    delivery_id = fields.Char('Delivery ID')

    payload = fields.Text('Payload')
    status = fields.Selection([
        ('received', 'Received'),
        ('processed', 'Processed'),
        ('ignored', 'Ignored'),
        ('error', 'Error'),
    ], string='Status', default='received')

    error_message = fields.Text('Error Message')

    def _compute_name(self):
        """Compute display name."""
        for record in self:
            record.name = f"{record.event_type} - {record.create_date}"


class GitHubPushEvent(models.Model):
    """Track push events to main branches."""

    _name = 'github.push.event'
    _description = 'GitHub Push Event'
    _order = 'create_date desc'

    name = fields.Char('Name', compute='_compute_name', store=True)
    repository_name = fields.Char('Repository', required=True)
    ref = fields.Char('Ref (branch)')

    commits_count = fields.Integer('Commits Count')
    pusher = fields.Char('Pusher')

    head_commit_sha = fields.Char('Head Commit SHA')
    head_commit_message = fields.Text('Head Commit Message')

    def _compute_name(self):
        """Compute display name."""
        for record in self:
            branch = record.ref.split('/')[-1] if record.ref else 'unknown'
            record.name = f"{record.repository_name}:{branch} ({record.commits_count} commits)"
