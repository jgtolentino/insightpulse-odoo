# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiTravelRequest(models.Model):
    _name = "ipai.travel.request"
    _description = "IPAI Travel Request"
    _order = "start_date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("ipai.travel.request"),
    )
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    project_id = fields.Many2one("project.project", string="Project / Job")
    destination = fields.Char(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    purpose = fields.Text()
    estimated_budget = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id.id,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("manager_approved", "Manager Approved"),
            ("finance_approved", "Finance Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company.id
    )

    def action_submit(self):
        for rec in self:
            rec.state = "submitted"

    def action_manager_approve(self):
        for rec in self:
            rec.state = "manager_approved"

    def action_finance_approve(self):
        for rec in self:
            rec.state = "finance_approved"

    def action_reject(self):
        for rec in self:
            rec.state = "rejected"


class HrExpense(models.Model):
    _inherit = "hr.expense"

    travel_request_id = fields.Many2one("ipai.travel.request", string="Travel Request")
    project_id = fields.Many2one("project.project", string="Project / Job")
