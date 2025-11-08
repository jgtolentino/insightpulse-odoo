from odoo import api, models
from urllib.parse import urlparse

SAFE_NETLOCS = set()


class IrActionsActUrl(models.Model):
    _inherit = "ir.actions.act_url"

    @api.model_create_multi
    def create(self, vals_list):
        """Sanitize external URLs to prevent odoo.com app store leakage"""
        apps_domain = self.env["ir.config_parameter"].sudo().get_param(
            "ip.apps_portal_domain", default=""
        )
        public_domain = self.env["ir.config_parameter"].sudo().get_param(
            "web.base.url", default=""
        )

        SAFE_NETLOCS.clear()
        for d in (apps_domain, public_domain):
            if d:
                netloc = urlparse("https://" + d.replace("https://", "").replace("http://", "")).netloc
                SAFE_NETLOCS.add(netloc)

        for vals in vals_list:
            url = vals.get("url") or ""
            if url:
                netloc = urlparse(url).netloc
                # Redirect any external domains (especially odoo.com) to local apps portal
                if netloc and netloc not in SAFE_NETLOCS and "odoo.com" in netloc:
                    vals["url"] = f"https://{apps_domain}/" if apps_domain else url

        return super().create(vals_list)

    def write(self, vals):
        """Sanitize URLs when modified"""
        if "url" in vals:
            apps_domain = self.env["ir.config_parameter"].sudo().get_param(
                "ip.apps_portal_domain", default=""
            )
            public_domain = self.env["ir.config_parameter"].sudo().get_param(
                "web.base.url", default=""
            )

            SAFE_NETLOCS.clear()
            for d in (apps_domain, public_domain):
                if d:
                    netloc = urlparse("https://" + d.replace("https://", "").replace("http://", "")).netloc
                    SAFE_NETLOCS.add(netloc)

            url = vals.get("url") or ""
            if url:
                netloc = urlparse(url).netloc
                if netloc and netloc not in SAFE_NETLOCS and "odoo.com" in netloc:
                    vals["url"] = f"https://{apps_domain}/" if apps_domain else url

        return super().write(vals)
