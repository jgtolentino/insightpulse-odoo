# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Dashboard Banner MIS Builder",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Display MIS builder KPIs in the accounting dashboard banner",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "development_status": "Beta",
    "website": "https://github.com/OCA/account-financial-tools",
    "depends": ["account_dashboard_banner", "mis_builder"],
    "data": [
        "views/account_dashboard_banner_cell.xml",
    ],
    "installable": True,
}
