# -*- coding: utf-8 -*-
"""GitHub OAuth controller for pulser-hub integration."""

from odoo import http
from odoo.http import request
import requests
import logging

_logger = logging.getLogger(__name__)


class GitHubOAuthController(http.Controller):
    """Handle GitHub OAuth callbacks for pulser-hub app."""

    @http.route('/odoo/github/auth/callback', type='http', auth='public', methods=['GET'])
    def github_oauth_callback(self, code=None, state=None, error=None, **kwargs):
        """
        Handle GitHub OAuth callback after app installation.

        Args:
            code (str): Authorization code from GitHub
            state (str): State parameter for CSRF protection
            error (str): Error message if authorization failed

        Returns:
            Rendered template with status
        """
        if error:
            _logger.error(f"GitHub OAuth error: {error}")
            return request.render('github_integration.oauth_error', {
                'error': error,
                'error_description': kwargs.get('error_description', '')
            })

        if not code:
            _logger.error("No authorization code received")
            return request.render('github_integration.oauth_error', {
                'error': 'No authorization code received'
            })

        try:
            # Exchange code for access token
            client_id = request.env['ir.config_parameter'].sudo().get_param('github.client_id')
            client_secret = request.env['ir.config_parameter'].sudo().get_param('github.client_secret')

            if not client_id or not client_secret:
                raise ValueError("GitHub OAuth credentials not configured")

            _logger.info(f"Exchanging code for token (client_id: {client_id})")

            token_response = requests.post(
                'https://github.com/login/oauth/access_token',
                headers={'Accept': 'application/json'},
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code,
                    'state': state,
                }
            )

            if token_response.status_code == 200:
                token_data = token_response.json()

                if 'error' in token_data:
                    raise Exception(token_data['error_description'])

                access_token = token_data.get('access_token')

                if not access_token:
                    raise Exception("No access token in response")

                # Store token (you may want to create a model for this)
                request.env['ir.config_parameter'].sudo().set_param(
                    'github.oauth_token',
                    access_token
                )

                _logger.info("GitHub OAuth successful - token stored")

                return request.render('github_integration.oauth_success', {
                    'message': 'GitHub App successfully connected!',
                    'scope': token_data.get('scope', ''),
                })
            else:
                raise Exception(f"Token exchange failed: {token_response.text}")

        except Exception as e:
            _logger.error(f"OAuth callback failed: {str(e)}")
            return request.render('github_integration.oauth_error', {
                'error': 'Authentication failed',
                'error_description': str(e)
            })
