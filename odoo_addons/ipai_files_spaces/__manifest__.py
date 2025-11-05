# -*- coding: utf-8 -*-
{
    'name': 'IPAI Files Storage',
    'version': '19.0.1.0.0',
    'category': 'Discuss',
    'summary': 'S3/DigitalOcean Spaces integration for large files',
    'description': """
Files Storage - Cloud Integration
=================================

Features:
- Offload large files to S3/DO Spaces
- Signed URLs for secure access
- Automatic cleanup
- CDN integration
- File analytics
- Storage quota management

Supported backends:
- DigitalOcean Spaces
- AWS S3
- MinIO
- S3-compatible storage

    """,
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': ['base'],
    'external_dependencies': {'python': ['boto3']},
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
