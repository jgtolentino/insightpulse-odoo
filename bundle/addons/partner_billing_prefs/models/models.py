# from odoo import models, fields, api


# class partner_billing_prefs(models.Model):
#     _name = 'partner_billing_prefs.partner_billing_prefs'
#     _description = 'partner_billing_prefs.partner_billing_prefs'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

