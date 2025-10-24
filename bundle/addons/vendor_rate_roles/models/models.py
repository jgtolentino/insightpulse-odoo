# from odoo import models, fields, api


# class vendor_rate_roles(models.Model):
#     _name = 'vendor_rate_roles.vendor_rate_roles'
#     _description = 'vendor_rate_roles.vendor_rate_roles'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

