#!/usr/bin/env python3
"""Generate __manifest__.py for all IPAI Slack modules"""

import os
from pathlib import Path

MANIFESTS = {
    'ipai_slack_bridge': {
        'name': 'IPAI Slack Bridge',
        'summary': 'Bidirectional Slack integration - OAuth, Events API, message sync',
        'depends': ['ipai_chat_core', 'base_rest'],
        'description': '''
Slack Bridge - Bidirectional Integration
========================================

Features:
- Slack App OAuth flow
- Events API (messages, reactions, files)
- Slash commands (/odoov, custom)
- Interactive components (buttons, modals)
- Bidirectional message sync
- File sync
- User mapping

Endpoints:
- POST /slack/oauth/callback
- POST /slack/events
- POST /slack/commands
- POST /slack/actions
''',
    },
    'ipai_scim_provisioner': {
        'name': 'IPAI SCIM Provisioner',
        'summary': 'SCIM 2.0 user lifecycle management - provision, deprovision, sync',
        'depends': ['base', 'base_rest', 'base_rest_auth_jwt'],
        'description': '''
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
''',
    },
    'ipai_audit_discovery': {
        'name': 'IPAI Audit & eDiscovery',
        'summary': 'Immutable audit trail, legal hold, eDiscovery export',
        'depends': ['ipai_chat_core', 'auditlog'],
        'description': '''
Audit & eDiscovery
=================

Features:
- Immutable audit trail
- Legal hold (freeze deletions)
- eDiscovery export (filtered)
- Export formats (JSON, CSV, ZIP)
- SIEM integration API
- Compliance reporting

Events tracked:
- User actions (login/logout)
- Channel operations
- Message operations
- File operations
- DLP violations
- Hold operations
- Export requests
''',
    },
    'ipai_retention_policies': {
        'name': 'IPAI Retention Policies',
        'summary': 'Data retention, auto-purge, legal hold exceptions',
        'depends': ['ipai_chat_core', 'ipai_audit_discovery'],
        'description': '''
Retention Policies
=================

Features:
- Per-channel retention rules
- Global retention policies
- Auto-purge (nightly cron)
- Legal hold exceptions
- Important message exceptions
- Retention reporting
- Compliance dashboard
''',
    },
    'ipai_dlp_guard': {
        'name': 'IPAI DLP Guard',
        'summary': 'Data Loss Prevention - pattern detection, quarantine, review',
        'depends': ['ipai_chat_core'],
        'description': '''
DLP Guard - Data Loss Prevention
================================

Features:
- Pattern-based detection (regex)
- Pre-defined rules (SSN, credit cards, API keys, TIN)
- Custom rules
- Actions (block, quarantine, mask, alert)
- Admin review queue
- Compliance reporting

Built-in patterns:
- US Social Security Numbers
- Credit card numbers
- API keys and tokens
- Philippine TIN
- Custom regex patterns
''',
    },
    'ipai_huddles_webrtc': {
        'name': 'IPAI Huddles WebRTC',
        'summary': 'Jitsi integration for audio/video calls and huddles',
        'depends': ['ipai_chat_core'],
        'description': '''
Huddles - Audio/Video Calls
===========================

Features:
- Jitsi Meet integration
- One-click huddle start from channel
- Optional recording
- Recording → Odoo attachment
- Participant tracking
- Call history and analytics

Requirements:
- Jitsi server (self-hosted or cloud)
- Optional: Jibri for recording
''',
    },
    'ipai_workflow_bot': {
        'name': 'IPAI Workflow Bot',
        'summary': 'Slash commands, interactive dialogs, workflow automation',
        'depends': ['ipai_chat_core', 'base_automation'],
        'description': '''
Workflow Bot - Automation
=========================

Features:
- Custom slash commands
- Interactive dialogs/modals
- Server action integration
- Workflow builder UI
- Command history
- Approval workflows

Built-in commands:
- /odoov - Search Odoo
- /approve - Approve request
- /status - Show status
- /leave - Request leave
- /expense - Create expense
- /invoice - Create invoice
- /task - Create task
''',
    },
    'ipai_connect_external': {
        'name': 'IPAI Connect External',
        'summary': 'Guest/partner collaboration spaces (Slack Connect equivalent)',
        'depends': ['ipai_chat_core', 'portal'],
        'description': '''
External Connect - Guest Collaboration
======================================

Features:
- Guest/partner portal access
- Fenced channels (external-only)
- Invite management
- Access expiration
- Activity tracking
- Partner spaces

Use cases:
- Vendor collaboration
- Client communication
- Partner projects
- External consultants
''',
    },
    'ipai_search_vector': {
        'name': 'IPAI Semantic Search',
        'summary': 'pgvector-based semantic search for messages and files',
        'depends': ['ipai_chat_core'],
        'external_dependencies': {'python': ['openai', 'anthropic']},
        'description': '''
Semantic Search - AI-Powered
============================

Features:
- Embedding generation (OpenAI/Anthropic)
- Vector similarity search
- Hybrid search (keyword + semantic)
- Search suggestions
- Search analytics
- Natural language queries

Requirements:
- PostgreSQL with pgvector extension
- OpenAI or Anthropic API key
''',
    },
    'ipai_files_spaces': {
        'name': 'IPAI Files Storage',
        'summary': 'S3/DigitalOcean Spaces integration for large files',
        'depends': ['base'],
        'external_dependencies': {'python': ['boto3']},
        'description': '''
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
''',
    },
}

def create_manifest(module_name, config):
    """Create __manifest__.py for module"""
    manifest_path = Path(f'/home/user/insightpulse-odoo/odoo_addons/{module_name}/__manifest__.py')

    external_deps = config.get('external_dependencies', {})
    ext_deps_str = f"'external_dependencies': {external_deps}," if external_deps else ""

    manifest_content = f'''# -*- coding: utf-8 -*-
{{
    'name': '{config['name']}',
    'version': '19.0.1.0.0',
    'category': 'Discuss',
    'summary': '{config['summary']}',
    'description': """{config['description']}
    """,
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': {config['depends']},
    {ext_deps_str}
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}}
'''

    manifest_path.write_text(manifest_content)
    print(f'✅ Created {module_name}/__manifest__.py')

if __name__ == '__main__':
    for module_name, config in MANIFESTS.items():
        create_manifest(module_name, config)
    print('\n🎉 All manifests created!')
