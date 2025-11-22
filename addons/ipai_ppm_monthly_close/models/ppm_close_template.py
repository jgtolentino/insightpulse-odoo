# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PpmCloseTemplate(models.Model):
    """
    Reusable task templates for monthly close.

    Templates define the standard tasks that repeat every month.
    """
    _name = 'ppm.close.template'
    _description = 'Monthly Close Task Template'
    _order = 'sequence, id'

    # Core fields
    active = fields.Boolean(
        string='Active',
        default=True,
        help="Inactive templates will not be used for task generation"
    )
    name = fields.Char(
        string='Template Name',
        compute='_compute_name',
        store=True
    )
    task_category = fields.Char(
        string='Task Category',
        required=True,
        help="Short code like 'RIM – Rent & Leases'"
    )
    detailed_task = fields.Text(
        string='Detailed Monthly Tasks',
        required=True,
        help="Full description of the task"
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Used for ordering tasks"
    )

    # Agency and roles
    agency_code = fields.Selection([
        ('RIM', 'RIM'),
        ('CKVC', 'CKVC'),
        ('BOM', 'BOM'),
        ('JPAL', 'JPAL'),
        ('JLI', 'JLI'),
        ('JAP', 'JAP'),
        ('LAS', 'LAS'),
        ('RMQB', 'RMQB'),
    ], string='Agency', required=True)

    owner_code = fields.Char(
        string='Owner (Employee Code)',
        required=True,
        help="Default owner for this task"
    )
    reviewer_code = fields.Char(
        string='Reviewer (Employee Code)',
        help="Default reviewer for this task"
    )
    approver_code = fields.Char(
        string='Approver (Employee Code)',
        help="Default approver for this task"
    )

    # Effort (in days)
    prep_days = fields.Float(
        string='Preparation Days',
        default=1.0,
        help="Estimated effort for preparation"
    )
    review_days = fields.Float(
        string='Review Days',
        default=0.5,
        help="Estimated effort for review"
    )
    approval_days = fields.Float(
        string='Approval Days',
        default=0.5,
        help="Estimated effort for approval"
    )
    total_days = fields.Float(
        string='Total Effort',
        compute='_compute_total_days',
        store=True
    )

    # Metadata
    notes = fields.Text(string='Notes')

    @api.depends('task_category', 'agency_code')
    def _compute_name(self):
        """Generate display name."""
        for template in self:
            if template.task_category and template.agency_code:
                template.name = f"{template.agency_code} – {template.task_category}"
            else:
                template.name = template.task_category or "New Template"

    @api.depends('prep_days', 'review_days', 'approval_days')
    def _compute_total_days(self):
        """Calculate total effort."""
        for template in self:
            template.total_days = (
                (template.prep_days or 0.0) +
                (template.review_days or 0.0) +
                (template.approval_days or 0.0)
            )
