# -*- coding: utf-8 -*-
"""AI Agent Interaction Logs"""

from odoo import fields, models


class IPAIAgentLog(models.Model):
    _name = "ipai.agent.log"
    _description = "AI Agent Interaction Log"
    _order = "create_date desc"

    message_id = fields.Many2one(
        "mail.message", string="Original Message", required=True, ondelete="cascade"
    )
    user_id = fields.Many2one(
        "res.users", string="User", required=True, ondelete="cascade"
    )
    query = fields.Text(string="User Query", required=True)
    response = fields.Text(string="Agent Response")
    actions = fields.Text(
        string="Actions Executed", help="JSON list of executed actions"
    )
    execution_time = fields.Float(string="Execution Time (s)", digits=(5, 2))
    success = fields.Boolean(string="Success", default=True)
    error_message = fields.Text(string="Error Message")
    context = fields.Text(string="Request Context", help="JSON context data")
