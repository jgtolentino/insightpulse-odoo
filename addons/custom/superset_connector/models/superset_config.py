from odoo import api, fields, models


class SupersetConfig(models.Model):
    _name = "superset.config"
    _description = "Superset Configuration"

    name = fields.Char(string="Configuration Name", required=True)
    base_url = fields.Char(
        string="Superset Base URL", required=True, default="http://superset:8088"
    )
    username = fields.Char(string="Username")
    password = fields.Char(string="Password")
    api_key = fields.Char(string="API Key")
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
        """Test connection to Superset instance"""
        # This would implement actual API connection test
        # For now, return success if URL is provided
        if self.base_url:
            self.connection_status = "success"
            self.last_connection_test = fields.Datetime.now()
        else:
            self.connection_status = "failed"
        return self.connection_status


class SupersetDashboard(models.Model):
    _name = "superset.dashboard"
    _description = "Superset Dashboard"

    name = fields.Char(string="Dashboard Name", required=True)
    dashboard_id = fields.Char(string="Superset Dashboard ID", required=True)
    config_id = fields.Many2one(
        "superset.config", string="Superset Configuration", required=True
    )
    embed_url = fields.Char(string="Embed URL", compute="_compute_embed_url")
    description = fields.Text(string="Description")
    is_active = fields.Boolean(string="Active", default=True)

    def _compute_embed_url(self):
        for record in self:
            if record.config_id.base_url and record.dashboard_id:
                base_url = record.config_id.base_url.rstrip("/")
                record.embed_url = (
                    f"{base_url}/superset/dashboard/{record.dashboard_id}/"
                )
            else:
                record.embed_url = False
