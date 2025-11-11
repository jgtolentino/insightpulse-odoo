# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class HROffboarding(models.Model):
    """
    Employee Offboarding Clearance Management (CE Compatible)

    Minimal version without Enterprise module dependencies.
    """

    _name = 'hr.offboarding'
    _description = 'Employee Offboarding Clearance'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'exit_date desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
        tracking=True
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        index=True,
        tracking=True,
        domain="[('company_id', '=', company_id)]"
    )

    exit_date = fields.Date(
        string='Last Working Day',
        required=True,
        tracking=True
    )

    exit_reason = fields.Text(
        string='Reason for Leaving',
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('clearance_pending', 'Clearance Pending'),
        ('done', 'Complete'),
    ], string='Status', default='draft', required=True, tracking=True)

    checklist_ids = fields.One2many(
        'hr.offboarding.checklist',
        'offboarding_id',
        string='Clearance Checklist'
    )

    final_pay_id = fields.Many2one(
        'hr.final.pay.computation',
        string='Final Pay Computation',
        readonly=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.offboarding') or _('New')
        return super().create(vals_list)

    def action_submit(self):
        """Submit offboarding for clearance"""
        for record in self:
            record.state = 'clearance_pending'
            record.message_post(body=_("Offboarding submitted for clearance"))

    def action_complete(self):
        """Mark offboarding as complete"""
        for record in self:
            record.state = 'done'
            record.message_post(body=_("Offboarding completed"))
