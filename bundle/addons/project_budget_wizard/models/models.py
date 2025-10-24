# from odoo import models, fields, api


# class project_budget_wizard(models.Model):
#     _name = 'project_budget_wizard.project_budget_wizard'
#     _description = 'project_budget_wizard.project_budget_wizard'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

