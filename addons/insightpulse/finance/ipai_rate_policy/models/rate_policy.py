# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class RatePolicy(models.Model):
    _name = 'rate.policy'
    _description = 'Rate Policy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Policy Name',
        required=True,
        tracking=True,
    )
    active = fields.Boolean(
        default=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    markup_percentage = fields.Float(
        string='Markup %',
        default=25.0,
        required=True,
        help='Markup percentage to apply to P60 base rate',
        tracking=True,
    )
    effective_date = fields.Date(
        string='Effective Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name='rate.policy.line',
        inverse_name='policy_id',
        string='Rate Lines',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('archived', 'Archived'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    notes = fields.Text(
        string='Notes',
    )

    @api.model
    def calculate_rate(self, p60_rate, markup_percentage=None):
        """Calculate rate with markup.

        Args:
            p60_rate: Base P60 rate
            markup_percentage: Optional markup percentage, defaults to policy default

        Returns:
            float: Calculated rate with markup
        """
        if markup_percentage is None:
            markup_percentage = self.markup_percentage
        return p60_rate * (1 + (markup_percentage / 100))

    def action_activate(self):
        """Activate rate policy."""
        self.write({'state': 'active'})

    def action_archive_policy(self):
        """Archive rate policy."""
        self.write({'state': 'archived', 'active': False})
