from odoo.exceptions import UserError, ValidationError

from odoo import _, api, fields, models


class ApprovalFlow(models.Model):
    """Generic approval workflow template that can be attached to any model."""

    _name = "ipai.approval.flow"
    _description = "Approval Workflow Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, index=True, tracking=True)
    model_id = fields.Many2one(
        "ir.model",
        string="Applied To Model",
        required=True,
        ondelete="cascade",
        help="The model this approval flow applies to",
    )
    model_name = fields.Char(related="model_id.model", store=True, index=True)
    active = fields.Boolean(default=True)
    description = fields.Text()

    stage_ids = fields.One2many(
        "ipai.approval.stage", "flow_id", string="Approval Stages", copy=True
    )
    request_ids = fields.One2many(
        "ipai.approval.request", "flow_id", string="Approval Requests"
    )

    # Configuration
    parallel_execution = fields.Boolean(
        default=False,
        help="If True, all approvers in a stage must approve. "
        "If False, any one approver is sufficient.",
    )
    auto_escalate = fields.Boolean(
        default=True, help="Automatically escalate if stage timeout exceeded"
    )
    default_timeout_hours = fields.Integer(
        default=48, help="Default timeout hours for stages without explicit timeout"
    )

    # Statistics
    request_count = fields.Integer(compute="_compute_request_count", store=False)
    avg_approval_hours = fields.Float(compute="_compute_avg_approval_hours")

    @api.depends("request_ids")
    def _compute_request_count(self):
        for flow in self:
            flow.request_count = len(flow.request_ids)

    @api.depends("request_ids.duration_hours")
    def _compute_avg_approval_hours(self):
        for flow in self:
            completed_requests = flow.request_ids.filtered(
                lambda r: r.state == "approved"
            )
            if completed_requests:
                flow.avg_approval_hours = sum(
                    completed_requests.mapped("duration_hours")
                ) / len(completed_requests)
            else:
                flow.avg_approval_hours = 0.0

    @api.constrains("stage_ids")
    def _check_stage_sequence(self):
        for flow in self:
            if not flow.stage_ids:
                raise ValidationError(_("Approval flow must have at least one stage."))


class ApprovalStage(models.Model):
    """Individual stage in an approval workflow."""

    _name = "ipai.approval.stage"
    _description = "Approval Stage"
    _order = "sequence, id"

    flow_id = fields.Many2one(
        "ipai.approval.flow", required=True, ondelete="cascade", index=True
    )
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10, help="Execution order of stages")

    # Actors
    approver_ids = fields.Many2many(
        "res.users",
        relation="approval_stage_user_rel",
        column1="stage_id",
        column2="user_id",
        string="Approvers",
        help="Users who can approve this stage",
    )
    approver_group_ids = fields.Many2many(
        "res.groups",
        relation="approval_stage_group_rel",
        column1="stage_id",
        column2="group_id",
        string="Approver Groups",
        help="Groups whose members can approve this stage",
    )

    # Configuration
    timeout_hours = fields.Integer(
        help="Hours before escalation. Leave empty to use flow default."
    )
    escalation_user_id = fields.Many2one(
        "res.users",
        string="Escalation User",
        help="User to notify if timeout exceeded",
    )
    escalation_action = fields.Selection(
        [
            ("notify", "Notify Only"),
            ("auto_approve", "Auto Approve"),
            ("reject", "Auto Reject"),
        ],
        default="notify",
        required=True,
        help="Action to take on timeout",
    )

    # Conditions
    condition_field_id = fields.Many2one(
        "ir.model.fields",
        string="Condition Field",
        domain="[('model_id', '=', parent.model_id)]",
        help="Field to evaluate for stage activation",
    )
    condition_operator = fields.Selection(
        [
            ("=", "Equal"),
            ("!=", "Not Equal"),
            (">", "Greater Than"),
            ("<", "Less Than"),
            (">=", "Greater or Equal"),
            ("<=", "Less or Equal"),
            ("in", "In List"),
            ("not in", "Not In List"),
        ],
        help="Comparison operator for condition",
    )
    condition_value = fields.Char(help="Value to compare against")

    @api.constrains("approver_ids", "approver_group_ids")
    def _check_approvers(self):
        for stage in self:
            if not stage.approver_ids and not stage.approver_group_ids:
                raise ValidationError(
                    _("Stage '%s' must have at least one approver or approver group.")
                    % stage.name
                )

    def get_approvers(self):
        """Get all users who can approve this stage."""
        self.ensure_one()
        approvers = self.approver_ids
        for group in self.approver_group_ids:
            approvers |= group.users
        return approvers.sorted("name")


class ApprovalRequest(models.Model):
    """Approval request instance for a specific record."""

    _name = "ipai.approval.request"
    _description = "Approval Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(compute="_compute_name", store=True)
    flow_id = fields.Many2one(
        "ipai.approval.flow", required=True, ondelete="restrict", index=True
    )
    model_id = fields.Many2one(related="flow_id.model_id", store=True)
    model_name = fields.Char(related="flow_id.model_name", store=True, index=True)

    # Record reference
    res_id = fields.Integer(string="Record ID", required=True, index=True)
    res_model_id = fields.Many2one("ir.model", related="flow_id.model_id")

    # State
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    current_stage_id = fields.Many2one(
        "ipai.approval.stage", string="Current Stage", tracking=True
    )

    # Logs
    log_ids = fields.One2many("ipai.approval.log", "request_id", string="Approval Log")

    # Metrics
    create_date = fields.Datetime(readonly=True, index=True)
    start_date = fields.Datetime(readonly=True)
    complete_date = fields.Datetime(readonly=True)
    duration_hours = fields.Float(
        compute="_compute_duration_hours", store=True, help="Total approval duration"
    )

    @api.depends("flow_id", "res_id")
    def _compute_name(self):
        for request in self:
            if request.flow_id and request.res_id:
                request.name = f"{request.flow_id.name} - {request.res_id}"
            else:
                request.name = "New Approval Request"

    @api.depends("start_date", "complete_date")
    def _compute_duration_hours(self):
        for request in self:
            if request.start_date and request.complete_date:
                delta = request.complete_date - request.start_date
                request.duration_hours = delta.total_seconds() / 3600
            else:
                request.duration_hours = 0.0

    def action_submit(self):
        """Submit request for approval."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Only draft requests can be submitted."))

        # Get first stage
        first_stage = self.flow_id.stage_ids.sorted("sequence")[0]
        if not first_stage:
            raise UserError(_("Approval flow has no stages defined."))

        self.write(
            {
                "state": "pending",
                "current_stage_id": first_stage.id,
                "start_date": fields.Datetime.now(),
            }
        )

        # Create log entry
        self.env["ipai.approval.log"].create(
            {
                "request_id": self.id,
                "stage_id": first_stage.id,
                "user_id": self.env.user.id,
                "action": "submit",
                "notes": "Request submitted for approval",
            }
        )

        # Notify approvers
        self._notify_approvers(first_stage)

        return True

    def action_approve(self):
        """Approve current stage."""
        self.ensure_one()
        if self.state != "pending":
            raise UserError(_("Only pending requests can be approved."))

        # Check if current user can approve
        current_stage = self.current_stage_id
        if self.env.user not in current_stage.get_approvers():
            raise UserError(_("You are not authorized to approve this stage."))

        # Create log entry
        self.env["ipai.approval.log"].create(
            {
                "request_id": self.id,
                "stage_id": current_stage.id,
                "user_id": self.env.user.id,
                "action": "approve",
                "notes": f"Approved stage: {current_stage.name}",
            }
        )

        # Check if there are more stages
        next_stage = self._get_next_stage(current_stage)
        if next_stage:
            self.write({"current_stage_id": next_stage.id})
            self._notify_approvers(next_stage)
        else:
            # All stages complete
            self.write({"state": "approved", "complete_date": fields.Datetime.now()})
            self._notify_completion()

        return True

    def action_reject(self, reason=None):
        """Reject current stage."""
        self.ensure_one()
        if self.state != "pending":
            raise UserError(_("Only pending requests can be rejected."))

        current_stage = self.current_stage_id
        if self.env.user not in current_stage.get_approvers():
            raise UserError(_("You are not authorized to reject this stage."))

        # Create log entry
        self.env["ipai.approval.log"].create(
            {
                "request_id": self.id,
                "stage_id": current_stage.id,
                "user_id": self.env.user.id,
                "action": "reject",
                "notes": reason or "Request rejected",
            }
        )

        self.write({"state": "rejected", "complete_date": fields.Datetime.now()})
        return True

    def action_cancel(self):
        """Cancel approval request."""
        self.ensure_one()
        if self.state in ("approved", "rejected"):
            raise UserError(_("Cannot cancel approved or rejected requests."))

        self.write({"state": "cancelled"})
        return True

    def _get_next_stage(self, current_stage):
        """Get next stage in sequence."""
        self.ensure_one()
        stages = self.flow_id.stage_ids.sorted("sequence")
        current_index = stages.ids.index(current_stage.id)
        if current_index + 1 < len(stages):
            return stages[current_index + 1]
        return False

    def _notify_approvers(self, stage):
        """Send notification to stage approvers."""
        self.ensure_one()
        approvers = stage.get_approvers()
        if approvers:
            self.message_post(
                body=_(
                    "Approval request pending. Stage: %s. "
                    "Please review and approve or reject."
                )
                % stage.name,
                subject=_("Approval Required: %s") % self.name,
                partner_ids=approvers.partner_id.ids,
                subtype_xmlid="mail.mt_comment",
            )

    def _notify_completion(self):
        """Send notification when approval complete."""
        self.ensure_one()
        self.message_post(
            body=_("Approval request has been approved."),
            subject=_("Approved: %s") % self.name,
            subtype_xmlid="mail.mt_comment",
        )


class ApprovalLog(models.Model):
    """Audit trail for approval actions."""

    _name = "ipai.approval.log"
    _description = "Approval Log"
    _order = "create_date desc"

    request_id = fields.Many2one(
        "ipai.approval.request", required=True, ondelete="cascade", index=True
    )
    stage_id = fields.Many2one(
        "ipai.approval.stage", required=True, ondelete="restrict"
    )
    user_id = fields.Many2one(
        "res.users", required=True, default=lambda self: self.env.user
    )
    action = fields.Selection(
        [
            ("submit", "Submitted"),
            ("approve", "Approved"),
            ("reject", "Rejected"),
            ("cancel", "Cancelled"),
            ("escalate", "Escalated"),
        ],
        required=True,
    )
    notes = fields.Text()
    create_date = fields.Datetime(readonly=True, index=True)
