import os
import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

class SupersetDashboard(models.Model):
    _name = "superset.dashboard"
    _description = "Superset Dashboard"
    
    name = fields.Char(string="Dashboard Title", required=True)
    dashboard_id = fields.Char(string="Dashboard ID", required=True)
    uuid = fields.Char(string="UUID")
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
    
    def open_dashboard(self):
        """Open the dashboard in embedded view"""
        for record in self:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/odoo/dashboards?dashboard_id={record.dashboard_id}',
                'target': 'new'
            }
    
    @api.model
    def refresh_dashboards(self):
        """Refresh dashboard list from Superset API"""
        superset_url = os.getenv("SUPERSET_URL", "")
        ss_user = os.getenv("SS_USER", "")
        ss_pass = os.getenv("SS_PASS", "")
        
        if not all([superset_url, ss_user, ss_pass]):
            raise UserError("Superset environment variables not configured")
        
        try:
            # Get access token
            login_response = requests.post(
                f"{superset_url}/api/v1/security/login",
                json={"username": ss_user, "password": ss_pass, "provider": "db", "refresh": False},
                timeout=10
            )
            login_response.raise_for_status()
            access_token = login_response.json()["access_token"]
            
            # Get dashboards
            dash_response = requests.get(
                f"{superset_url}/api/v1/dashboard/?q=(page:0,page_size:50)",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            dash_response.raise_for_status()
            dashboards = dash_response.json().get("result", [])
            
            # Update or create dashboard records
            created_count = 0
            updated_count = 0
            for dash in dashboards:
                existing = self.search([("dashboard_id", "=", str(dash.get("id")))])
                if existing:
                    existing.write({
                        "name": dash.get("dashboard_title", "Unknown"),
                        "uuid": dash.get("uuid"),
                        "description": f"Superset Dashboard: {dash.get('dashboard_title', 'Unknown')}"
                    })
                    updated_count += 1
                else:
                    self.create({
                        "name": dash.get("dashboard_title", "Unknown"),
                        "dashboard_id": str(dash.get("id")),
                        "uuid": dash.get("uuid"),
                        "description": f"Superset Dashboard: {dash.get('dashboard_title', 'Unknown')}"
                    })
                    created_count += 1
            
            message = f"Successfully refreshed dashboards: {created_count} created, {updated_count} updated"
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Dashboard Refresh',
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(f"Failed to refresh dashboards: {str(e)}")
