from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    ipai_email_opt_in = fields.Boolean(default=True)
    ipai_policy_version = fields.Char()
