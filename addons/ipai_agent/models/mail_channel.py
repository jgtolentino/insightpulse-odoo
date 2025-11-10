# -*- coding: utf-8 -*-
"""
AI Agent Integration with Odoo Discuss
Adapts GitHub-Slack webhook patterns for Odoo messaging

Key patterns from GitHub-Slack integration:
- Webhook receivers → Odoo message_post hook
- Slash commands → @ipai-bot mentions
- Interactive messages → Odoo chatter formatting
- OAuth → Odoo's built-in authentication
"""

import logging
import re

from odoo.exceptions import UserError

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class MailChannel(models.Model):
    _inherit = "mail.channel"

    is_agent_enabled = fields.Boolean(
        string="AI Agent Enabled",
        default=False,
        help="Enable AI agent responses in this channel",
    )


class MailMessage(models.Model):
    _inherit = "mail.message"

    is_agent_query = fields.Boolean(
        string="AI Agent Query", default=False, help="Message was processed by AI agent"
    )
    agent_response_id = fields.Many2one(
        "mail.message", string="Agent Response", help="AI agent response to this query"
    )

    @api.model
    def create(self, vals):
        """
        Intercept message creation to detect AI agent mentions
        Similar to GitHub webhook receiver pattern
        """
        message = super(MailMessage, self).create(vals)

        # Check if message mentions @ipai-bot
        if self._should_trigger_agent(message):
            self._process_agent_query(message)

        return message

    def _should_trigger_agent(self, message):
        """
        Determine if message should trigger AI agent
        Adapted from GitHub-Slack slash command detection
        """
        # Skip if no body
        if not message.body:
            return False

        # Check for @ipai-bot mention
        if "@ipai-bot" not in message.body.lower():
            return False

        # Check if channel has agent enabled
        if message.model == "mail.channel":
            channel = self.env["mail.channel"].browse(message.res_id)
            if not channel.is_agent_enabled:
                return False

        # Skip agent's own messages (prevent loops)
        bot_user = self.env.ref("ipai_agent.user_agent_bot", raise_if_not_found=False)
        if bot_user and message.author_id.id == bot_user.partner_id.id:
            return False

        return True

    def _process_agent_query(self, message):
        """
        Process AI agent query asynchronously
        Adapted from GitHub webhook processing pattern
        """
        try:
            # Mark as agent query
            message.write({"is_agent_query": True})

            # Extract query text (remove @ipai-bot mention)
            query = re.sub(r"@ipai-bot", "", message.body, flags=re.IGNORECASE).strip()

            # Get user context (similar to GitHub user metadata)
            context = self._build_agent_context(message)

            # Call agent API (similar to GitHub API webhook)
            agent_api = self.env["ipai.agent.api"]
            response = agent_api.call_agent(query, context)

            # Post agent response (similar to Slack message posting)
            self._post_agent_response(message, response)

            # Log interaction
            self._log_agent_interaction(message, query, response, context)

        except Exception as e:
            _logger.error(f"AI Agent error: {str(e)}", exc_info=True)
            self._post_error_response(message, str(e))

    def _build_agent_context(self, message):
        """
        Build context for AI agent
        Adapted from GitHub-Slack user metadata pattern
        """
        user = (
            message.author_id.user_ids[0]
            if message.author_id.user_ids
            else self.env.user
        )

        # Get user's agencies (from partner categories/tags)
        agencies = user.partner_id.category_id.mapped("name")

        # Get channel info
        channel_name = None
        if message.model == "mail.channel":
            channel = self.env["mail.channel"].browse(message.res_id)
            channel_name = channel.name

        # Check user permissions (similar to GitHub scopes)
        permissions = {
            "can_approve_expenses": user.has_group(
                "hr_expense.group_hr_expense_team_approver"
            ),
            "can_deploy": user.has_group("ipai_agent.group_deployer"),
            "can_manage_bir": user.has_group("account.group_account_manager"),
            "is_admin": user.has_group("base.group_system"),
        }

        return {
            "user_id": user.id,
            "user_name": user.name,
            "user_email": user.email,
            "agencies": agencies,
            "channel": channel_name,
            "permissions": permissions,
            "company_id": user.company_id.id,
            "company_name": user.company_id.name,
            "timestamp": fields.Datetime.now().isoformat(),
        }

    def _post_agent_response(self, original_message, response):
        """
        Post AI agent response to channel
        Adapted from Slack message posting API
        """
        bot_user = self.env.ref("ipai_agent.user_agent_bot", raise_if_not_found=False)
        if not bot_user:
            raise UserError(
                _("AI Agent bot user not configured. Please install ipai_agent data.")
            )

        # Format response body (similar to Slack message formatting)
        body = self._format_agent_response(response)

        # Post message in same channel/thread
        response_message = self.env["mail.message"].create(
            {
                "model": original_message.model,
                "res_id": original_message.res_id,
                "body": body,
                "author_id": bot_user.partner_id.id,
                "message_type": "comment",
                "subtype_id": self.env.ref("mail.mt_comment").id,
                "parent_id": original_message.id,  # Thread reply
            }
        )

        # Link response to original query
        original_message.write({"agent_response_id": response_message.id})

        return response_message

    def _format_agent_response(self, response):
        """
        Format agent response with Odoo HTML
        Adapted from Slack message blocks/attachments
        """
        message = response.get("message", "")
        actions = response.get("actions", [])

        # Build formatted response
        html_parts = [f"<p>{message}</p>"]

        # Add action summaries (similar to Slack action blocks)
        if actions:
            html_parts.append("<hr/><strong>Actions Executed:</strong><ul>")
            for action in actions:
                status = "✅" if action.get("success") else "❌"
                html_parts.append(
                    f'<li>{status} {action.get("description", action.get("type"))}</li>'
                )
            html_parts.append("</ul>")

        # Add metadata (similar to Slack message footer)
        if response.get("execution_time"):
            html_parts.append(
                f'<p><small><i>Response time: {response["execution_time"]}s</i></small></p>'
            )

        return "".join(html_parts)

    def _post_error_response(self, original_message, error_message):
        """Post error response to user"""
        bot_user = self.env.ref("ipai_agent.user_agent_bot", raise_if_not_found=False)
        if not bot_user:
            return

        self.env["mail.message"].create(
            {
                "model": original_message.model,
                "res_id": original_message.res_id,
                "body": f"<p>⚠️ <strong>Error</strong>: {error_message}</p>",
                "author_id": bot_user.partner_id.id,
                "message_type": "comment",
                "subtype_id": self.env.ref("mail.mt_comment").id,
                "parent_id": original_message.id,
            }
        )

    def _log_agent_interaction(self, message, query, response, context):
        """Log agent interaction for analytics"""
        self.env["ipai.agent.log"].create(
            {
                "message_id": message.id,
                "user_id": context["user_id"],
                "query": query,
                "response": response.get("message", ""),
                "actions": str(response.get("actions", [])),
                "execution_time": response.get("execution_time", 0),
                "success": response.get("success", True),
                "error_message": response.get("error"),
                "context": str(context),
            }
        )
