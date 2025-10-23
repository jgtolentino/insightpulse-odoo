from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bi_agent_api_base = fields.Char(
        string="BI Agent API Base",
        config_parameter='bi_agent.api_base',
        default='http://localhost:8001',
        help="Base URL for the BI Agent FastAPI service"
    )

    bi_agent_superset_url = fields.Char(
        string="Superset URL",
        config_parameter='bi_agent.superset_url',
        default='http://localhost:8088',
        help="Base URL for Apache Superset instance"
    )

    bi_agent_dataset_id = fields.Integer(
        string="Default Dataset ID",
        config_parameter='bi_agent.dataset_id',
        default=1,
        help="Default Superset dataset ID for analytics queries"
    )
