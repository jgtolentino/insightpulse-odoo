"""MCP Operation - Track and execute MCP server operations"""

import logging
import os

import httpx

from odoo import fields, models

_logger = logging.getLogger(__name__)


class MCPOperation(models.Model):
    """History and execution tracking for MCP operations"""

    _name = "mcp.operation"
    _description = "MCP Operation History"
    _order = "create_date desc"

    name = fields.Char(string="Operation", required=True, index=True)
    server_id = fields.Many2one(
        "mcp.server", string="MCP Server", required=True, ondelete="cascade"
    )

    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("running", "Running"),
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        string="State",
        default="pending",
        required=True,
    )

    params = fields.Json(string="Parameters")
    result = fields.Json(string="Result")
    error_message = fields.Text(string="Error Message")

    duration_ms = fields.Integer(string="Duration (ms)")
    user_id = fields.Many2one(
        "res.users", string="User", default=lambda self: self.env.user
    )

    def execute(self):
        """Execute the MCP operation"""
        self.ensure_one()

        coordinator_url = os.getenv("MCP_COORDINATOR_URL", "http://localhost:8001")

        self.write({"state": "running"})

        import time

        start_time = time.time()

        try:
            # Call MCP Coordinator
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{coordinator_url}/mcp",
                    json={
                        "method": "tools/call",
                        "params": {"name": self.name, "arguments": self.params or {}},
                        "server": self.server_id.code,
                    },
                )
                response.raise_for_status()
                result_data = response.json()

            duration = int((time.time() - start_time) * 1000)

            if "error" in result_data:
                self.write(
                    {
                        "state": "failed",
                        "error_message": result_data["error"].get(
                            "message", "Unknown error"
                        ),
                        "duration_ms": duration,
                    }
                )
            else:
                self.write(
                    {
                        "state": "success",
                        "result": result_data.get("result"),
                        "duration_ms": duration,
                    }
                )

        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            _logger.error(f"MCP operation failed: {e}")
            self.write(
                {"state": "failed", "error_message": str(e), "duration_ms": duration}
            )
