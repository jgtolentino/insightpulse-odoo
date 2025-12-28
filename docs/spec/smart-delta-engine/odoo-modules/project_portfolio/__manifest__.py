# -*- coding: utf-8 -*-
{
    'name': 'Project Portfolio Management',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Portfolio management for Clarity PPM parity',
    'description': """
Project Portfolio Management
============================

Enterprise PPM parity module providing:
- Portfolio creation and governance
- Portfolio-to-project hierarchy
- Budget allocation per portfolio
- Scoring and prioritization
- Notion integration via webhooks

Smart Delta Classification:
- Gap Level: 2 (Minimal Custom)
- Justification: No OCA module for portfolio hierarchy
- OCA Contribution Path: OCA/project enhancement proposal

Dependencies:
- project (core)
- analytic (cost center integration)
- base_tier_validation (OCA - approval workflows)
    """,
    'author': 'Smart Delta Engine',
    'website': 'https://github.com/jgtolentino/superset',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'analytic',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/portfolio_security.xml',
        'views/project_portfolio_views.xml',
        'views/project_views.xml',
        'data/portfolio_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
