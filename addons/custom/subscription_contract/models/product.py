from odoo import models, fields
class ProductTemplate(models.Model):
    _inherit = "product.template"
    is_subscription = fields.Boolean(string="Subscription Product")
