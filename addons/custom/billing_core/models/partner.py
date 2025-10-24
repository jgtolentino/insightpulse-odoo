from odoo import models, fields
class ResPartner(models.Model):
    _inherit = "res.partner"
    billing_profile_id = fields.One2many("billing.profile","partner_id", string="Billing Profiles")
