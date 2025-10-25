from odoo import fields, models


class AuthOAuthProvider(models.Model):
    _inherit = "auth.oauth.provider"

    allowed_domains = fields.Char(
        help="Comma-separated list of domains that can use this provider.",
    )
