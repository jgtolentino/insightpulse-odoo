from odoo.exceptions import UserError

from odoo import _, api, fields, models


class CostSheet(models.Model):
    """Project cost sheet with vendor-privacy separation."""

    _name = "ipai.cost.sheet"
    _description = "Project Cost Sheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, index=True, tracking=True)
    code = fields.Char(readonly=True, copy=False, index=True)
    active = fields.Boolean(default=True)
    description = fields.Text()

    # Project linkage
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    analytic_account_id = fields.Many2one(
        related="project_id.analytic_account_id",
        string="Analytic Account",
        store=True,
    )

    # Dates
    date_start = fields.Date(required=True, tracking=True)
    date_end = fields.Date(tracking=True)

    # State
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # Lines
    line_ids = fields.One2many(
        "ipai.cost.sheet.line",
        "cost_sheet_id",
        string="Cost Lines",
    )

    # Currency
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    # AM View (Public Rates - Role-based)
    public_subtotal = fields.Monetary(
        compute="_compute_public_totals",
        store=True,
        currency_field="currency_id",
        help="Total based on public rates (visible to Account Managers)",
    )
    public_total = fields.Monetary(
        compute="_compute_public_totals",
        store=True,
        currency_field="currency_id",
    )

    # FD View (Vendor Costs - Actual)
    vendor_subtotal = fields.Monetary(
        compute="_compute_vendor_totals",
        store=True,
        currency_field="currency_id",
        groups="ipai_ppm_costsheet.group_finance_director",
        help="Total based on vendor costs (visible only to Finance Directors)",
    )
    vendor_total = fields.Monetary(
        compute="_compute_vendor_totals",
        store=True,
        currency_field="currency_id",
        groups="ipai_ppm_costsheet.group_finance_director",
    )

    # Profit Analysis (FD Only)
    profit_amount = fields.Monetary(
        compute="_compute_profit",
        store=True,
        currency_field="currency_id",
        groups="ipai_ppm_costsheet.group_finance_director",
        help="Profit = Public Total - Vendor Total",
    )
    profit_margin = fields.Float(
        compute="_compute_profit",
        store=True,
        groups="ipai_ppm_costsheet.group_finance_director",
        help="Profit Margin % = (Profit / Public Total) * 100",
    )

    # Approval integration
    approval_request_id = fields.Many2one(
        "ipai.approval.request",
        string="Approval Request",
        readonly=True,
        copy=False,
    )
    approval_state = fields.Selection(
        related="approval_request_id.state",
        string="Approval Status",
        store=True,
    )

    # Statistics
    line_count = fields.Integer(compute="_compute_line_count", store=False)

    _sql_constraints = [
        (
            "code_unique",
            "UNIQUE(code)",
            "Cost sheet code must be unique.",
        ),
    ]

    @api.model
    def create(self, vals):
        """Generate code sequence on create."""
        if not vals.get("code"):
            vals["code"] = (
                self.env["ir.sequence"].next_by_code("ipai.cost.sheet") or "/"
            )
        return super().create(vals)

    @api.depends("line_ids.public_subtotal")
    def _compute_public_totals(self):
        """Calculate totals based on public rates (AM view)."""
        for sheet in self:
            sheet.public_subtotal = sum(sheet.line_ids.mapped("public_subtotal"))
            sheet.public_total = sheet.public_subtotal

    @api.depends("line_ids.vendor_subtotal")
    def _compute_vendor_totals(self):
        """Calculate totals based on vendor costs (FD view)."""
        for sheet in self:
            sheet.vendor_subtotal = sum(sheet.line_ids.mapped("vendor_subtotal"))
            sheet.vendor_total = sheet.vendor_subtotal

    @api.depends("public_total", "vendor_total")
    def _compute_profit(self):
        """Calculate profit metrics (FD only)."""
        for sheet in self:
            sheet.profit_amount = sheet.public_total - sheet.vendor_total
            if sheet.public_total:
                sheet.profit_margin = (sheet.profit_amount / sheet.public_total) * 100
            else:
                sheet.profit_margin = 0.0

    @api.depends("line_ids")
    def _compute_line_count(self):
        for sheet in self:
            sheet.line_count = len(sheet.line_ids)

    def action_activate(self):
        """Activate cost sheet."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Only draft cost sheets can be activated."))
        self.state = "active"
        self.message_post(body=_("Cost sheet activated."))
        return True

    def action_complete(self):
        """Complete cost sheet."""
        self.ensure_one()
        if self.state != "active":
            raise UserError(_("Only active cost sheets can be completed."))
        self.state = "completed"
        self.message_post(body=_("Cost sheet completed."))
        return True

    def action_cancel(self):
        """Cancel cost sheet."""
        self.ensure_one()
        if self.state == "completed":
            raise UserError(_("Completed cost sheets cannot be cancelled."))
        self.state = "cancelled"
        self.message_post(body=_("Cost sheet cancelled."))
        return True

    def action_view_lines(self):
        """Open cost sheet lines."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "ipai.cost.sheet.line",
            "domain": [("cost_sheet_id", "=", self.id)],
            "context": {"default_cost_sheet_id": self.id},
            "view_mode": "tree,form",
            "target": "current",
        }
