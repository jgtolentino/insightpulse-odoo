# -*- coding: utf-8 -*-

from odoo.exceptions import UserError

from odoo import _, api, fields, models


class FinanceClosingTask(models.Model):
    """
    Individual month-end closing task.
    Notion equivalent: Database item/row in a closing checklist database.
    """

    _name = "finance.closing.task"
    _description = "Month-End Closing Task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, due_date, id"

    # Basic Information
    name = fields.Char(string="Task Name", required=True, tracking=True)
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Html(string="Description")

    # Period & Company
    period_id = fields.Many2one(
        "finance.closing.period",
        string="Closing Period",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Agency/Company",
        required=True,
        default=lambda self: self.env.company,
        help="Agency: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB",
    )

    # Task Type
    task_type = fields.Selection(
        [
            ("journal_entry", "Journal Entry"),
            ("bank_recon", "Bank Reconciliation"),
            ("ar_review", "AR Aging Review"),
            ("ap_review", "AP Aging Review"),
            ("inventory_count", "Inventory Count"),
            ("depreciation", "Depreciation Calculation"),
            ("accruals", "Accruals & Prepayments"),
            ("intercompany_recon", "Intercompany Reconciliation"),
            ("trial_balance", "Trial Balance Review"),
            ("financial_statements", "Financial Statements Preparation"),
            ("variance_analysis", "Variance Analysis"),
            ("bir_filing", "BIR Tax Filing"),
            ("other", "Other"),
        ],
        string="Task Type",
        required=True,
        tracking=True,
    )

    # Assignment
    assigned_to = fields.Many2one(
        "res.users", string="Assigned To", tracking=True, index=True
    )
    department_id = fields.Many2one("hr.department", string="Department", tracking=True)

    # Dates
    due_date = fields.Date(string="Due Date", required=True, tracking=True)
    start_date = fields.Date(string="Start Date", tracking=True)
    completed_date = fields.Date(string="Completed Date", tracking=True)

    # Status
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("review", "Under Review"),
            ("completed", "Completed"),
            ("blocked", "Blocked"),
        ],
        string="Status",
        default="pending",
        required=True,
        tracking=True,
        index=True,
    )

    # Progress
    progress = fields.Integer(
        string="Progress (%)", default=0, help="Manual progress tracking (0-100%)"
    )

    # Priority
    priority = fields.Selection(
        [
            ("0", "Low"),
            ("1", "Normal"),
            ("2", "High"),
            ("3", "Urgent"),
        ],
        string="Priority",
        default="1",
        tracking=True,
    )

    # Review
    reviewer_id = fields.Many2one("res.users", string="Reviewer", tracking=True)
    review_notes = fields.Html(string="Review Notes")

    # Attachments
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "closing_task_attachment_rel",
        "task_id",
        "attachment_id",
        string="Attachments",
    )
    attachment_count = fields.Integer(
        string="Attachment Count", compute="_compute_attachment_count"
    )

    # Dependencies
    depends_on_ids = fields.Many2many(
        "finance.closing.task",
        "closing_task_dependency_rel",
        "task_id",
        "depends_on_id",
        string="Depends On",
        help="Tasks that must be completed before this task can start",
    )
    blocked_by_count = fields.Integer(
        string="Blocked By", compute="_compute_dependency_status"
    )
    blocks_count = fields.Integer(string="Blocks", compute="_compute_dependency_status")

    # Timing
    estimated_hours = fields.Float(
        string="Estimated Hours", help="Estimated time to complete the task"
    )
    actual_hours = fields.Float(
        string="Actual Hours", help="Actual time spent on the task"
    )

    # Archive
    active = fields.Boolean(string="Active", default=True)

    # Notes
    notes = fields.Html(string="Work Notes")

    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        """Compute the number of attachments"""
        for task in self:
            task.attachment_count = len(task.attachment_ids)

    @api.depends("depends_on_ids", "depends_on_ids.state")
    def _compute_dependency_status(self):
        """Compute dependency status"""
        for task in self:
            # Count how many tasks this task depends on (and are not completed)
            task.blocked_by_count = len(
                task.depends_on_ids.filtered(lambda t: t.state != "completed")
            )

            # Count how many tasks depend on this task
            blocking_tasks = self.search([("depends_on_ids", "in", task.id)])
            task.blocks_count = len(blocking_tasks)

    @api.onchange("state")
    def _onchange_state(self):
        """Update dates based on state changes"""
        if self.state == "in_progress" and not self.start_date:
            self.start_date = fields.Date.today()
        elif self.state == "completed":
            self.completed_date = fields.Date.today()
            self.progress = 100

    def action_start(self):
        """Start the task"""
        for task in self:
            if task.state != "pending":
                raise UserError(_("Only pending tasks can be started."))

            # Check dependencies
            if task.blocked_by_count > 0:
                raise UserError(
                    _(
                        "This task depends on %d incomplete task(s). "
                        "Please complete those tasks first."
                    )
                    % task.blocked_by_count
                )

            task.write(
                {
                    "state": "in_progress",
                    "start_date": fields.Date.today(),
                }
            )
            task.message_post(body=_("Task started."))

    def action_submit_for_review(self):
        """Submit task for review"""
        for task in self:
            if task.state != "in_progress":
                raise UserError(
                    _("Only in-progress tasks can be submitted for review.")
                )
            if not task.reviewer_id:
                raise UserError(_("Please assign a reviewer before submitting."))

            task.write({"state": "review"})
            task.message_post(body=_("Task submitted for review."))

            # Create activity for reviewer
            task.activity_schedule(
                "finance_ssc_closing.mail_act_task_review",
                user_id=task.reviewer_id.id,
                summary=_("Review Task: %s") % task.name,
            )

    def action_approve(self):
        """Approve and complete the task"""
        for task in self:
            if task.state != "review":
                raise UserError(_("Only tasks under review can be approved."))

            task.write(
                {
                    "state": "completed",
                    "completed_date": fields.Date.today(),
                    "progress": 100,
                }
            )
            task.message_post(body=_("Task approved and completed."))

    def action_reject(self):
        """Reject the task and send back to in-progress"""
        for task in self:
            if task.state != "review":
                raise UserError(_("Only tasks under review can be rejected."))

            task.write({"state": "in_progress"})
            task.message_post(
                body=_("Task rejected. Please address the review comments.")
            )

    def action_block(self):
        """Block the task"""
        for task in self:
            task.write({"state": "blocked"})
            task.message_post(body=_("Task blocked."))

    def action_unblock(self):
        """Unblock the task"""
        for task in self:
            if task.state != "blocked":
                raise UserError(_("Only blocked tasks can be unblocked."))

            task.write({"state": "pending"})
            task.message_post(body=_("Task unblocked."))

    def action_view_attachments(self):
        """View task attachments"""
        self.ensure_one()
        return {
            "name": _("Attachments"),
            "type": "ir.actions.act_window",
            "res_model": "ir.attachment",
            "view_mode": "kanban,tree,form",
            "domain": [("id", "in", self.attachment_ids.ids)],
            "context": {
                "default_res_model": self._name,
                "default_res_id": self.id,
            },
        }

    @api.model
    def _cron_send_overdue_reminders(self):
        """
        Cron job to send reminders for overdue tasks
        Scheduled to run daily
        """
        today = fields.Date.today()
        overdue_tasks = self.search(
            [
                ("state", "in", ("pending", "in_progress")),
                ("due_date", "<", today),
            ]
        )

        for task in overdue_tasks:
            if task.assigned_to:
                task.activity_schedule(
                    "finance_ssc_closing.mail_act_task_overdue",
                    user_id=task.assigned_to.id,
                    summary=_("Overdue Task: %s") % task.name,
                )
