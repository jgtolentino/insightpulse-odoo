from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    """Extend Purchase Order with approval workflow integration."""

    _inherit = "purchase.order"

    approval_request_id = fields.Many2one(
        "ipai.approval.request",
        string="Approval Request",
        readonly=True,
        copy=False,
        help="Current approval request for this purchase order",
    )
    approval_state = fields.Selection(
        related="approval_request_id.state",
        string="Approval Status",
        store=True,
    )
    requires_approval = fields.Boolean(
        compute="_compute_requires_approval",
        store=True,
        help="Whether this PO requires approval based on rules",
    )

    @api.depends("amount_total", "partner_id", "company_id")
    def _compute_requires_approval(self):
        """Determine if PO requires approval based on rules."""
        for order in self:
            # Get approval flow for purchase orders
            flow = self.env["ipai.approval.flow"].search(
                [
                    ("model_id.model", "=", "purchase.order"),
                    ("active", "=", True),
                ],
                limit=1,
            )

            if not flow:
                order.requires_approval = False
                continue

            # Check amount threshold (configurable via flow conditions)
            # Default: >100,000 requires approval
            threshold = 100000
            order.requires_approval = order.amount_total > threshold

    def action_submit_for_approval(self):
        """Submit purchase order for approval."""
        self.ensure_one()

        if not self.requires_approval:
            raise UserError(_("This purchase order does not require approval."))

        if self.approval_request_id:
            raise UserError(
                _("An approval request already exists for this purchase order.")
            )

        # Get approval flow
        flow = self.env["ipai.approval.flow"].search(
            [
                ("model_id.model", "=", "purchase.order"),
                ("active", "=", True),
            ],
            limit=1,
        )

        if not flow:
            raise UserError(
                _(
                    "No approval flow configured for purchase orders. "
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
            body=_("Purchase order submitted for approval."),
            subject=_("Approval Request Created"),
        )

        return True

    def action_approve_po(self):
        """Approve current stage of PO approval."""
        self.ensure_one()

        if not self.approval_request_id:
            raise UserError(_("No approval request found for this purchase order."))

        self.approval_request_id.action_approve()

        # If fully approved, confirm PO
        if self.approval_request_id.state == "approved":
            self.button_confirm()
            self.message_post(
                body=_("Purchase order approved and confirmed."),
                subject=_("Approval Completed"),
            )

        return True

    def action_reject_po(self):
        """Reject PO approval."""
        self.ensure_one()

        if not self.approval_request_id:
            raise UserError(_("No approval request found for this purchase order."))

        self.approval_request_id.action_reject()

        self.message_post(
            body=_("Purchase order approval rejected."),
            subject=_("Approval Rejected"),
        )

        return True

    def action_view_approval(self):
        """Open approval request form view."""
        self.ensure_one()

        if not self.approval_request_id:
            raise UserError(_("No approval request found for this purchase order."))

        return {
            "type": "ir.actions.act_window",
            "res_model": "ipai.approval.request",
            "res_id": self.approval_request_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def button_confirm(self):
        """Override to check approval requirement."""
        for order in self:
            if order.requires_approval and not order.approval_request_id:
                raise UserError(
                    _(
                        "This purchase order requires approval before confirmation. "
                        "Please submit for approval first."
                    )
                )

            if order.approval_request_id and order.approval_state != "approved":
                raise UserError(
                    _(
                        "This purchase order has not been approved yet. "
                        "Current status: %s"
                    )
                    % dict(
                        order.approval_request_id._fields["state"].selection
                    ).get(order.approval_state)
                )

        return super().button_confirm()
