# -*- coding: utf-8 -*-
from odoo import api, fields, models

class IpTeDashboard(models.TransientModel):
    _name = "ip.te.dashboard"
    _description = "T&E Admin Dashboard (KPI)"

    pending_approvals = fields.Integer(compute="_compute_kpis")
    overdue_liquidations = fields.Integer(compute="_compute_kpis")
    open_cash_advances = fields.Integer(compute="_compute_kpis")
    ocr_queue = fields.Integer(compute="_compute_kpis")

    @api.depends()
    def _compute_kpis(self):
        Expense = self.env["hr.expense"].sudo()
        Liquid = self.env["ip.liquidation"].sudo()
        CA = self.env["ip.cash.advance"].sudo()
        for rec in self:
            rec.pending_approvals = Expense.search_count([("state", "in", ["reported","submitted"])])
            rec.ocr_queue = Expense.search_count([("ocr_status", "in", ["new","queued"])])
            rec.open_cash_advances = CA.search_count([("state","in",["approved","released"])])
            rec.overdue_liquidations = Liquid.search_count([("state","in",["draft","submitted"])])
