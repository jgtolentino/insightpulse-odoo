# -*- coding: utf-8 -*-

from odoo import models, fields


class ChatCategory(models.Model):
    """Channel categories for organization"""
    _name = 'ipai.chat.category'
    _description = 'Chat Channel Category'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string='Color Index')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    channel_ids = fields.One2many('mail.channel', 'category_id', string='Channels')
    channel_count = fields.Integer(compute='_compute_channel_count', store=True)

    @fields.depends('channel_ids')
    def _compute_channel_count(self):
        for category in self:
            category.channel_count = len(category.channel_ids)
