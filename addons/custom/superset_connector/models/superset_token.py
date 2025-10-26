"""Superset SSO Token Management"""
import secrets
import logging
from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SupersetToken(models.Model):
    """Manage Superset guest tokens for SSO authentication"""

    _name = 'superset.token'
    _description = 'Superset Guest Token'
    _order = 'create_date desc'

    name = fields.Char(string='Token Name', compute='_compute_name', store=True)
    token = fields.Char(string='Guest Token', required=True, readonly=True, index=True)
    user_id = fields.Many2one('res.users', string='User', required=True, index=True, ondelete='cascade')
    dashboard_id = fields.Many2one('superset.dashboard', string='Dashboard', required=True, index=True, ondelete='cascade')
    config_id = fields.Many2one('superset.config', string='Superset Configuration', required=True, ondelete='cascade')

    # Token lifecycle
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now, readonly=True)
    expires_at = fields.Datetime(string='Expires At', required=True, index=True)
    last_used_at = fields.Datetime(string='Last Used At')
    is_active = fields.Boolean(string='Active', default=True, index=True)

    # Usage tracking
    use_count = fields.Integer(string='Usage Count', default=0, readonly=True)

    # Security
    user_ip = fields.Char(string='User IP Address')
    user_agent = fields.Char(string='User Agent')

    @api.depends('user_id', 'dashboard_id', 'created_at')
    def _compute_name(self):
        """Compute human-readable token name"""
        for record in self:
            if record.user_id and record.dashboard_id:
                record.name = f"{record.user_id.name} - {record.dashboard_id.name} ({record.created_at})"
            else:
                record.name = f"Token {record.id}"

    @api.model
    def create(self, vals):
        """Override create to generate token and set expiry"""
        # Generate secure random token if not provided
        if 'token' not in vals:
            vals['token'] = self._generate_guest_token()

        # Set expiry if not provided (default: 24 hours)
        if 'expires_at' not in vals:
            vals['expires_at'] = datetime.now() + timedelta(hours=24)

        # Get user context information if available
        if not vals.get('user_ip') and hasattr(self, 'env'):
            request = self.env.context.get('request')
            if request:
                vals['user_ip'] = request.httprequest.remote_addr
                vals['user_agent'] = request.httprequest.user_agent.string

        return super().create(vals)

    def write(self, vals):
        """Override write to track usage"""
        # Prevent modification of immutable fields
        immutable_fields = ['token', 'user_id', 'dashboard_id', 'config_id', 'created_at']
        for field in immutable_fields:
            if field in vals and field != 'token':  # Allow token on create
                raise ValidationError(f"Field '{field}' cannot be modified after creation")

        return super().write(vals)

    def _generate_guest_token(self):
        """
        Generate cryptographically secure guest token

        Returns:
            str: Secure random token
        """
        # Generate 32-byte random token (256 bits)
        return secrets.token_urlsafe(32)

    @api.model
    def get_or_create_token(self, dashboard_id, user_id=None, force_new=False):
        """
        Get existing valid token or create new one

        Args:
            dashboard_id: ID of superset.dashboard record
            user_id: ID of res.users record (default: current user)
            force_new: Force creation of new token even if valid one exists

        Returns:
            superset.token record
        """
        if not user_id:
            user_id = self.env.user.id

        if not force_new:
            # Try to find existing valid token
            existing_token = self.search([
                ('dashboard_id', '=', dashboard_id),
                ('user_id', '=', user_id),
                ('is_active', '=', True),
                ('expires_at', '>', fields.Datetime.now())
            ], limit=1)

            if existing_token:
                # Update last used timestamp
                existing_token.write({
                    'last_used_at': fields.Datetime.now(),
                    'use_count': existing_token.use_count + 1
                })
                return existing_token

        # Get dashboard and config
        dashboard = self.env['superset.dashboard'].browse(dashboard_id)
        if not dashboard.exists():
            raise ValidationError(f'Dashboard {dashboard_id} not found')

        # Create new token
        token = self.create({
            'dashboard_id': dashboard_id,
            'user_id': user_id,
            'config_id': dashboard.config_id.id,
        })

        _logger.info(f"Created new guest token for user {user_id}, dashboard {dashboard_id}")
        return token

    def invalidate_token(self):
        """Invalidate this token"""
        self.ensure_one()
        self.write({'is_active': False})
        _logger.info(f"Invalidated token {self.id}")

    @api.model
    def cleanup_expired_tokens(self):
        """Cron job to clean up expired tokens"""
        # Find expired tokens
        expired_tokens = self.search([
            ('expires_at', '<', fields.Datetime.now()),
            ('is_active', '=', True)
        ])

        if expired_tokens:
            expired_tokens.write({'is_active': False})
            _logger.info(f"Deactivated {len(expired_tokens)} expired tokens")

        # Delete old inactive tokens (older than 30 days)
        old_cutoff = datetime.now() - timedelta(days=30)
        old_tokens = self.search([
            ('is_active', '=', False),
            ('created_at', '<', old_cutoff)
        ])

        if old_tokens:
            count = len(old_tokens)
            old_tokens.unlink()
            _logger.info(f"Deleted {count} old inactive tokens")

        return True

    @api.model
    def get_token_stats(self):
        """
        Get token usage statistics

        Returns:
            dict: Token statistics
        """
        total_tokens = self.search_count([])
        active_tokens = self.search_count([('is_active', '=', True)])
        expired_tokens = self.search_count([
            ('expires_at', '<', fields.Datetime.now()),
            ('is_active', '=', True)
        ])

        # Most used tokens
        most_used = self.search([('is_active', '=', True)], order='use_count desc', limit=5)

        return {
            'total_tokens': total_tokens,
            'active_tokens': active_tokens,
            'expired_tokens': expired_tokens,
            'most_used_tokens': [(t.name, t.use_count) for t in most_used]
        }


class SupersetConfig(models.Model):
    """Extend Superset Configuration with CSP settings"""

    _inherit = 'superset.config'

    # CSP Security Settings
    allowed_origins = fields.Char(
        string='Allowed Origins',
        help='Comma-separated list of allowed origins for CSP (e.g., https://superset.example.com)',
        default=lambda self: self.base_url
    )

    # Token Settings
    token_expiry_hours = fields.Integer(
        string='Token Expiry (Hours)',
        default=24,
        help='Default token expiration time in hours'
    )

    max_tokens_per_user = fields.Integer(
        string='Max Tokens Per User',
        default=5,
        help='Maximum number of active tokens per user per dashboard'
    )

    @api.onchange('base_url')
    def _onchange_base_url(self):
        """Auto-set allowed origins when base URL changes"""
        if self.base_url and not self.allowed_origins:
            self.allowed_origins = self.base_url
