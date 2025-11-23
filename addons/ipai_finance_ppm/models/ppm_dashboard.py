# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
import requests

_logger = logging.getLogger(__name__)


class FinancePpmDashboard(models.Model):
    _name = "finance.ppm.dashboard"
    _description = "Finance PPM Automation Dashboard"
    _rec_name = "name"
    _order = "sequence, workflow_code"

    name = fields.Char(required=True)
    workflow_code = fields.Selection(
        selection=[
            ("bir_deadline_alert", "BIR Deadline Alert"),
            ("task_escalation", "Task Escalation"),
            ("monthly_report", "Monthly Compliance Report"),
        ],
        required=True,
        index=True,
    )
    sequence = fields.Integer(default=10)

    # Status coming from n8n / Supabase
    last_run_at = fields.Datetime(string="Last Run")
    last_status = fields.Selection(
        selection=[
            ("ok", "OK"),
            ("warning", "Warning"),
            ("error", "Error"),
        ],
        string="Last Status",
    )
    last_message = fields.Text(string="Last Message")
    next_scheduled_at = fields.Datetime(string="Next Scheduled Run")
    total_runs = fields.Integer(string="Total Runs")
    failures_24h = fields.Integer(string="Failures (24h)")

    # UX helpers
    status_color = fields.Selection(
        selection=[
            ("success", "Green"),
            ("warning", "Yellow"),
            ("danger", "Red"),
        ],
        compute="_compute_status_color",
    )

    @api.depends("last_status")
    def _compute_status_color(self):
        for rec in self:
            if rec.last_status == "ok":
                rec.status_color = "success"
            elif rec.last_status == "warning":
                rec.status_color = "warning"
            elif rec.last_status == "error":
                rec.status_color = "danger"
            else:
                rec.status_color = False

    # -------------------------------------------------------------------------
    # Integration helpers
    # -------------------------------------------------------------------------

    def _get_status_endpoint(self):
        """Read endpoint + key from system parameters.

        Set in Odoo: Settings → Technical → Parameters → System Parameters:

        - finance_ppm.status_api_url
        - finance_ppm.status_api_key
        """
        icp = self.env["ir.config_parameter"].sudo()
        url = icp.get_param("finance_ppm.status_api_url")
        api_key = icp.get_param("finance_ppm.status_api_key")
        if not url or not api_key:
            raise UserError(
                _(
                    "Finance PPM status API is not configured.\n"
                    "Please set 'finance_ppm.status_api_url' and "
                    "'finance_ppm.status_api_key' in System Parameters."
                )
            )
        return url, api_key

    @api.model
    def action_refresh_dashboard(self):
        """Refresh all dashboard rows from external status API.

        Expected JSON schema (example):

        {
          "workflows": [
            {
              "workflow_code": "bir_deadline_alert",
              "name": "BIR Deadline Alert",
              "last_run_at": "2025-11-23T08:00:00Z",
              "last_status": "ok",
              "last_message": "Executed 128 BIR checks",
              "next_scheduled_at": "2025-11-24T08:00:00Z",
              "total_runs": 42,
              "failures_24h": 0
            },
            ...
          ]
        }
        """
        url, api_key = self._get_status_endpoint()
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            _logger.exception("Failed to fetch Finance PPM status from %s", url)
            raise UserError(_("Failed to fetch Finance PPM status:\n%s") % e)

        workflows = data.get("workflows", [])
        existing = {
            rec.workflow_code: rec
            for rec in self.search([("workflow_code", "in", [w.get("workflow_code") for w in workflows])])
        }

        for w in workflows:
            vals = {
                "name": w.get("name") or w.get("workflow_code"),
                "workflow_code": w.get("workflow_code"),
                "last_run_at": w.get("last_run_at"),
                "last_status": w.get("last_status"),
                "last_message": w.get("last_message"),
                "next_scheduled_at": w.get("next_scheduled_at"),
                "total_runs": w.get("total_runs") or 0,
                "failures_24h": w.get("failures_24h") or 0,
            }
            rec = existing.get(w.get("workflow_code"))
            if rec:
                rec.write(vals)
            else:
                self.create(vals)

        return True
