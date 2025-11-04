from odoo import models, fields, api

class IpaiStatementWizard(models.TransientModel):
    _name = "ipai.statement.wizard"
    _description = "Generate Statement of Account"

    partner_id = fields.Many2one("res.partner", required=True)
    send_email = fields.Boolean(default=True)

    def action_generate(self):
        # TODO: compute balances; generate PDF; optionally send email
        return {"status":"ok", "partner": self.partner_id.id}
