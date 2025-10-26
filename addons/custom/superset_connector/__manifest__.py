# -*- coding: utf-8 -*-
{
    'name': 'Superset Connector',
    'version': '19.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Integrate Apache Superset for advanced BI and data visualization',
    'description': """
Apache Superset Integration
============================

This module provides integration between Odoo and Apache Superset for advanced
Business Intelligence and data visualization capabilities.

Key Features
------------
* Secure dashboard embedding with guest tokens
* Row-level security (RLS) support
* Multi-company data isolation
* SSO authentication integration
* Content Security Policy (CSP) configuration
* Configurable Superset connection settings

Technical Details
-----------------
* Supports Superset 3.0+
* PostgreSQL database views for analytics
* OAuth/JWT token management
* Embedded iframe with security headers

Configuration
-------------
After installation:
1. Go to Settings > General Settings > Superset Integration
2. Configure Superset URL and authentication
3. Set up database connection in Superset
4. Create dashboards in Superset
5. Embed dashboards in Odoo using dashboard UUIDs

Security
--------
* Guest token authentication for embedded dashboards
* CSP headers to restrict iframe sources
* RLS enforcement based on Odoo user permissions
* Secure token storage with server environment support

For more information, see the README.rst file.
    """,
    'author': 'InsightPulseAI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/superset_menu.xml',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
