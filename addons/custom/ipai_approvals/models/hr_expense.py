from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrExpense(models.Model):
    """Extend Expense with approval workflow integration."""

    _inherit = "hr.expense"

    approval_request_id = fields.Many2one(
        "ipai.approval.request",
        string="Approval Request",
        readonly=True,
        copy=False,
        help="Current approval request for this expense",
    )
    approval_state = fields.Selection(
        related="approval_request_id.state",
        string="Approval Status",
        store=True,
    )


class HrExpenseSheet(models.Model):
    """Extend Expense Sheet with approval workflow integration."""

    _inherit = "hr.expense.sheet"

    approval_request_id = fields.Many2one(
        "ipai.approval.request",
        string="Approval Request",
        readonly=True,
        copy=False,
        help="Current approval request for this expense sheet",
    )
    approval_state = fields.Selection(
        related="approval_request_id.state",
        string="Approval Status",
        store=True,
    )
    requires_approval = fields.Boolean(
        compute="_compute_requires_approval",
        store=True,
        help="Whether this expense sheet requires approval based on rules",
    )

    @api.depends("total_amount", "employee_id", "company_id")
    def _compute_requires_approval(self):
        """Determine if expense sheet requires approval based on rules."""
        for sheet in self:
            # Get approval flow for expense sheets
            flow = self.env["ipai.approval.flow"].search(
                [
                    ("model_id.model", "=", "hr.expense.sheet"),
                    ("active", "=", True),
                ],
                limit=1,
            )

            if not flow:
                sheet.requires_approval = False
                continue

            # Check amount threshold (configurable via flow conditions)
            # Default: >10,000 requires approval
            threshold = 10000
            sheet.requires_approval = sheet.total_amount > threshold

    def action_submit_for_approval(self):
        """Submit expense sheet for approval."""
        self.ensure_one()

        if not self.requires_approval:
            raise UserError(_("This expense sheet does not require approval."))

        if self.approval_request_id:
            raise UserError(
                _("An approval request already exists for this expense sheet.")
            )

        # Get approval flow
        flow = self.env["ipai.approval.flow"].search(
            [
                ("model_id.model", "=", "hr.expense.sheet"),
                ("active", "=", True),
            ],
            limit=1,
        )

        if not flow:
            raise UserError(
                _(
                    "No approval flow configured for expense sheets. "
                    "Please contact your administrator."
                )
            )

        # Create approval request
        approval_request = self.env["ipai.approval.request"].create(
            {
                "flow_id": flow.id,
                "res_id": self.id,
            }
        )

        self.approval_request_id = approval_request

        # Submit for approval
        approval_request.action_submit()

        self.message_post(
            body=_("Expense sheet submitted for approval."),
            subject=_("Approval Request Created"),
        )

        return True

    def action_approve_expense(self):
        """Approve current stage of expense approval."""
        self.ensure_one()

        if not self.approval_request_id:
            raise UserError(_("No approval request found for this expense sheet."))

        self.approval_request_id.action_approve()

        # If fully approved, approve expense sheet
        if self.approval_request_id.state == "approved":
            self.approve_expense_sheets()
            self.message_post(
                body=_("Expense sheet approved."),
                subject=_("Approval Completed"),
            )

        return True

    def action_reject_expense(self):
        """Reject expense approval."""
        self.ensure_one()

        if not self.approval_request_id:
            raise UserError(_("No approval request found for this expense sheet."))

        self.approval_request_id.action_reject()

        self.message_post(
            body=_("Expense sheet approval rejected."),
            subject=_("Approval Rejected"),
        )

        return True

    def action_view_approval(self):
        """Open approval request form view."""
        self.ensure_one()

        if not self.approval_request_id:
            raise UserError(_("No approval request found for this expense sheet."))

        return {
            "type": "ir.actions.act_window",
            "res_model": "ipai.approval.request",
            "res_id": self.approval_request_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def approve_expense_sheets(self):
        """Override to check approval requirement."""
        for sheet in self:
            if sheet.requires_approval and not sheet.approval_request_id:
                raise UserError(
                    _(
                        "This expense sheet requires approval before confirmation. "
                        "Please submit for approval first."
                    )
                )

            if sheet.approval_request_id and sheet.approval_state != "approved":
                raise UserError(
                    _(
                        "This expense sheet has not been approved yet. "
                        "Current status: %s"
                    )
                    % dict(
                        sheet.approval_request_id._fields["state"].selection
                    ).get(sheet.approval_state)
                )

        return super().approve_expense_sheets()
