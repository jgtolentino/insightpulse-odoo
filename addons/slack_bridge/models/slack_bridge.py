"""Slack Bridge API client for posting messages"""
import requests
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class SlackBridge(models.AbstractModel):
    """Helper methods for Slack API interactions"""
    _name = "slack.bridge"
    _description = "Slack Bridge Helpers"

    @api.model
    def post_message(self, channel, text, thread_ts=None, blocks=None):
        """Post a message to a Slack channel

        Args:
            channel: Slack channel ID (e.g., 'C01234567')
            text: Message text (fallback for notifications)
            thread_ts: Optional thread timestamp for threaded replies
            blocks: Optional Block Kit blocks for rich formatting

        Returns:
            dict: Slack API response
        """
        token = self.env["ir.config_parameter"].sudo().get_param("slack.bot_token", "")

        if not token:
            _logger.error("Slack bot token not configured")
            raise ValueError("Slack bot token not configured in System Parameters")

        payload = {
            "channel": channel,
            "text": text,
        }

        if thread_ts:
            payload["thread_ts"] = thread_ts

        if blocks:
            payload["blocks"] = blocks

        try:
            response = requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()

            if not result.get("ok"):
                _logger.error(f"Slack API error: {result.get('error')}")
                raise ValueError(f"Slack API error: {result.get('error')}")

            _logger.info(f"Posted message to {channel}: {text[:50]}...")
            return result

        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to post Slack message: {e}")
            raise

    @api.model
    def post_expense_notification(self, expense_id, action="created"):
        """Post expense notification to appropriate Slack channel

        Args:
            expense_id: Expense record ID
            action: Action type (created, approved, rejected, paid)
        """
        expense = self.env["hr.expense"].browse(expense_id)
        if not expense.exists():
            return

        # Find agency channel mapping
        channel_mapping = self.env["slack.channel"].search([
            ("agency_code", "=", expense.company_id.code)
        ], limit=1)

        if not channel_mapping:
            _logger.warning(f"No Slack channel mapping for company {expense.company_id.name}")
            return

        emoji_map = {
            "created": "📋",
            "approved": "✅",
            "rejected": "❌",
            "paid": "💰"
        }
        emoji = emoji_map.get(action, "💼")

        message = f"{emoji} **Expense {action.capitalize()}**\n"
        message += f"• Amount: {expense.currency_id.symbol}{expense.total_amount:,.2f}\n"
        message += f"• Employee: {expense.employee_id.name}\n"
        message += f"• Description: {expense.name}\n"
        message += f"• Date: {expense.date.strftime('%Y-%m-%d')}"

        self.post_message(channel_mapping.channel_id, message)

    @api.model
    def post_bir_deadline_reminder(self, form_name, deadline_date, days_remaining):
        """Post BIR deadline reminder to finance channel

        Args:
            form_name: BIR form name (e.g., '1601-C')
            deadline_date: Deadline date object
            days_remaining: Days until deadline
        """
        # Find finance channel
        channel_mapping = self.env["slack.channel"].search([
            ("channel_type", "=", "finance")
        ], limit=1)

        if not channel_mapping:
            _logger.warning("No finance Slack channel configured")
            return

        urgency_emoji = "🚨" if days_remaining <= 3 else "⏰"

        message = f"{urgency_emoji} **BIR Deadline Reminder**\n"
        message += f"• Form: {form_name}\n"
        message += f"• Deadline: {deadline_date.strftime('%Y-%m-%d')}\n"
        message += f"• Days remaining: {days_remaining}\n"

        if days_remaining <= 3:
            message += "\n**⚠️ URGENT: Deadline approaching!**"

        self.post_message(channel_mapping.channel_id, message)

    @api.model
    def post_sale_order_notification(self, order_id):
        """Post sale order creation notification

        Args:
            order_id: Sale order record ID
        """
        order = self.env["sale.order"].browse(order_id)
        if not order.exists():
            return

        # Find sales channel
        channel_mapping = self.env["slack.channel"].search([
            ("channel_type", "=", "sales")
        ], limit=1)

        if not channel_mapping:
            return

        message = f"💼 **New Sale Order: {order.name}**\n"
        message += f"• Customer: {order.partner_id.name}\n"
        message += f"• Amount: {order.currency_id.symbol}{order.amount_total:,.2f}\n"
        message += f"• Salesperson: {order.user_id.name}\n"
        message += f"• Date: {order.date_order.strftime('%Y-%m-%d')}"

        self.post_message(channel_mapping.channel_id, message)
