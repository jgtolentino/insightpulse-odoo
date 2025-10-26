from odoo import api, fields, models
from odoo.exceptions import ValidationError


class IpaiDunningStep(models.Model):
    _name = "ipai.dunning.step"
    _description = "Dunning Step"
    
    name = fields.Char(required=True)
    day_offset = fields.Integer(required=True)  # days after invoice due
    action = fields.Selection([
        ("email", "Email"), ("suspend", "Suspend"), ("cancel", "Cancel")
    ], default="email")

    @api.constrains('day_offset')
    def _check_day_offset(self):
        for rec in self:
            if rec.day_offset < 0:
                raise ValidationError("Day offset must be >= 0")
