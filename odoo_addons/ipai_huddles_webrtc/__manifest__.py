# -*- coding: utf-8 -*-
{
    'name': 'IPAI Huddles WebRTC',
    'version': '19.0.1.0.0',
    'category': 'Discuss',
    'summary': 'Jitsi integration for audio/video calls and huddles',
    'description': """
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

    """,
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': ['ipai_chat_core'],
    
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
