# -*- coding: utf-8 -*-
"""AI Agent Configuration Settings"""

from odoo import fields, models


class IPAIAgentConfig(models.TransientModel):
    _name = "ipai.agent.config"
    _inherit = "res.config.settings"
    _description = "AI Agent Configuration"

    agent_api_url = fields.Char(
        string="Agent API URL",
        default="https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat",
        help="DigitalOcean Agent Platform endpoint",
    )
    agent_api_key = fields.Char(
        string="API Key", help="Optional API key for authentication"
    )
    agent_timeout = fields.Integer(
        string="Timeout (seconds)", default=30, help="API request timeout"
    )
    agent_max_retries = fields.Integer(
        string="Max Retries", default=2, help="Number of retry attempts on failure"
    )
    agent_enabled = fields.Boolean(
        string="Enable AI Agent", default=True, help="Enable/disable AI agent globally"
    )

    def get_values(self):
        res = super(IPAIAgentConfig, self).get_values()
        IrConfigParam = self.env["ir.config_parameter"].sudo()
        res.update(
            {
                "agent_api_url": IrConfigParam.get_param(
                    "ipai_agent.api_url",
                    default="https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat",
                ),
                "agent_api_key": IrConfigParam.get_param(
                    "ipai_agent.api_key", default=""
                ),
                "agent_timeout": int(
                    IrConfigParam.get_param("ipai_agent.timeout", default="30")
                ),
                "agent_max_retries": int(
                    IrConfigParam.get_param("ipai_agent.max_retries", default="2")
                ),
                "agent_enabled": IrConfigParam.get_param(
                    "ipai_agent.enabled", default="True"
                )
                == "True",
            }
        )
        return res

    def set_values(self):
        super(IPAIAgentConfig, self).set_values()
        IrConfigParam = self.env["ir.config_parameter"].sudo()
        IrConfigParam.set_param("ipai_agent.api_url", self.agent_api_url or "")
        IrConfigParam.set_param("ipai_agent.api_key", self.agent_api_key or "")
        IrConfigParam.set_param("ipai_agent.timeout", str(self.agent_timeout))
        IrConfigParam.set_param("ipai_agent.max_retries", str(self.agent_max_retries))
        IrConfigParam.set_param("ipai_agent.enabled", str(self.agent_enabled))
