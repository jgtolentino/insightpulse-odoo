# -*- coding: utf-8 -*-
{
    'name': 'InsightPulse AI Agent Hybrid',
    'version': '19.0.1.0.0',
    'category': 'Productivity/AI',
    'summary': 'Odoo Studio × Notion Agent - Hybrid no-code + AI orchestration',
    'description': """
InsightPulse AI Agent Hybrid
============================

**Odoo Studio meets Notion Agent**: Studio handles your data + UI, the agent plans and executes multi-step work.

Features:
---------
* **Studio Macros**: Small, named automations defined in Odoo Studio
* **Agent Orchestrator**: LLM plans → calls tools → writes back to Odoo
* **Durable Memory**: KV + embeddings for voice/style/where-things-live
* **Connectors**: Slack, Google Drive, GitHub, Web

Core Models:
-----------
* **ip.page**: Notion-like document pages with markdown support
* **ip.agent.run**: Agent execution logs with cost tracking
* **ip.memory.kv**: Durable memory (user/team/org scope)

Workflows:
----------
* Meeting → PRD → Tasks → Slack
* Notion sync → Odoo pages
* GitHub issues → Odoo tickets
* BIR deadline → PRD → Compliance tasks

Integration:
-----------
* Works with slack_bridge for notifications
* Integrates with ipai_agent for AI processing
* Uses pg_cron for scheduled triggers
* Uses pg_net for webhooks

Author: Jake Tolentino
License: AGPL-3
    """,
    'author': 'Jake Tolentino',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'project',
        'calendar',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/memory_seeds.xml',
        'views/ip_page_views.xml',
        'views/ip_agent_run_views.xml',
        'views/ip_memory_kv_views.xml',
        'views/menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
