# -*- coding: utf-8 -*-
"""
LLM Router with Gradient API Integration
Provides intelligent fallback when DigitalOcean Agent Platform is unavailable

Priority:
1. DigitalOcean Agent Platform (existing)
2. Gradient API (120B parameter models)
3. Error response with graceful degradation
"""

import os
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class LLMRouter:
    """
    Intelligent LLM routing with automatic fallback

    Usage:
        router = LLMRouter(env)
        response = router.chat(
            messages=[{"role": "user", "content": "Deploy ade-ocr"}],
            context={'user_id': 1, 'company': 'RIM'}
        )
    """

    def __init__(self, odoo_env):
        """
        Initialize LLM router

        Args:
            odoo_env: Odoo environment for config params
        """
        self.env = odoo_env
        self._gradient_client = None
        self._config = self._load_config()

    def _load_config(self):
        """Load LLM configuration from Odoo settings"""
        IrConfigParam = self.env['ir.config_parameter'].sudo()

        return {
            # DigitalOcean Agent Platform (primary)
            'do_agent_url': IrConfigParam.get_param(
                'ipai_agent.api_url',
                default='https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat'
            ),
            'do_agent_key': IrConfigParam.get_param('ipai_agent.api_key', default=''),

            # Gradient API (fallback)
            'gradient_enabled': IrConfigParam.get_param('ipai_agent.gradient_enabled', default='True') == 'True',
            'gradient_model': IrConfigParam.get_param('ipai_agent.gradient_model', default='openai-gpt-oss-120b'),
            'gradient_max_tokens': int(IrConfigParam.get_param('ipai_agent.gradient_max_tokens', default='500')),

            # General settings
            'timeout': int(IrConfigParam.get_param('ipai_agent.timeout', default='30')),
        }

    def _get_gradient_client(self):
        """
        Lazy-load Gradient client
        Only imports and initializes when needed
        """
        if self._gradient_client is not None:
            return self._gradient_client

        try:
            from gradient import Gradient

            # Get API key from environment variable
            model_access_key = os.environ.get('MODEL_ACCESS_KEY')

            if not model_access_key:
                _logger.warning("MODEL_ACCESS_KEY not set - Gradient API unavailable")
                return None

            self._gradient_client = Gradient(
                model_access_key=model_access_key
            )
            _logger.info("Gradient API client initialized successfully")
            return self._gradient_client

        except ImportError:
            _logger.warning("Gradient SDK not installed - run: pip install gradient")
            return None
        except Exception as e:
            _logger.error(f"Failed to initialize Gradient client: {str(e)}")
            return None

    def chat(self, messages, context=None, prefer_gradient=False):
        """
        Route chat request with intelligent fallback

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            context: Optional context dict (user, company, etc.)
            prefer_gradient: If True, try Gradient first (for testing)

        Returns:
            dict: {
                'content': str,
                'provider': 'digitalocean'|'gradient'|'error',
                'model': str,
                'success': bool
            }
        """
        if not prefer_gradient:
            # Try DigitalOcean Agent Platform first (normal flow)
            do_response = self._try_do_agent(messages, context)
            if do_response['success']:
                return do_response

        # Fallback to Gradient API
        if self._config['gradient_enabled']:
            gradient_response = self._try_gradient(messages)
            if gradient_response['success']:
                return gradient_response

        # All providers failed
        return {
            'content': '⚠️ All AI services temporarily unavailable. Please try again later.',
            'provider': 'error',
            'model': 'none',
            'success': False,
            'error': 'All LLM providers failed'
        }

    def _try_do_agent(self, messages, context):
        """
        Try DigitalOcean Agent Platform

        Returns response dict with success flag
        """
        try:
            import requests

            # Extract message content (simple text for DO agent)
            query = messages[-1].get('content', '') if messages else ''

            payload = {
                'message': query,
                'context': context or {},
                'max_tokens': 4096,
            }

            headers = {'Content-Type': 'application/json'}
            if self._config['do_agent_key']:
                headers['Authorization'] = f"Bearer {self._config['do_agent_key']}"

            response = requests.post(
                self._config['do_agent_url'],
                json=payload,
                headers=headers,
                timeout=self._config['timeout']
            )

            if response.status_code == 200:
                data = response.json()
                _logger.info("DigitalOcean Agent Platform response received")
                return {
                    'content': data.get('message', ''),
                    'provider': 'digitalocean',
                    'model': 'claude-3.5-sonnet',
                    'success': True,
                    'actions': data.get('actions', []),
                }

            _logger.warning(f"DO Agent returned status {response.status_code}")
            return {'success': False, 'error': f'HTTP {response.status_code}'}

        except Exception as e:
            _logger.warning(f"DigitalOcean Agent unavailable: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _try_gradient(self, messages):
        """
        Try Gradient API

        Returns response dict with success flag
        """
        client = self._get_gradient_client()
        if not client:
            return {'success': False, 'error': 'Gradient client not available'}

        try:
            response = client.chat.completions.create(
                messages=messages,
                model=self._config['gradient_model'],
                max_tokens=self._config['gradient_max_tokens']
            )

            content = response.choices[0].message.content
            _logger.info(f"Gradient API response received (model: {self._config['gradient_model']})")

            return {
                'content': content,
                'provider': 'gradient',
                'model': self._config['gradient_model'],
                'success': True,
                'usage': {
                    'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                    'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                    'total_tokens': getattr(response.usage, 'total_tokens', 0),
                }
            }

        except Exception as e:
            _logger.error(f"Gradient API failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_status(self):
        """
        Check availability of all LLM providers

        Returns:
            dict: Status of each provider
        """
        status = {
            'digitalocean': {
                'configured': bool(self._config['do_agent_url']),
                'available': False,
            },
            'gradient': {
                'configured': self._config['gradient_enabled'] and bool(os.environ.get('MODEL_ACCESS_KEY')),
                'available': False,
            }
        }

        # Quick health check
        try:
            test_messages = [{"role": "user", "content": "ping"}]

            # Test DO Agent
            do_result = self._try_do_agent(test_messages, {})
            status['digitalocean']['available'] = do_result['success']

            # Test Gradient
            if status['gradient']['configured']:
                gradient_result = self._try_gradient(test_messages)
                status['gradient']['available'] = gradient_result['success']

        except Exception as e:
            _logger.error(f"Status check failed: {str(e)}")

        return status
