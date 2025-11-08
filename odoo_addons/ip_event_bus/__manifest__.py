# -*- coding: utf-8 -*-
{
    "name": "InsightPulse Event Bus",
    "version": "19.0.1.0.0",
    "summary": "Signed event ingress/egress for Supabase bridge",
    "description": """
        InsightPulse Event Bus
        ======================

        Bi-directional event bridge between Odoo and Supabase:

        * **Odoo → Supabase**: Fire signed webhooks on model changes
        * **Supabase → Odoo**: Receive signed action requests
        * **Security**: HMAC-SHA256 signatures on all requests
        * **Audit**: Log all events to ir.logging
        * **Extensible**: Plugin architecture for custom actions

        Features:
        ---------
        * HTTP controllers for event push/pull
        * HMAC signature verification
        * API key authentication
        * Configurable via System Parameters
        * Audit logging for compliance

        Configuration:
        --------------
        Set these System Parameters:
        * ip.hmac.secret - Shared HMAC secret
        * ip.odoo.api_key - API key for inbound requests
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "category": "Tools",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
