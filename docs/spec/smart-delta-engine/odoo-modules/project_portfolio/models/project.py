# -*- coding: utf-8 -*-
"""
Project Extension for Portfolio Management

Extends project.project to link to portfolios.
"""

from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    # Portfolio Link
    portfolio_id = fields.Many2one(
        'project.portfolio',
        'Portfolio',
        tracking=True,
        help="Parent portfolio for this project"
    )

    # Budget (for portfolio aggregation)
    budget_total = fields.Monetary(
        'Project Budget',
        currency_field='currency_id',
        tracking=True
    )
    budget_spent = fields.Monetary(
        'Budget Spent',
        compute='_compute_budget_spent',
        store=True,
        currency_id='currency_id'
    )
    budget_remaining = fields.Monetary(
        'Budget Remaining',
        compute='_compute_budget_remaining',
        currency_id='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    # External Integration
    notion_project_id = fields.Char('Notion Project ID', copy=False)
    clarity_project_id = fields.Char('Clarity Project ID', copy=False)

    @api.depends('analytic_account_id.line_ids.amount')
    def _compute_budget_spent(self):
        """Calculate actual spend from analytic lines."""
        for project in self:
            if project.analytic_account_id:
                spent = sum(
                    abs(line.amount)
                    for line in project.analytic_account_id.line_ids
                    if line.amount < 0
                )
                project.budget_spent = spent
            else:
                project.budget_spent = 0

    @api.depends('budget_total', 'budget_spent')
    def _compute_budget_remaining(self):
        for project in self:
            project.budget_remaining = project.budget_total - project.budget_spent

    @api.onchange('portfolio_id')
    def _onchange_portfolio_id(self):
        """Inherit analytic account from portfolio if not set."""
        if self.portfolio_id and not self.analytic_account_id:
            self.analytic_account_id = self.portfolio_id.analytic_account_id
