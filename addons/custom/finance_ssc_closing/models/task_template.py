# -*- coding: utf-8 -*-

from odoo import fields, models


class FinanceClosingTaskTemplate(models.Model):
    """
    Templates for common month-end closing tasks.
    Allows quick task generation from predefined templates.
    """

    _name = "finance.closing.task.template"
    _description = "Closing Task Template"
    _order = "sequence, name"

    name = fields.Char(string="Template Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Html(string="Description")
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
    )

    estimated_hours = fields.Float(string="Estimated Hours")
    priority = fields.Selection(
        [
            ("0", "Low"),
            ("1", "Normal"),
            ("2", "High"),
            ("3", "Urgent"),
        ],
        string="Priority",
        default="1",
    )

    department_id = fields.Many2one("hr.department", string="Default Department")
    days_to_complete = fields.Integer(string="Days to Complete", default=1)
    active = fields.Boolean(string="Active", default=True)
