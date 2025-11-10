"""MCP Server Registry - Configure and manage MCP servers"""

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MCPServer(models.Model):
    """Registry of available MCP servers and their capabilities"""

    _name = "mcp.server"
    _description = "MCP Server Registry"
    _order = "sequence, name"

    name = fields.Char(string="Server Name", required=True, index=True)
    code = fields.Selection(
        [
            ("github", "GitHub (pulser-hub)"),
            ("digitalocean", "DigitalOcean App Platform"),
            ("supabase", "Supabase PostgreSQL"),
            ("notion", "Notion Workspace"),
            ("superset", "Apache Superset"),
            ("tableau", "Tableau Cloud"),
        ],
        string="Server Type",
        required=True,
    )

    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    # Connection settings
    url = fields.Char(string="Base URL", help="MCP server endpoint URL")
    description = fields.Text(string="Description")

    # Capabilities
    operations_count = fields.Integer(
        string="Operations", compute="_compute_operations_count", store=False
    )

    # Credentials
    credential_id = fields.Many2one(
        "mcp.credential", string="Credential", ondelete="set null"
    )

    # Statistics
    operation_ids = fields.One2many("mcp.operation", "server_id", string="Operations")

    last_operation_date = fields.Datetime(
        string="Last Operation", compute="_compute_last_operation", store=False
    )

    success_rate = fields.Float(
        string="Success Rate (%)", compute="_compute_success_rate", store=False
    )

    @api.depends("operation_ids")
    def _compute_operations_count(self):
        for server in self:
            server.operations_count = len(server.operation_ids)

    @api.depends("operation_ids.create_date")
    def _compute_last_operation(self):
        for server in self:
            if server.operation_ids:
                server.last_operation_date = max(
                    server.operation_ids.mapped("create_date")
                )
            else:
                server.last_operation_date = False

    @api.depends("operation_ids.state")
    def _compute_success_rate(self):
        for server in self:
            if server.operation_ids:
                total = len(server.operation_ids)
                success = len(
                    server.operation_ids.filtered(lambda op: op.state == "success")
                )
                server.success_rate = (success / total) * 100 if total else 0.0
            else:
                server.success_rate = 0.0

    def call_operation(self, operation_name, params=None):
        """
        Call MCP operation on this server

        Args:
            operation_name (str): Operation to execute
            params (dict): Operation parameters

        Returns:
            mcp.operation: Created operation record
        """
        self.ensure_one()

        operation = self.env["mcp.operation"].create(
            {
                "name": operation_name,
                "server_id": self.id,
                "params": params or {},
                "state": "pending",
            }
        )

        try:
            operation.execute()
        except Exception as e:
            _logger.error(f"MCP operation failed: {e}")
            operation.write({"state": "failed", "error_message": str(e)})

        return operation

    def action_view_operations(self):
        """View all operations for this server"""
        self.ensure_one()
        return {
            "name": f"{self.name} Operations",
            "type": "ir.actions.act_window",
            "res_model": "mcp.operation",
            "view_mode": "tree,form",
            "domain": [("server_id", "=", self.id)],
            "context": {"default_server_id": self.id},
        }

    def action_test_connection(self):
        """Test connection to MCP server"""
        self.ensure_one()

        # Call health check operation
        operation = self.call_operation("health_check", {})

        if operation.state == "success":
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": f"{self.name} is healthy",
                    "type": "success",
                    "sticky": False,
                },
            }
        else:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Error",
                    "message": f"Connection failed: {operation.error_message}",
                    "type": "danger",
                    "sticky": True,
                },
            }
