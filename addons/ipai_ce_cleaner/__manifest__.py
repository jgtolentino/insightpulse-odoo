# -*- coding: utf-8 -*-
{
    "name": "IPAI CE Cleaner (No Enterprise/IAP)",
    "summary": "Hides Enterprise/IAP upsells and rewires links away from odoo.com.",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "views/ipai_ce_cleaner_views.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            ("prepend", "ipai_ce_cleaner/static/src/css/ipai_ce_cleaner.css"),
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
