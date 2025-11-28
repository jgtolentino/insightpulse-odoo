# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FinanceLogframe(models.Model):
    """
    Logical Framework tracking for Finance operations

    Hierarchy:
    - Goal (highest level)
    - Outcome
    - IM1 (Immediate Objective 1 - Month-End Closing)
    - IM2 (Immediate Objective 2 - Tax Filing)
    - Output (Deliverables)
    - Activity (Specific tasks)
    """
    _name = 'ipai.finance.logframe'
    _description = 'Finance Logical Framework'
    _order = 'sequence, level, name'

    name = fields.Char(
        string='Objective',
        required=True,
        help='Name of the logframe objective'
    )

    code = fields.Char(
        string='Code',
        help='Hierarchical logframe code (e.g., "GOAL 1", "OUTCOME 1.1", "IM 1.1", "OUTPUT 1.1.1")'
    )

    level = fields.Selection([
        ('goal', 'Goal'),
        ('outcome', 'Outcome'),
        ('im1', 'IM1 - Month-End Closing'),
        ('im2', 'IM2 - Tax Filing'),
        ('output', 'Output'),
        ('activity', 'Activity'),
    ], string='Level', required=True, default='activity',
       help='Hierarchical level in the logical framework')

    description = fields.Text(
        string='Description',
        help='Detailed description of the objective'
    )

    indicator = fields.Char(
        string='Indicator',
        help='Measurable indicator of success (e.g., "100% on-time filing", "Zero penalties")'
    )

    means_of_verification = fields.Text(
        string='Means of Verification',
        help='How to verify the indicator was achieved (e.g., "BIR submission receipts", "Bank reconciliation reports")'
    )

    assumptions = fields.Text(
        string='Assumptions',
        help='Risk factors and assumptions (e.g., "Stable tax regulations", "Timely bank statement availability")'
    )

    target_value = fields.Float(
        string='Target Value',
        help='Numeric target for the indicator (e.g., 100 for 100%)'
    )

    parent_id = fields.Many2one(
        'ipai.finance.logframe',
        string='Parent Objective',
        ondelete='cascade',
        help='Parent objective in the hierarchy'
    )

    child_ids = fields.One2many(
        'ipai.finance.logframe',
        'parent_id',
        string='Child Objectives'
    )

    task_ids = fields.One2many(
        'project.task',
        'finance_logframe_id',
        string='Related Tasks',
        help='Project tasks linked to this logframe objective'
    )

    task_count = fields.Integer(
        string='Task Count',
        compute='_compute_task_count',
        store=True
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Display order'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.depends('task_ids')
    def _compute_task_count(self):
        """Compute total number of tasks linked to this objective"""
        for record in self:
            record.task_count = len(record.task_ids)

    def name_get(self):
        """Display level and name together"""
        result = []
        for record in self:
            level_label = dict(record._fields['level'].selection).get(record.level, '')
            name = f"[{level_label}] {record.name}"
            result.append((record.id, name))
        return result

    def action_view_tasks(self):
        """Open tasks linked to this logframe objective"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tasks - {self.name}',
            'res_model': 'project.task',
            'view_mode': 'tree,form',
            'domain': [('finance_logframe_id', '=', self.id)],
            'context': {'default_finance_logframe_id': self.id}
        }
