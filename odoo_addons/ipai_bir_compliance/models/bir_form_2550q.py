# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class BIRForm2550Q(models.Model):
    """BIR Form 2550Q - Quarterly Value-Added Tax Return"""

    _name = 'bir.form.2550q'
    _description = 'BIR Form 2550Q - Quarterly VAT Return'
    _order = 'period_year desc, period_quarter desc, id desc'
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

    period_quarter = fields.Selection([
        ('1', 'Q1 (Jan-Mar)'),
        ('2', 'Q2 (Apr-Jun)'),
        ('3', 'Q3 (Jul-Sep)'),
        ('4', 'Q4 (Oct-Dec)')
    ], string='Quarter', required=True)

    period_year = fields.Integer(
        string='Year',
        required=True,
        default=lambda self: fields.Date.today().year
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('filed', 'Filed'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)

    # TODO: Implement full 2550Q logic in M1 (similar to 1601-C)

    @api.depends('period_year', 'period_quarter')
    def _compute_name(self):
        for record in self:
            if record.period_year and record.period_quarter:
                record.name = f"2550Q {record.period_year}-Q{record.period_quarter}"
            else:
                record.name = "BIR Form 2550Q (New)"
