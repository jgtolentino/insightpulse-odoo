# -*- coding: utf-8 -*-

import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class SupersetEmbeddedController(http.Controller):

    @http.route('/superset/dashboard/<string:dashboard_id>', type='http', auth='user', website=True)
    def embedded_dashboard(self, dashboard_id, **kwargs):
        """
        Render embedded Superset dashboard with authentication
        
        Args:
            dashboard_id: UUID of the Superset dashboard
            
        Query parameters:
            rls_filter: Optional custom RLS filter clause
            standalone: Set to '1' for standalone mode (default)
            height: Dashboard height in pixels (default: 800)
        """
        # Get configuration
        config = request.env['res.config.settings'].sudo().get_superset_config()
        
        if not config.get('url'):
            return request.render('superset_connector.error_not_configured')
        
        # Get or create guest token
        rls_filter = kwargs.get('rls_filter')
        try:
            token = request.env['superset.token'].get_or_create_token(
                dashboard_id=dashboard_id,
                rls_filter=rls_filter
            )
        except Exception as e:
            _logger.error(f"Failed to get Superset token: {e}")
            return request.render('superset_connector.error_token_generation', {
                'error': str(e)
            })
        
        # Build dashboard URL
        standalone = kwargs.get('standalone', '1')
        dashboard_url = f"{config['url']}/superset/dashboard/{dashboard_id}/"
        dashboard_url += f"?standalone={standalone}&guest_token={token}"
        
        # Dashboard height
        height = kwargs.get('height', '800')
        
        # Prepare CSP header value
        csp_value = None
        if config.get('csp_enabled'):
            superset_origin = config['url'].rstrip('/')
            csp_value = f"frame-src 'self' {superset_origin};"
        
        # Render template
        response = request.render('superset_connector.embedded_dashboard', {
            'dashboard_url': dashboard_url,
            'dashboard_id': dashboard_id,
            'height': height,
            'superset_url': config['url'],
        })
        
        # Add CSP header if enabled
        if csp_value:
            response.headers['Content-Security-Policy'] = csp_value
        
        return response

    @http.route('/superset/dashboards', type='http', auth='user', website=True)
    def dashboard_list(self, **kwargs):
        """List available Superset dashboards"""
        config = request.env['res.config.settings'].sudo().get_superset_config()
        
        if not config.get('url'):
            return request.render('superset_connector.error_not_configured')
        
        # Get user's token records
        tokens = request.env['superset.token'].search([
            ('user_id', '=', request.env.user.id),
            ('active', '=', True)
        ], order='create_date desc')
        
        return request.render('superset_connector.dashboard_list', {
            'tokens': tokens,
            'superset_url': config['url'],
        })

    @http.route('/superset/token/refresh/<int:token_id>', type='json', auth='user')
    def refresh_token(self, token_id):
        """Refresh a specific guest token"""
        token = request.env['superset.token'].browse(token_id)
        
        if token.user_id != request.env.user:
            return {'error': 'Unauthorized'}
        
        try:
            token.generate_token()
            return {
                'success': True,
                'token': token.token,
                'expiry': token.expiry_date.isoformat() if token.expiry_date else None
            }
        except Exception as e:
            _logger.error(f"Failed to refresh token: {e}")
            return {'error': str(e)}
