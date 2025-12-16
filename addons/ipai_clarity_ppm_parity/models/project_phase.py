# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectPhase(models.Model):
    _inherit = 'project.task'

    # Phase Identification
    is_phase = fields.Boolean(
        string="Is Phase",
        default=False,
        index=True,
        help="Mark this task as a Clarity Phase (WBS container)"
    )

    phase_type = fields.Selection([
        ('initiation', 'Initiation'),
        ('planning', 'Planning'),
        ('design', 'Design'),
        ('implementation', 'Implementation'),
        ('testing', 'Testing'),
        ('deployment', 'Deployment'),
        ('closeout', 'Closeout')
    ], string="Phase Type", help="Clarity standard phase types")

    # Phase Metrics
    child_task_count = fields.Integer(
        string="Tasks in Phase",
        compute='_compute_child_task_count'
    )

    milestone_count = fields.Integer(
        string="Milestones in Phase",
        compute='_compute_milestone_count'
    )

    phase_progress = fields.Float(
        string="Phase Progress (%)",
        compute='_compute_phase_progress',
        store=True,
        help="Rollup of all child task progress"
    )

    phase_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string="Phase Status", default='not_started', tracking=True)

    # Phase Gate Fields
    has_gate = fields.Boolean(
        string="Has Phase Gate",
        help="This phase requires a formal gate review before proceeding"
    )

    gate_milestone_id = fields.Many2one(
        'project.milestone',
        string="Gate Milestone",
        help="Milestone representing the phase gate"
    )

    gate_decision = fields.Selection([
        ('pending', 'Pending'),
        ('go', 'Go'),
        ('no_go', 'No Go'),
        ('conditional', 'Conditional Go')
    ], string="Gate Decision", default='pending', tracking=True)

    gate_approver_id = fields.Many2one(
        'res.users',
        string="Gate Approver",
        help="User authorized to approve phase gate"
    )

    # Baseline for Phase
    phase_baseline_start = fields.Date(string="Phase Baseline Start")
    phase_baseline_finish = fields.Date(string="Phase Baseline Finish")

    phase_variance_days = fields.Integer(
        string="Phase Variance (days)",
        compute='_compute_phase_variance',
        help="Schedule variance for this phase"
    )

    @api.depends('child_ids')
    def _compute_child_task_count(self):
        """Count non-phase child tasks"""
        for phase in self:
            if phase.is_phase:
                phase.child_task_count = len(phase.child_ids.filtered(
                    lambda t: not t.is_phase
                ))
            else:
                phase.child_task_count = 0

    def _compute_milestone_count(self):
        """Count milestones linked to this phase"""
        for phase in self:
            if phase.is_phase:
                # Count milestones linked to this phase's tasks
                milestones = self.env['project.milestone'].search([
                    ('task_ids', 'in', phase.child_ids.ids)
                ])
                phase.milestone_count = len(milestones)
            else:
                phase.milestone_count = 0

    @api.depends('child_ids.stage_id', 'child_ids.is_phase')
    def _compute_phase_progress(self):
        """Calculate phase progress from child tasks (based on done stages)"""
        for phase in self:
            if phase.is_phase:
                children = phase.child_ids.filtered(lambda t: not t.is_phase)
                if children:
                    done_children = children.filtered(lambda t: t.stage_id.fold)
                    phase.phase_progress = (len(done_children) / len(children)) * 100.0
                else:
                    phase.phase_progress = 0.0
            else:
                phase.phase_progress = 0.0

    @api.depends('date_deadline', 'phase_baseline_finish')
    def _compute_phase_variance(self):
        """Calculate schedule variance for phase"""
        for phase in self:
            if phase.is_phase and phase.phase_baseline_finish and phase.date_deadline:
                delta = (phase.date_deadline - phase.phase_baseline_finish).days
                phase.phase_variance_days = delta
            else:
                phase.phase_variance_days = 0

    @api.constrains('parent_id', 'is_phase')
    def _check_phase_hierarchy(self):
        """Ensure phases don't nest under regular tasks"""
        for phase in self:
            if phase.is_phase and phase.parent_id and not phase.parent_id.is_phase:
                raise ValidationError(_(
                    "Phases can only be children of other phases, not regular tasks. "
                    "Phase: %s, Parent: %s"
                ) % (phase.name, phase.parent_id.name))

    def action_start_phase(self):
        """Mark phase as started"""
        self.ensure_one()
        if not self.is_phase:
            raise ValidationError(_("This action is only for phases"))

        self.write({
            'phase_status': 'in_progress',
            'date_start': fields.Date.today()
        })
        return True

    def action_complete_phase(self):
        """Mark phase as completed (requires gate approval if applicable)"""
        self.ensure_one()
        if not self.is_phase:
            raise ValidationError(_("This action is only for phases"))

        if self.has_gate and self.gate_decision != 'go':
            raise ValidationError(_(
                "Phase gate approval required before completing phase. "
                "Current gate decision: %s"
            ) % dict(self._fields['gate_decision'].selection).get(self.gate_decision))

        # Check if all child tasks are done
        incomplete_tasks = self.child_ids.filtered(
            lambda t: not t.is_phase and not t.stage_id.fold
        )

        if incomplete_tasks:
            raise ValidationError(_(
                "Cannot complete phase. %d task(s) still incomplete:\n%s"
            ) % (len(incomplete_tasks), '\n'.join(incomplete_tasks.mapped('name'))))

        self.write({
            'phase_status': 'completed',
            'date_end': fields.Date.today()
        })
        return True

    def action_approve_gate(self):
        """Approve phase gate"""
        self.ensure_one()
        if not self.is_phase or not self.has_gate:
            raise ValidationError(_("This phase does not have a gate to approve"))

        if self.gate_decision == 'go':
            raise ValidationError(_("Gate already approved"))

        # Check gate milestone completion criteria
        if self.gate_milestone_id and not self.gate_milestone_id.is_reached:
            raise ValidationError(_(
                "Gate milestone '%s' has not been reached. "
                "Complete all associated tasks first."
            ) % self.gate_milestone_id.name)

        self.write({
            'gate_decision': 'go'
        })

        # Log approval in chatter
        self.message_post(
            body=_(
                "Phase gate approved by %s on %s"
            ) % (self.env.user.name, fields.Date.today()),
            message_type='notification'
        )

        return True

    def action_reject_gate(self):
        """Reject phase gate"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Phase Gate',
            'res_model': 'phase.gate.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_phase_id': self.id}
        }

    def action_view_phase_tasks(self):
        """View all tasks in this phase"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tasks in {self.name}',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('parent_id', '=', self.id), ('is_phase', '=', False)],
            'context': {
                'default_parent_id': self.id,
                'default_project_id': self.project_id.id
            }
        }
