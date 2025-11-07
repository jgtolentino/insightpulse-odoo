from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    ipai_code = fields.Char(
        string="IPAI Code",
        index=True,
        help="Internal InsightPulse AI identification code",
    )

    @api.depends("name", "ipai_code")
    def _compute_display_name(self):
        """Override display name to include IPAI code if present."""
        super()._compute_display_name()
        for rec in self:
            if rec.ipai_code:
                rec.display_name = f"{rec.display_name} [{rec.ipai_code}]"
