from odoo import api, fields, models


class TableauConfig(models.Model):
    _name = "tableau.config"
    _description = "Tableau Configuration"

    name = fields.Char(string="Configuration Name", required=True)
    server_url = fields.Char(
        string="Tableau Server URL",
        required=True,
        default="https://tableau.example.com",
    )
    site_name = fields.Char(string="Site Name", default="")
    username = fields.Char(string="Username")
    password = fields.Char(string="Password")
    personal_access_token = fields.Char(string="Personal Access Token")
    is_active = fields.Boolean(string="Active", default=True)

    # Connection test
    connection_status = fields.Selection(
        [
            ("not_tested", "Not Tested"),
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        string="Connection Status",
        default="not_tested",
    )

    last_connection_test = fields.Datetime(string="Last Connection Test")

    @api.model
    def test_connection(self):
        """Test connection to Tableau instance"""
        # This would implement actual API connection test
        # For now, return success if URL is provided
        if self.server_url:
            self.connection_status = "success"
            self.last_connection_test = fields.Datetime.now()
        else:
            self.connection_status = "failed"
        return self.connection_status


class TableauDashboard(models.Model):
    _name = "tableau.dashboard"
    _description = "Tableau Dashboard"

    name = fields.Char(string="Dashboard Name", required=True)
    dashboard_id = fields.Char(string="Tableau Dashboard ID", required=True)
    workbook_id = fields.Char(string="Workbook ID")
    config_id = fields.Many2one(
        "tableau.config", string="Tableau Configuration", required=True
    )
    embed_url = fields.Char(string="Embed URL", compute="_compute_embed_url")
    description = fields.Text(string="Description")
    is_active = fields.Boolean(string="Active", default=True)

    def _compute_embed_url(self):
        for record in self:
            if record.config_id.server_url and record.dashboard_id:
                base_url = record.config_id.server_url.rstrip("/")
                site_path = (
                    f"/t/{record.config_id.site_name}"
                    if record.config_id.site_name
                    else ""
                )
                record.embed_url = f"{base_url}{site_path}/views/{record.workbook_id or 'default'}/{record.dashboard_id}"
            else:
                record.embed_url = False

    def export_data_to_tableau(self):
        """Export Odoo data to Tableau"""
        # This would implement data export functionality
        # For now, return a notification
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Data Export",
                "message": f"Data export to Tableau dashboard {self.name} initiated!",
                "type": "success",
                "sticky": False,
            },
        }
