from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import os

UNSLOTH_PARAM = "ip_unsloth_base_url"

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    unsloth_base_url = fields.Char(
        string="Unsloth API Base URL",
        config_parameter=UNSLOTH_PARAM,
        default=lambda self: os.getenv("UNSLOTH_API_BASE", "http://unsloth-api:8000"),
        help="e.g., http://unsloth-api:8000 or https://ml.example.com",
    )

class IpUnslothWizard(models.TransientModel):
    _name = "ip.unsloth.wizard"
    _description = "Unsloth Test Inference"

    prompt = fields.Text(required=True)
    response = fields.Text(readonly=True)

    def action_run(self):
        base = self.env["ir.config_parameter"].sudo().get_param(
            UNSLOTH_PARAM, os.getenv("UNSLOTH_API_BASE", "http://unsloth-api:8000")
        )
        url = f"{base.rstrip('/')}/predict"
        try:
            r = requests.post(url, json={"text": self.prompt}, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            raise UserError(_("Unsloth call failed: %s") % e)
        self.write({"response": data.get("output", "")})
        return {
            "type": "ir.actions.act_window",
            "res_model": "ip.unsloth.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }
