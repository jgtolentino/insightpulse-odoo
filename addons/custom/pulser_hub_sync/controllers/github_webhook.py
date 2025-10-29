import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timedelta

import jwt
import requests

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

# GitHub App credentials from environment
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID", "2191216")
GITHUB_APP_PEM_PATH = os.getenv(
    "GITHUB_APP_PEM_PATH", os.path.expanduser("~/.github/apps/pulser-hub.pem")
)

# Note: CLIENT_ID and CLIENT_SECRET only needed if using OAuth user flow (we use JWT instead)


class GitHubWebhookController(http.Controller):

    @http.route(
        "/odoo/github/health", type="http", auth="public", methods=["GET"], csrf=False
    )
    def health_check(self):
        """Health check endpoint for monitoring"""
        import json

        return json.dumps(
            {
                "status": "ok",
                "service": "pulser-hub-sync",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    @http.route(
        "/pulser/issue", type="json", auth="public", methods=["POST"], csrf=False
    )
    def create_issue_api(self, **kwargs):
        """
        API endpoint to create GitHub issues

        POST /pulser/issue
        {
            "owner": "jgtolentino",
            "repo": "insightpulse-odoo",
            "title": "Issue title",
            "body": "Issue description (markdown supported)",
            "labels": ["bug", "urgent"],  // optional
            "assignees": ["jgtolentino"]  // optional
        }

        Returns:
        {
            "status": "success",
            "issue_number": 123,
            "url": "https://github.com/owner/repo/issues/123"
        }
        """
        try:
            # Get request data
            data = request.jsonrequest or kwargs

            owner = data.get("owner")
            repo = data.get("repo")
            title = data.get("title")
            body = data.get("body", "")
            labels = data.get("labels")
            assignees = data.get("assignees")

            if not all([owner, repo, title]):
                return {
                    "status": "error",
                    "message": "Missing required fields: owner, repo, title",
                }

            # Get integration and create issue
            integration = (
                request.env["github.integration"]
                .sudo()
                .get_integration_for_repo(owner, repo)
            )
            result = integration.create_issue(
                owner, repo, title, body, labels, assignees
            )

            return {
                "status": "success",
                "issue_number": result["number"],
                "url": result["html_url"],
                "api_url": result["url"],
            }

        except Exception as e:
            _logger.error(f"Issue creation error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    @http.route(
        "/pulser/commit", type="json", auth="public", methods=["POST"], csrf=False
    )
    def commit_file_api(self, **kwargs):
        """
        API endpoint to commit files to GitHub

        POST /pulser/commit
        {
            "owner": "jgtolentino",
            "repo": "insightpulse-odoo",
            "path": "docs/README.md",
            "content": "# File content here",
            "message": "Update README",
            "branch": "main"  // optional, defaults to 'main'
        }

        Returns:
        {
            "status": "success",
            "commit_sha": "abc123...",
            "url": "https://github.com/owner/repo/commit/abc123"
        }
        """
        try:
            # Get request data
            data = request.jsonrequest or kwargs

            owner = data.get("owner")
            repo = data.get("repo")
            path = data.get("path")
            content = data.get("content")
            message = data.get("message")
            branch = data.get("branch", "main")

            if not all([owner, repo, path, content, message]):
                return {
                    "status": "error",
                    "message": "Missing required fields: owner, repo, path, content, message",
                }

            # Get integration and commit file
            integration = (
                request.env["github.integration"]
                .sudo()
                .get_integration_for_repo(owner, repo)
            )
            result = integration.commit_file(
                owner, repo, path, content, message, branch
            )

            return {
                "status": "success",
                "commit_sha": result["commit"]["sha"],
                "url": result["commit"]["html_url"],
                "content_url": result["content"]["html_url"],
            }

        except Exception as e:
            _logger.error(f"Commit error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def _generate_jwt(self):
        """Generate GitHub App JWT for authentication"""
        try:
            with open(GITHUB_APP_PEM_PATH) as pem_file:
                private_key = pem_file.read()

            now = datetime.utcnow()
            payload = {
                "iat": int(now.timestamp()) - 60,  # Issued 60 seconds ago
                "exp": int(
                    (now + timedelta(minutes=10)).timestamp()
                ),  # Expires in 10 minutes
                "iss": GITHUB_APP_ID,
            }

            token = jwt.encode(payload, private_key, algorithm="RS256")
            return token
        except Exception as e:
            _logger.error(f"Failed to generate JWT: {e}")
            return None

    def _get_installation_token(self, installation_id):
        """Get installation access token for API calls"""
        jwt_token = self._generate_jwt()
        if not jwt_token:
            return None

        try:
            response = requests.post(
                f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            response.raise_for_status()
            return response.json().get("token")
        except Exception as e:
            _logger.error(f"Failed to get installation token: {e}")
            return None

    def _verify_webhook_signature(self, payload_body, signature_header):
        """Verify GitHub webhook signature using HMAC-SHA256"""
        # Note: Webhook secret should be stored in github.integration model
        integration = request.env["github.integration"].sudo().search([], limit=1)
        if not integration or not integration.webhook_secret:
            _logger.warning("No webhook secret configured")
            return False

        webhook_secret = integration.webhook_secret.encode("utf-8")
        hash_object = hmac.new(
            webhook_secret, msg=payload_body, digestmod=hashlib.sha256
        )
        expected_signature = "sha256=" + hash_object.hexdigest()

        return hmac.compare_digest(expected_signature, signature_header)

    @http.route(
        "/odoo/github/auth/callback",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def github_oauth_callback(self, **kwargs):
        """
        GitHub App installation callback (simplified - no OAuth exchange needed)

        Query parameters:
        - installation_id: GitHub App installation ID
        - setup_action: Action type (install/update)

        Note: We use JWT + Installation Tokens, not OAuth flow
        """
        installation_id = kwargs.get("installation_id")
        setup_action = kwargs.get("setup_action", "install")

        _logger.info(
            f"GitHub App callback: installation_id={installation_id}, setup_action={setup_action}"
        )

        if not installation_id:
            return request.render(
                "pulser_hub_sync.oauth_error", {"error": "Missing installation ID"}
            )

        try:
            # Get installation token using JWT (no OAuth needed!)
            installation_token = self._get_installation_token(installation_id)
            if not installation_token:
                raise Exception("Failed to get installation token")

            # Fetch installation details
            install_response = requests.get(
                f"https://api.github.com/app/installations/{installation_id}",
                headers={
                    "Authorization": f"token {installation_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            install_response.raise_for_status()
            install_data = install_response.json()

            # Store integration in database
            integration = (
                request.env["github.integration"]
                .sudo()
                .search([("installation_id", "=", installation_id)], limit=1)
            )

            if integration:
                integration.write(
                    {
                        "installation_token": installation_token,
                        "token_expires_at": datetime.utcnow() + timedelta(hours=1),
                        "account_login": install_data["account"]["login"],
                        "repository_selection": install_data.get(
                            "repository_selection", "all"
                        ),
                        "last_sync": datetime.utcnow(),
                    }
                )
            else:
                request.env["github.integration"].sudo().create(
                    {
                        "installation_id": installation_id,
                        "installation_token": installation_token,
                        "token_expires_at": datetime.utcnow() + timedelta(hours=1),
                        "account_login": install_data["account"]["login"],
                        "repository_selection": install_data.get(
                            "repository_selection", "all"
                        ),
                        "app_id": GITHUB_APP_ID,
                        "last_sync": datetime.utcnow(),
                    }
                )

            _logger.info(
                f"GitHub App installed successfully for {install_data['account']['login']}"
            )

            return request.render(
                "pulser_hub_sync.oauth_success",
                {
                    "account": install_data["account"]["login"],
                    "installation_id": installation_id,
                },
            )

        except Exception as e:
            _logger.error(f"Installation callback error: {e}", exc_info=True)
            return request.render("pulser_hub_sync.oauth_error", {"error": str(e)})

    @http.route(
        "/odoo/github/webhook", type="json", auth="public", methods=["POST"], csrf=False
    )
    def github_webhook_listener(self, **kwargs):
        """
        GitHub webhook listener for repository events

        Headers:
        - X-GitHub-Event: Event type (push, pull_request, issues, etc.)
        - X-Hub-Signature-256: HMAC signature for verification
        - X-GitHub-Delivery: Unique delivery ID
        """
        try:
            # Get request data
            payload_body = request.httprequest.data
            signature = request.httprequest.headers.get("X-Hub-Signature-256", "")
            event_type = request.httprequest.headers.get("X-GitHub-Event", "")
            delivery_id = request.httprequest.headers.get("X-GitHub-Delivery", "")

            _logger.info(
                f"Webhook received: event={event_type}, delivery={delivery_id}"
            )

            # Verify signature
            if not self._verify_webhook_signature(payload_body, signature):
                _logger.warning(f"Invalid webhook signature for delivery {delivery_id}")
                return {"status": "error", "message": "Invalid signature"}

            # Parse payload
            payload = json.loads(payload_body)

            # Create webhook event record
            event = (
                request.env["github.webhook.event"]
                .sudo()
                .create(
                    {
                        "event_type": event_type,
                        "delivery_id": delivery_id,
                        "payload": json.dumps(payload),
                        "installation_id": payload.get("installation", {}).get("id"),
                        "repository": payload.get("repository", {}).get("full_name"),
                        "sender": payload.get("sender", {}).get("login"),
                        "processed": False,
                    }
                )
            )

            # Queue async job for processing (10s GitHub timeout protection)
            event.with_delay().process_webhook_async()

            return {"status": "success", "message": "Webhook queued for processing"}

        except Exception as e:
            _logger.error(f"Webhook processing error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
