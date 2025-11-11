# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class BIRForm1702RT(models.Model):
    """BIR Form 1702-RT - Annual Income Tax Return (Regular)"""

    _name = 'bir.form.1702rt'
    _description = 'BIR Form 1702-RT - Annual Income Tax Return'
    _order = 'period_year desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Form Name',
        compute='_compute_name',
        store=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    period_year = fields.Integer(
        string='Year',
        required=True,
        default=lambda self: fields.Date.today().year - 1
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('filed', 'Filed'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)

    # TODO: Implement full 1702-RT logic in M2 (Annual return)

    @api.depends('period_year')
    def _compute_name(self):
        for record in self:
            if record.period_year:
                record.name = f"1702-RT {record.period_year}"
            else:
                record.name = "BIR Form 1702-RT (New)"
