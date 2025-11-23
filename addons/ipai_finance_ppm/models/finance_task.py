# -*- coding: utf-8 -*-
from odoo import models, fields

class FinanceTaskTemplate(models.Model):
    _name = 'ipai.finance.task.template'
    _description = 'Monthly Finance Task Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Text(string='Task Description', required=True)
    category = fields.Char(string='Category', help="e.g. Payables, Reporting")
    
    employee_code_id = fields.Many2one('ipai.finance.person', string='Owner', tracking=True)
    reviewed_by_id = fields.Many2one('ipai.finance.person', string='Reviewer')
    approved_by_id = fields.Many2one('ipai.finance.person', string='Approver')
    
    prep_duration = fields.Float(string='Prep SLA (Days)', default=1.0)
    review_duration = fields.Float(string='Review SLA (Days)', default=0.5)
    approval_duration = fields.Float(string='Approval SLA (Days)', default=0.5)
