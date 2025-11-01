# -*- coding: utf-8 -*-
import base64
import hmac
import json
import logging
import os
import time
from hashlib import sha256

import requests
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


def _b64_to_pem(b64txt: str) -> bytes:
    """Convert base64-encoded PEM to bytes."""
    try:
        return base64.b64decode(b64txt.encode())
    except Exception:
        return b64txt.encode()


def _sign(body: bytes, secret: str) -> str:
    """Generate HMAC signature for webhook validation."""
    mac = hmac.new(secret.encode(), body, sha256).hexdigest()
    return f"sha256={mac}"


def _check_sig(body: bytes, header_sig: str, secret: str) -> bool:
    """Verify HMAC signature."""
    return hmac.compare_digest(_sign(body, secret), header_sig or "")


def _jwt_for_app(app_id: str, pem: bytes) -> str:
    """Generate JWT for GitHub App authentication."""
    try:
        import jwt  # PyJWT
    except ImportError:
        raise ImportError("PyJWT is required for GitHub App authentication. Install with: pip install PyJWT")
    
    now = int(time.time())
    payload = {
        "iat": now - 60,  # Issued 60 seconds ago
        "exp": now + 9 * 60,  # Expires in 9 minutes
        "iss": app_id,  # GitHub App ID
    }
    return jwt.encode(payload, pem, algorithm="RS256")


class PulserWebhook(http.Controller):
    """
    Webhook controller for triggering GitHub repository_dispatch events.
    
    Endpoint: POST /pulser/git-ops
    
    Headers:
        X-Pulser-Secret: Shared secret for authentication
        X-Pulser-Signature: HMAC-SHA256 signature of request body
    
    Body (JSON):
        {
            "branch": "gitops/push",
            "message": "chore: update",
            "kv_key": "env",  # optional
            "kv_value": "staging"  # optional
        }
    """

    @http.route("/pulser/git-ops", type="json", auth="public", methods=["POST"], csrf=False)
    def git_ops(self, **kw):
        """
        Trigger GitHub repository_dispatch event for git-ops workflow.
        
        Returns:
            dict: {"ok": bool, "status": int, "detail": str}
        """
        body = request.httprequest.get_data() or b""
        secret = os.getenv("PULSER_WEBHOOK_SECRET", "")
        
        if not secret:
            _logger.error("PULSER_WEBHOOK_SECRET environment variable not set")
            return {"ok": False, "error": "missing PULSER_WEBHOOK_SECRET"}

        # Validate request signature
        header_secret = request.httprequest.headers.get("X-Pulser-Secret", "")
        header_sig = request.httprequest.headers.get("X-Pulser-Signature", "")

        if header_secret != secret or not _check_sig(body, header_sig, secret):
            _logger.warning("Unauthorized webhook request from %s", request.httprequest.remote_addr)
            return {"ok": False, "error": "unauthorized"}

        # Parse request payload
        try:
            payload = json.loads(body.decode() or "{}")
        except json.JSONDecodeError as e:
            _logger.error("Invalid JSON payload: %s", e)
            return {"ok": False, "error": "invalid_json"}

        branch = payload.get("branch", "gitops/push")
        message = payload.get("message", "chore(gitops): repo-dispatch")
        kv_key = payload.get("kv_key")
        kv_val = payload.get("kv_value")

        # Load GitHub App credentials
        app_id = os.getenv("GITHUB_APP_ID")
        inst_id = os.getenv("GITHUB_INSTALLATION_ID")
        owner = os.getenv("GITHUB_REPO_OWNER")
        repo = os.getenv("GITHUB_REPO_NAME")
        pem_b64 = os.getenv("GITHUB_APP_PRIVATE_KEY_BASE64")

        if not all([app_id, inst_id, owner, repo, pem_b64]):
            _logger.error("Missing GitHub environment variables")
            return {"ok": False, "error": "missing GitHub envs"}

        try:
            # Generate JWT for GitHub App
            jwt_token = _jwt_for_app(app_id, _b64_to_pem(pem_b64))

            # Exchange JWT for installation access token
            tok_res = requests.post(
                f"https://api.github.com/app/installations/{inst_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github+json",
                },
                timeout=20,
            )
            
            if tok_res.status_code >= 300:
                _logger.error("GitHub token exchange failed: %s %s", tok_res.status_code, tok_res.text)
                return {
                    "ok": False,
                    "error": f"token_exchange_failed:{tok_res.status_code}",
                    "detail": tok_res.text[:500],
                }
            
            gh_token = tok_res.json().get("token")

            # Fire repository_dispatch event
            disp = {
                "event_type": "git-ops",
                "client_payload": {
                    "branch": branch,
                    "message": message,
                    "kv_key": kv_key,
                    "kv_value": kv_val,
                },
            }
            
            res = requests.post(
                f"https://api.github.com/repos/{owner}/{repo}/dispatches",
                headers={
                    "Authorization": f"token {gh_token}",
                    "Accept": "application/vnd.github+json",
                },
                json=disp,
                timeout=20,
            )
            
            ok = res.status_code in (201, 204)
            
            if ok:
                _logger.info("GitHub dispatch successful: %s → %s/%s", message, owner, repo)
            else:
                _logger.error("GitHub dispatch failed: %s %s", res.status_code, res.text)
            
            return {
                "ok": ok,
                "status": res.status_code,
                "detail": res.text[:500] if not ok else "dispatched",
            }
            
        except Exception as e:
            _logger.exception("Error in git-ops webhook: %s", e)
            return {"ok": False, "error": str(e)}
