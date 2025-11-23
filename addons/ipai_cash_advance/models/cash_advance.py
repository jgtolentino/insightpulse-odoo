from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CashAdvance(models.Model):
    _name = "ipai.cash.advance"
    _description = "Cash Advance Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )

    date = fields.Date(
        string="Date Prepared",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Name",
        required=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True,
    )

    department_id = fields.Many2one(
        "hr.department",
        string="Dept / Group",
        related="employee_id.department_id",
        readonly=True,
        store=True,
    )

    purpose = fields.Char(string="Purpose / Justification")

    amount_requested = fields.Monetary(
        string="Cash Advanced",
        currency_field="currency_id",
        tracking=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("paid", "Paid / Disbursed"),
            ("liquidating", "Liquidating"),
            ("liquidated", "Liquidated"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    # Liquidation Fields
    line_ids = fields.One2many(
        "ipai.cash.advance.line",
        "advance_id",
        string="Liquidation Lines",
    )

    total_liquidated = fields.Monetary(
        string="Total Expenses",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )

    amount_due = fields.Monetary(
        string="Amount Due to/(from) Agency",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
        help="Positive: Employee returns cash. Negative: Agency reimburses employee.",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("ipai.cash.advance") or _("New")
        return super().create(vals)

    @api.depends("line_ids.total", "amount_requested")
    def _compute_totals(self):
        for record in self:
            total_expenses = sum(line.total for line in record.line_ids)
            record.total_liquidated = total_expenses
            # If Advanced 1000, Spent 800 -> Due 200 (Employee returns)
            # If Advanced 1000, Spent 1200 -> Due -200 (Agency pays)
            record.amount_due = record.amount_requested - total_expenses

    def action_submit(self):
        self.write({"state": "submitted"})

    def action_approve(self):
        self.write({"state": "approved"})

    def action_pay(self):
        self.write({"state": "paid"})

    def action_start_liquidation(self):
        self.write({"state": "liquidating"})

    def action_finish_liquidation(self):
        self.write({"state": "liquidated"})

    def action_close(self):
        self.write({"state": "closed"})


class CashAdvanceLine(models.Model):
    _name = "ipai.cash.advance.line"
    _description = "Cash Advance Liquidation Line"

    advance_id = fields.Many2one("ipai.cash.advance", string="Advance", ondelete="cascade")
    date = fields.Date(string="Date", required=True)
    particulars = fields.Char(string="Particulars", required=True)
    client = fields.Char(string="Client")
    ce_number = fields.Char(string="CE Number")
    
    # Expense Categories
    amount_meals = fields.Monetary(string="Meals", currency_field="currency_id")
    amount_transpo = fields.Monetary(string="Transpo", currency_field="currency_id")
    amount_misc = fields.Monetary(string="Misc", currency_field="currency_id")
    
    total = fields.Monetary(
        string="Total",
        compute="_compute_total",
        store=True,
        currency_field="currency_id",
    )
    
    currency_id = fields.Many2one(
        "res.currency",
        related="advance_id.currency_id",
        readonly=True,
    )

    @api.depends("amount_meals", "amount_transpo", "amount_misc")
    def _compute_total(self):
        for line in self:
            line.total = line.amount_meals + line.amount_transpo + line.amount_misc
