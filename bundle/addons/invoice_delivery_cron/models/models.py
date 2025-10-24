# from odoo import models, fields, api


# class invoice_delivery_cron(models.Model):
#     _name = 'invoice_delivery_cron.invoice_delivery_cron'
#     _description = 'invoice_delivery_cron.invoice_delivery_cron'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

