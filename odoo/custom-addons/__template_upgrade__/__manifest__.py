# -*- coding: utf-8 -*-
{
    'name': 'OpenUpgrade Migration Template',
    'version': '19.0.1.0.0',
    'category': 'Hidden',
    'summary': 'Template for OpenUpgrade migration scripts',
    'description': """
OpenUpgrade Migration Template
===============================

This is a template module showing OpenUpgrade migration script structure.

DO NOT INSTALL THIS MODULE IN PRODUCTION!

Usage:
------
1. Copy this module to your custom addon (e.g., `my_custom_module`)
2. Update migrations/19.0.1.0.0/ scripts with your migration logic
3. Adjust version number to match your upgrade path
4. Test migration with OpenUpgrade test suite

Migration Script Types:
-----------------------
- pre-migration.py: Runs BEFORE module load (schema changes)
- post-migration.py: Runs AFTER module load (data updates)
- end-migration.py: Runs at END of upgrade (cleanup, validation)

References:
-----------
- OpenUpgrade Docs: https://github.com/OCA/OpenUpgrade
- Migration Guide: https://github.com/OCA/openupgradelib
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': ['base'],
    'installable': False,  # Template only - not installable
    'application': False,
    'auto_install': False,
}
