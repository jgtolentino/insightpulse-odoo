import base64
import logging
import os
from datetime import datetime, timedelta

import jwt
import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID", "2191216")
GITHUB_APP_PEM_PATH = os.getenv(
    "GITHUB_APP_PEM_PATH", os.path.expanduser("~/.github/apps/pulser-hub.pem")
)


class GitHubIntegration(models.Model):
    _name = "github.integration"
    _description = "GitHub App Integration"
    _order = "last_sync desc"

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    app_id = fields.Char(string="App ID", default="2191216", readonly=True)
    installation_id = fields.Char(string="Installation ID", required=True, index=True)
    account_login = fields.Char(string="GitHub Account", required=True)
    repository_selection = fields.Selection(
        [
            ("all", "All repositories"),
            ("selected", "Selected repositories"),
        ],
        string="Repository Selection",
        default="all",
    )

    # OAuth tokens
    access_token = fields.Char(string="Access Token")
    installation_token = fields.Char(string="Installation Token")
    token_expires_at = fields.Datetime(string="Token Expires At")

    # Webhook configuration
    webhook_secret = fields.Char(
        string="Webhook Secret", help="Secret for verifying webhook signatures"
    )

    # Sync tracking
    last_sync = fields.Datetime(string="Last Sync", default=fields.Datetime.now)
    active = fields.Boolean(string="Active", default=True)

    # Statistics
    webhook_count = fields.Integer(
        string="Webhook Events", compute="_compute_webhook_count"
    )

    @api.depends("account_login", "installation_id")
    def _compute_name(self):
        for record in self:
            record.name = f"{record.account_login} ({record.installation_id})"

    def _compute_webhook_count(self):
        for record in self:
            record.webhook_count = self.env["github.webhook.event"].search_count(
                [("installation_id", "=", record.installation_id)]
            )

    @api.model
    def refresh_installation_token(self, installation_id):
        """Refresh installation token if expired"""
        integration = self.search([("installation_id", "=", installation_id)], limit=1)
        if not integration:
            return False

        # Check if token is expired or will expire soon (within 10 minutes)
        if (
            integration.token_expires_at
            and integration.token_expires_at
            > datetime.utcnow().replace(minute=datetime.utcnow().minute + 10)
        ):
            return True  # Token still valid

        # Generate new JWT and get fresh installation token
        # (Implementation would call the controller's _get_installation_token method)
        # For now, mark as needing refresh
        integration.write({"token_expires_at": False})
        return False

    def action_view_webhooks(self):
        """Open webhook events for this integration"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Webhooks for {self.account_login}",
            "res_model": "github.webhook.event",
            "view_mode": "tree,form",
            "domain": [("installation_id", "=", self.installation_id)],
            "context": {"default_installation_id": self.installation_id},
        }

    # ========== GitHub API Methods ==========

    def _generate_jwt(self):
        """Generate GitHub App JWT for authentication"""
        try:
            with open(GITHUB_APP_PEM_PATH) as pem_file:
                private_key = pem_file.read()

            now = datetime.utcnow()
            payload = {
                "iat": int(now.timestamp()) - 60,
                "exp": int((now + timedelta(minutes=10)).timestamp()),
                "iss": GITHUB_APP_ID,
            }

            token = jwt.encode(payload, private_key, algorithm="RS256")
            return token
        except Exception as e:
            _logger.error(f"Failed to generate JWT: {e}")
            return None

    def _get_installation_token(self):
        """Get fresh installation token for this integration"""
        self.ensure_one()

        # Check if current token is still valid (>10 min remaining)
        if self.installation_token and self.token_expires_at:
            if self.token_expires_at > datetime.utcnow() + timedelta(minutes=10):
                return self.installation_token

        # Generate new token
        jwt_token = self._generate_jwt()
        if not jwt_token:
            raise Exception("Failed to generate JWT")

        try:
            response = requests.post(
                f"{GITHUB_API}/app/installations/{self.installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github+json",
                },
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()

            # Update stored token
            self.write(
                {
                    "installation_token": data["token"],
                    "token_expires_at": datetime.utcnow() + timedelta(hours=1),
                }
            )

            return data["token"]

        except Exception as e:
            _logger.error(f"Failed to get installation token: {e}")
            raise

    def create_issue(self, owner, repo, title, body="", labels=None, assignees=None):
        """
        Create a GitHub issue

        Args:
            owner: Repository owner (e.g., 'jgtolentino')
            repo: Repository name (e.g., 'insightpulse-odoo')
            title: Issue title
            body: Issue description (markdown supported)
            labels: List of label names (optional)
            assignees: List of usernames to assign (optional)

        Returns:
            dict: GitHub API response with issue data
        """
        self.ensure_one()
        token = self._get_installation_token()

        payload = {
            "title": title,
            "body": body,
        }
        if labels:
            payload["labels"] = labels
        if assignees:
            payload["assignees"] = assignees

        url = f"{GITHUB_API}/repos/{owner}/{repo}/issues"
        response = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=20,
        )
        response.raise_for_status()

        result = response.json()
        _logger.info(f"Created issue #{result['number']}: {result['html_url']}")
        return result

    def commit_file(self, owner, repo, path, content_str, message, branch="main"):
        """
        Create or update a file in GitHub repository

        Args:
            owner: Repository owner
            repo: Repository name
            path: File path in repo (e.g., 'docs/README.md')
            content_str: File content as string
            message: Commit message
            branch: Target branch (default: 'main')

        Returns:
            dict: GitHub API response with commit data
        """
        self.ensure_one()
        token = self._get_installation_token()

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }

        # Check if file exists to get SHA
        get_url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
        sha = None

        get_response = requests.get(
            get_url, headers=headers, params={"ref": branch}, timeout=20
        )

        if get_response.status_code == 200:
            sha = get_response.json().get("sha")

        # Create/update file
        payload = {
            "message": message,
            "content": base64.b64encode(content_str.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }

        if sha:
            payload["sha"] = sha  # Update existing file

        put_response = requests.put(get_url, headers=headers, json=payload, timeout=20)
        put_response.raise_for_status()

        result = put_response.json()
        _logger.info(f"Committed file {path}: {result['commit']['html_url']}")
        return result

    @api.model
    def get_integration_for_repo(self, owner, repo=None):
        """
        Get integration record for a repository

        Args:
            owner: Repository owner or full name (e.g., 'jgtolentino' or 'jgtolentino/insightpulse-odoo')
            repo: Repository name (optional if owner is full name)

        Returns:
            github.integration: Integration record
        """
        # Handle full repo name
        if "/" in owner and not repo:
            owner, repo = owner.split("/", 1)

        # Try to find by account login
        integration = self.search([("account_login", "=", owner)], limit=1)

        if not integration:
            raise Exception(f"No GitHub integration found for {owner}")

        return integration
