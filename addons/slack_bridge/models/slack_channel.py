"""Slack channel mapping model for agency-channel associations"""

from odoo import api, fields, models


class SlackChannel(models.Model):
    """Slack channel configuration and mapping"""

    _name = "slack.channel"
    _description = "Slack Channel Mapping"
    _rec_name = "channel_name"

    channel_id = fields.Char(
        string="Channel ID", required=True, help="Slack channel ID (e.g., C01234567)"
    )
    channel_name = fields.Char(
        string="Channel Name",
        required=True,
        help="Slack channel name (e.g., #rim-finance)",
    )
    agency_code = fields.Selection(
        selection=[
            ("RIM", "RIM"),
            ("CKVC", "CKVC"),
            ("BOM", "BOM"),
            ("JPAL", "JPAL"),
            ("JLI", "JLI"),
            ("JAP", "JAP"),
            ("LAS", "LAS"),
            ("RMQB", "RMQB"),
        ],
        string="Agency",
        help="Associated agency code",
    )
    channel_type = fields.Selection(
        selection=[
            ("general", "General"),
            ("finance", "Finance"),
            ("sales", "Sales"),
            ("expense", "Expense"),
            ("bir", "BIR Compliance"),
            ("support", "Support"),
        ],
        string="Channel Type",
        required=True,
        default="general",
    )
    auto_respond = fields.Boolean(
        string="Auto-Respond",
        default=False,
        help="Automatically respond to messages in this channel",
    )
    active = fields.Boolean(default=True)
    notes = fields.Text(string="Notes")

    _sql_constraints = [
        (
            "channel_id_unique",
            "UNIQUE(channel_id)",
            "This Slack channel is already configured!",
        )
    ]

    @api.model
    def get_channel_for_agency(self, agency_code, channel_type="general"):
        """Get Slack channel ID for a specific agency and type

        Args:
            agency_code: Agency code (RIM, CKVC, etc.)
            channel_type: Channel type (general, finance, etc.)

        Returns:
            str: Slack channel ID or None
        """
        channel = self.search(
            [
                ("agency_code", "=", agency_code),
                ("channel_type", "=", channel_type),
                ("active", "=", True),
            ],
            limit=1,
        )

        return channel.channel_id if channel else None

    @api.model
    def get_all_finance_channels(self):
        """Get all finance Slack channels

        Returns:
            list: List of channel IDs
        """
        channels = self.search(
            [("channel_type", "=", "finance"), ("active", "=", True)]
        )

        return [ch.channel_id for ch in channels]
