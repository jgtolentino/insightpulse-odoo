# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Task Dependencies (enhanced from OCA module)
    # OCA project_task_dependency provides:
    # - depend_on_ids (predecessors)
    # - dependent_ids (successors)
    # - dependency_type (fs, ss, ff, sf)

    # Add Clarity-specific dependency fields
    lag_days = fields.Integer(
        string="Lag (days)",
        default=0,
        help="Delay between predecessor completion and successor start (positive value)"
    )

    lead_days = fields.Integer(
        string="Lead (days)",
        default=0,
        help="Overlap between predecessor and successor (negative lag, positive value)"
    )

    # Critical Path Analysis
    critical_path = fields.Boolean(
        string="On Critical Path",
        compute='_compute_critical_path',
        store=True,
        index=True,
        help="Task is on the critical path (zero total float)"
    )

    total_float = fields.Integer(
        string="Total Float (days)",
        compute='_compute_float',
        store=True,
        help="Maximum delay possible without impacting project finish"
    )

    free_float = fields.Integer(
        string="Free Float (days)",
        compute='_compute_float',
        store=True,
        help="Maximum delay possible without impacting successor start"
    )

    # Resource Management
    resource_allocation = fields.Float(
        string="Resource Allocation (%)",
        default=100.0,
        help="Percentage of resource time allocated to this task"
    )

    planned_hours = fields.Float(
        string="Planned Hours",
        help="Originally planned effort hours"
    )

    actual_hours = fields.Float(
        string="Actual Hours",
        compute='_compute_actual_hours',
        store=True,
        help="Actual hours spent on task"
    )

    remaining_hours = fields.Float(
        string="Remaining Hours",
        help="Estimate to Complete (ETC)"
    )

    # Work Breakdown Structure (WBS) Code
    wbs_code = fields.Char(
        string="WBS Code",
        compute='_compute_wbs_code',
        store=True,
        help="Hierarchical WBS code (e.g., 1.2.3.1)"
    )

    # Earned Value Management (EVM) Fields
    planned_value = fields.Float(
        string="Planned Value (PV)",
        help="Budgeted cost of work scheduled"
    )

    earned_value = fields.Float(
        string="Earned Value (EV)",
        compute='_compute_earned_value',
        store=True,
        help="Budgeted cost of work performed"
    )

    actual_cost = fields.Float(
        string="Actual Cost (AC)",
        help="Actual cost of work performed"
    )

    schedule_variance = fields.Float(
        string="Schedule Variance (SV)",
        compute='_compute_variances',
        help="EV - PV (positive is ahead of schedule)"
    )

    cost_variance = fields.Float(
        string="Cost Variance (CV)",
        compute='_compute_variances',
        help="EV - AC (positive is under budget)"
    )

    @api.depends('depend_on_ids', 'date_deadline')
    def _compute_critical_path(self):
        """
        Determine if task is on critical path.
        Critical path tasks have zero total float.
        """
        for task in self:
            if not task.is_phase:
                task.critical_path = (task.total_float == 0)
            else:
                task.critical_path = False

    @api.depends('date_deadline', 'depend_on_ids', 'dependent_ids')
    def _compute_float(self):
        """
        Calculate Total Float and Free Float.
        Total Float = Latest Finish - Earliest Finish
        Free Float = min(Successor Early Start) - Earliest Finish
        """
        for task in self:
            if task.is_phase:
                task.total_float = 0
                task.free_float = 0
                continue

            # Simplified calculation (full CPM would require project-wide network analysis)
            if task.date_deadline and task.project_id.date:
                from datetime import date as date_type

                # Convert both to dates for comparison
                project_deadline = task.project_id.date
                task_deadline = task.date_deadline.date() if hasattr(task.date_deadline, 'date') else task.date_deadline

                # Total float: days between task deadline and project deadline
                total_float_days = (project_deadline - task_deadline).days
                task.total_float = max(0, total_float_days)

                # Free float: days to earliest successor
                if task.dependent_ids:
                    # Convert all successor deadlines to dates
                    successor_deadlines = []
                    for dep in task.dependent_ids:
                        if dep.date_deadline:
                            dl = dep.date_deadline.date() if hasattr(dep.date_deadline, 'date') else dep.date_deadline
                            successor_deadlines.append(dl)

                    if successor_deadlines:
                        earliest_successor = min(successor_deadlines)
                        free_float_days = (earliest_successor - task_deadline).days
                        task.free_float = max(0, free_float_days)
                    else:
                        task.free_float = task.total_float
                else:
                    task.free_float = task.total_float
            else:
                task.total_float = 0
                task.free_float = 0

    # Removed timesheet dependency - requires hr_timesheet module
    def _compute_actual_hours(self):
        """Placeholder for actual hours (requires hr_timesheet module)"""
        for task in self:
            task.actual_hours = 0.0

    @api.depends('parent_id', 'parent_id.wbs_code', 'project_id')
    def _compute_wbs_code(self):
        """
        Generate hierarchical WBS code.
        Format: 1.2.3.1 (Project.Phase.Task.Subtask)
        """
        for task in self:
            if task.parent_id and task.parent_id.wbs_code:
                # Get sibling count for numbering
                siblings = self.search([
                    ('parent_id', '=', task.parent_id.id),
                    ('id', '<=', task.id)
                ], order='id')
                sibling_num = len(siblings)
                task.wbs_code = f"{task.parent_id.wbs_code}.{sibling_num}"
            elif task.project_id:
                # Top-level task
                siblings = self.search([
                    ('project_id', '=', task.project_id.id),
                    ('parent_id', '=', False),
                    ('id', '<=', task.id)
                ], order='id')
                task.wbs_code = str(len(siblings))
            else:
                task.wbs_code = ''

    # Removed progress dependency - requires OCA module
    def _compute_earned_value(self):
        """Placeholder for Earned Value (requires progress tracking module)"""
        for task in self:
            task.earned_value = 0.0

    @api.depends('earned_value', 'planned_value', 'actual_cost')
    def _compute_variances(self):
        """Calculate Schedule Variance and Cost Variance"""
        for task in self:
            # Schedule Variance (SV) = EV - PV
            task.schedule_variance = task.earned_value - task.planned_value

            # Cost Variance (CV) = EV - AC
            task.cost_variance = task.earned_value - task.actual_cost

    def action_view_dependencies(self):
        """View dependency graph for this task"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Task Dependencies',
            'res_model': 'project.task.dependency',
            'view_mode': 'list,form,graph',
            'domain': [
                '|',
                ('task_id', '=', self.id),
                ('depend_on_id', '=', self.id)
            ]
        }

    def action_add_to_critical_path(self):
        """Manually mark task as critical"""
        self.write({'critical_path': True})
        return True

    def action_calculate_float(self):
        """Recalculate float values"""
        self._compute_float()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Float Recalculated'),
                'message': _(
                    'Total Float: %d days\n'
                    'Free Float: %d days\n'
                    'Critical: %s'
                ) % (self.total_float, self.free_float, 'Yes' if self.critical_path else 'No'),
                'type': 'info',
                'sticky': False,
            }
        }
