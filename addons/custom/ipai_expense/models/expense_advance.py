from odoo import fields, models


class IpaiExpenseAdvance(models.Model):
    _name = "ipai.expense.advance"
    _description = "IPAI Cash Advance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        default=lambda s: s.env["ir.sequence"].next_by_code("ipai.advance") or "/",
        tracking=True,
    )
    employee_id = fields.Many2one("hr.employee", required=True, tracking=True)
    amount = fields.Monetary(required=True, tracking=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda s: s.env.company.currency_id.id
    )
    purpose = fields.Char()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("released", "Released"),
            ("liquidated", "Liquidated"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )
    liquidation_sheet_id = fields.Many2one(
        "hr.expense.sheet", string="Liquidation Sheet"
    )
