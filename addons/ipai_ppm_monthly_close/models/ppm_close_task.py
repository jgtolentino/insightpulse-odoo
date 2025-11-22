# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PpmCloseTask(models.Model):
    """
    Individual closing task with owner/reviewer/approver workflow.

    Workflow: Owner (prep) → Reviewer (review) → Approver (final sign-off)
    """
    _name = 'ppm.close.task'
    _description = 'Monthly Close Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'monthly_close_id desc, sequence, id'

    # Core fields
    name = fields.Char(
        string='Task Category',
        required=True,
        tracking=True
    )
    detailed_task = fields.Text(
        string='Detailed Monthly Tasks',
        required=True,
        help="Detailed description of what needs to be done"
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Used for ordering tasks"
    )

    # Relationships
    monthly_close_id = fields.Many2one(
        'ppm.monthly.close',
        string='Monthly Close',
        required=True,
        ondelete='cascade',
        index=True
    )
    template_id = fields.Many2one(
        'ppm.close.template',
        string='Template',
        help="Template this task was created from"
    )

    # Agency and role codes
    agency_code = fields.Selection([
        ('RIM', 'RIM'),
        ('CKVC', 'CKVC'),
        ('BOM', 'BOM'),
        ('JPAL', 'JPAL'),
        ('JLI', 'JLI'),
        ('JAP', 'JAP'),
        ('LAS', 'LAS'),
        ('RMQB', 'RMQB'),
    ], string='Agency', required=True, tracking=True)

    owner_code = fields.Char(
        string='Owner (Employee Code)',
        required=True,
        tracking=True,
        help="Primary person responsible for task preparation"
    )
    reviewer_code = fields.Char(
        string='Reviewer (Employee Code)',
        tracking=True,
        help="Person who reviews the task after preparation"
    )
    approver_code = fields.Char(
        string='Approver (Employee Code)',
        tracking=True,
        help="Person who gives final approval"
    )

    # Effort tracking (in days)
    prep_days = fields.Float(
        string='Preparation Days',
        default=1.0,
        help="Effort required for preparation phase"
    )
    review_days = fields.Float(
        string='Review Days',
        default=0.5,
        help="Effort required for review phase"
    )
    approval_days = fields.Float(
        string='Approval Days',
        default=0.5,
        help="Effort required for approval phase"
    )
    total_days = fields.Float(
        string='Total Effort',
        compute='_compute_total_days',
        store=True,
        help="Sum of prep + review + approval days"
    )

    # Computed dates from parent schedule
    prep_start = fields.Date(
        string='Prep Start',
        related='monthly_close_id.prep_start_date',
        store=True
    )
    review_due = fields.Date(
        string='Review Due',
        related='monthly_close_id.review_due_date',
        store=True
    )
    approval_due = fields.Date(
        string='Approval Due',
        related='monthly_close_id.approval_due_date',
        store=True
    )

    # Status and tracking
    state = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('for_review', 'For Review'),
        ('for_approval', 'For Approval'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='todo', tracking=True, required=True)

    # Completion tracking
    prep_completed_date = fields.Date(
        string='Prep Completed On',
        tracking=True
    )
    prep_completed_by = fields.Char(
        string='Prep Completed By',
        tracking=True
    )
    review_completed_date = fields.Date(
        string='Review Completed On',
        tracking=True
    )
    review_completed_by = fields.Char(
        string='Review Completed By',
        tracking=True
    )
    approval_completed_date = fields.Date(
        string='Approval Completed On',
        tracking=True
    )
    approval_completed_by = fields.Char(
        string='Approval Completed By',
        tracking=True
    )

    # Notes
    notes = fields.Text(string='Notes')
    completion_notes = fields.Text(string='Completion Notes')

    @api.depends('prep_days', 'review_days', 'approval_days')
    def _compute_total_days(self):
        """Calculate total effort across all phases."""
        for task in self:
            task.total_days = (
                (task.prep_days or 0.0) +
                (task.review_days or 0.0) +
                (task.approval_days or 0.0)
            )

    def action_start_prep(self):
        """Start preparation phase."""
        self.ensure_one()
        if self.state != 'todo':
            raise UserError(_("Task must be in 'To Do' state to start preparation."))

        self.state = 'in_progress'
        self.message_post(
            body=_("Preparation started by %s") % self.env.user.name,
            subtype_xmlid='mail.mt_note'
        )

    def action_submit_for_review(self):
        """Submit task for review."""
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_("Task must be 'In Progress' to submit for review."))

        self.write({
            'state': 'for_review',
            'prep_completed_date': fields.Date.today(),
            'prep_completed_by': self.env.user.login,
        })

        # Notify reviewer
        if self.reviewer_code:
            self.action_notify_reviewer()

        self.message_post(
            body=_("Submitted for review by %s") % self.env.user.name,
            subtype_xmlid='mail.mt_note'
        )

    def action_submit_for_approval(self):
        """Submit task for approval after review."""
        self.ensure_one()
        if self.state != 'for_review':
            raise UserError(_("Task must be 'For Review' to submit for approval."))

        self.write({
            'state': 'for_approval',
            'review_completed_date': fields.Date.today(),
            'review_completed_by': self.env.user.login,
        })

        # Notify approver
        if self.approver_code:
            self.action_notify_approver()

        self.message_post(
            body=_("Submitted for approval by %s (Reviewer)") % self.env.user.name,
            subtype_xmlid='mail.mt_note'
        )

    def action_approve(self):
        """Final approval - mark task as done."""
        self.ensure_one()
        if self.state != 'for_approval':
            raise UserError(_("Task must be 'For Approval' to approve."))

        self.write({
            'state': 'done',
            'approval_completed_date': fields.Date.today(),
            'approval_completed_by': self.env.user.login,
        })

        self.message_post(
            body=_("Approved and completed by %s (Approver)") % self.env.user.name,
            subtype_xmlid='mail.mt_note'
        )

        # Check if all tasks are done
        if all(task.state == 'done' for task in self.monthly_close_id.task_ids):
            self.monthly_close_id.state = 'done'

    def action_reject(self):
        """Reject task - send back to owner."""
        self.ensure_one()
        if self.state not in ('for_review', 'for_approval'):
            raise UserError(_("Task must be under review or approval to reject."))

        self.state = 'in_progress'

        # Notify owner
        self.action_notify_owner()

        self.message_post(
            body=_("Rejected by %s. Returned to owner for corrections.") % self.env.user.name,
            subtype_xmlid='mail.mt_note'
        )

    def action_notify_owner(self):
        """Send notification to task owner."""
        self.ensure_one()
        # TODO: Integrate with Odoo messaging or n8n webhook
        _logger.info("Notification sent to owner: %s for task: %s",
                    self.owner_code, self.name)

    def action_notify_reviewer(self):
        """Send notification to reviewer."""
        self.ensure_one()
        if not self.reviewer_code:
            return
        # TODO: Integrate with Odoo messaging or n8n webhook
        _logger.info("Notification sent to reviewer: %s for task: %s",
                    self.reviewer_code, self.name)

    def action_notify_approver(self):
        """Send notification to approver."""
        self.ensure_one()
        if not self.approver_code:
            return
        # TODO: Integrate with Odoo messaging or n8n webhook
        _logger.info("Notification sent to approver: %s for task: %s",
                    self.approver_code, self.name)

    @api.model
    def cron_send_daily_reminders(self):
        """
        Daily cron to send reminders for pending tasks.

        Checks:
        - Tasks in 'todo' state on prep_start date
        - Tasks in 'for_review' state on review_due date
        - Tasks in 'for_approval' state on approval_due date
        """
        today = fields.Date.today()

        # Find tasks needing reminders
        tasks_to_start = self.search([
            ('state', '=', 'todo'),
            ('prep_start', '=', today),
        ])

        tasks_for_review = self.search([
            ('state', '=', 'for_review'),
            ('review_due', '=', today),
        ])

        tasks_for_approval = self.search([
            ('state', '=', 'for_approval'),
            ('approval_due', '=', today),
        ])

        # Send notifications
        for task in tasks_to_start:
            task.action_notify_owner()

        for task in tasks_for_review:
            task.action_notify_reviewer()

        for task in tasks_for_approval:
            task.action_notify_approver()

        _logger.info("Daily reminders sent: %d to start, %d for review, %d for approval",
                    len(tasks_to_start), len(tasks_for_review), len(tasks_for_approval))
