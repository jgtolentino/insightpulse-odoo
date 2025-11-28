# -*- coding: utf-8 -*-
from odoo import fields, models


class IpaiWorkspaceMarketing(models.Model):
    """
    Marketing Agency vertical extension for ipai.workspace.

    Adds campaign-specific fields that only appear when industry='marketing_agency'.
    Smart Delta pattern: Keep vertical logic isolated from core workspace model.
    """

    _inherit = "ipai.workspace"

    # CAMPAIGN METADATA
    campaign_type = fields.Selection(
        [
            ("brand", "Brand Campaign"),
            ("activation", "Activation"),
            ("digital", "Digital"),
            ("social", "Social"),
            ("performance", "Performance Marketing"),
        ],
        string="Campaign Type",
        help="Type of marketing campaign for workspace",
    )

    brand_name = fields.Char(
        string="Brand",
        help="Brand or product name for this campaign",
    )

    channel_mix = fields.Char(
        string="Channel Mix",
        help="e.g. 'TV 40% + Digital 30% + OOH 20% + Radio 10%'",
    )
