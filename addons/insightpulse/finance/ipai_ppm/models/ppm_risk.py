# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class PPMRisk(models.Model):
    _name = 'ppm.risk'
    _description = 'PPM Risk'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'risk_score desc, name'

    name = fields.Char(
        string='Risk Title',
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
    risk_category = fields.Selection(
        selection=[
            ('technical', 'Technical'),
            ('financial', 'Financial'),
            ('resource', 'Resource'),
            ('schedule', 'Schedule'),
            ('quality', 'Quality'),
            ('external', 'External'),
        ],
        string='Category',
        required=True,
        tracking=True,
    )
    probability = fields.Selection(
        selection=[
            ('1', 'Very Low (10%)'),
            ('2', 'Low (30%)'),
            ('3', 'Medium (50%)'),
            ('4', 'High (70%)'),
            ('5', 'Very High (90%)'),
        ],
        string='Probability',
        required=True,
        default='3',
        tracking=True,
    )
    impact = fields.Selection(
        selection=[
            ('1', 'Very Low'),
            ('2', 'Low'),
            ('3', 'Medium'),
            ('4', 'High'),
            ('5', 'Very High'),
        ],
        string='Impact',
        required=True,
        default='3',
        tracking=True,
    )
    risk_score = fields.Integer(
        string='Risk Score',
        compute='_compute_risk_score',
        store=True,
    )
    status = fields.Selection(
        selection=[
            ('identified', 'Identified'),
            ('analyzing', 'Analyzing'),
            ('planning', 'Planning Response'),
            ('monitoring', 'Monitoring'),
            ('mitigated', 'Mitigated'),
            ('occurred', 'Occurred'),
            ('closed', 'Closed'),
        ],
        default='identified',
        required=True,
        tracking=True,
    )
    owner_id = fields.Many2one(
        comodel_name='res.users',
        string='Risk Owner',
        tracking=True,
    )
    identification_date = fields.Date(
        string='Identified On',
        required=True,
        default=fields.Date.context_today,
    )
    mitigation_plan = fields.Text(
        string='Mitigation Plan',
    )
    contingency_plan = fields.Text(
        string='Contingency Plan',
    )
    description = fields.Text(
        string='Description',
        required=True,
    )
    notes = fields.Text(
        string='Notes',
    )

    @api.depends('probability', 'impact')
    def _compute_risk_score(self):
        """Calculate risk score as probability × impact."""
        for risk in self:
            prob = int(risk.probability) if risk.probability else 0
            imp = int(risk.impact) if risk.impact else 0
            risk.risk_score = prob * imp
