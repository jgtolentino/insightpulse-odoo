# -*- coding: utf-8 -*-
"""
Project Portfolio Model

Smart Delta Classification: Gap Level 2 (Minimal Custom)
Clarity PPM Parity: Portfolio creation & governance

This module provides portfolio management capabilities matching
Clarity PPM's portfolio management features.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import json


class ProjectPortfolio(models.Model):
    _name = 'project.portfolio'
    _description = 'Project Portfolio'
    _order = 'priority desc, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Core Fields
    name = fields.Char('Portfolio Name', required=True, tracking=True)
    code = fields.Char('Code', copy=False)
    description = fields.Html('Description')
    active = fields.Boolean(default=True)

    # Governance
    sponsor_id = fields.Many2one('res.partner', 'Sponsor', tracking=True)
    manager_id = fields.Many2one('res.users', 'Portfolio Manager',
                                  default=lambda self: self.env.user, tracking=True)
    company_id = fields.Many2one('res.company', 'Company',
                                  default=lambda self: self.env.company, required=True)

    # Status & Priority
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('closed', 'Closed'),
    ], default='draft', tracking=True, string='Status')

    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical'),
    ], default='1', string='Priority')

    # Scoring (for prioritization)
    strategic_alignment = fields.Integer('Strategic Alignment', default=0,
                                          help='Score 0-100')
    business_value = fields.Integer('Business Value', default=0)
    risk_level = fields.Integer('Risk Level', default=0)
    resource_availability = fields.Integer('Resource Availability', default=0)
    total_score = fields.Float('Total Score', compute='_compute_total_score', store=True)

    # Financial
    budget_total = fields.Monetary('Total Budget', currency_field='currency_id')
    budget_allocated = fields.Monetary('Allocated Budget',
                                        compute='_compute_budget_allocated', store=True)
    budget_remaining = fields.Monetary('Remaining Budget',
                                        compute='_compute_budget_remaining', store=True)
    currency_id = fields.Many2one('res.currency',
                                   default=lambda self: self.env.company.currency_id)

    # Dates
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')

    # Relations
    project_ids = fields.One2many('project.project', 'portfolio_id', 'Projects')
    project_count = fields.Integer('Project Count', compute='_compute_project_count')
    analytic_account_id = fields.Many2one('account.analytic.account',
                                           'Analytic Account',
                                           help='Cost center for portfolio')

    # External Integration
    notion_db_id = fields.Char('Notion Database ID', copy=False)
    notion_page_id = fields.Char('Notion Page ID', copy=False)
    external_ref = fields.Char('External Reference', copy=False)

    # Computed Fields
    @api.depends('strategic_alignment', 'business_value', 'risk_level', 'resource_availability')
    def _compute_total_score(self):
        """Calculate weighted score for portfolio prioritization."""
        weights = {
            'strategic_alignment': 0.35,
            'business_value': 0.30,
            'risk_level': 0.15,  # Inverted: lower risk = higher score
            'resource_availability': 0.20,
        }
        for portfolio in self:
            score = (
                portfolio.strategic_alignment * weights['strategic_alignment'] +
                portfolio.business_value * weights['business_value'] +
                (100 - portfolio.risk_level) * weights['risk_level'] +  # Invert risk
                portfolio.resource_availability * weights['resource_availability']
            )
            portfolio.total_score = score

    @api.depends('project_ids')
    def _compute_project_count(self):
        for portfolio in self:
            portfolio.project_count = len(portfolio.project_ids)

    @api.depends('project_ids.budget_total')
    def _compute_budget_allocated(self):
        for portfolio in self:
            portfolio.budget_allocated = sum(portfolio.project_ids.mapped('budget_total'))

    @api.depends('budget_total', 'budget_allocated')
    def _compute_budget_remaining(self):
        for portfolio in self:
            portfolio.budget_remaining = portfolio.budget_total - portfolio.budget_allocated

    # State Transitions
    def action_submit(self):
        """Submit portfolio for approval."""
        self.write({'state': 'submitted'})
        self._notify_n8n_webhook('portfolio_submitted')

    def action_approve(self):
        """Approve portfolio and create analytic account."""
        for portfolio in self:
            if not portfolio.analytic_account_id:
                analytic = self.env['account.analytic.account'].create({
                    'name': f"Portfolio - {portfolio.name}",
                    'company_id': portfolio.company_id.id,
                })
                portfolio.analytic_account_id = analytic.id
        self.write({'state': 'approved'})
        self._notify_n8n_webhook('portfolio_approved')

    def action_activate(self):
        """Activate portfolio for project execution."""
        self.write({'state': 'active'})

    def action_hold(self):
        """Put portfolio on hold."""
        self.write({'state': 'on_hold'})
        self._notify_n8n_webhook('portfolio_on_hold')

    def action_close(self):
        """Close portfolio."""
        self.write({'state': 'closed'})

    # Notion Sync
    def _notify_n8n_webhook(self, event_type, data=None):
        """Send webhook notification to n8n for Notion sync."""
        webhook_url = self.env['ir.config_parameter'].sudo().get_param(
            'project_portfolio.n8n_webhook_url', False
        )
        if not webhook_url:
            return

        payload = {
            'event': event_type,
            'portfolio_id': self.id,
            'portfolio_name': self.name,
            'state': self.state,
            'notion_page_id': self.notion_page_id,
            'data': data or {},
        }

        try:
            requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
        except requests.RequestException:
            # Log but don't fail - webhook is async notification
            pass

    def sync_from_notion(self, notion_data):
        """Update portfolio from Notion database row."""
        self.ensure_one()
        vals = {
            'name': notion_data.get('name', self.name),
            'budget_total': notion_data.get('budget', self.budget_total),
            'priority': str(notion_data.get('priority', '1')),
            'description': notion_data.get('description', ''),
        }
        if notion_data.get('status'):
            state_map = {
                'Draft': 'draft',
                'Submitted': 'submitted',
                'Approved': 'approved',
                'Active': 'active',
                'On Hold': 'on_hold',
                'Closed': 'closed',
            }
            vals['state'] = state_map.get(notion_data['status'], self.state)

        self.write(vals)

    # Constraints
    @api.constrains('budget_allocated', 'budget_total')
    def _check_budget_allocation(self):
        for portfolio in self:
            if portfolio.budget_allocated > portfolio.budget_total:
                raise ValidationError(
                    "Allocated budget cannot exceed total portfolio budget."
                )

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for portfolio in self:
            if portfolio.date_start and portfolio.date_end:
                if portfolio.date_start > portfolio.date_end:
                    raise ValidationError("End date must be after start date.")

    # Name Generation
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('project.portfolio') or 'NEW'
        return super().create(vals)
