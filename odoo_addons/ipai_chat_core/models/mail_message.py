# -*- coding: utf-8 -*-

from odoo import models, fields, api
import markdown


class MailMessageInherit(models.Model):
    """Extends mail.message with enterprise features"""
    _inherit = 'mail.message'

    # Threading
    parent_message_id = fields.Many2one(
        'mail.message',
        string='Parent Message',
        help='Message this is replying to'
    )

    thread_count = fields.Integer(
        string='Replies',
        compute='_compute_thread_count',
        store=True
    )

    # Reactions
    reaction_ids = fields.One2many(
        'ipai.message.reaction',
        'message_id',
        string='Reactions'
    )

    # Priority
    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='normal')

    is_pinned = fields.Boolean(string='Pinned', default=False)
    pinned_by = fields.Many2one('res.users', string='Pinned By')
    pinned_date = fields.Datetime(string='Pinned Date')

    # Read receipts
    read_by_ids = fields.Many2many(
        'res.users',
        'message_read_receipt_rel',
        'message_id',
        'user_id',
        string='Read By'
    )

    # Formatting
    message_format = fields.Selection([
        ('plain', 'Plain Text'),
        ('html', 'HTML'),
        ('markdown', 'Markdown'),
    ], default='plain')

    # DLP
    dlp_checked = fields.Boolean(default=False)
    dlp_status = fields.Selection([
        ('clean', 'Clean'),
        ('warning', 'Warning'),
        ('quarantine', 'Quarantined'),
        ('blocked', 'Blocked'),
    ], default='clean')

    dlp_rule_ids = fields.Many2many(
        'ipai.dlp.rule',
        'message_dlp_hit_rel',
        string='DLP Rules Hit'
    )

    @api.depends('parent_message_id')
    def _compute_thread_count(self):
        """Count thread replies"""
        for message in self:
            message.thread_count = self.search_count([
                ('parent_message_id', '=', message.id)
            ])

    def action_add_reaction(self, emoji):
        """Add reaction to message"""
        self.ensure_one()

        existing = self.env['ipai.message.reaction'].search([
            ('message_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('emoji', '=', emoji)
        ])

        if existing:
            existing.unlink()  # Remove reaction
        else:
            self.env['ipai.message.reaction'].create({
                'message_id': self.id,
                'user_id': self.env.user.id,
                'emoji': emoji
            })

    def render_markdown(self):
        """Convert markdown to HTML"""
        self.ensure_one()
        if self.message_format == 'markdown':
            return markdown.markdown(self.body or '')
        return self.body

    def mark_as_read(self):
        """Mark message as read by current user"""
        for message in self:
            if self.env.user not in message.read_by_ids:
                message.write({
                    'read_by_ids': [(4, self.env.user.id)]
                })


class MessageReaction(models.Model):
    """Message reactions (emoji)"""
    _name = 'ipai.message.reaction'
    _description = 'Message Reaction'

    message_id = fields.Many2one('mail.message', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', required=True)
    emoji = fields.Char(required=True)
    created_date = fields.Datetime(default=fields.Datetime.now)

    _sql_constraints = [
        ('unique_reaction', 'unique(message_id, user_id, emoji)',
         'User can only react once with the same emoji')
    ]
