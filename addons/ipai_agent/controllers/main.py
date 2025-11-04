# -*- coding: utf-8 -*-
"""
AI Agent HTTP Controllers
Optional webhook endpoints for external integrations
"""

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class IPAIAgentController(http.Controller):

    @http.route('/ipai/agent/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def agent_webhook(self, **kwargs):
        """
        Webhook endpoint for external services to trigger agent
        Similar to GitHub webhook receiver pattern

        Example payload:
        {
            "query": "Approve all expenses for RIM",
            "user_email": "jgtolentino_rn@yahoo.com",
            "api_key": "secret_key"
        }
        """
        # Validate API key
        config_api_key = request.env['ir.config_parameter'].sudo().get_param('ipai_agent.webhook_api_key')

        if not config_api_key or kwargs.get('api_key') != config_api_key:
            return {'error': 'Unauthorized', 'code': 401}

        # Find user by email
        user = request.env['res.users'].sudo().search([
            ('email', '=', kwargs.get('user_email'))
        ], limit=1)

        if not user:
            return {'error': 'User not found', 'code': 404}

        # Build context
        context = {
            'user_id': user.id,
            'user_name': user.name,
            'user_email': user.email,
            'agencies': user.partner_id.category_id.mapped('name'),
            'channel': 'webhook',
            'permissions': {
                'can_approve_expenses': user.has_group('hr_expense.group_hr_expense_team_approver'),
                'can_deploy': user.has_group('ipai_agent.group_deployer'),
                'can_manage_bir': user.has_group('account.group_account_manager'),
                'is_admin': user.has_group('base.group_system'),
            },
            'company_id': user.company_id.id,
            'company_name': user.company_id.name,
            'timestamp': request.env['mail.message'].sudo().fields.Datetime.now().isoformat(),
        }

        # Call agent API
        query = kwargs.get('query', '')
        agent_api = request.env['ipai.agent.api'].sudo()
        response = agent_api.call_agent(query, context)

        return response

    @http.route('/ipai/agent/health', type='http', auth='public', methods=['GET'])
    def agent_health(self):
        """Health check endpoint"""
        return 'OK'
