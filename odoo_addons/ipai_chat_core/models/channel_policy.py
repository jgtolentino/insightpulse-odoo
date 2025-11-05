# -*- coding: utf-8 -*-

from odoo import models, fields


class ChannelPolicy(models.Model):
    """Channel policies for retention, DLP, access"""
    _name = 'ipai.channel.policy'
    _description = 'Channel Policy'

    name = fields.Char(required=True)
    description = fields.Text()

    # Retention
    retention_days = fields.Integer(
        string='Retention (Days)',
        help='Delete messages older than this. 0 = keep forever'
    )
    archive_on_close = fields.Boolean(
        string='Archive on Channel Close',
        default=False
    )

    # DLP
    require_dlp_scan = fields.Boolean(
        string='Require DLP Scan',
        default=False
    )
    dlp_rule_ids = fields.Many2many(
        'ipai.dlp.rule',
        'policy_dlp_rule_rel',
        string='DLP Rules'
    )

    # Access
    allow_guest_access = fields.Boolean(default=False)
    require_approval = fields.Boolean(default=False)

    # Legal hold
    legal_hold = fields.Boolean(
        string='Legal Hold',
        help='Prevent message deletion regardless of retention'
    )

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
