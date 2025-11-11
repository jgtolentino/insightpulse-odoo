# -*- coding: utf-8 -*-

from odoo import fields, models


class HROffboardingChecklist(models.Model):
    """
    Clearance Checklist Items

    Individual clearance items that must be completed before employee exit.
    Each item is assigned to a responsible user from a specific department.
    """

    _name = "hr.offboarding.checklist"
    _description = "Offboarding Clearance Checklist Item"
    _order = "sequence, id"

    offboarding_id = fields.Many2one(
        "hr.offboarding",
        string="Offboarding",
        required=True,
        ondelete="cascade",
        index=True,
    )

    name = fields.Char(
        string="Item",
        required=True,
        help="Clearance item description (e.g., 'Return laptop and access card')",
    )

    department = fields.Selection(
        [
            ("it", "IT Department"),
            ("finance", "Finance Department"),
            ("admin", "Admin Department"),
            ("hr", "HR Department"),
        ],
        string="Department",
        required=True,
        index=True,
    )

    responsible_user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        required=True,
        help="User responsible for verifying this checklist item",
    )

    sequence = fields.Integer(string="Sequence", default=10)

    description = fields.Text(
        string="Description", help="Detailed instructions for completing this item"
    )

    completed = fields.Boolean(string="Completed", default=False, tracking=True)

    completed_date = fields.Datetime(string="Completion Date", readonly=True)

    completed_by_user_id = fields.Many2one(
        "res.users", string="Completed By", readonly=True
    )

    notes = fields.Text(
        string="Notes", help="Additional notes from the responsible user"
    )

    # ========================
    # Business Logic
    # ========================

    def action_mark_complete(self):
        """Mark checklist item as completed"""
        for record in self:
            record.write(
                {
                    "completed": True,
                    "completed_date": fields.Datetime.now(),
                    "completed_by_user_id": self.env.user.id,
                }
            )

            # Update offboarding state based on department
            record.offboarding_id._update_state_on_checklist_complete(record.department)

    def action_mark_incomplete(self):
        """Mark checklist item as incomplete"""
        for record in self:
            record.write(
                {
                    "completed": False,
                    "completed_date": False,
                    "completed_by_user_id": False,
                }
            )


class HROffboardingChecklistTemplate(models.Model):
    """
    Clearance Checklist Templates

    Pre-defined checklist item templates that are automatically created
    when a new offboarding record is initiated.
    """

    _name = "hr.offboarding.checklist.template"
    _description = "Offboarding Checklist Template"
    _order = "sequence, id"

    name = fields.Char(string="Item Name", required=True)

    department = fields.Selection(
        [
            ("it", "IT Department"),
            ("finance", "Finance Department"),
            ("admin", "Admin Department"),
            ("hr", "HR Department"),
        ],
        string="Department",
        required=True,
    )

    responsible_user_id = fields.Many2one(
        "res.users",
        string="Default Responsible",
        help="Default user responsible for this item (can be changed per offboarding)",
    )

    sequence = fields.Integer(string="Sequence", default=10)

    description = fields.Text(string="Description")

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        help="If set, template only applies to this company. If blank, applies to all companies.",
    )

    active = fields.Boolean(string="Active", default=True)
