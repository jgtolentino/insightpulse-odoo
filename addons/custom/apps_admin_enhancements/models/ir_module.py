from odoo import api, fields, models
from odoo.modules.module import get_module_path


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    source = fields.Selection(
        [("odoo", "Odoo"), ("oca", "OCA"), ("custom", "Custom")],
        compute="_compute_source",
        store=False,
    )
    is_accessible = fields.Boolean(
        string="Accessible", compute="_compute_is_accessible", store=False
    )
    website_effective = fields.Char(
        string="Website (Effective)", compute="_compute_website_effective", store=False
    )

    def _compute_source(self):
        for rec in self:
            a = (rec.author or "").lower()
            if "oca" in a:
                rec.source = "oca"
            elif "odoo" in a:
                rec.source = "odoo"
            else:
                rec.source = "custom"

    def _compute_is_accessible(self):
        for rec in self:
            try:
                rec.is_accessible = bool(get_module_path(rec.name))
            except Exception:
                rec.is_accessible = False

    @api.depends("website")
    def _compute_website_effective(self):
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url") or ""
        for rec in self:
            if rec.website:
                rec.website_effective = rec.website
            else:
                rec.website_effective = f"{base}/apps#module={rec.name}"
