# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Task Stock Product Set",
    "version": "18.0.1.0.0",
    "category": "Project Management",
    "website": "https://github.com/OCA/project",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["project_task_stock", "product_set"],
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "wizard/project_task_stock_product_set_wizard_view.xml",
        "views/project_task_view.xml",
    ],
    "maintainers": ["victoralmau"],
}
