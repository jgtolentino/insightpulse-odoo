# -*- coding: utf-8 -*-

"""
InsightPulse Event Bus Controllers
Bi-directional event bridge between Odoo and Supabase
"""

from odoo import http
from odoo.http import request
import hmac
import hashlib
import json
import logging

_logger = logging.getLogger(__name__)


def _verify(sig, raw, secret):
    """
    Verify HMAC-SHA256 signature using timing-safe comparison

    Args:
        sig: Hex-encoded signature from header
        raw: Raw request bytes
        secret: Shared HMAC secret

    Returns:
        True if signature is valid, False otherwise
    """
    if not secret or not sig:
        return False

    try:
        mac = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
        return hmac.compare_digest(mac, sig or "")
    except Exception as e:
        _logger.error(f"HMAC verification error: {e}")
        return False


class EventBusController(http.Controller):
    """
    HTTP controllers for Odoo-Supabase event bridge

    Endpoints:
    - /api/agent/event_push - Receive events from Supabase
    - /api/agent/apply - Apply actions from Supabase
    """

    @http.route("/api/agent/event_push", type="json", auth="none", methods=["POST"], csrf=False)
    def event_push(self, **kw):
        """
        Receive events from Supabase → Odoo

        Expected headers:
        - x-signature: HMAC-SHA256 of raw request body

        Expected body:
        {
            "event_type": "supabase.event",
            "resource_id": "123",
            "payload": {...}
        }
        """
        req = request.httprequest

        # Get HMAC secret from system parameters
        secret = request.env['ir.config_parameter'].sudo().get_param('ip.hmac.secret', default="")
        if not secret:
            _logger.warning("ip.hmac.secret not configured")
            return request.make_json_response({"error": "server configuration error"}, status=500)

        # Verify signature
        sig = req.headers.get("x-signature", "")
        raw = req.get_data()  # raw bytes

        if not _verify(sig, raw, secret):
            _logger.warning(f"Invalid signature from {req.remote_addr}")
            return request.make_json_response({"error": "invalid signature"}, status=401)

        try:
            body = json.loads(raw.decode())
            event_type = body.get('event_type', 'unknown')
            resource_id = body.get('resource_id', '')

            _logger.info(f"Event received: {event_type} (resource: {resource_id})")

            # Log to ir.logging for audit trail
            request.env['ir.logging'].sudo().create({
                'name': 'supabase_event',
                'type': 'server',
                'dbname': request.env.cr.dbname,
                'level': 'INFO',
                'message': json.dumps(body)[:1024],
                'path': 'ip_event_bus',
                'line': 0,
                'func': 'event_push',
            })

            # TODO: Add custom event handling logic here
            # Example: trigger server actions, update records, etc.

            return {"ok": True, "event_type": event_type}

        except Exception as e:
            _logger.error(f"Error processing event: {e}")
            return request.make_json_response({"error": str(e)}, status=500)

    @http.route("/api/agent/apply", type="json", auth="none", methods=["POST"], csrf=False)
    def apply(self, **kw):
        """
        Apply actions from Supabase → Odoo

        Expected headers:
        - x-api-key: API key for authentication
        - x-signature: HMAC-SHA256 of raw request body

        Expected body:
        {
            "action": "account.move.post",
            "args": {"id": 1234}
        }

        Supported actions:
        - account.move.post: Post an account move
        - res.partner.update: Update partner record
        - (Add more as needed)
        """
        req = request.httprequest

        # Verify API key
        api_key = req.headers.get("x-api-key", "")
        conf_key = request.env['ir.config_parameter'].sudo().get_param('ip.odoo.api_key', default="")

        if not conf_key:
            _logger.warning("ip.odoo.api_key not configured")
            return request.make_json_response({"error": "server configuration error"}, status=500)

        if api_key != conf_key:
            _logger.warning(f"Invalid API key from {req.remote_addr}")
            return request.make_json_response({"error": "unauthorized"}, status=401)

        # Verify HMAC signature
        secret = request.env['ir.config_parameter'].sudo().get_param('ip.hmac.secret', default="")
        if not secret:
            _logger.warning("ip.hmac.secret not configured")
            return request.make_json_response({"error": "server configuration error"}, status=500)

        sig = req.headers.get("x-signature", "")
        raw = req.get_data()

        if not _verify(sig, raw, secret):
            _logger.warning(f"Invalid signature from {req.remote_addr}")
            return request.make_json_response({"error": "invalid signature"}, status=401)

        try:
            body = json.loads(raw.decode())
            action = body.get("action")
            args = body.get("args", {})

            _logger.info(f"Action requested: {action}")

            # Action router (extend as needed)
            if action == "account.move.post":
                move_id = int(args.get("id", 0))
                if not move_id:
                    return request.make_json_response({"error": "missing move id"}, status=400)

                move = request.env["account.move"].sudo().browse(move_id)
                if not move.exists():
                    return request.make_json_response({"error": "move not found"}, status=404)

                move.action_post()
                _logger.info(f"Posted account move {move_id}")
                return {"ok": True, "posted": move_id, "state": move.state}

            elif action == "res.partner.update":
                partner_id = int(args.get("id", 0))
                values = args.get("values", {})

                if not partner_id:
                    return request.make_json_response({"error": "missing partner id"}, status=400)

                partner = request.env["res.partner"].sudo().browse(partner_id)
                if not partner.exists():
                    return request.make_json_response({"error": "partner not found"}, status=404)

                partner.write(values)
                _logger.info(f"Updated partner {partner_id}")
                return {"ok": True, "updated": partner_id}

            else:
                _logger.warning(f"Unknown action: {action}")
                return request.make_json_response({"error": "unknown action"}, status=400)

        except Exception as e:
            _logger.error(f"Error applying action: {e}")
            return request.make_json_response({"error": str(e)}, status=500)
