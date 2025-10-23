from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class BiSupersetAnalytics(models.Model):
    _name = "bi.superset.analytics"
    _description = "BI Superset Analytics Query"
    _order = "create_date desc"

    name = fields.Char(string="Query Name", required=True, default="New Analytics Query")
    query = fields.Text(string="Natural Language Query", required=True,
                       help="Ask a question in natural language (e.g., 'Show top 10 expenses by category')")

    # Results
    result_sql = fields.Text(string="Generated SQL", readonly=True)
    chart_id = fields.Char(string="Chart ID", readonly=True)
    chart_url = fields.Char(string="Chart URL", readonly=True)
    dashboard_id = fields.Char(string="Dashboard ID", readonly=True)
    dashboard_url = fields.Char(string="Dashboard URL", readonly=True)

    # Configuration
    dataset_id = fields.Integer(string="Dataset ID", help="Superset dataset ID (optional)")
    create_dashboard = fields.Boolean(string="Create Dashboard", default=False,
                                     help="Create a dashboard instead of just a chart")

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

    def action_run_agent(self):
        """Execute the BI agent workflow"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'bi_agent.api_base', 'http://localhost:8001'
        )

        for rec in self:
            rec.state = 'running'

            payload = {
                "query": rec.query,
                "create_dashboard": rec.create_dashboard
            }

            if rec.dataset_id:
                payload["dataset_id"] = rec.dataset_id

            try:
                response = requests.post(
                    f"{base_url}/agent/run",
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()

                rec.write({
                    'result_sql': data.get('sql'),
                    'chart_id': str(data.get('chart_id')) if data.get('chart_id') else False,
                    'chart_url': data.get('chart_url'),
                    'dashboard_id': str(data.get('dashboard_id')) if data.get('dashboard_id') else False,
                    'dashboard_url': data.get('dashboard_url'),
                    'state': 'done',
                    'error_message': False
                })

                _logger.info(f"BI Agent executed successfully: {rec.query[:50]}")

            except requests.RequestException as e:
                error_msg = f"Agent API error: {str(e)}"
                rec.write({
                    'state': 'error',
                    'error_message': error_msg
                })
                _logger.error(f"BI Agent error: {error_msg}")

            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                rec.write({
                    'state': 'error',
                    'error_message': error_msg
                })
                _logger.error(f"BI Agent error: {error_msg}")

        return True

    def action_view_chart(self):
        """Open chart in new window"""
        self.ensure_one()
        if not self.chart_url:
            return {}

        return {
            'type': 'ir.actions.act_url',
            'url': self.chart_url,
            'target': 'new',
        }

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
