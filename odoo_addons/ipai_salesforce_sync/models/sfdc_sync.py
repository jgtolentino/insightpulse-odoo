from odoo import models, api

class IpaiSfdcSync(models.TransientModel):
    _name = "ipai.sfdc.sync"
    _description = "Pull SFDC Accounts/Contacts/Leads"

    @api.model
    def action_pull(self):
        # TODO: call connector / MCP tool → upsert res.partner, crm.lead
        return {"status":"ok"}
