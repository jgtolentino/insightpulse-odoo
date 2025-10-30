# -*- coding: utf-8 -*-
"""GitHub issue model."""

from odoo import models, fields, api


class GitHubIssue(models.Model):
    """Track GitHub issues in Odoo."""

    _name = 'github.issue'
    _description = 'GitHub Issue'
    _order = 'number desc'

    name = fields.Char('Name', compute='_compute_name', store=True)
    number = fields.Integer('Issue Number', required=True)
    title = fields.Char('Title', required=True)
    body = fields.Text('Description')

    repository_name = fields.Char('Repository', required=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
    ], string='State', default='open')

    author = fields.Char('Author')
    url = fields.Char('URL')

    created_at = fields.Datetime('Created At')
    updated_at = fields.Datetime('Updated At')
    closed_at = fields.Datetime('Closed At')

    odoo_task_id = fields.Many2one('project.task', string='Odoo Task', ondelete='set null')

    _sql_constraints = [
        ('unique_issue', 'unique(number, repository_name)',
         'Issue number must be unique per repository!')
    ]

    @api.depends('number', 'repository_name')
    def _compute_name(self):
        """Compute display name."""
        for record in self:
            record.name = f"{record.repository_name}#{record.number}"

    def action_view_task(self):
        """Open linked Odoo task."""
        self.ensure_one()
        if self.odoo_task_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.task',
                'res_id': self.odoo_task_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
