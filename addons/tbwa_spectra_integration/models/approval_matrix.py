# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TBWAApprovalMatrix(models.Model):
    """
    Configurable approval matrix for cash advances and expenses.

    Rules based on:
    - Amount thresholds
    - Employee department
    - Expense category
    - Project type
    """
    _name = 'tbwa.approval.matrix'
    _description = 'Approval Matrix Configuration'
    _order = 'amount_min, sequence'

    name = fields.Char(string='Rule Name', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Amount thresholds
    amount_min = fields.Float(string='Minimum Amount', required=True, default=0.0)
    amount_max = fields.Float(string='Maximum Amount', required=True, default=999999999.99)

    # Approval levels
    approver_level_1 = fields.Selection([
        ('manager', 'Immediate Manager'),
        ('department_head', 'Department Head'),
        ('finance_head', 'Finance Head'),
    ], string='Level 1 Approver', required=True, default='manager')

    approver_level_2 = fields.Selection([
        ('department_head', 'Department Head'),
        ('finance_head', 'Finance Head'),
        ('cfo', 'CFO'),
        ('ceo', 'CEO'),
    ], string='Level 2 Approver', required=True, default='finance_head')

    # Optional: Department-specific rules
    department_ids = fields.Many2many('hr.department', string='Applicable Departments',
                                      help='Leave empty for all departments')

    # Optional: Category-specific rules
    category_ids = fields.Many2many('product.category', string='Expense Categories',
                                    help='Leave empty for all categories')

    # SLA
    sla_hours_l1 = fields.Integer(string='L1 SLA (hours)', default=24,
                                  help='Expected approval time for Level 1')
    sla_hours_l2 = fields.Integer(string='L2 SLA (hours)', default=48,
                                  help='Expected approval time for Level 2')

    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    _sql_constraints = [
        ('amount_range_check', 'CHECK(amount_max >= amount_min)',
         'Maximum amount must be greater than or equal to minimum amount!'),
    ]

    @api.constrains('amount_min', 'amount_max')
    def _check_amount_overlap(self):
        """Ensure no overlapping amount ranges for same context."""
        for record in self:
            domain = [
                ('id', '!=', record.id),
                ('active', '=', True),
                ('amount_min', '<=', record.amount_max),
                ('amount_max', '>=', record.amount_min),
            ]

            # Check department overlap
            if record.department_ids:
                domain.append(('department_ids', 'in', record.department_ids.ids))

            overlapping = self.search(domain, limit=1)
            if overlapping:
                raise ValidationError(
                    _('Amount range overlaps with existing rule: %s') % overlapping.name
                )
