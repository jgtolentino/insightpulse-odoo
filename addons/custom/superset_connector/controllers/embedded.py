"""Superset Embedded Dashboard Controller with CSP Security"""

import logging
import re
from datetime import datetime
from urllib.parse import quote, urlencode

from odoo.exceptions import ValidationError
from odoo.http import request

from odoo import http

_logger = logging.getLogger(__name__)


class SupersetEmbedController(http.Controller):
    """Controller for embedding Superset dashboards with SSO and CSP"""

    @http.route(
        "/superset/embed/<int:dashboard_id>", type="http", auth="user", website=True
    )
    def embed_dashboard(self, dashboard_id, **kwargs):
        """
        Embed Superset dashboard with authentication and CSP headers

        Args:
            dashboard_id: ID of superset.dashboard record
            **kwargs: Additional parameters (filters, etc.)

        Returns:
            Rendered iframe view with CSP headers
        """
        try:
            # Get dashboard record
            Dashboard = request.env["superset.dashboard"].sudo()
            dashboard = Dashboard.browse(dashboard_id)

            if not dashboard.exists():
                return request.render(
                    "superset_connector.dashboard_not_found",
                    {"error": f"Dashboard {dashboard_id} not found"},
                )

            if not dashboard.is_active:
                return request.render(
                    "superset_connector.dashboard_inactive",
                    {"error": f"Dashboard {dashboard.name} is not active"},
                )

            # Get or create guest token
            token = self._get_or_create_token(dashboard, request.env.user)

            if not token:
                _logger.error(f"Failed to generate token for dashboard {dashboard_id}")
                return request.render(
                    "superset_connector.token_error",
                    {"error": "Failed to generate authentication token"},
                )

            # Build embed URL with token
            embed_url = self._build_embed_url(dashboard, token, kwargs)

            # Get CSP configuration
            csp_config = dashboard.config_id
            allowed_origins = csp_config.allowed_origins or dashboard.config_id.base_url

            # Render template with CSP headers
            response = request.render(
                "superset_connector.embed_dashboard",
                {
                    "dashboard": dashboard,
                    "embed_url": embed_url,
                    "token": token.token,
                    "expires_at": token.expires_at,
                },
            )

            # Add CSP headers
            response.headers["Content-Security-Policy"] = self._build_csp_header(
                allowed_origins
            )
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
            response.headers["X-Content-Type-Options"] = "nosniff"

            return response

        except Exception as e:
            _logger.exception(f"Error embedding dashboard {dashboard_id}: {e!s}")
            return request.render("superset_connector.embed_error", {"error": str(e)})

    @http.route("/superset/dashboards", type="http", auth="user", website=True)
    def dashboard_list(self, dashboard_id=None, **kwargs):
        """
        List available Superset dashboards or show specific dashboard

        Args:
            dashboard_id: Optional UUID of specific dashboard to display
            **kwargs: Additional filters

        Returns:
            Rendered dashboard list or specific dashboard view
        """
        try:
            Dashboard = request.env["superset.dashboard"].sudo()

            if dashboard_id:
                # Show specific dashboard
                dashboard = Dashboard.search(
                    [("dashboard_id", "=", dashboard_id), ("is_active", "=", True)],
                    limit=1,
                )

                if dashboard:
                    return self.embed_dashboard(dashboard.id, **kwargs)
                else:
                    return request.render(
                        "superset_connector.dashboard_not_found",
                        {"error": f"Dashboard {dashboard_id} not found or inactive"},
                    )
            else:
                # List all active dashboards
                dashboards = Dashboard.search([("is_active", "=", True)])
                return request.render(
                    "superset_connector.dashboard_list", {"dashboards": dashboards}
                )

        except Exception as e:
            _logger.exception(f"Error loading dashboards: {e!s}")
            return request.render("superset_connector.embed_error", {"error": str(e)})

    @http.route("/superset/token/refresh", type="json", auth="user")
    def refresh_token(self, dashboard_id):
        """
        Refresh expired or expiring token for dashboard

        Args:
            dashboard_id: ID of superset.dashboard record

        Returns:
            dict: New token and expiry information
        """
        try:
            Dashboard = request.env["superset.dashboard"].sudo()
            dashboard = Dashboard.browse(dashboard_id)

            if not dashboard.exists():
                raise ValidationError(f"Dashboard {dashboard_id} not found")

            # Invalidate old token and create new one
            Token = request.env["superset.token"].sudo()
            old_tokens = Token.search(
                [
                    ("dashboard_id", "=", dashboard_id),
                    ("user_id", "=", request.env.user.id),
                    ("is_active", "=", True),
                ]
            )
            old_tokens.write({"is_active": False})

            # Create new token
            new_token = self._get_or_create_token(
                dashboard, request.env.user, force_new=True
            )

            return {
                "success": True,
                "token": new_token.token,
                "expires_at": new_token.expires_at.isoformat(),
                "expires_in": int(
                    (new_token.expires_at - datetime.now()).total_seconds()
                ),
            }

        except Exception as e:
            _logger.exception(f"Error refreshing token: {e!s}")
            return {"success": False, "error": str(e)}

    def _get_or_create_token(self, dashboard, user, force_new=False):
        """
        Get existing valid token or create new one

        Args:
            dashboard: superset.dashboard record
            user: res.users record
            force_new: Force creation of new token even if valid one exists

        Returns:
            superset.token record
        """
        Token = request.env["superset.token"].sudo()

        if not force_new:
            # Try to find existing valid token
            existing_token = Token.search(
                [
                    ("dashboard_id", "=", dashboard.id),
                    ("user_id", "=", user.id),
                    ("is_active", "=", True),
                    ("expires_at", ">", datetime.now()),
                ],
                limit=1,
            )

            if existing_token:
                return existing_token

        # Create new token
        token = Token.create(
            {
                "dashboard_id": dashboard.id,
                "user_id": user.id,
                "config_id": dashboard.config_id.id,
            }
        )

        return token

    def _validate_filter_param(self, key, value):
        """
        Validate and sanitize filter parameters to prevent URL injection

        Args:
            key: Parameter key (must start with 'filter_')
            value: Parameter value to validate

        Returns:
            tuple: (validated_key, validated_value) or None if invalid

        Raises:
            ValidationError: If parameter is malicious
        """
        # Validate key format: filter_<name> where name is alphanumeric+underscore
        if not re.match(r"^filter_[a-zA-Z0-9_]+$", key):
            _logger.warning(f"Invalid filter parameter key: {key}")
            raise ValidationError(f"Invalid filter parameter format: {key}")

        # Validate value constraints
        if not isinstance(value, (str, int, float, bool)):
            raise ValidationError(f"Invalid filter value type for {key}: {type(value)}")

        # Convert to string and validate length (prevent DOS via huge params)
        value_str = str(value)
        if len(value_str) > 500:
            raise ValidationError(
                f"Filter value too long for {key}: {len(value_str)} chars"
            )

        # Check for URL injection patterns
        dangerous_patterns = [
            r"javascript:",  # XSS
            r"data:",  # Data URI XSS
            r"<script",  # Script injection
            r"onerror=",  # Event handler injection
            r"\.\./",  # Path traversal
            r"//",  # Protocol-relative URL
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, value_str, re.IGNORECASE):
                _logger.error(
                    f"Detected injection attempt in filter {key}: {value_str[:100]}"
                )
                raise ValidationError(f"Invalid characters in filter value for {key}")

        return (key, value_str)

    def _build_embed_url(self, dashboard, token, params):
        """
        Build Superset embed URL with authentication token

        Args:
            dashboard: superset.dashboard record
            token: superset.token record
            params: dict of additional URL parameters

        Returns:
            str: Complete embed URL
        """
        base_url = dashboard.config_id.base_url.rstrip("/")
        dashboard_uuid = dashboard.dashboard_id

        # Build query parameters (using dict for proper URL encoding)
        query_params = {
            "standalone": "1",
            "guest_token": token.token,
        }

        # Add validated filter parameters
        if params:
            for key, value in params.items():
                if key.startswith("filter_"):
                    try:
                        validated_key, validated_value = self._validate_filter_param(
                            key, value
                        )
                        query_params[validated_key] = validated_value
                    except ValidationError as e:
                        _logger.error(f"Filter validation failed: {e}")
                        # Skip invalid parameters instead of failing entire request
                        continue

        # Use urllib.parse.urlencode for proper URL encoding (prevents injection)
        query_string = urlencode(query_params, safe="", quote_via=quote)

        return f"{base_url}/superset/dashboard/{dashboard_uuid}/?{query_string}"

    def _build_csp_header(self, allowed_origins):
        """
        Build Content Security Policy header

        Args:
            allowed_origins: Comma-separated list of allowed origins

        Returns:
            str: CSP header value
        """
        # Parse allowed origins
        origins = [origin.strip() for origin in allowed_origins.split(",")]

        # Build CSP directives
        csp_directives = [
            "default-src 'self'",
            f"frame-src 'self' {' '.join(origins)}",
            f"connect-src 'self' {' '.join(origins)}",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
        ]

        return "; ".join(csp_directives)
