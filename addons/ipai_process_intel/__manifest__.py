# -*- coding: utf-8 -*-
{
    'name': 'InsightPulse AI - Process Intelligence',
    'version': '19.0.1.0.0',
    'category': 'Productivity/AI',
    'summary': 'SAP Process Intelligence integration for process mining and analytics',
    'description': """
SAP Process Intelligence Integration
=====================================

Integrate SAP S/4HANA process mining capabilities directly into Odoo:

* Extract and analyze SAP process events (P2P, O2C, R2R)
* Variant analysis and conformance checking
* Bottleneck detection with P90 wait time analysis
* KPI prediction (throughput, delay, anomaly risk)
* Auto-generated process diagrams (Draw.io)
* ChatOps integration via Mattermost

Features:
---------
* Purchase Order process analysis
* Sales Order process analysis
* Real-time process diagrams
* Integration with Agent Gateway
* Supabase storage for analytics
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'purchase',
        'sale',
        'stock',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/process_intel_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
