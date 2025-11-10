# -*- coding: utf-8 -*-

from odoo.exceptions import UserError

from odoo import _, api, fields, models


class FinanceClosingPeriod(models.Model):
    """
    Represents a month-end closing period for Finance SSC operations.
    This model manages the overall closing workflow for a specific period.
    """

    _name = "finance.closing.period"
    _description = "Month-End Closing Period"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_date desc"

    # Basic Information
    name = fields.Char(
        string="Period Name",
        required=True,
        tracking=True,
        help="e.g., 2025-01 for January 2025",
    )
    start_date = fields.Date(string="Start Date", required=True, tracking=True)
    end_date = fields.Date(string="End Date", required=True, tracking=True)
    fiscal_year = fields.Char(string="Fiscal Year", required=True, tracking=True)

    # State Management
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("review", "Under Review"),
            ("approved", "Approved"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )

    # Tasks
    task_ids = fields.One2many(
        "finance.closing.task", "period_id", string="Closing Tasks"
    )
    task_count = fields.Integer(
        string="Total Tasks", compute="_compute_task_statistics", store=True
    )
    task_completed_count = fields.Integer(
        string="Completed Tasks", compute="_compute_task_statistics", store=True
    )
    task_pending_count = fields.Integer(
        string="Pending Tasks", compute="_compute_task_statistics", store=True
    )
    completion_percentage = fields.Float(
        string="Completion %", compute="_compute_task_statistics", store=True
    )

    # BIR Compliance
    bir_task_ids = fields.One2many(
        "finance.bir.compliance.task", "period_id", string="BIR Compliance Tasks"
    )
    bir_all_filed = fields.Boolean(
        string="All BIR Forms Filed", compute="_compute_bir_status", store=True
    )

    # Ownership
    responsible_id = fields.Many2one(
        "res.users",
        string="Responsible",
        default=lambda self: self.env.user,
        tracking=True,
    )
    reviewer_ids = fields.Many2many(
        "res.users",
        "closing_period_reviewer_rel",
        "period_id",
        "user_id",
        string="Reviewers",
    )

    # Dates
    actual_close_date = fields.Date(string="Actual Close Date", tracking=True)
    approved_date = fields.Date(string="Approved Date", tracking=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By")

    # Notes
    notes = fields.Html(string="Notes")

    # Constraints
    _sql_constraints = [
        ("name_unique", "unique(name)", "Period name must be unique!"),
        (
            "date_check",
            "check(end_date >= start_date)",
            "End date must be after start date!",
        ),
    ]

    @api.depends("task_ids", "task_ids.state")
    def _compute_task_statistics(self):
        """Compute task statistics for the period"""
        for period in self:
            tasks = period.task_ids
            period.task_count = len(tasks)
            period.task_completed_count = len(
                tasks.filtered(lambda t: t.state == "completed")
            )
            period.task_pending_count = len(
                tasks.filtered(lambda t: t.state in ("pending", "in_progress"))
            )

            if period.task_count > 0:
                period.completion_percentage = (
                    period.task_completed_count / period.task_count
                ) * 100
            else:
                period.completion_percentage = 0.0

    @api.depends("bir_task_ids", "bir_task_ids.state")
    def _compute_bir_status(self):
        """Check if all BIR forms are filed"""
        for period in self:
            bir_tasks = period.bir_task_ids
            if bir_tasks:
                period.bir_all_filed = all(task.state == "filed" for task in bir_tasks)
            else:
                period.bir_all_filed = False

    def action_open(self):
        """Open the period for task creation"""
        for period in self:
            if period.state != "draft":
                raise UserError(_("Only draft periods can be opened."))
            period.write({"state": "open"})
            period.message_post(body=_("Period opened for task creation."))

    def action_start_closing(self):
        """Start the closing process"""
        for period in self:
            if period.state != "open":
                raise UserError(_("Only open periods can be started."))
            if not period.task_ids:
                raise UserError(
                    _(
                        "Please create closing tasks before starting the closing process."
                    )
                )

            period.write({"state": "in_progress"})
            period.message_post(body=_("Closing process started."))

            # Send notifications to assignees
            period._send_start_notifications()

    def action_submit_for_review(self):
        """Submit period for review"""
        for period in self:
            if period.state != "in_progress":
                raise UserError(
                    _("Only in-progress periods can be submitted for review.")
                )
            if period.completion_percentage < 100:
                raise UserError(
                    _("All tasks must be completed before submitting for review.")
                )

            period.write({"state": "review"})
            period.message_post(body=_("Period submitted for review."))

            # Send notifications to reviewers
            period._send_review_notifications()

    def action_approve(self):
        """Approve the period"""
        for period in self:
            if period.state != "review":
                raise UserError(_("Only periods under review can be approved."))

            period.write(
                {
                    "state": "approved",
                    "approved_date": fields.Date.today(),
                    "approved_by_id": self.env.user.id,
                }
            )
            period.message_post(body=_("Period approved by %s.") % self.env.user.name)

    def action_close(self):
        """Close the period"""
        for period in self:
            if period.state != "approved":
                raise UserError(_("Only approved periods can be closed."))

            period.write(
                {
                    "state": "closed",
                    "actual_close_date": fields.Date.today(),
                }
            )
            period.message_post(body=_("Period closed."))

            # Archive completed tasks
            period.task_ids.write({"active": False})

    def action_reopen(self):
        """Reopen a closed period"""
        for period in self:
            if period.state != "closed":
                raise UserError(_("Only closed periods can be reopened."))

            period.write(
                {
                    "state": "in_progress",
                    "actual_close_date": False,
                    "approved_date": False,
                    "approved_by_id": False,
                }
            )
            period.message_post(body=_("Period reopened."))

            # Reactivate tasks
            period.task_ids.write({"active": True})

    def action_generate_tasks(self):
        """Open wizard to generate tasks from templates"""
        return {
            "name": _("Generate Closing Tasks"),
            "type": "ir.actions.act_window",
            "res_model": "finance.closing.generate.tasks.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_period_id": self.id,
            },
        }

    def _send_start_notifications(self):
        """Send notifications when closing process starts"""
        for period in self:
            assignees = period.task_ids.mapped("assigned_to")
            for user in assignees:
                period.activity_schedule(
                    "finance_ssc_closing.mail_act_closing_started",
                    user_id=user.id,
                    summary=_("Month-End Closing Started: %s") % period.name,
                )

    def _send_review_notifications(self):
        """Send notifications to reviewers"""
        for period in self:
            for reviewer in period.reviewer_ids:
                period.activity_schedule(
                    "finance_ssc_closing.mail_act_closing_review",
                    user_id=reviewer.id,
                    summary=_("Review Month-End Closing: %s") % period.name,
                )

    @api.model
    def _cron_send_deadline_reminders(self):
        """
        Cron job to send reminders for approaching deadlines
        Scheduled to run daily
        """
        today = fields.Date.today()
        periods = self.search(
            [
                ("state", "in", ("open", "in_progress")),
                ("end_date", ">=", today),
            ]
        )

        for period in periods:
            days_remaining = (period.end_date - today).days

            if days_remaining in (
                7,
                3,
                1,
            ):  # Send reminders at 7, 3, and 1 day before deadline
                period.message_post(
                    body=_("Reminder: %d days remaining until closing deadline.")
                    % days_remaining,
                    subject=_("Closing Deadline Reminder: %s") % period.name,
                )
