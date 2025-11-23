from odoo import models, fields, api
from datetime import datetime, timedelta, date
import logging

_logger = logging.getLogger(__name__)


class FinanceLogframe(models.Model):
    """TBWA Finance Logical Framework Model"""

    _name = "ipai.finance.logframe"
    _description = "Finance Logical Framework"
    _order = "level, sequence, id"

    level = fields.Selection([
        ("goal", "Goal"),
        ("outcome", "Outcome"),
        ("im1", "Immediate Objective 1"),
        ("im2", "Immediate Objective 2"),
        ("output", "Output"),
        ("activity_im1", "Activity (IM1)"),
        ("activity_im2", "Activity (IM2)"),
    ], string="Level", required=True, help="Hierarchical level in logical framework")

    code = fields.Char(string="Code", help="Short code identifier (e.g., IM2, OUT1)")
    name = fields.Char(string="Objective / Description", required=True)
    sequence = fields.Integer(string="Sequence", default=10)

    # Logical framework components
    indicators = fields.Text(string="Indicators", help="Objectively verifiable indicators")
    means_of_verification = fields.Text(string="Means of Verification (MoV)",
                                       help="How indicators will be measured")
    assumptions = fields.Text(string="Assumptions",
                             help="External factors affecting success")

    # Relationships
    task_ids = fields.One2many("project.task", "finance_logframe_id",
                              string="Linked Tasks")
    bir_schedule_ids = fields.One2many("ipai.finance.bir_schedule", "logframe_id",
                                      string="BIR Schedules")

    # Computed fields
    task_count = fields.Integer(string="Task Count", compute="_compute_task_count", store=True)

    @api.depends("task_ids")
    def _compute_task_count(self):
        for record in self:
            record.task_count = len(record.task_ids)


class FinanceBIRSchedule(models.Model):
    """BIR Filing Schedule with Multi-Step Deadlines"""

    _name = "ipai.finance.bir_schedule"
    _description = "BIR Filing Schedule"
    _order = "filing_deadline desc, id desc"

    name = fields.Char(string="Schedule Name", required=True,
                      help="e.g., '1601-C (Compensation) – Dec 2025'")
    period_covered = fields.Char(string="Period Covered", help="e.g., 'Dec 2025'")

    # Deadlines (in descending order: filing → approval → review → prep)
    filing_deadline = fields.Date(string="BIR Filing Deadline", required=True)
    prep_deadline = fields.Date(string="Preparation Deadline",
                               help="Filing deadline - 4 business days")
    review_deadline = fields.Date(string="Review Deadline",
                                  help="Filing deadline - 2 business days")
    approval_deadline = fields.Date(string="Approval Deadline",
                                   help="Filing deadline - 1 business day")

    # Assignees
    supervisor_id = fields.Many2one("res.users", string="Supervisor")
    reviewer_id = fields.Many2one("res.users", string="Reviewer")
    approver_id = fields.Many2one("res.users", string="Approver")

    # Status tracking
    status = fields.Selection([
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("submitted", "Submitted"),
        ("filed", "Filed & Paid"),
        ("late", "Late"),
    ], string="Status", default="not_started", required=True)

    completion_pct = fields.Float(string="Completion %", default=0.0)

    # Link to logframe
    logframe_id = fields.Many2one("ipai.finance.logframe", string="Logframe Entry",
                                  help="Link to IM2 Tax Filing Compliance")

    # Task references
    prep_task_id = fields.Many2one("project.task", string="Preparation Task")
    review_task_id = fields.Many2one("project.task", string="Review Task")
    approval_task_id = fields.Many2one("project.task", string="Approval Task")

    @api.model
    def _cron_sync_bir_tasks(self):
        """
        Scheduled cron job (daily 8 AM) to create/update project.task records
        for each BIR schedule entry.

        Creates 3 tasks per BIR schedule:
        1. Preparation task (assigned to supervisor)
        2. Review task (assigned to reviewer)
        3. Approval task (assigned to approver)
        """
        _logger.info("Starting BIR task sync cron job")

        # Get default project for Finance tasks
        project = self.env["project.project"].search([
            ("name", "=", "TBWA Finance – Month-End & BIR")
        ], limit=1)

        if not project:
            _logger.warning("Project 'TBWA Finance – Month-End & BIR' not found. Creating...")
            project = self.env["project.project"].create({
                "name": "TBWA Finance – Month-End & BIR",
            })

        schedules = self.search([("status", "!=", "filed")])
        _logger.info(f"Found {len(schedules)} active BIR schedules to sync")

        for schedule in schedules:
            self._create_or_update_tasks(schedule, project)

        _logger.info("BIR task sync cron job completed")

    def _create_or_update_tasks(self, schedule, project):
        """Create or update the 3 tasks for a BIR schedule"""

        # Task 1: Preparation
        if not schedule.prep_task_id:
            prep_task = self.env["project.task"].create({
                "name": f"{schedule.name} – Preparation",
                "project_id": project.id,
                "finance_logframe_id": schedule.logframe_id.id if schedule.logframe_id else False,
                "date_deadline": schedule.prep_deadline,
                "user_ids": [(6, 0, [schedule.supervisor_id.id])] if schedule.supervisor_id else False,
                "description": f"Prepare data and forms for {schedule.name}",
            })
            schedule.prep_task_id = prep_task.id
            _logger.info(f"Created prep task for {schedule.name}")
        else:
            schedule.prep_task_id.write({
                "date_deadline": schedule.prep_deadline,
                "user_ids": [(6, 0, [schedule.supervisor_id.id])] if schedule.supervisor_id else False,
            })

        # Task 2: Review
        if not schedule.review_task_id:
            review_task = self.env["project.task"].create({
                "name": f"{schedule.name} – Review",
                "project_id": project.id,
                "finance_logframe_id": schedule.logframe_id.id if schedule.logframe_id else False,
                "date_deadline": schedule.review_deadline,
                "user_ids": [(6, 0, [schedule.reviewer_id.id])] if schedule.reviewer_id else False,
                "description": f"Review and validate forms for {schedule.name}",
            })
            schedule.review_task_id = review_task.id
            _logger.info(f"Created review task for {schedule.name}")
        else:
            schedule.review_task_id.write({
                "date_deadline": schedule.review_deadline,
                "user_ids": [(6, 0, [schedule.reviewer_id.id])] if schedule.reviewer_id else False,
            })

        # Task 3: Approval
        if not schedule.approval_task_id:
            approval_task = self.env["project.task"].create({
                "name": f"{schedule.name} – Approval",
                "project_id": project.id,
                "finance_logframe_id": schedule.logframe_id.id if schedule.logframe_id else False,
                "date_deadline": schedule.approval_deadline,
                "user_ids": [(6, 0, [schedule.approver_id.id])] if schedule.approver_id else False,
                "description": f"Final approval and submission for {schedule.name}",
            })
            schedule.approval_task_id = approval_task.id
            _logger.info(f"Created approval task for {schedule.name}")
        else:
            schedule.approval_task_id.write({
                "date_deadline": schedule.approval_deadline,
                "user_ids": [(6, 0, [schedule.approver_id.id])] if schedule.approver_id else False,
            })

        # Update completion percentage based on task states
        completed = 0
        total = 3
        if schedule.prep_task_id and schedule.prep_task_id.stage_id.fold:
            completed += 1
        if schedule.review_task_id and schedule.review_task_id.stage_id.fold:
            completed += 1
        if schedule.approval_task_id and schedule.approval_task_id.stage_id.fold:
            completed += 1

        schedule.completion_pct = (completed / total) * 100

        # Update status based on completion
        if schedule.completion_pct == 100:
            schedule.status = "filed"
        elif schedule.completion_pct > 0:
            schedule.status = "in_progress"
        elif schedule.filing_deadline < date.today():
            schedule.status = "late"


class ProjectTask(models.Model):
    """Extend project.task to link to finance logframe"""

    _inherit = "project.task"

    finance_logframe_id = fields.Many2one("ipai.finance.logframe",
                                         string="Finance Logframe",
                                         help="Link to logical framework entry")
