# -*- coding: utf-8 -*-

from odoo import models, api
import os
import logging

_logger = logging.getLogger(__name__)


class SupabaseClientWrapper(models.AbstractModel):
    """
    Supabase Client Wrapper for Odoo

    Provides access to Supabase Python client for querying scout schema tables.
    Reuses the SupabaseClient from ipai-agent service.

    Usage:
        supabase = self.env['supabase.client'].get_client()
        transactions = supabase.query("scout.transactions", filters={"company_id": 1})
    """

    _name = 'supabase.client'
    _description = 'Supabase Client Wrapper'

    @api.model
    def get_client(self):
        """
        Get Supabase client instance

        Returns configured SupabaseClient with service role access
        """
        try:
            # Import SupabaseClient from ipai-agent
            # NOTE: This assumes ipai-agent service tools are in Python path
            # Alternative: Copy SupabaseClient code directly into this module
            from tools.supabase_client import SupabaseClient

            # Initialize with service role for backend operations
            client = SupabaseClient(use_service_role=True)

            _logger.info(f"✅ Connected to Supabase at {client.url}")
            return client

        except ImportError:
            _logger.error("❌ Failed to import SupabaseClient. Ensure ipai-agent tools are in PYTHONPATH.")

            # Fallback: Create inline SupabaseClient
            return self._create_inline_client()

    @api.model
    def _create_inline_client(self):
        """
        Create inline Supabase client if ipai-agent tools not available

        This is a minimal implementation for Odoo-only deployments
        """
        try:
            from supabase import create_client, Client

            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

            if not url or not key:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")

            client = create_client(url, key)
            _logger.info(f"✅ Created inline Supabase client for {url}")

            # Wrap in simple helper class
            class SimpleSupabaseClient:
                def __init__(self, client):
                    self.client = client
                    self.url = url

                def query(self, table, select="*", filters=None, order=None, limit=None):
                    """Simple query helper"""
                    query_builder = self.client.table(table).select(select)

                    if filters:
                        for key, value in filters.items():
                            query_builder = query_builder.eq(key, value)

                    if order:
                        parts = order.split('.')
                        column = parts[0]
                        ascending = len(parts) == 1 or parts[1] != "desc"
                        query_builder = query_builder.order(column, desc=not ascending)

                    if limit:
                        query_builder = query_builder.limit(limit)

                    response = query_builder.execute()
                    return response.data

            return SimpleSupabaseClient(client)

        except Exception as e:
            _logger.error(f"❌ Failed to create Supabase client: {str(e)}")
            raise
