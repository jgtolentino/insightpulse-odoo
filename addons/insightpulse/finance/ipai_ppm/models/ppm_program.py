# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class PPMProgram(models.Model):
    _name = 'ppm.program'
    _description = 'PPM Program'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Program Name',
        required=True,
        tracking=True,
    )
    active = fields.Boolean(
        default=True,
        tracking=True,
    )
    code = fields.Char(
        string='Program Code',
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    program_manager_id = fields.Many2one(
        comodel_name='res.users',
        string='Program Manager',
        tracking=True,
    )
    start_date = fields.Date(
        string='Start Date',
        required=True,
        tracking=True,
    )
    end_date = fields.Date(
        string='End Date',
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('planning', 'Planning'),
            ('active', 'Active'),
            ('on_hold', 'On Hold'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    project_ids = fields.One2many(
        comodel_name='project.project',
        inverse_name='program_id',
        string='Projects',
    )
    project_count = fields.Integer(
        string='Project Count',
        compute='_compute_project_count',
    )
    roadmap_ids = fields.One2many(
        comodel_name='ppm.roadmap',
        inverse_name='program_id',
        string='Roadmaps',
    )
    risk_ids = fields.One2many(
        comodel_name='ppm.risk',
        inverse_name='program_id',
        string='Risks',
    )
    budget_ids = fields.One2many(
        comodel_name='ppm.budget',
        inverse_name='program_id',
        string='Budgets',
    )
    total_budget = fields.Monetary(
        string='Total Budget',
        compute='_compute_total_budget',
        store=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    description = fields.Html(
        string='Description',
    )
    notes = fields.Text(
        string='Notes',
    )

    @api.depends('project_ids')
    def _compute_project_count(self):
        for program in self:
            program.project_count = len(program.project_ids)

    @api.depends('budget_ids.amount')
    def _compute_total_budget(self):
        for program in self:
            program.total_budget = sum(program.budget_ids.mapped('amount'))

    def action_start_planning(self):
        """Move program to planning state."""
        self.write({'state': 'planning'})

    def action_activate(self):
        """Activate program."""
        self.write({'state': 'active'})

    def action_put_on_hold(self):
        """Put program on hold."""
        self.write({'state': 'on_hold'})

    def action_complete(self):
        """Complete program."""
        self.write({'state': 'completed'})

    def action_cancel(self):
        """Cancel program."""
        self.write({'state': 'cancelled'})
