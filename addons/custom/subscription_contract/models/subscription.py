from odoo import models, fields, api
from datetime import date
class Contract(models.Model):
    _inherit = "contract.contract"
    proration_mode = fields.Selection([("none","No Proration"),("daily","Daily"),("half_month","Half-month")],
                                      default="none", string="Proration Mode")
    @api.model
    def cron_generate_recurring_invoices(self):
        today = fields.Date.to_string(date.today())
        contracts = self.search([("active","=",True),("recurring_next_date","<=",today)])
        for c in contracts:
            m = getattr(c, "recurring_create_invoice", None)
            if callable(m): m()
