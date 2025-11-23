# -*- coding: utf-8 -*-
{
    "name": "IPAI Equipment Management",
    "summary": "Cheqroom-style equipment catalog, bookings, and incidents on Odoo CE + OCA.",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "maintenance",
        "project",
        "mail",
    ],
    "data": [
        "data/ipai_equipment_sequences.xml",
        "data/ipai_equipment_cron.xml",
        "security/ir.model.access.csv",
        "views/ipai_equipment_menus.xml",
        "views/ipai_equipment_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
