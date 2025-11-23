from odoo import fields, models


class IpaiDocTag(models.Model):
    _name = "ipai.doc.tag"
    _description = "IPAI Doc Tag"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer(string="Color Index")
