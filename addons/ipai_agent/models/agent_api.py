# -*- coding: utf-8 -*-
"""
AI Agent API Client
Connects to DigitalOcean Agent Platform (Claude 3.5 Sonnet)

Adapted from GitHub-Slack webhook patterns:
- External API calls with retries
- Timeout handling
- Response parsing
- Error recovery
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging
import json

_logger = logging.getLogger(__name__)


class IPAIAgentAPI(models.AbstractModel):
    _name = 'ipai.agent.api'
    _description = 'AI Agent API Client'

    @api.model
    def call_agent(self, query, context):
        """
        Call AI agent with query and context
        Returns formatted response with actions

        Similar to GitHub webhook payload processing
        """
        config = self._get_agent_config()

        # Build request payload (similar to GitHub webhook payload)
        payload = self._build_agent_payload(query, context)

        # Call agent API with retry logic
        try:
            response = self._make_api_request(config['url'], payload, config)
            return self._parse_agent_response(response, context)
        except Exception as e:
            _logger.error(f"Agent API call failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f"⚠️ Agent unavailable: {str(e)}",
                'error': str(e),
            }

    def _get_agent_config(self):
        """Get agent configuration from Odoo settings"""
        IrConfigParam = self.env['ir.config_parameter'].sudo()

        return {
            'url': IrConfigParam.get_param(
                'ipai_agent.api_url',
                default='https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat'
            ),
            'api_key': IrConfigParam.get_param('ipai_agent.api_key', default=''),
            'timeout': int(IrConfigParam.get_param('ipai_agent.timeout', default='30')),
            'max_retries': int(IrConfigParam.get_param('ipai_agent.max_retries', default='2')),
        }

    def _build_agent_payload(self, query, context):
        """
        Build agent API payload
        Similar to GitHub webhook payload structure
        """
        return {
            'message': query,
            'context': {
                'user': {
                    'id': context['user_id'],
                    'name': context['user_name'],
                    'email': context['user_email'],
                },
                'agencies': context['agencies'],
                'channel': context['channel'],
                'permissions': context['permissions'],
                'company': {
                    'id': context['company_id'],
                    'name': context['company_name'],
                },
                'timestamp': context['timestamp'],
            },
            'tools': ['digitalocean', 'supabase', 'github', 'odoo'],
            'max_tokens': 4096,
        }

    def _make_api_request(self, url, payload, config):
        """
        Make HTTP request to agent API with retry logic
        Adapted from GitHub's webhook retry pattern
        """
        headers = {
            'Content-Type': 'application/json',
        }

        if config['api_key']:
            headers['Authorization'] = f"Bearer {config['api_key']}"

        max_retries = config['max_retries']
        timeout = config['timeout']

        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=timeout
                )

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    _logger.warning(f"Agent API timeout (attempt {attempt + 1}/{max_retries + 1})")
                    continue
                raise UserError(_('Agent API timeout after %d attempts') % (max_retries + 1))

            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    _logger.warning(f"Agent API error (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")
                    continue
                raise UserError(_('Agent API error: %s') % str(e))

    def _parse_agent_response(self, response, context):
        """
        Parse agent response and extract actions
        Similar to GitHub webhook response processing
        """
        message = response.get('message', '')
        actions = response.get('actions', [])

        # Execute authorized actions
        executed_actions = []
        for action in actions:
            try:
                result = self._execute_action(action, context)
                executed_actions.append({
                    **action,
                    'success': True,
                    'result': result,
                })
            except Exception as e:
                _logger.error(f"Action execution failed: {str(e)}", exc_info=True)
                executed_actions.append({
                    **action,
                    'success': False,
                    'error': str(e),
                })

        return {
            'success': True,
            'message': message,
            'actions': executed_actions,
            'execution_time': response.get('execution_time', 0),
        }

    def _execute_action(self, action, context):
        """
        Execute authorized action
        Similar to GitHub Actions workflow execution
        """
        action_type = action.get('type')
        user_id = context['user_id']
        user = self.env['res.users'].sudo().browse(user_id)

        # Map action types to handlers
        handlers = {
            'approve_expense': self._action_approve_expense,
            'deploy_service': self._action_deploy_service,
            'generate_bir_form': self._action_generate_bir_form,
            'query_data': self._action_query_data,
            'run_visual_test': self._action_run_visual_test,
        }

        handler = handlers.get(action_type)
        if not handler:
            raise UserError(_('Unknown action type: %s') % action_type)

        # Check user permissions
        self._check_action_permission(action_type, user, context)

        # Execute action with user context
        return handler(action, user, context)

    def _check_action_permission(self, action_type, user, context):
        """Check if user has permission to execute action"""
        permission_map = {
            'approve_expense': 'can_approve_expenses',
            'deploy_service': 'can_deploy',
            'generate_bir_form': 'can_manage_bir',
        }

        required_permission = permission_map.get(action_type)
        if required_permission and not context['permissions'].get(required_permission):
            raise AccessError(
                _('User %s does not have permission to %s') % (user.name, action_type)
            )

    def _action_approve_expense(self, action, user, context):
        """Approve expense sheets"""
        expense_ids = action.get('expense_ids', [])
        agency = action.get('agency')
        max_amount = action.get('max_amount')

        domain = [('id', 'in', expense_ids)]
        if agency:
            domain.append(('employee_id.department_id.name', 'ilike', agency))
        if max_amount:
            domain.append(('total_amount', '<=', max_amount))

        expenses = self.env['hr.expense.sheet'].sudo().search(domain)

        approved_count = 0
        for expense in expenses:
            if expense.state == 'submit':
                expense.sudo().approve_expense_sheets()
                approved_count += 1

        return {
            'approved_count': approved_count,
            'total_amount': sum(expenses.mapped('total_amount')),
        }

    def _action_deploy_service(self, action, user, context):
        """Trigger deployment via CLI"""
        import subprocess

        service = action.get('service')
        environment = action.get('environment', 'production')

        # Call ipai-cli (to be implemented)
        cmd = ['ipai', 'deploy', service, '--env', environment]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                raise UserError(result.stderr)

            return {
                'service': service,
                'environment': environment,
                'output': result.stdout,
            }
        except subprocess.TimeoutExpired:
            raise UserError(_('Deployment timeout after 5 minutes'))

    def _action_generate_bir_form(self, action, user, context):
        """Generate BIR tax form"""
        form_type = action.get('form_type')  # 1601-C, 1702-RT, 2550Q
        agency = action.get('agency')
        period = action.get('period')

        # TODO: Implement BIR form generation logic
        # For now, return placeholder

        return {
            'form_type': form_type,
            'agency': agency,
            'period': period,
            'file_url': '/web/content/attachment/placeholder',
        }

    def _action_query_data(self, action, user, context):
        """Query Odoo data"""
        model = action.get('model')
        domain = action.get('domain', [])
        fields_list = action.get('fields', [])

        # Security: only allow specific safe models
        allowed_models = [
            'hr.expense.sheet',
            'hr.expense',
            'account.move',
            'account.move.line',
            'res.partner',
        ]

        if model not in allowed_models:
            raise AccessError(_('Querying model %s is not allowed') % model)

        records = self.env[model].sudo().search(domain)

        if not fields_list:
            fields_list = ['id', 'name', 'display_name']

        return records.read(fields_list)

    def _action_run_visual_test(self, action, user, context):
        """Run visual parity tests"""
        import subprocess

        routes = action.get('routes', '/expenses,/tasks')

        cmd = ['ipai', 'test', 'visual', '--routes', routes]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,  # 3 minute timeout
            )

            return {
                'success': result.returncode == 0,
                'output': result.stdout,
            }
        except subprocess.TimeoutExpired:
            raise UserError(_('Visual test timeout after 3 minutes'))
