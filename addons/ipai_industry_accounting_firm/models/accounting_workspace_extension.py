# -*- coding: utf-8 -*-
from odoo import fields, models


class IpaiWorkspaceAccounting(models.Model):
    """
    Accounting Firm vertical extension for ipai.workspace.

    Adds month-end closing and compliance fields that only appear when industry='accounting_firm'.
    Smart Delta pattern: Keep vertical logic isolated from core workspace model.
    """

    _inherit = "ipai.workspace"

    # MONTH-END CLOSING METADATA
    fiscal_period = fields.Char(
        string="Fiscal Period",
        help="e.g. '2025-12' for December 2025",
    )

    entity_code = fields.Char(
        string="Legal Entity Code",
        help="Client's legal entity identifier",
    )

    closing_stage = fields.Selection(
        [
            ("prep", "Preparation"),
            ("execute", "Execution"),
            ("review", "Review"),
            ("file", "File & Archive"),
        ],
        string="Closing Stage",
        help="Month-end closing workflow stage",
    )
