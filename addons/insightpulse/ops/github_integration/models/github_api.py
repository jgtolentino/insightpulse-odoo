# -*- coding: utf-8 -*-
"""GitHub API client for Odoo."""

import logging
import time

import jwt
import requests

from odoo import api, models

_logger = logging.getLogger(__name__)


class GitHubAPI(models.AbstractModel):
    """GitHub API client using pulser-hub app credentials."""

    _name = "github.api"
    _description = "GitHub API Client"

    @api.model
    def _get_app_id(self):
        """Get GitHub App ID from system parameters."""
        return int(
            self.env["ir.config_parameter"].sudo().get_param("github.app_id", "2191216")
        )

    @api.model
    def _get_private_key(self):
        """Get GitHub App private key from system parameters."""
        return (
            self.env["ir.config_parameter"].sudo().get_param("github.private_key", "")
        )

    @api.model
    def _generate_jwt(self):
        """Generate JWT for GitHub App authentication."""
        app_id = self._get_app_id()
        private_key = self._get_private_key()

        if not private_key:
            raise ValueError("GitHub private key not configured in system parameters")

        payload = {
            "iat": int(time.time()),
            "exp": int(time.time()) + (10 * 60),  # 10 minutes
            "iss": app_id,
        }

        token = jwt.encode(payload, private_key, algorithm="RS256")
        return token

    @api.model
    def _get_installation_token(self, installation_id=None):
        """
        Get installation access token.

        Args:
            installation_id (int, optional): Installation ID. If not provided,
                                             retrieves from system parameters.

        Returns:
            str: Installation access token
        """
        if not installation_id:
            installation_id = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("github.installation_id")
            )

        jwt_token = self._generate_jwt()

        response = requests.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

        if response.status_code == 201:
            return response.json()["token"]
        else:
            raise Exception(f"Failed to get installation token: {response.text}")

    @api.model
    def create_issue(self, repo, title, body, labels=None):
        """
        Create GitHub issue.

        Args:
            repo (str): Repository full name (owner/repo)
            title (str): Issue title
            body (str): Issue body
            labels (list, optional): Labels to apply

        Returns:
            dict: Created issue data
        """
        token = self._get_installation_token()

        data = {
            "title": title,
            "body": body,
        }
        if labels:
            data["labels"] = labels

        response = requests.post(
            f"https://api.github.com/repos/{repo}/issues",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
            },
            json=data,
        )

        if response.status_code == 201:
            _logger.info(f"Created GitHub issue: {repo}#{response.json()['number']}")
            return response.json()
        else:
            _logger.error(f"Failed to create issue: {response.text}")
            raise Exception(f"Failed to create issue: {response.text}")

    @api.model
    def create_comment(self, repo, issue_number, body):
        """
        Create comment on GitHub issue/PR.

        Args:
            repo (str): Repository full name
            issue_number (int): Issue/PR number
            body (str): Comment body

        Returns:
            dict: Created comment data
        """
        token = self._get_installation_token()

        response = requests.post(
            f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
            },
            json={"body": body},
        )

        if response.status_code == 201:
            _logger.info(f"Created comment on {repo}#{issue_number}")
            return response.json()
        else:
            raise Exception(f"Failed to create comment: {response.text}")

    @api.model
    def trigger_workflow(self, repo, workflow_id, ref="main", inputs=None):
        """
        Trigger GitHub Actions workflow.

        Args:
            repo (str): Repository full name
            workflow_id (str): Workflow file name or ID
            ref (str): Branch/tag/commit to run workflow on
            inputs (dict, optional): Workflow inputs

        Returns:
            bool: True if triggered successfully
        """
        token = self._get_installation_token()

        data = {
            "ref": ref,
        }
        if inputs:
            data["inputs"] = inputs

        response = requests.post(
            f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/dispatches",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
            },
            json=data,
        )

        if response.status_code == 204:
            _logger.info(f"Triggered workflow {workflow_id} on {repo}")
            return True
        else:
            _logger.error(f"Failed to trigger workflow: {response.text}")
            return False
