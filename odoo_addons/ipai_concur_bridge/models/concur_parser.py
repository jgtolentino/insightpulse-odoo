from odoo import models, fields
import json

class IpaiConcurIngest(models.TransientModel):
    _name = "ipai.concur.ingest"
    _description = "Ingest Concur SAE payload"

    payload = fields.Text(required=True, help="Raw SAE JSON or CSV converted to JSON")

    def action_parse(self):
        data = json.loads(self.payload)
        # TODO: map rows → hr.expense / hr.expense.sheet
        return {"status": "ok", "lines": len(data)}
