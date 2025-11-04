from odoo import models, fields

class IpaiVisualSnapshot(models.Model):
    _name = "ipai.visual.snapshot"
    _description = "Stored visual diff metadata"

    path = fields.Char(required=True)
    baseline_hash = fields.Char()
    current_hash = fields.Char()
    passed = fields.Boolean(default=False)
