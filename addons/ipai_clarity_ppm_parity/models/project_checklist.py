# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProjectTaskChecklistItem(models.Model):
    _inherit = 'project.task.checklist.item'

    # OCA project_task_checklist provides:
    # - name (To-Do description)
    # - is_done (Checkbox)
    # - task_id (Parent task)
    # - sequence (Ordering)

    # Add Clarity-specific To-Do extensions

    # Assignment
    assigned_user_id = fields.Many2one(
        'res.users',
        string="Assigned To",
        help="Who is responsible for this to-do item"
    )

    # Scheduling
    due_date = fields.Date(
        string="Due Date",
        help="When this to-do should be completed"
    )

    completed_date = fields.Date(
        string="Completed Date",
        readonly=True,
        help="Actual completion date"
    )

    # Priority
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], default='1', string="Priority", help="Importance of this to-do item")

    # Effort Tracking
    estimated_hours = fields.Float(
        string="Estimated Hours",
        help="How long this to-do should take"
    )

    actual_hours = fields.Float(
        string="Actual Hours",
        help="Time actually spent on this to-do"
    )

    # Status
    status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('completed', 'Completed')
    ], string="Status", default='not_started', compute='_compute_status', store=True)

    # Notes
    notes = fields.Text(
        string="Notes",
        help="Additional details or instructions"
    )

    # Blocking Issues
    blocker_description = fields.Text(
        string="Blocker Description",
        help="What is preventing completion of this to-do"
    )

    @api.depends('is_done')
    def _compute_status(self):
        """Compute status based on checkbox and dates"""
        for item in self:
            if item.is_done:
                item.status = 'completed'
            elif item.blocker_description:
                item.status = 'blocked'
            elif item.actual_hours and item.actual_hours > 0:
                item.status = 'in_progress'
            else:
                item.status = 'not_started'

    def write(self, vals):
        """Track completion date when checkbox is checked"""
        if 'is_done' in vals and vals['is_done']:
            vals['completed_date'] = fields.Date.today()
            vals['status'] = 'completed'
        elif 'is_done' in vals and not vals['is_done']:
            vals['completed_date'] = False

        return super().write(vals)

    @api.model
    def create(self, vals):
        """Set default status on creation"""
        if 'status' not in vals:
            if vals.get('is_done'):
                vals['status'] = 'completed'
                vals['completed_date'] = fields.Date.today()
            else:
                vals['status'] = 'not_started'

        return super().create(vals)

    def action_mark_in_progress(self):
        """Mark to-do as in progress"""
        self.ensure_one()
        self.write({
            'status': 'in_progress',
            'is_done': False
        })
        return True

    def action_mark_blocked(self):
        """Mark to-do as blocked and request blocker description"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mark as Blocked',
            'res_model': 'checklist.blocker.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_checklist_item_id': self.id}
        }

    def action_complete(self):
        """Mark to-do as complete"""
        self.ensure_one()
        self.write({
            'is_done': True,
            'status': 'completed',
            'completed_date': fields.Date.today()
        })
        return True
