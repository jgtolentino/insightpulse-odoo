# -*- coding: utf-8 -*-
from odoo import models, fields

class BirFormSchedule(models.Model):
    _name = 'ipai.bir.form.schedule'
    _description = 'BIR Compliance Schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'form_code'

    form_code = fields.Char(string='Form Code', required=True, tracking=True)
    period = fields.Char(string='Period Covered', required=True, tracking=True)
    
    bir_deadline = fields.Date(string='BIR Deadline', required=True, tracking=True)
    
    prep_date = fields.Date(string='Prep Deadline')
    review_date = fields.Date(string='Review Deadline')
    approval_date = fields.Date(string='Approval Deadline')
    
    responsible_prep_id = fields.Many2one('ipai.finance.person', string='Prep By')
    responsible_review_id = fields.Many2one('ipai.finance.person', string='Review By')
    responsible_approval_id = fields.Many2one('ipai.finance.person', string='Approve By')
    
    step_ids = fields.One2many('ipai.bir.process.step', 'schedule_id', string='Process Steps')

class BirProcessStep(models.Model):
    _name = 'ipai.bir.process.step'
    _description = 'BIR Process Step'
    _order = 'step_no'

    schedule_id = fields.Many2one('ipai.bir.form.schedule', string='Schedule', ondelete='cascade')
    step_no = fields.Integer(string='Step #', required=True)
    title = fields.Char(string='Step Name', required=True)
    detail = fields.Text(string='SOP Detail')
    
    target_offset = fields.Integer(string='Days Before Deadline')
    role = fields.Char(string='Role')
    person_id = fields.Many2one('ipai.finance.person', string='Assignee')
