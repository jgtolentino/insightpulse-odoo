# -*- coding: utf-8 -*-
{
    'name': 'IPAI Semantic Search',
    'version': '19.0.1.0.0',
    'category': 'Discuss',
    'summary': 'pgvector-based semantic search for messages and files',
    'description': """
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

    """,
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': ['ipai_chat_core'],
    'external_dependencies': {'python': ['openai', 'anthropic']},
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
