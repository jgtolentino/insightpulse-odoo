from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class BiSupersetDashboard(models.Model):
    _name = "bi.superset.dashboard"
    _description = "BI Superset Dashboard"
    _order = "create_date desc"

    name = fields.Char(string="Dashboard Name", required=True)
    analytics_ids = fields.Many2many('bi.superset.analytics', string="Analytics Queries",
                                    help="Charts to include in this dashboard")

    # Results
    dashboard_id = fields.Char(string="Dashboard ID", readonly=True)
    dashboard_url = fields.Char(string="Dashboard URL", readonly=True)

    # Configuration
    custom_css = fields.Text(string="Custom CSS", help="Optional CSS for dashboard styling")

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('error', 'Error')
    ], string="Status", default='draft', readonly=True)

    error_message = fields.Text(string="Error Message", readonly=True)

    # Multi-company
    company_id = fields.Many2one('res.company', string='Company',
                                default=lambda self: self.env.company)

    def action_create_dashboard(self):
        """Create Superset dashboard from selected analytics"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'bi_agent.api_base', 'http://localhost:8001'
        )

        for rec in self:
            rec.state = 'running'

            # Collect chart IDs from analytics
            chart_ids = []
            for analytics in rec.analytics_ids:
                if analytics.chart_id:
                    try:
                        chart_ids.append(int(analytics.chart_id))
                    except ValueError:
                        continue

            if not chart_ids:
                rec.write({
                    'state': 'error',
                    'error_message': 'No valid charts found. Run analytics queries first.'
                })
                continue

            payload = {
                "title": rec.name,
                "chart_ids": chart_ids,
                "css": rec.custom_css or ""
            }

            try:
                response = requests.post(
                    f"{base_url}/dashboard/create",
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()

                rec.write({
                    'dashboard_id': str(data.get('dashboard_id')),
                    'dashboard_url': data.get('dashboard_url'),
                    'state': 'done',
                    'error_message': False
                })

                _logger.info(f"Dashboard created successfully: {rec.name}")

            except requests.RequestException as e:
                error_msg = f"Dashboard API error: {str(e)}"
                rec.write({
                    'state': 'error',
                    'error_message': error_msg
                })
                _logger.error(f"Dashboard error: {error_msg}")

            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                rec.write({
                    'state': 'error',
                    'error_message': error_msg
                })
                _logger.error(f"Dashboard error: {error_msg}")

        return True

    def action_view_dashboard(self):
        """Open dashboard in new window"""
        self.ensure_one()
        if not self.dashboard_url:
            return {}

        return {
            'type': 'ir.actions.act_url',
            'url': self.dashboard_url,
            'target': 'new',
        }
