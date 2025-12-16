# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'

    # Milestone Type Classification
    milestone_type = fields.Selection([
        ('phase_gate', 'Phase Gate'),
        ('deliverable', 'Deliverable'),
        ('approval', 'Approval Required'),
        ('decision', 'Decision Point'),
        ('review', 'Review Point'),
        ('checkpoint', 'Checkpoint')
    ], string="Milestone Type", default='phase_gate', required=True)

    # Gate Status (for phase gates)
    gate_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('conditional', 'Conditional Pass')
    ], string="Gate Status", default='not_started', tracking=True)

    # Approval Workflow
    approval_required = fields.Boolean(
        string="Approval Required",
        help="Requires formal approval to complete"
    )

    approver_id = fields.Many2one(
        'res.users',
        string="Approver",
        help="User responsible for milestone approval"
    )

    approval_date = fields.Date(string="Approval Date", readonly=True)

    # Associated Tasks
    task_ids = fields.One2many(
        'project.task',
        'milestone_id',
        string="Associated Tasks",
        help="Tasks that must be completed for this milestone"
    )

    task_count = fields.Integer(
        string="Number of Tasks",
        compute='_compute_task_count'
    )

    completed_task_count = fields.Integer(
        string="Completed Tasks",
        compute='_compute_task_count'
    )

    # Completion Criteria
    completion_criteria = fields.Text(
        string="Completion Criteria",
        help="What must be true for this milestone to be complete"
    )

    deliverables = fields.Text(
        string="Expected Deliverables",
        help="List of deliverables required for milestone completion"
    )

    # Risk Assessment
    risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk')
    ], string="Risk Level", default='low')

    risk_notes = fields.Text(
        string="Risk Notes",
        help="Identified risks and mitigation strategies"
    )

    # Alert Settings
    alert_days_before = fields.Integer(
        string="Alert Days Before Deadline",
        default=7,
        help="Send notifications X days before milestone deadline"
    )

    last_alert_sent = fields.Date(string="Last Alert Sent", readonly=True)

    # Variance Tracking
    baseline_deadline = fields.Date(
        string="Baseline Deadline",
        help="Original planned deadline from approved baseline"
    )

    variance_days = fields.Integer(
        string="Variance (days)",
        compute='_compute_variance',
        store=True,
        help="Days difference between baseline and current deadline"
    )

    @api.depends('task_ids', 'task_ids.stage_id')
    def _compute_task_count(self):
        """Count total and completed tasks"""
        for milestone in self:
            tasks = milestone.task_ids
            milestone.task_count = len(tasks)
            milestone.completed_task_count = len(tasks.filtered(
                lambda t: t.stage_id.fold
            ))

    @api.depends('deadline', 'baseline_deadline')
    def _compute_variance(self):
        """Calculate deadline variance"""
        for milestone in self:
            if milestone.baseline_deadline and milestone.deadline:
                delta = (milestone.deadline - milestone.baseline_deadline).days
                milestone.variance_days = delta
            else:
                milestone.variance_days = 0

    @api.depends('task_ids.stage_id', 'approval_required', 'approval_date')
    def _compute_is_reached(self):
        """
        Override OCA compute method.
        Milestone reached only when:
        1. All associated tasks are done
        2. If approval required, approval is granted
        """
        for milestone in self:
            tasks = milestone.task_ids
            if tasks:
                all_done = all(task.stage_id.fold for task in tasks)
                if milestone.approval_required:
                    milestone.is_reached = all_done and bool(milestone.approval_date)
                else:
                    milestone.is_reached = all_done
            else:
                # No tasks: check manual approval
                if milestone.approval_required:
                    milestone.is_reached = bool(milestone.approval_date)
                else:
                    milestone.is_reached = False

    @api.constrains('deadline', 'baseline_deadline')
    def _check_deadlines(self):
        """Validate deadline logic"""
        for milestone in self:
            if milestone.baseline_deadline and milestone.deadline:
                if milestone.deadline < milestone.baseline_deadline - timedelta(days=365):
                    raise ValidationError(_(
                        "Milestone deadline cannot be more than 1 year before baseline. "
                        "Milestone: %s"
                    ) % milestone.name)

    def action_approve_milestone(self):
        """Approve milestone"""
        self.ensure_one()

        if not self.approval_required:
            raise ValidationError(_("This milestone does not require approval"))

        if self.approval_date:
            raise ValidationError(_("Milestone already approved on %s") % self.approval_date)

        # Check if all tasks are complete
        if self.task_ids:
            incomplete = self.task_ids.filtered(lambda t: not t.stage_id.fold)
            if incomplete:
                raise ValidationError(_(
                    "Cannot approve milestone. %d task(s) still incomplete:\n%s"
                ) % (len(incomplete), '\n'.join(incomplete.mapped('name'))))

        # Approve
        self.write({
            'approval_date': fields.Date.today(),
            'gate_status': 'passed' if self.milestone_type == 'phase_gate' else self.gate_status,
            'is_reached': True
        })

        # Log approval
        self.message_post(
            body=_(
                "Milestone approved by %s on %s"
            ) % (self.env.user.name, fields.Date.today()),
            message_type='notification'
        )

        return True

    def action_send_alert(self):
        """Send deadline alert notification"""
        self.ensure_one()

        if not self.deadline:
            raise ValidationError(_("Milestone has no deadline set"))

        # Check if alert already sent recently (within 24 hours)
        if self.last_alert_sent and (fields.Date.today() - self.last_alert_sent).days < 1:
            raise ValidationError(_("Alert already sent today. Wait 24 hours before resending."))

        # Compose notification message
        days_left = (self.deadline - fields.Date.today()).days
        message = _(
            "⚠️ Milestone Alert: %s\n"
            "Deadline: %s (%d days remaining)\n"
            "Status: %s\n"
            "Completed Tasks: %d / %d\n"
            "Approver: %s"
        ) % (
            self.name,
            self.deadline,
            days_left,
            dict(self._fields['gate_status'].selection).get(self.gate_status),
            self.completed_task_count,
            self.task_count,
            self.approver_id.name if self.approver_id else 'Not assigned'
        )

        # Send via Mattermost (if configured)
        try:
            self.env['mattermost.notification'].send({
                'text': message,
                'channel': 'project-alerts'
            })
        except Exception:
            pass  # Mattermost not configured, skip

        # Post to chatter
        self.message_post(
            body=message,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

        # Update last alert sent
        self.last_alert_sent = fields.Date.today()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Alert Sent'),
                'message': _('Milestone alert sent successfully'),
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def _cron_send_milestone_alerts(self):
        """
        Cron job to send alerts for upcoming milestones.
        Run daily at 8 AM.
        """
        today = fields.Date.today()

        # Find milestones approaching deadline
        milestones = self.search([
            ('deadline', '>=', today),
            ('deadline', '<=', today + timedelta(days=7)),
            ('is_reached', '=', False),
            ('alert_days_before', '>', 0)
        ])

        for milestone in milestones:
            days_left = (milestone.deadline - today).days
            if days_left <= milestone.alert_days_before:
                # Check if alert already sent recently
                if not milestone.last_alert_sent or (today - milestone.last_alert_sent).days >= 1:
                    milestone.action_send_alert()

        return True

    def action_view_tasks(self):
        """View all tasks associated with this milestone"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tasks for {self.name}',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('milestone_id', '=', self.id)],
            'context': {
                'default_milestone_id': self.id,
                'default_project_id': self.project_id.id
            }
        }
