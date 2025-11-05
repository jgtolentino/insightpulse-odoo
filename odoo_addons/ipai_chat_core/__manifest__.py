# -*- coding: utf-8 -*-
{
    'name': 'IPAI Chat Core',
    'version': '19.0.1.0.0',
    'category': 'Discuss',
    'summary': 'Enterprise-grade chat foundation - RBAC, channel policies, thread UX',
    'description': """
IPAI Chat Core - Enterprise Chat Foundation
===========================================

Hardens Odoo Discuss for enterprise use with:

**Features:**
- Advanced RBAC for channels (read/write/admin/moderate)
- Channel policies (retention, DLP, guest access)
- Enhanced thread UX (threaded conversations, reactions)
- Message priority and pinning
- Channel categories and organization
- Read receipts and typing indicators
- Rich message formatting (markdown)
- @mentions with notifications
- Message search and filters
- Channel analytics

**Slack Enterprise Equivalent:**
Provides the foundation for Slack-like workspace chat with:
- Public/private channels
- Direct messages
- Threads and replies
- Reactions and emojis
- File sharing
- Search
- Notifications

**Integration:**
- Works with mail.channel (Odoo Discuss)
- Extends mail.message for enterprise features
- Integrates with auditlog for compliance
- Ready for ipai_slack_bridge integration

**Dependencies:**
- mail (native Odoo)
- web_responsive (OCA)
- web_widget_markdown (OCA)
- auditlog (OCA - optional)

**Technical:**
- Adds channel access control lists
- Message threading improvements
- Real-time updates via longpolling
- Mobile-responsive UI
- Accessible (WCAG 2.1 AA)

**For Finance SSC:**
- Multi-agency channel isolation
- Compliance-ready messaging
- Audit trail for all communications
- Integration with BIR workflows
    """,
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'base',
        'web',
    ],
    'external_dependencies': {
        'python': ['markdown'],
    },
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/security.xml',

        # Data
        'data/channel_categories.xml',
        'data/message_templates.xml',

        # Views
        'views/mail_channel_views.xml',
        'views/mail_message_views.xml',
        'views/chat_dashboard_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ipai_chat_core/static/src/css/chat.css',
            'ipai_chat_core/static/src/js/chat_thread.js',
            'ipai_chat_core/static/src/js/chat_message.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
