# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging
import os

import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PulserGitOpsWizard(models.TransientModel):
    """
    Wizard for triggering GitHub repository_dispatch events from Odoo.
    
    Opens from any record via Server Action: "Pulser: Dispatch Git-Ops…"
    
    Workflow:
        1. User clicks action button on any record
        2. Wizard opens with auto-populated message from context
        3. User confirms branch/message/optional KV pairs
        4. POST to /pulser/git-ops webhook endpoint
        5. Webhook calls GitHub API to trigger repository_dispatch
        6. GitHub Actions workflow (git-ops.yml) runs
    """
    _name = "pulser.gitops.wizard"
    _description = "Pulser Git-Ops Dispatch"

    branch = fields.Char(
        string="Branch",
        default="gitops/push",
        required=True,
        help="Target branch for git operations",
    )
    message = fields.Char(
        string="Commit Message",
        required=True,
        help="Git commit message",
    )
    kv_key = fields.Char(
        string="KV Key",
        help="Optional key to write into ops/kv/<key>.txt",
    )
    kv_value = fields.Char(
        string="KV Value",
        help="Optional value written with kv_key",
    )
    response = fields.Text(
        string="Response",
        readonly=True,
        help="HTTP response from webhook endpoint",
    )

    @api.model
    def default_get(self, fields_list):
        """Set default message from active record context."""
        res = super().default_get(fields_list)
        
        if "message" in fields_list and not res.get("message"):
            model = self._context.get("active_model")
            rec_id = self._context.get("active_id")
            name = ""
            
            if model and rec_id:
                try:
                    rec = self.env[model].browse(rec_id)
                    name = rec.display_name or str(rec_id)
                except Exception:
                    name = str(rec_id)
            
            res["message"] = f"chore(gitops): dispatch from {model or 'manual'} #{rec_id or ''} {name}".strip()
        
        return res

    def action_dispatch(self):
        """
        Dispatch Git-Ops event via webhook.
        
        Process:
            1. Validate PULSER_WEBHOOK_SECRET exists
            2. Build JSON payload with branch/message/kv
            3. Sign payload with HMAC-SHA256
            4. POST to /pulser/git-ops endpoint
            5. Display response in wizard
        """
        self.ensure_one()
        
        secret = os.getenv("PULSER_WEBHOOK_SECRET", "")
        if not secret:
            raise UserError(_("Missing PULSER_WEBHOOK_SECRET in environment."))

        # Build payload
        payload = {
            "branch": self.branch,
            "message": self.message,
            "kv_key": self.kv_key or None,
            "kv_value": self.kv_value or None,
        }
        body = json.dumps(payload).encode("utf-8")
        
        # Sign payload
        sig = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        # Get webhook URL
        base_url = self.env["ir.config_parameter"].sudo().get_param(
            "web.base.url", "http://127.0.0.1:8069"
        ).rstrip("/")
        url = f"{base_url}/pulser/git-ops"

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Pulser-Secret": secret,
            "X-Pulser-Signature": sig,
        }

        # POST to webhook
        try:
            r = requests.post(url, headers=headers, data=body, timeout=20)
            ok = 200 <= r.status_code < 300
            
            self.response = f"POST {url}\nStatus: {r.status_code}\nBody: {r.text[:2000]}"
            
            if not ok:
                _logger.error("Git-Ops dispatch failed: %s %s", r.status_code, r.text)
                raise UserError(
                    _("Dispatch failed (HTTP %s). See response field for details.") % r.status_code
                )
            
            _logger.info("Git-Ops dispatch successful: %s", self.message)
            
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Git-Ops Dispatched"),
                    "message": _("Successfully triggered GitHub Actions workflow."),
                    "type": "success",
                    "sticky": False,
                },
            }
            
        except requests.RequestException as e:
            _logger.exception("HTTP error in git-ops dispatch: %s", e)
            raise UserError(_("HTTP error: %s") % str(e))
