# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    module_source = fields.Selection(
        [
            ("odoo_community", "Odoo Community"),
            ("oca", "OCA (Odoo Community Association)"),
            ("custom", "Custom/InsightPulse AI"),
            ("third_party", "Third Party"),
        ],
        string="Source",
        compute="_compute_module_source",
        store=True,
        search="_search_module_source",
    )

    source_repository = fields.Char(
        string="Repository URL", compute="_compute_source_repository"
    )
    source_path = fields.Char(string="File Path", compute="_compute_source_path")
    is_oca_module = fields.Boolean(
        string="Is OCA Module", compute="_compute_module_source", store=True
    )

    @api.depends("name")
    def _compute_module_source(self):
        """Determine the source of each module based on its path"""
        for module in self:
            module_path = module._get_module_path()

            if "/oca-" in module_path or "/OCA/" in module_path:
                module.module_source = "oca"
                module.is_oca_module = True
            elif any(
                x in module_path
                for x in ["/custom", "/insightpulse", "/bir-forms", "/document-ai"]
            ):
                module.module_source = "custom"
                module.is_oca_module = False
            elif "/odoo/addons" in module_path or "/dist-packages/odoo" in module_path:
                module.module_source = "odoo_community"
                module.is_oca_module = False
            else:
                module.module_source = "third_party"
                module.is_oca_module = False

    @api.depends("name", "module_source")
    def _compute_source_repository(self):
        """Generate repository URL based on source"""
        for module in self:
            if module.module_source == "odoo_community":
                module.source_repository = (
                    f"https://github.com/odoo/odoo/tree/19.0/addons/{module.name}"
                )
            elif module.module_source == "oca":
                # Try to determine which OCA repo
                module_path = module._get_module_path()
                if "account-financial-tools" in module_path:
                    repo = "account-financial-tools"
                elif "server-tools" in module_path:
                    repo = "server-tools"
                elif "web" in module_path:
                    repo = "web"
                elif "reporting-engine" in module_path:
                    repo = "reporting-engine"
                elif "philippines" in module_path:
                    repo = "l10n-philippines"
                elif "account-invoicing" in module_path:
                    repo = "account-invoicing"
                elif "hr" in module_path:
                    repo = "hr"
                elif "manufacture" in module_path:
                    repo = "manufacture"
                else:
                    repo = "unknown"
                module.source_repository = (
                    f"https://github.com/OCA/{repo}/tree/19.0/{module.name}"
                )
            elif module.module_source == "custom":
                module.source_repository = (
                    f"https://insightpulseai.net/odoo/apps/{module.name}"
                )
            else:
                module.source_repository = False

    @api.depends("name")
    def _compute_source_path(self):
        """Get the actual file system path of the module"""
        for module in self:
            module.source_path = module._get_module_path()

    def _get_module_path(self):
        """Helper to get module's file system path"""
        try:
            return self.env["ir.module.module"].get_module_path(self.name)
        except Exception:
            return ""

    @api.model
    def _search_module_source(self, operator, value):
        """Enable filtering by module source"""
        modules = self.search([])
        filtered_ids = []
        for module in modules:
            module._compute_module_source()
            if operator == "=" and module.module_source == value:
                filtered_ids.append(module.id)
            elif operator == "!=" and module.module_source != value:
                filtered_ids.append(module.id)
        return [("id", "in", filtered_ids)]

    def action_view_source_repository(self):
        """Open source repository in browser"""
        self.ensure_one()
        if self.source_repository:
            return {
                "type": "ir.actions.act_url",
                "url": self.source_repository,
                "target": "new",
            }
