import logging

from odoo.http import request

from odoo import http

_logger = logging.getLogger(__name__)


class SecurityHardeningController(http.Controller):

    @http.route(
        "/web/database/manager", type="http", auth="public", methods=["GET", "POST"]
    )
    def block_database_manager(self, **kwargs):
        """Block database manager access in production"""
        _logger.warning(
            "Database manager access attempt blocked from IP: %s",
            request.httprequest.remote_addr,
        )

        # Return 403 Forbidden
        return request.render(
            "security_hardening.blocked_page",
            {
                "message": "Database manager access is disabled in production environment."
            },
        )

    @http.route(
        "/web/database/selector", type="http", auth="public", methods=["GET", "POST"]
    )
    def block_database_selector(self, **kwargs):
        """Block database selector access in production"""
        _logger.warning(
            "Database selector access attempt blocked from IP: %s",
            request.httprequest.remote_addr,
        )

        # Return 403 Forbidden
        return request.render(
            "security_hardening.blocked_page",
            {
                "message": "Database selector access is disabled in production environment."
            },
        )
