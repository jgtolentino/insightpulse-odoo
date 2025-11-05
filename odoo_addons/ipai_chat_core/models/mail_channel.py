# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class MailChannelInherit(models.Model):
    """
    Extends mail.channel with enterprise features
    """
    _inherit = 'mail.channel'

    # Enterprise features
    channel_type_extended = fields.Selection([
        ('public', 'Public Channel'),
        ('private', 'Private Channel'),
        ('group', 'Group DM'),
        ('direct', 'Direct Message'),
        ('announcement', 'Announcement Only'),
        ('external', 'External/Guest Channel'),
    ], string='Channel Type', default='public')

    category_id = fields.Many2one(
        'ipai.chat.category',
        string='Category',
        help='Organize channels into categories'
    )

    policy_id = fields.Many2one(
        'ipai.channel.policy',
        string='Channel Policy',
        help='Retention, DLP, and access policies'
    )

    # Access control
    channel_admin_ids = fields.Many2many(
        'res.users',
        'channel_admin_rel',
        'channel_id',
        'user_id',
        string='Channel Admins',
        help='Users who can manage channel settings'
    )

    moderator_ids = fields.Many2many(
        'res.users',
        'channel_moderator_rel',
        'channel_id',
        'user_id',
        string='Moderators',
        help='Users who can moderate messages'
    )

    read_only_member_ids = fields.Many2many(
        'res.users',
        'channel_readonly_rel',
        'channel_id',
        'user_id',
        string='Read-Only Members',
        help='Members who can only read messages'
    )

    # Settings
    allow_guests = fields.Boolean(
        string='Allow Guest Access',
        default=False,
        help='Allow external users (portal) to access this channel'
    )

    require_approval = fields.Boolean(
        string='Require Join Approval',
        default=False,
        help='Channel admins must approve new members'
    )

    announcement_only = fields.Boolean(
        string='Announcement Only',
        default=False,
        help='Only admins can post'
    )

    pin_messages = fields.Boolean(
        string='Allow Pin Messages',
        default=True
    )

    allow_reactions = fields.Boolean(
        string='Allow Reactions',
        default=True
    )

    allow_threads = fields.Boolean(
        string='Allow Threaded Replies',
        default=True
    )

    # Statistics
    message_count = fields.Integer(
        string='Message Count',
        compute='_compute_statistics',
        store=True
    )

    active_members_count = fields.Integer(
        string='Active Members',
        compute='_compute_statistics',
        store=True
    )

    last_activity_date = fields.Datetime(
        string='Last Activity',
        compute='_compute_statistics',
        store=True
    )

    # Slack integration
    slack_channel_id = fields.Char(
        string='Slack Channel ID',
        help='Connected Slack channel'
    )

    slack_workspace_id = fields.Many2one(
        'ipai.slack.workspace',
        string='Slack Workspace'
    )

    @api.depends('message_ids', 'channel_partner_ids')
    def _compute_statistics(self):
        """Compute channel statistics"""
        for channel in self:
            messages = self.env['mail.message'].search([
                ('model', '=', 'mail.channel'),
                ('res_id', '=', channel.id)
            ])
            channel.message_count = len(messages)
            channel.active_members_count = len(channel.channel_partner_ids)
            channel.last_activity_date = messages[:1].date if messages else False

    def action_add_members(self, partner_ids):
        """
        Add members with approval check
        """
        self.ensure_one()

        if self.require_approval:
            # Create approval request
            self.env['ipai.channel.join.request'].create({
                'channel_id': self.id,
                'partner_ids': [(6, 0, partner_ids)],
                'requested_by': self.env.user.id,
                'state': 'pending'
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Join request sent to channel admins'),
                    'type': 'info',
                    'sticky': False,
                }
            }
        else:
            # Add directly
            return super().action_add_members(partner_ids)

    def check_access_rights_channel(self, operation):
        """
        Check if current user can perform operation

        Args:
            operation: 'read', 'write', 'admin', 'moderate'
        """
        self.ensure_one()

        user = self.env.user

        # System users can do anything
        if user.has_group('base.group_system'):
            return True

        # Channel admins can do anything
        if user in self.channel_admin_ids:
            return True

        # Moderators can read, write, moderate
        if operation in ('read', 'write', 'moderate') and user in self.moderator_ids:
            return True

        # Read-only members can only read
        if operation == 'read' and user in self.read_only_member_ids:
            return True

        # Regular members can read and write (if not read-only)
        if operation in ('read', 'write'):
            if user.partner_id in self.channel_partner_ids and user not in self.read_only_member_ids:
                return True

        return False

    def action_archive_channel(self):
        """Archive channel with proper cleanup"""
        self.ensure_one()

        if not self.check_access_rights_channel('admin'):
            raise AccessError(_('Only channel admins can archive channels'))

        # Archive messages based on policy
        if self.policy_id and self.policy_id.archive_on_close:
            self.message_ids.write({'active': False})

        self.active = False

        self.message_post(
            body=_('Channel archived by %s') % self.env.user.name,
            message_type='notification'
        )

    @api.model
    def create_channel_with_policy(self, name, channel_type, policy_template=None):
        """
        Create channel with default policy

        Args:
            name: Channel name
            channel_type: Type of channel
            policy_template: Policy template to use

        Returns:
            mail.channel record
        """
        # Create channel
        channel = self.create({
            'name': name,
            'channel_type_extended': channel_type,
            'channel_admin_ids': [(4, self.env.user.id)]
        })

        # Apply policy template if provided
        if policy_template:
            policy = self.env['ipai.channel.policy'].search([
                ('name', '=', policy_template)
            ], limit=1)
            if policy:
                channel.policy_id = policy.id

        return channel
