# -*- coding: utf-8 -*-
from odoo import fields, models

class IpTravelRequest(models.Model):
    _name = "ip.travel.request"
    _description = "Travel Request"

    name = fields.Char(required=True)
    employee_id = fields.Many2one("hr.employee", required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    destination = fields.Char()
    no_car_service = fields.Boolean(string="No Car Service")
    state = fields.Selection([("draft","Draft"),("approved","Approved"),("done","Done")], default="draft")
