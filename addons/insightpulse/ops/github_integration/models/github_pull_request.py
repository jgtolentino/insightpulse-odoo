# -*- coding: utf-8 -*-
"""GitHub pull request model."""

from odoo import models, fields, api


class GitHubPullRequest(models.Model):
    """Track GitHub pull requests in Odoo."""

    _name = 'github.pull.request'
    _description = 'GitHub Pull Request'
    _order = 'number desc'

    name = fields.Char('Name', compute='_compute_name', store=True)
    number = fields.Integer('PR Number', required=True)
    title = fields.Char('Title', required=True)
    body = fields.Text('Description')

    repository_name = fields.Char('Repository', required=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
    ], string='State', default='open')

    author = fields.Char('Author')
    url = fields.Char('URL')

    head_ref = fields.Char('Head Branch')
    base_ref = fields.Char('Base Branch')

    merged = fields.Boolean('Merged', default=False)
    approvals = fields.Integer('Approvals', default=0)

    created_at = fields.Datetime('Created At')
    updated_at = fields.Datetime('Updated At')
    closed_at = fields.Datetime('Closed At')

    _sql_constraints = [
        ('unique_pr', 'unique(number, repository_name)',
         'PR number must be unique per repository!')
    ]

    @api.depends('number', 'repository_name')
    def _compute_name(self):
        """Compute display name."""
        for record in self:
            record.name = f"{record.repository_name}#{record.number}"
