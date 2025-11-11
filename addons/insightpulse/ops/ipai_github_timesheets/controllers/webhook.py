# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import http
from odoo.http import request
import logging
import json
import hmac
import hashlib

_logger = logging.getLogger(__name__)


class GitHubWebhookController(http.Controller):
    """Controller for receiving GitHub webhook events"""

    @http.route("/github/webhook", type="json", auth="public", methods=["POST"], csrf=False)
    def github_webhook(self, **kwargs):
        """
        Endpoint for GitHub webhooks

        Setup in GitHub:
        1. Go to Settings → Webhooks → Add webhook
        2. Payload URL: https://your-odoo-domain.com/github/webhook
        3. Content type: application/json
        4. Secret: (same as configured in Odoo GitHub Config)
        5. Events: Pull requests, Issues, Projects (or all)
        """
        try:
            # Get the request data
            payload = json.loads(request.httprequest.data.decode("utf-8"))
            event_type = request.httprequest.headers.get("X-GitHub-Event")
            signature = request.httprequest.headers.get("X-Hub-Signature-256")
            delivery_id = request.httprequest.headers.get("X-GitHub-Delivery")

            _logger.info(
                "Received GitHub webhook: event=%s, delivery=%s", event_type, delivery_id
            )

            # Verify webhook signature
            config = request.env["github.config"].sudo().search([], limit=1)
            if not config:
                _logger.error("No GitHub config found")
                return {"status": "error", "message": "No GitHub config"}

            if config.webhook_secret:
                if not self._verify_signature(
                    signature, request.httprequest.data, config.webhook_secret
                ):
                    _logger.warning("Invalid webhook signature")
                    return {"status": "error", "message": "Invalid signature"}

            # Route to appropriate handler
            if event_type == "pull_request":
                return self._handle_pull_request(payload, config)
            elif event_type == "issues":
                return self._handle_issue(payload, config)
            elif event_type == "project":
                return self._handle_project(payload, config)
            elif event_type == "ping":
                return {"status": "success", "message": "Pong!"}
            else:
                _logger.info("Unhandled event type: %s", event_type)
                return {"status": "ignored", "message": f"Event {event_type} not handled"}

        except Exception as e:
            _logger.error("GitHub webhook error: %s", str(e), exc_info=True)
            return {"status": "error", "message": str(e)}

    def _verify_signature(self, signature, payload, secret):
        """Verify GitHub webhook signature"""
        if not signature:
            return False

        expected_signature = "sha256=" + hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def _handle_pull_request(self, payload, config):
        """Handle pull_request event"""
        action = payload.get("action")
        pr_data = payload.get("pull_request", {})

        _logger.info("PR webhook: action=%s, pr=%s", action, pr_data.get("number"))

        # Determine state
        if pr_data.get("merged"):
            state = "merged"
        elif pr_data.get("state") == "closed":
            state = "closed"
        else:
            state = "open"

        # Find or create PR record
        pr_model = request.env["github.pull.request"].sudo()
        pr_record = pr_model.search([("github_pr_id", "=", pr_data["id"])], limit=1)

        vals = {
            "github_pr_number": pr_data["number"],
            "github_pr_id": pr_data["id"],
            "title": pr_data["title"],
            "description": pr_data.get("body", ""),
            "github_url": pr_data["html_url"],
            "github_state": state,
            "github_author": pr_data["user"]["login"],
            "github_created_at": pr_data["created_at"],
            "github_updated_at": pr_data["updated_at"],
            "github_merged_at": pr_data.get("merged_at"),
            "github_closed_at": pr_data.get("closed_at"),
            "source_branch": pr_data["head"]["ref"],
            "target_branch": pr_data["base"]["ref"],
            "config_id": config.id,
        }

        if pr_record:
            pr_record.write(vals)
        else:
            pr_record = pr_model.create(vals)

            # Auto-create task if enabled
            if config.auto_create_tasks and state == "open":
                pr_record.action_create_task()

        # Handle merged PRs
        if (
            action == "closed"
            and pr_data.get("merged")
            and config.prompt_timesheet_on_merge
            and not pr_record.timesheet_prompted
        ):
            pr_record.action_prompt_timesheet()

        return {"status": "success", "pr_number": pr_data["number"], "action": action}

    def _handle_issue(self, payload, config):
        """Handle issues event"""
        action = payload.get("action")
        issue_data = payload.get("issue", {})

        _logger.info("Issue webhook: action=%s, issue=%s", action, issue_data.get("number"))

        # Similar to PR handling (implementation can be added as needed)
        return {"status": "success", "issue_number": issue_data.get("number"), "action": action}

    def _handle_project(self, payload, config):
        """Handle project event"""
        action = payload.get("action")
        project_data = payload.get("project", {})

        _logger.info("Project webhook: action=%s, project=%s", action, project_data.get("name"))

        # Trigger project sync
        if config.sync_projects:
            request.env["github.project"].sudo()._sync_from_github(config)

        return {"status": "success", "project_name": project_data.get("name"), "action": action}
