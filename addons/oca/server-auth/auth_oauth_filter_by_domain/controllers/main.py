from odoo.http import request

from odoo.addons.auth_oauth.controllers.main import OAuthLogin


class OAuthLoginCustom(OAuthLogin):
    def list_providers(self):
        """Filter OAuth Providers based on the current domain"""
        providers = super().list_providers()
        host = request.httprequest.host.split(":")[0]

        filtered_providers = []
        for provider in providers:
            allowed_domains = provider.get("allowed_domains", "")
            if not allowed_domains or host in [
                domain.strip() for domain in allowed_domains.split(",")
            ]:
                filtered_providers.append(provider)

        return filtered_providers
