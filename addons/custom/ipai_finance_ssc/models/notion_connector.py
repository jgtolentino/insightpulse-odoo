# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

# Notion client (optional dependency)
try:
    from notion_client import Client
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    _logger.info("Notion client not installed (optional). Run: pip install notion-client")


class NotionConnector(models.Model):
    """
    Notion Integration (Optional)

    Features:
    - Month-end task sync
    - BIR filing schedule
    - Workflow tracking

    NOTE: This is an optional integration. System works without Notion.
    """
    _name = 'finance.ssc.notion.connector'
    _description = 'Notion Connector (Optional)'

    def _get_client(self):
        """Get authenticated Notion client"""
        if not NOTION_AVAILABLE:
            _logger.warning('Notion client not available (optional dependency)')
            return None

        token = self.env['ir.config_parameter'].sudo().get_param('notion.token')
        if not token:
            _logger.warning('Notion token not configured (optional)')
            return None

        return Client(auth=token)

    def sync_month_end_tasks(self, agency):
        """Sync month-end closing tasks to Notion (optional)"""
        client = self._get_client()
        if not client:
            _logger.info(f"Skipping Notion sync for {agency.code} (not configured)")
            return

        # TODO: Implement Notion sync logic
        _logger.info(f"Notion sync not yet implemented for {agency.code}")

    @api.model
    def cron_sync_tasks(self):
        """Cron job for Notion sync (optional)"""
        client = self._get_client()
        if not client:
            return

        # TODO: Implement cron sync
        _logger.info("Notion cron sync not yet implemented")
