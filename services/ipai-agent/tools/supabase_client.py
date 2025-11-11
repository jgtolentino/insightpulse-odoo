"""
Supabase Client
Provides high-level interface to Supabase database and Edge Functions
"""
import os
import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Supabase client for agent operations

    Environment variables:
    - SUPABASE_URL: Supabase project URL (e.g., https://spdtwktxdalcfigzeqrz.supabase.co)
    - SUPABASE_SERVICE_ROLE_KEY: Service role key (for backend operations, bypasses RLS)
    - SUPABASE_ANON_KEY: Anonymous key (for frontend operations, enforces RLS)
    """

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        use_service_role: bool = True
    ):
        """
        Initialize Supabase client

        Args:
            url: Supabase project URL (defaults to SUPABASE_URL env var)
            key: API key (defaults to SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY)
            use_service_role: If True, use service role key (bypasses RLS)
        """
        self.url = url or os.getenv('SUPABASE_URL')

        # Select appropriate key based on use_service_role flag
        if use_service_role:
            self.key = key or os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        else:
            self.key = key or os.getenv('SUPABASE_ANON_KEY')

        if not self.url or not self.key:
            raise ValueError("Supabase URL and API key required")

        # Initialize Supabase client
        try:
            self.client: Client = create_client(self.url, self.key)
            logger.info(f"✅ Connected to Supabase at {self.url}")
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """Test if connection is working"""
        try:
            # Simple query to test connection (tenants table always exists)
            response = self.client.table("tenants").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Supabase connection test failed: {str(e)}")
            return False

    def table(self, table_name: str):
        """
        Get table instance for queries

        Args:
            table_name: Name of the table (e.g., 'scout.transactions')

        Returns:
            Table instance for chaining queries

        Example:
            transactions = client.table("scout.transactions").select("*").execute()
        """
        return self.client.table(table_name)

    def rpc(self, function_name: str, params: Dict[str, Any]) -> Any:
        """
        Call Supabase RPC function

        Args:
            function_name: Name of the PostgreSQL function
            params: Parameters to pass to the function

        Returns:
            Function result

        Example:
            result = client.rpc("route_and_enqueue", {
                "p_kind": "DEPLOY_ADE",
                "p_payload": {"deployment_id": "abc123"}
            })
        """
        try:
            response = self.client.rpc(function_name, params).execute()
            return response.data
        except Exception as e:
            logger.error(f"❌ RPC call failed ({function_name}): {str(e)}")
            raise

    def query(
        self,
        table: str,
        select: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Simple query helper for common operations

        Args:
            table: Table name
            select: Fields to select (default: "*")
            filters: Dictionary of filters (e.g., {"company_id": 1, "state": "completed"})
            order: Order by clause (e.g., "created_at.desc")
            limit: Limit number of results

        Returns:
            List of records

        Example:
            transactions = client.query(
                "scout.transactions",
                filters={"company_id": 1, "transaction_type": "withholding_tax"},
                order="transaction_date.desc",
                limit=100
            )
        """
        try:
            query_builder = self.table(table).select(select)

            # Apply filters
            if filters:
                for key, value in filters.items():
                    query_builder = query_builder.eq(key, value)

            # Apply order
            if order:
                # Parse order (e.g., "created_at.desc" -> column, direction)
                parts = order.split('.')
                column = parts[0]
                ascending = len(parts) == 1 or parts[1] != "desc"
                query_builder = query_builder.order(column, desc=not ascending)

            # Apply limit
            if limit:
                query_builder = query_builder.limit(limit)

            response = query_builder.execute()
            return response.data

        except Exception as e:
            logger.error(f"❌ Query failed ({table}): {str(e)}")
            raise

    def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Insert a single record

        Args:
            table: Table name
            data: Record data

        Returns:
            Inserted record

        Example:
            record = client.insert("scout.transactions", {
                "company_id": 1,
                "transaction_date": "2025-11-10",
                "amount_withheld": 1000.00,
                ...
            })
        """
        try:
            response = self.table(table).insert(data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"❌ Insert failed ({table}): {str(e)}")
            raise

    def insert_many(
        self,
        table: str,
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Insert multiple records

        Args:
            table: Table name
            data: List of records

        Returns:
            List of inserted records
        """
        try:
            response = self.table(table).insert(data).execute()
            return response.data
        except Exception as e:
            logger.error(f"❌ Batch insert failed ({table}): {str(e)}")
            raise

    def update(
        self,
        table: str,
        filters: Dict[str, Any],
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Update records

        Args:
            table: Table name
            filters: Match conditions
            data: Update data

        Returns:
            List of updated records

        Example:
            updated = client.update(
                "scout.bir_batch_generation",
                {"batch_id": "batch123"},
                {"state": "submitted", "submitted_at": "2025-11-10T10:00:00Z"}
            )
        """
        try:
            query_builder = self.table(table).update(data)

            # Apply filters
            for key, value in filters.items():
                query_builder = query_builder.eq(key, value)

            response = query_builder.execute()
            return response.data

        except Exception as e:
            logger.error(f"❌ Update failed ({table}): {str(e)}")
            raise

    def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Delete records

        Args:
            table: Table name
            filters: Match conditions

        Returns:
            List of deleted records
        """
        try:
            query_builder = self.table(table).delete()

            # Apply filters
            for key, value in filters.items():
                query_builder = query_builder.eq(key, value)

            response = query_builder.execute()
            return response.data

        except Exception as e:
            logger.error(f"❌ Delete failed ({table}): {str(e)}")
            raise
