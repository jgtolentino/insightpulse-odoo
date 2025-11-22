# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class PpmMonthlyClose(models.Model):
    """
    Master monthly close schedule.

    Implements recurrence rule:
    - C = last business day of month
    - S = C - 3 working days (prep start)
    - Review Due = S + 1 working day (AM)
    - Approval Due = S + 1 working day (EOD)
    """
    _name = 'ppm.monthly.close'
    _description = 'Monthly Financial Close Schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'close_month desc'

    # Core fields
    name = fields.Char(
        string='Close Period',
        compute='_compute_name',
        store=True,
        tracking=True
    )
    close_month = fields.Date(
        string='Close Month',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
        tracking=True,
        help="Month being closed (stored as first day of month)"
    )

    # Computed schedule dates
    month_end_date = fields.Date(
        string='Month End (C)',
        compute='_compute_schedule_dates',
        store=True,
        help="Last business day of the month"
    )
    prep_start_date = fields.Date(
        string='Prep Start (S)',
        compute='_compute_schedule_dates',
        store=True,
        help="C - 3 working days"
    )
    review_due_date = fields.Date(
        string='Review Due',
        compute='_compute_schedule_dates',
        store=True,
        help="S + 1 working day (AM)"
    )
    approval_due_date = fields.Date(
        string='Approval Due',
        compute='_compute_schedule_dates',
        store=True,
        help="S + 1 working day (EOD)"
    )

    # Task tracking
    task_ids = fields.One2many(
        'ppm.close.task',
        'monthly_close_id',
        string='Closing Tasks'
    )
    task_count = fields.Integer(
        string='Total Tasks',
        compute='_compute_task_stats',
        store=True
    )
    task_completed = fields.Integer(
        string='Completed Tasks',
        compute='_compute_task_stats',
        store=True
    )
    progress_percentage = fields.Float(
        string='Progress %',
        compute='_compute_task_stats',
        store=True
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('approval', 'Pending Approval'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    # Metadata
    notes = fields.Text(string='Notes')
    created_by_cron = fields.Boolean(
        string='Auto-Created',
        default=False,
        help="Created automatically by scheduled action"
    )

    @api.depends('close_month')
    def _compute_name(self):
        """Generate display name from close month."""
        for record in self:
            if record.close_month:
                record.name = f"FIN CLOSE – {record.close_month.strftime('%B %Y')}"
            else:
                record.name = "New Monthly Close"

    @api.depends('close_month')
    def _compute_schedule_dates(self):
        """
        Compute schedule dates using business day logic:
        - C = last business day of month
        - S = C - 3 working days
        - Review = S + 1 working day
        - Approval = S + 1 working day (EOD)
        """
        for record in self:
            if not record.close_month:
                record.month_end_date = False
                record.prep_start_date = False
                record.review_due_date = False
                record.approval_due_date = False
                continue

            # Calculate last day of month
            next_month = record.close_month + relativedelta(months=1)
            last_day = next_month - timedelta(days=1)

            # Find last business day (C)
            month_end = self._get_previous_business_day(last_day)
            record.month_end_date = month_end

            # Calculate S = C - 3 working days
            prep_start = self._subtract_business_days(month_end, 3)
            record.prep_start_date = prep_start

            # Review and Approval = S + 1 working day
            review_approval = self._add_business_days(prep_start, 1)
            record.review_due_date = review_approval
            record.approval_due_date = review_approval

    @api.depends('task_ids.state')
    def _compute_task_stats(self):
        """Calculate task completion statistics."""
        for record in self:
            tasks = record.task_ids
            record.task_count = len(tasks)
            record.task_completed = len(tasks.filtered(lambda t: t.state == 'done'))
            record.progress_percentage = (
                (record.task_completed / record.task_count * 100)
                if record.task_count > 0 else 0.0
            )

    def _get_business_days(self):
        """
        Get list of business days (Monday-Friday).
        Excludes weekends. Could be extended to exclude holidays.
        """
        # TODO: Integrate with resource.calendar for holiday exclusions
        return [0, 1, 2, 3, 4]  # Monday to Friday

    def _is_business_day(self, date):
        """Check if date is a business day."""
        return date.weekday() in self._get_business_days()

    def _get_previous_business_day(self, date):
        """Get previous business day from given date."""
        current = date
        while not self._is_business_day(current):
            current -= timedelta(days=1)
        return current

    def _get_next_business_day(self, date):
        """Get next business day from given date."""
        current = date
        while not self._is_business_day(current):
            current += timedelta(days=1)
        return current

    def _subtract_business_days(self, start_date, num_days):
        """Subtract N business days from start date."""
        current = start_date
        days_subtracted = 0

        while days_subtracted < num_days:
            current -= timedelta(days=1)
            if self._is_business_day(current):
                days_subtracted += 1

        return current

    def _add_business_days(self, start_date, num_days):
        """Add N business days to start date."""
        current = start_date
        days_added = 0

        while days_added < num_days:
            current += timedelta(days=1)
            if self._is_business_day(current):
                days_added += 1

        return current

    def action_generate_tasks(self):
        """
        Generate tasks from template for this close period.
        Called manually or by cron.
        """
        self.ensure_one()

        if self.task_ids:
            raise UserError(_("Tasks already exist for this close period. Delete existing tasks first."))

        # Get active templates
        templates = self.env['ppm.close.template'].search([('active', '=', True)])

        if not templates:
            raise UserError(_("No active task templates found. Please create templates first."))

        # Create tasks from templates
        created_tasks = self.env['ppm.close.task']
        for template in templates:
            task_vals = {
                'monthly_close_id': self.id,
                'template_id': template.id,
                'name': template.task_category,
                'detailed_task': template.detailed_task,
                'agency_code': template.agency_code,
                'owner_code': template.owner_code,
                'reviewer_code': template.reviewer_code,
                'approver_code': template.approver_code,
                'prep_days': template.prep_days,
                'review_days': template.review_days,
                'approval_days': template.approval_days,
                'sequence': template.sequence,
            }
            task = self.env['ppm.close.task'].create(task_vals)
            created_tasks |= task

        # Update state
        if self.state == 'draft':
            self.state = 'scheduled'

        # Log activity
        self.message_post(
            body=_("Generated %d tasks from templates") % len(created_tasks),
            subtype_xmlid='mail.mt_note'
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tasks Generated'),
                'message': _('%d tasks created successfully') % len(created_tasks),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_start_close(self):
        """Start the close process - send notifications."""
        self.ensure_one()
        self.state = 'in_progress'

        # Send notifications to all task owners
        for task in self.task_ids:
            task.action_notify_owner()

        self.message_post(
            body=_("Close process started. Notifications sent to all task owners."),
            subtype_xmlid='mail.mt_note'
        )

    def action_complete_close(self):
        """Mark close as completed."""
        self.ensure_one()

        # Verify all tasks are done
        pending_tasks = self.task_ids.filtered(lambda t: t.state != 'done')
        if pending_tasks:
            raise UserError(
                _("Cannot complete close. %d tasks are still pending:\n%s") % (
                    len(pending_tasks),
                    '\n'.join(pending_tasks.mapped('name'))
                )
            )

        self.state = 'done'
        self.message_post(
            body=_("Monthly close completed successfully!"),
            subtype_xmlid='mail.mt_note'
        )

    @api.model
    def cron_create_monthly_close(self):
        """
        Scheduled action to create next month's close schedule.

        Runs on the 3rd business day before month-end.
        Creates schedule for next month if it doesn't exist.
        """
        today = fields.Date.today()

        # Calculate next month
        next_month_start = (today + relativedelta(months=1)).replace(day=1)

        # Check if schedule already exists
        existing = self.search([
            ('close_month', '=', next_month_start)
        ], limit=1)

        if existing:
            _logger.info("Monthly close for %s already exists (ID: %s)",
                        next_month_start.strftime('%B %Y'), existing.id)
            return existing

        # Create new schedule
        new_close = self.create({
            'close_month': next_month_start,
            'created_by_cron': True,
        })

        # Generate tasks
        new_close.action_generate_tasks()

        _logger.info("Created monthly close for %s (ID: %s)",
                    next_month_start.strftime('%B %Y'), new_close.id)

        return new_close
