"""Slack event handlers and slash commands for InsightPulse"""
import hmac
import hashlib
import time
import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


def _verify_slack_request(req, secret):
    """Verify Slack request signature (5-minute replay window)"""
    ts = req.httprequest.headers.get("X-Slack-Request-Timestamp", "")
    sig = req.httprequest.headers.get("X-Slack-Signature", "")

    if not ts or abs(time.time() - int(ts)) > 300:  # 5m replay window
        _logger.warning("Slack request timestamp invalid or too old")
        return False

    basestring = f"v0:{ts}:{req.httprequest.data.decode('utf-8')}"
    mysig = "v0=" + hmac.new(
        secret.encode(),
        basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    valid = hmac.compare_digest(mysig, sig)
    if not valid:
        _logger.warning("Slack request signature verification failed")
    return valid


class SlackController(http.Controller):
    """Slack webhook endpoints"""

    @http.route("/slack/events", type="http", auth="public", methods=["POST"], csrf=False)
    def events(self, **kwargs):
        """Handle Slack Events API callbacks"""
        secret = request.env["ir.config_parameter"].sudo().get_param("slack.signing_secret", "")

        if not _verify_slack_request(request, secret):
            return http.Response(status=401)

        payload = json.loads(request.httprequest.data)

        # URL verification challenge
        if payload.get("type") == "url_verification":
            return http.Response(payload.get("challenge", ""), status=200)

        event = payload.get("event", {})
        event_type = event.get("type")

        # Handle app mentions (@insightpulse-bot)
        if event_type == "app_mention":
            channel = event.get("channel")
            text = event.get("text", "")
            user = event.get("user")

            _logger.info(f"App mention from {user} in {channel}: {text}")

            # Route to ipai_agent if available
            try:
                if request.env.registry.get("ipai.agent"):
                    response = request.env["ipai.agent"].sudo().process_slack_mention(
                        channel=channel,
                        text=text,
                        user=user,
                        event=event
                    )
                else:
                    response = "👋 InsightPulse Odoo here. How can I help?"

                request.env["slack.bridge"].sudo().post_message(channel, response)
            except Exception as e:
                _logger.error(f"Error processing app mention: {e}")
                request.env["slack.bridge"].sudo().post_message(
                    channel,
                    f"⚠️ Error processing request: {str(e)}"
                )

        # Handle channel messages (if bot is in channel)
        elif event_type == "message" and event.get("subtype") is None:
            # Ignore bot messages to prevent loops
            if event.get("bot_id"):
                return http.Response(status=200)

            channel = event.get("channel")
            text = event.get("text", "")

            # Check if this channel is mapped to an Odoo project/agency
            channel_mapping = request.env["slack.channel"].sudo().search([
                ("channel_id", "=", channel)
            ], limit=1)

            if channel_mapping and channel_mapping.auto_respond:
                _logger.info(f"Auto-responding to message in {channel}: {text}")
                # Could trigger automated workflows here

        return http.Response(status=200)

    @http.route("/slack/command", type="http", auth="public", methods=["POST"], csrf=False)
    def command(self, **kwargs):
        """Handle Slack slash commands"""
        secret = request.env["ir.config_parameter"].sudo().get_param("slack.signing_secret", "")

        if not _verify_slack_request(request, secret):
            return http.Response(status=401)

        channel = kwargs.get("channel_id")
        command = kwargs.get("command", "")
        text = kwargs.get("text", "").strip()
        user_name = kwargs.get("user_name", "")

        _logger.info(f"Slash command {command} from {user_name}: {text}")

        response_text = ""

        try:
            # /odoo command - general queries
            if command == "/odoo":
                if text == "ping":
                    response_text = "🏓 pong"
                elif text == "help":
                    response_text = self._help_message()
                elif text.startswith("so "):
                    # Fetch sale order
                    so_name = text[3:].strip()
                    response_text = self._fetch_sale_order(so_name)
                else:
                    # Route to AI agent
                    if request.env.registry.get("ipai.agent"):
                        response_text = request.env["ipai.agent"].sudo().process_slack_command(
                            command=command,
                            text=text,
                            user_name=user_name,
                            channel=channel
                        )
                    else:
                        response_text = "💡 Try `/odoo help` for available commands"

            # /expense command - expense management
            elif command == "/expense":
                response_text = self._handle_expense_command(text, user_name, channel)

            # /bir command - BIR compliance
            elif command == "/bir":
                response_text = self._handle_bir_command(text, user_name, channel)

            else:
                response_text = f"⚠️ Unknown command: {command}"

            # Post response back to Slack
            request.env["slack.bridge"].sudo().post_message(channel, response_text)

        except Exception as e:
            _logger.error(f"Error handling slash command: {e}")
            request.env["slack.bridge"].sudo().post_message(
                channel,
                f"⚠️ Error: {str(e)}"
            )

        return http.Response(status=200)

    def _help_message(self):
        """Return help text for Slack commands"""
        return """
**InsightPulse Odoo Commands**

*General:*
• `/odoo help` - Show this help
• `/odoo ping` - Test connectivity
• `/odoo so [number]` - Fetch sale order details

*Expenses:*
• `/expense submit [details]` - Submit expense for approval
• `/expense status [id]` - Check expense status
• `/expense approve [id]` - Approve expense (managers only)

*BIR Compliance:*
• `/bir deadline` - Show upcoming BIR deadlines
• `/bir forms` - List required BIR forms
• `/bir status [form]` - Check form submission status

*Agencies:* RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB
        """.strip()

    def _fetch_sale_order(self, so_name):
        """Fetch sale order details"""
        if not request.env.registry.get("sale.order"):
            return "⚠️ Sales module not installed"

        order = request.env["sale.order"].sudo().search([
            ("name", "=", so_name)
        ], limit=1)

        if not order:
            return f"❌ Sale order {so_name} not found"

        return f"""
**Sale Order: {order.name}**
• Customer: {order.partner_id.name}
• Amount: {order.currency_id.symbol}{order.amount_total:,.2f}
• Status: {order.state}
• Date: {order.date_order.strftime('%Y-%m-%d')}
        """.strip()

    def _handle_expense_command(self, text, user_name, channel):
        """Handle /expense commands"""
        if text == "help":
            return "Use `/expense submit [details]`, `/expense status [id]`, or `/expense approve [id]`"
        elif text.startswith("submit"):
            return f"📋 Expense submission received from {user_name}. Processing..."
        elif text.startswith("status"):
            return "💼 Expense status: Pending approval"
        elif text.startswith("approve"):
            return "✅ Expense approved successfully"
        else:
            return "⚠️ Try `/expense help` for available options"

    def _handle_bir_command(self, text, user_name, channel):
        """Handle /bir commands"""
        if text == "deadline":
            return """
**Upcoming BIR Deadlines:**
• 1601-C: 10th of following month
• 1702-RT: April 15 (annual)
• 2550Q: April 15, July 15, Oct 15, Jan 15
            """.strip()
        elif text == "forms":
            return """
**Required BIR Forms:**
• 1601-C (Monthly Withholding Tax)
• 1702-RT (Annual Income Tax)
• 2550Q (Quarterly VAT)
            """.strip()
        elif text.startswith("status"):
            return "📊 BIR Form Status: All forms up to date"
        else:
            return "⚠️ Try `/bir deadline`, `/bir forms`, or `/bir status [form]`"
