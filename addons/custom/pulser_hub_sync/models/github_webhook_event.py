import json
import logging

from odoo import api, fields, models
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class GitHubWebhookEvent(models.Model):
    _name = "github.webhook.event"
    _description = "GitHub Webhook Event Log"
    _order = "create_date desc"

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    event_type = fields.Char(string="Event Type", required=True, index=True)
    delivery_id = fields.Char(string="Delivery ID", required=True, index=True)
    installation_id = fields.Char(string="Installation ID", index=True)
    repository = fields.Char(string="Repository")
    sender = fields.Char(string="Sender")

    payload = fields.Text(string="Payload", help="Full JSON payload from GitHub")
    processed = fields.Boolean(string="Processed", default=False)
    processing_error = fields.Text(string="Processing Error")

    create_date = fields.Datetime(string="Received At", readonly=True)

    @api.depends("event_type", "repository", "delivery_id")
    def _compute_name(self):
        for record in self:
            repo_name = (
                record.repository.split("/")[-1] if record.repository else "unknown"
            )
            record.name = (
                f"{record.event_type} on {repo_name} ({record.delivery_id[:8]})"
            )

    def action_reprocess(self):
        """Reprocess failed webhook event"""
        self.ensure_one()
        # Implementation would call the controller's _process_webhook_event method
        self.write({"processed": False, "processing_error": False})
        return True

    def action_view_payload(self):
        """View full webhook payload"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Webhook Payload: {self.name}",
            "res_model": "github.webhook.event",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    @job
    def process_webhook_async(self):
        """Process webhook event asynchronously via queue_job"""
        self.ensure_one()
        try:
            _logger.info(
                f"Processing webhook event {self.delivery_id} ({self.event_type})"
            )

            payload = json.loads(self.payload)

            # Call event-specific handlers
            self._dispatch_event(self.event_type, payload)

            self.write(
                {
                    "processed": True,
                    "processing_error": False,
                }
            )
            _logger.info(f"Webhook {self.delivery_id} processed successfully")

        except Exception as e:
            _logger.error(f"Webhook processing error: {e}", exc_info=True)
            self.write(
                {
                    "processed": False,
                    "processing_error": str(e),
                }
            )
            raise

    def _dispatch_event(self, event_type, payload):
        """Dispatch to event-specific handler methods"""
        handler_map = {
            "push": self._handle_push,
            "pull_request": self._handle_pull_request,
            "issues": self._handle_issues,
            "workflow_run": self._handle_workflow_run,
        }

        handler = handler_map.get(event_type)
        if handler:
            handler(payload)
        else:
            _logger.info(f"No handler for event type: {event_type}")

    def _handle_push(self, payload):
        """Handle push events"""
        ref = payload.get("ref", "")
        repository = payload.get("repository", {}).get("full_name", "")
        commits = payload.get("commits", [])
        _logger.info(f"Push to {repository} on {ref}: {len(commits)} commits")
        # Add your custom logic here

    def _handle_pull_request(self, payload):
        """Handle pull request events"""
        action = payload.get("action", "")
        pr_number = payload.get("pull_request", {}).get("number", "")
        repository = payload.get("repository", {}).get("full_name", "")
        _logger.info(f"PR #{pr_number} {action} in {repository}")
        # Add your custom logic here

    def _handle_issues(self, payload):
        """Handle issues events"""
        action = payload.get("action", "")
        issue_number = payload.get("issue", {}).get("number", "")
        repository = payload.get("repository", {}).get("full_name", "")
        _logger.info(f"Issue #{issue_number} {action} in {repository}")
        # Add your custom logic here

    def _handle_workflow_run(self, payload):
        """Handle workflow run events"""
        conclusion = payload.get("workflow_run", {}).get("conclusion", "")
        workflow_name = payload.get("workflow_run", {}).get("name", "")
        repository = payload.get("repository", {}).get("full_name", "")
        _logger.info(f"Workflow '{workflow_name}' {conclusion} in {repository}")
        # Add your custom logic here
