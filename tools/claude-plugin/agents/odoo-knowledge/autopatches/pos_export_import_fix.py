"""
Auto-Patch: POS Backend Sync Fix
Category: point_of_sale
Guardrail: GR-POS-001

Fixes custom fields not syncing from POS to backend orders.
"""

# Example patch for pos.order.line model

def export_json(self):
    """Override to include custom fields in POS export"""
    res = super().export_json()

    # Add custom fields here
    if hasattr(self, 'serial_id'):
        res['serial_id'] = self.serial_id

    if hasattr(self, 'custom_attribute'):
        res['custom_attribute'] = self.custom_attribute

    return res

def import_json(self, vals):
    """Override to handle custom fields from POS import"""
    # Extract custom fields before super call
    serial_id = vals.pop('serial_id', None)
    custom_attribute = vals.pop('custom_attribute', None)

    # Call parent
    res = super().import_json(vals)

    # Apply custom fields
    if serial_id:
        self.serial_id = serial_id
    if custom_attribute:
        self.custom_attribute = custom_attribute

    return res

# Usage in your custom module:
# from odoo import models
#
# class PosOrderLine(models.Model):
#     _inherit = 'pos.order.line'
#
#     # Add the methods above
#     export_json = export_json
#     import_json = import_json
