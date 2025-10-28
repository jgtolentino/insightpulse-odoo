from odoo import fields, models


class IpaiVendorCatalog(models.Model):
    _name = "ipai.vendor.catalog"
    _description = "IPAI Vendor Catalog"
    _order = "vendor_id, product_id"

    _sql_constraints = [
        (
            "vendor_product_unique",
            "unique(vendor_id, product_id, valid_from, valid_to)",
            "Vendor catalog entry must be unique per product and validity period",
        ),
    ]

    vendor_id = fields.Many2one(
        "res.partner", required=True, domain=[("supplier_rank", ">", 0)]
    )
    product_id = fields.Many2one("product.product", required=True)
    price = fields.Float(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda s: s.env.company.currency_id.id
    )
    valid_from = fields.Date()
    valid_to = fields.Date()
    notes = fields.Char()
