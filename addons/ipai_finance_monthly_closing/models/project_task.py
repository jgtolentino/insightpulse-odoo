# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    # Closing clusters
    cluster = fields.Selection(
        [
            ("A", "Cluster A – Foundation"),
            ("B", "Cluster B – Revenue / WIP / Interco"),
            ("C", "Cluster C – VAT & Tax"),
            ("D", "Cluster D – WC & Reporting"),
        ],
        string="Cluster",
    )

    relative_due = fields.Char(
        string="Relative Due",
        help="Relative to month-end, e.g. M-5, M-3, M+2.",
    )

    closing_due_date = fields.Date(
        string="Closing Due Date",
        help="Concrete due date for this closing task.",
    )

    owner_code = fields.Char(
        string="Owner Code",
        help="Short code like CKVC, RIM, LAS.",
    )

    reviewer_id = fields.Many2one(
        "res.users",
        string="Reviewer",
        help="Person who reviews completion of this task.",
    )

    approver_id = fields.Many2one(
        "res.users",
        string="Approver",
        help="Person who gives final approval for this task.",
    )

    erp_ref = fields.Char(
        string="ERP Reference",
        help="ID/reference from Spectra or other ERP once synced.",
    )

    auto_sync = fields.Boolean(
        string="Auto Sync to ERP",
        default=False,
        help="If enabled, task is eligible for n8n/agent-driven sync.",
    )

    # BIR-related fields
    bir_related = fields.Boolean(
        string="BIR Related Task",
        default=False,
    )

    bir_form = fields.Selection(
        [
            ("1601C", "1601-C"),
            ("0619E", "0619-E"),
            ("1601EQ", "1601-EQ"),
            ("2550M", "2550M"),
            ("2550Q", "2550Q"),
            ("1702Q", "1702Q"),
        ],
        string="BIR Form",
    )

    bir_period_label = fields.Char(
        string="BIR Period",
        help="Human label e.g. Dec 2025, Q4 2025.",
    )

    bir_deadline = fields.Date(string="BIR Filing Deadline")
    bir_prep_due_date = fields.Date(string="Preparation Due Date")
    bir_approval_due_date = fields.Date(string="Approval Due Date")
    bir_payment_due_date = fields.Date(string="Payment Due Date")

    finance_supervisor_id = fields.Many2one(
        "res.users",
        string="Finance Supervisor",
    )

    sfm_id = fields.Many2one(
        "res.users",
        string="Senior Finance Manager",
    )

    fd_id = fields.Many2one(
        "res.users",
        string="Finance Director",
    )
