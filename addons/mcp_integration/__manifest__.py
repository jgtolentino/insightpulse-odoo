{
    'name': 'MCP Integration',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'summary': 'Model Context Protocol integration for Odoo workflows',
    'description': """
MCP Integration Module
======================

Integrate Odoo with MCP Coordinator for seamless multi-server operations:

- GitHub: Branch, PR, workflow automation
- DigitalOcean: App Platform deployment and monitoring
- Supabase: Direct database operations
- Notion: Knowledge base integration
- Superset: BI dashboard automation
- Tableau: Analytics integration

Features:
---------
* MCP Server Registry (6 servers)
* Operation History & Audit Trail
* Secure Credential Vault (encrypted)
* Odoo UI → MCP Coordinator Bridge
* MCP → Odoo Webhook Callbacks
* Admin Dashboard

Supported MCP Servers:
----------------------
1. GitHub (pulser-hub GitHub App)
2. DigitalOcean App Platform
3. Supabase PostgreSQL
4. Notion Workspace
5. Apache Superset
6. Tableau Cloud

Configuration:
--------------
Set environment variable MCP_COORDINATOR_URL or configure in Settings > MCP Integration

Author: Jake Tolentino
Website: https://github.com/jgtolentino/insightpulse-odoo
    """,
    'author': 'Jake Tolentino',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/mcp_server_views.xml',
        'views/mcp_operation_views.xml',
        'views/mcp_credential_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
