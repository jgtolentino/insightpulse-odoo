# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

def _auth_ok(req):
    secret_param = request.env["ir.config_parameter"].sudo().get_param("ipai.mm_webhook_secret", default="")
    provided = req.httprequest.headers.get("X-IPAI-Webhook-Secret", "")
    return secret_param and provided and secret_param == provided

def _log_event(source: str, payload: dict):
    # Store a compact audit trail in ir.logging
    message = json.dumps({"source": source, "keys": list(payload.keys())}, ensure_ascii=False)[:1000]
    request.env["ir.logging"].sudo().create({
        "name": f"ipai_mattermost_bridge:{source}",
        "type": "server",
        "level": "INFO",
        "dbname": request.env.cr.dbname,
        "message": message,
        "path": "ipai_mattermost_bridge",
        "func": "webhook",
        "line": 0,
    })
    _logger.info("Mattermost bridge event [%s]: %s", source, message)

class MattermostBridge(http.Controller):

    @http.route("/ipai/mattermost/github", type="json", auth="public", methods=["POST"], csrf=False)
    def github(self, **kwargs):
        if not _auth_ok(request):
            return {"ok": False, "error": "unauthorized"}
        payload = request.jsonrequest or {}
        _log_event("github", payload)
        # Future: map PR/issue events to Odoo records
        return {"ok": True}

    @http.route("/ipai/mattermost/jira", type="json", auth="public", methods=["POST"], csrf=False)
    def jira(self, **kwargs):
        if not _auth_ok(request):
            return {"ok": False, "error": "unauthorized"}
        payload = request.jsonrequest or {}
        _log_event("jira", payload)
        return {"ok": True}

    @http.route("/ipai/mattermost/servicenow", type="json", auth="public", methods=["POST"], csrf=False)
    def servicenow(self, **kwargs):
        if not _auth_ok(request):
            return {"ok": False, "error": "unauthorized"}
        payload = request.jsonrequest or {}
        _log_event("servicenow", payload)
        return {"ok": True}
