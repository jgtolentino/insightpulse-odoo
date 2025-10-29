import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ChatWidgetController(http.Controller):
    """Controller for InsightPulseAI Chat Widget API endpoint."""

    @http.route('/api/chat', type='json', auth='public', methods=['POST'], csrf=False)
    def chat_endpoint(self, **kwargs):
        """
        Optional API endpoint for chat widget.

        This endpoint can be extended to integrate with AI services, knowledge bases,
        or other chat backends. Currently returns a simple fallback response.

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

            # Placeholder for AI/knowledge base integration
            # TODO: Integrate with OpenAI, Claude, or internal knowledge base

            # For now, return None to let the widget use its rule-based responses
            return {'reply': None}

        except Exception as e:
            _logger.error(f"Error in chat endpoint: {str(e)}")
            return {'reply': None}
