from odoo.exceptions import UserError

from odoo import _, api, fields, models


class AccountMove(models.Model):
    """Extend Invoice with approval workflow integration."""

    _inherit = "account.move"

    approval_request_id = fields.Many2one(
        "ipai.approval.request",
        string="Approval Request",
        readonly=True,
        copy=False,
        help="Current approval request for this invoice",
    )
    approval_state = fields.Selection(
        related="approval_request_id.state",
        string="Approval Status",
        store=True,
    )
    requires_approval = fields.Boolean(
        compute="_compute_requires_approval",
        store=True,
        help="Whether this invoice requires approval based on rules",
    )

    @api.depends("amount_total", "partner_id", "company_id", "move_type")
    def _compute_requires_approval(self):
        """Determine if invoice requires approval based on rules."""
        for move in self:
            # Only apply to vendor bills
            if move.move_type not in ("in_invoice", "in_refund"):
                move.requires_approval = False
                continue

            # Get approval flow for invoices
            flow = self.env["ipai.approval.flow"].search(
                [
                    ("model_id.model", "=", "account.move"),
                    ("active", "=", True),
                ],
                limit=1,
            )

            if not flow:
                move.requires_approval = False
                continue

            # Check amount threshold (configurable via flow conditions)
            # Default: >50,000 requires approval
            threshold = 50000
            move.requires_approval = move.amount_total > threshold

    def action_submit_for_approval(self):
        """Submit invoice for approval."""
        self.ensure_one()

        if not self.requires_approval:
            raise UserError(_("This invoice does not require approval."))

        if self.approval_request_id:
            raise UserError(_("An approval request already exists for this invoice."))

        # Get approval flow
        flow = self.env["ipai.approval.flow"].search(
            [
                ("model_id.model", "=", "account.move"),
                ("active", "=", True),
            ],
            limit=1,
        )

        if not flow:
            raise UserError(
                _(
                    "No approval flow configured for invoices. "
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
            body=_("Invoice submitted for approval."),
            subject=_("Approval Request Created"),
        )

        return True

    def action_approve_invoice(self):
        """Approve current stage of invoice approval."""
        self.ensure_one()

        if not self.approval_request_id:
            raise UserError(_("No approval request found for this invoice."))

        self.approval_request_id.action_approve()

        # If fully approved, post invoice
        if self.approval_request_id.state == "approved":
            self.action_post()
            self.message_post(
                body=_("Invoice approved and posted."),
                subject=_("Approval Completed"),
            )

        return True

    def action_reject_invoice(self):
        """Reject invoice approval."""
        self.ensure_one()

        if not self.approval_request_id:
            raise UserError(_("No approval request found for this invoice."))

        self.approval_request_id.action_reject()

        self.message_post(
            body=_("Invoice approval rejected."),
            subject=_("Approval Rejected"),
        )

        return True

    def action_view_approval(self):
        """Open approval request form view."""
        self.ensure_one()

        if not self.approval_request_id:
            raise UserError(_("No approval request found for this invoice."))

        return {
            "type": "ir.actions.act_window",
            "res_model": "ipai.approval.request",
            "res_id": self.approval_request_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_post(self):
        """Override to check approval requirement."""
        for move in self:
            if (
                move.move_type in ("in_invoice", "in_refund")
                and move.requires_approval
                and not move.approval_request_id
            ):
                raise UserError(
                    _(
                        "This invoice requires approval before posting. "
                        "Please submit for approval first."
                    )
                )

            if move.approval_request_id and move.approval_state != "approved":
                raise UserError(
                    _("This invoice has not been approved yet. " "Current status: %s")
                    % dict(move.approval_request_id._fields["state"].selection).get(
                        move.approval_state
                    )
                )

        return super().action_post()
