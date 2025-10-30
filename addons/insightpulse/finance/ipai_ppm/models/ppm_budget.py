# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class PPMBudget(models.Model):
    _name = 'ppm.budget'
    _description = 'PPM Budget'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Budget Name',
        required=True,
        tracking=True,
    )
    program_id = fields.Many2one(
        comodel_name='ppm.program',
        string='Program',
        required=True,
        ondelete='cascade',
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        ondelete='cascade',
    )
    budget_type = fields.Selection(
        selection=[
            ('capex', 'Capital Expenditure'),
            ('opex', 'Operating Expenditure'),
            ('labor', 'Labor'),
            ('material', 'Material'),
            ('other', 'Other'),
        ],
        string='Type',
        required=True,
        default='opex',
        tracking=True,
    )
    amount = fields.Monetary(
        string='Budget Amount',
        required=True,
        tracking=True,
    )
    spent_amount = fields.Monetary(
        string='Spent Amount',
        tracking=True,
    )
    remaining_amount = fields.Monetary(
        string='Remaining Amount',
        compute='_compute_remaining_amount',
        store=True,
    )
    utilization_percentage = fields.Float(
        string='Utilization %',
        compute='_compute_utilization_percentage',
        store=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    fiscal_year = fields.Char(
        string='Fiscal Year',
        required=True,
    )
    start_date = fields.Date(
        string='Start Date',
        required=True,
    )
    end_date = fields.Date(
        string='End Date',
        required=True,
    )
    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('active', 'Active'),
            ('exceeded', 'Exceeded'),
            ('closed', 'Closed'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    approver_id = fields.Many2one(
        comodel_name='res.users',
        string='Approver',
        tracking=True,
    )
    approval_date = fields.Date(
        string='Approval Date',
        tracking=True,
    )
    description = fields.Text(
        string='Description',
    )
    notes = fields.Text(
        string='Notes',
    )

    @api.depends('amount', 'spent_amount')
    def _compute_remaining_amount(self):
        """Calculate remaining budget."""
        for budget in self:
            budget.remaining_amount = budget.amount - budget.spent_amount

    @api.depends('amount', 'spent_amount')
    def _compute_utilization_percentage(self):
        """Calculate budget utilization percentage."""
        for budget in self:
            if budget.amount:
                budget.utilization_percentage = (
                    budget.spent_amount / budget.amount * 100
                )
            else:
                budget.utilization_percentage = 0.0

    def action_approve(self):
        """Approve budget."""
        self.write({
            'status': 'approved',
            'approver_id': self.env.user.id,
            'approval_date': fields.Date.context_today(self),
        })

    def action_activate(self):
        """Activate budget."""
        self.write({'status': 'active'})

    def action_close(self):
        """Close budget."""
        self.write({'status': 'closed'})
