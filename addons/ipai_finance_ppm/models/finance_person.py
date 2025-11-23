# -*- coding: utf-8 -*-
from odoo import models, fields

class FinancePerson(models.Model):
    _name = 'ipai.finance.person'
    _description = 'Finance Team Directory'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True, tracking=True, help="e.g. CKVC, RIM")
    name = fields.Char(string='Name', required=True, tracking=True)
    email = fields.Char(string='Email')
    role = fields.Selection([
        ('staff', 'Staff'),
        ('supervisor', 'Supervisor'),
        ('manager', 'Manager'),
        ('director', 'Director')
    ], string='Role', default='staff', tracking=True)
    user_id = fields.Many2one('res.users', string='Odoo User')

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Personnel code must be unique!')
    ]
