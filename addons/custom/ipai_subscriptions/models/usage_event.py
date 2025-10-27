from odoo import fields, models


class IpaiUsageEvent(models.Model):
    _name = "ipai.usage.event"
    _description = "Metered Usage Event"
    
    subscription_id = fields.Many2one(
        "ipai.subscription", required=True, index=True
    )
    metric = fields.Char(required=True)   # e.g., "seats", "api_calls"
    quantity = fields.Float(required=True)
    event_at = fields.Datetime(required=True, default=fields.Datetime.now)
