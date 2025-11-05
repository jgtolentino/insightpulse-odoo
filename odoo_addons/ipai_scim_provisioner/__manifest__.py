# -*- coding: utf-8 -*-
{
    'name': 'IPAI SCIM Provisioner',
    'version': '19.0.1.0.0',
    'category': 'Discuss',
    'summary': 'SCIM 2.0 user lifecycle management - provision, deprovision, sync',
    'description': """
SCIM 2.0 Provisioner
===================

Features:
- SCIM 2.0 compliant endpoints
- User provisioning (create/update/delete)
- Group management
- Role mapping (external → Odoo groups)
- Automatic deprovisioning
- Sync status tracking

Endpoints:
- GET/POST/PUT/PATCH/DELETE /scim/v2/Users
- GET/POST /scim/v2/Groups

Integration: Azure AD, Okta, OneLogin

    """,
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': ['base', 'base_rest', 'base_rest_auth_jwt'],
    
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
