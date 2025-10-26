# -*- coding: utf-8 -*-

import logging
import requests
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SupersetToken(models.Model):
    _name = 'superset.token'
    _description = 'Superset Guest Token'
    _order = 'create_date desc'

    name = fields.Char(string='Token Name', required=True)
    dashboard_id = fields.Char(string='Dashboard ID', required=True, help='UUID of the Superset dashboard')
    token = fields.Text(string='Guest Token', readonly=True)
    expiry_date = fields.Datetime(string='Expiry Date', readonly=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    rls_filter = fields.Text(string='RLS Filter', help='Row-level security SQL filter clause')
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def _get_superset_api_token(self):
        """Authenticate with Superset and get API access token"""
        config = self.env['res.config.settings'].get_superset_config()
        
        if not config.get('url') or not config.get('username') or not config.get('password'):
            raise UserError(_('Superset connection is not configured. Please configure in Settings > General Settings > Superset Integration.'))
        
        login_url = f"{config['url']}/api/v1/security/login"
        payload = {
            'username': config['username'],
            'password': config['password'],
            'provider': 'db',
            'refresh': True
        }
        
        try:
            response = requests.post(login_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('access_token')
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to authenticate with Superset: {e}")
            raise UserError(_('Failed to authenticate with Superset: %s') % str(e))

    @api.model
    def _generate_guest_token(self, dashboard_id, user=None, company=None, rls_filter=None):
        """Generate a guest token for embedded dashboard access"""
        if not user:
            user = self.env.user
        if not company:
            company = self.env.company
        
        config = self.env['res.config.settings'].get_superset_config()
        access_token = self._get_superset_api_token()
        
        # Prepare guest token request
        guest_url = f"{config['url']}/api/v1/security/guest_token/"
        
        # Build RLS filters
        rls_rules = []
        if config.get('enable_rls'):
            if rls_filter:
                rls_rules.append({'clause': rls_filter})
            else:
                # Default RLS: filter by company
                rls_rules.append({
                    'clause': f"company_id = {company.id}"
                })
        
        # Guest token payload
        payload = {
            'user': {
                'username': user.login,
                'first_name': user.name.split()[0] if user.name else 'Guest',
                'last_name': ' '.join(user.name.split()[1:]) if len(user.name.split()) > 1 else 'User'
            },
            'resources': [{
                'type': 'dashboard',
                'id': dashboard_id
            }],
            'rls': rls_rules
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(guest_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('token')
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to generate guest token: {e}")
            raise UserError(_('Failed to generate guest token: %s') % str(e))

    def generate_token(self):
        """Generate a new guest token for this record"""
        self.ensure_one()
        config = self.env['res.config.settings'].get_superset_config()
        
        token = self._generate_guest_token(
            dashboard_id=self.dashboard_id,
            user=self.user_id,
            company=self.company_id,
            rls_filter=self.rls_filter
        )
        
        self.write({
            'token': token,
            'expiry_date': datetime.now() + timedelta(seconds=config.get('token_expiry', 3600))
        })
        
        return True

    @api.model
    def get_or_create_token(self, dashboard_id, rls_filter=None):
        """Get existing valid token or create new one"""
        # Search for existing valid token
        domain = [
            ('dashboard_id', '=', dashboard_id),
            ('user_id', '=', self.env.user.id),
            ('company_id', '=', self.env.company.id),
            ('expiry_date', '>', fields.Datetime.now()),
            ('active', '=', True)
        ]
        
        token_record = self.search(domain, limit=1)
        
        if token_record:
            return token_record.token
        
        # Create new token
        token_record = self.create({
            'name': f"{self.env.user.name} - {dashboard_id}",
            'dashboard_id': dashboard_id,
            'user_id': self.env.user.id,
            'company_id': self.env.company.id,
            'rls_filter': rls_filter,
        })
        
        token_record.generate_token()
        return token_record.token

    @api.model
    def cleanup_expired_tokens(self):
        """Cron job to clean up expired tokens"""
        expired_tokens = self.search([
            ('expiry_date', '<=', fields.Datetime.now()),
            ('active', '=', True)
        ])
        expired_tokens.write({'active': False})
        _logger.info(f"Deactivated {len(expired_tokens)} expired Superset tokens")
        return True
