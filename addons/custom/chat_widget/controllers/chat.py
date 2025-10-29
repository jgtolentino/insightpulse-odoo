import json
import logging
import requests

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ChatWidgetController(http.Controller):
    """Controller for InsightPulseAI Chat Widget API endpoint."""

    @http.route('/api/chat', type='json', auth='public', methods=['POST'], csrf=False)
    def chat_endpoint(self, **kwargs):
        """
        API endpoint for chat widget with LLM integration.

        This endpoint integrates with the microservices LLM service to provide
        intelligent responses to user queries.

        Expected POST body:
        {
            "message": "user message here",
            "source": "welcome-widget"
        }

        Returns:
        {
            "reply": "bot response here"
        }
        """
        try:
            # Get the message from the request
            message = kwargs.get('message', '').strip()
            source = kwargs.get('source', 'unknown')

            if not message:
                return {'reply': None}

            _logger.info(
                f"Chat widget request from {source}: {message[:50]}..."
            )

            # Get active microservices configuration
            config = request.env['microservices.config'].sudo().search(
                [('is_active', '=', True)],
                limit=1
            )

            if not config or not config.llm_service_url:
                _logger.warning("No active LLM service configuration found")
                return {'reply': None}

            # Call LLM service
            try:
                llm_url = config.llm_service_url.rstrip('/')
                auth_token = config._get_decrypted_auth_token()

                # Prepare headers
                headers = {
                    'Content-Type': 'application/json'
                }
                if auth_token:
                    headers['Authorization'] = f'Bearer {auth_token}'

                # Prepare payload for LLM service
                # This assumes the LLM service expects a chat completion format
                payload = {
                    'message': message,
                    'source': source,
                    'context': {
                        'product': 'InsightPulseAI',
                        'channel': 'website-chat-widget'
                    }
                }

                # Call LLM service with timeout
                response = requests.post(
                    f"{llm_url}/chat",
                    json=payload,
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    reply = data.get('reply') or data.get('response') or data.get('message')

                    if reply:
                        _logger.info(f"LLM service responded successfully")
                        return {'reply': reply.strip()}
                    else:
                        _logger.warning(f"LLM service returned empty response")
                        return {'reply': None}
                else:
                    _logger.error(
                        f"LLM service returned status {response.status_code}: {response.text[:200]}"
                    )
                    return {'reply': None}

            except requests.exceptions.Timeout:
                _logger.error("LLM service request timed out")
                return {'reply': None}
            except requests.exceptions.ConnectionError as e:
                _logger.error(f"Could not connect to LLM service: {e}")
                return {'reply': None}
            except Exception as e:
                _logger.error(f"Error calling LLM service: {str(e)}")
                return {'reply': None}

        except Exception as e:
            _logger.error(f"Error in chat endpoint: {str(e)}")
            return {'reply': None}
