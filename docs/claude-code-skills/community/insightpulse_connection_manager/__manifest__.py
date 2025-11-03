# -*- coding: utf-8 -*-
{
    'name': 'InsightPulse Connection Manager',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'summary': 'Supabase-style connection UI for managing InsightPulse AI infrastructure',
    'description': """
        Connection Manager for InsightPulse AI Infrastructure
        ======================================================
        
        Centralized connection management interface inspired by Supabase's connection UI.
        
        Features:
        * Manage connections to Superset, Odoo, MCP servers, Supabase
        * Copy-to-clipboard for connection strings and env vars
        * Test connections and monitor health
        * Environment variable generation
        * Docker Compose snippet generation
        * Secure credential storage with encryption
        
        Perfect for Finance SSC operations managing:
        - BIR compliance dashboards (Superset)
        - Multi-agency Odoo instances
        - MCP server fleet
        - Supabase database
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/default_endpoints.xml',
        'views/connection_endpoint_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'insightpulse_connection_manager/static/src/scss/connection_manager.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
