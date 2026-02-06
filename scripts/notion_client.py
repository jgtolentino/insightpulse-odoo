"""
Notion API Client with External ID Upsert Pattern

Provides idempotent operations for Finance SSC automation workflows.
External IDs prevent duplicate entries when workflows run multiple times.

Usage:
    client = NotionClient(api_token=os.getenv('NOTION_API_TOKEN'))
    client.upsert_page(
        database_id='your_database_id',
        external_id='bir_Form_1601-C_RIM_2025_01',
        properties={'Title': 'BIR Form 1601-C - RIM'}
    )

Dependencies:
    pip install notion-client python-dateutil
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from notion_client import Client
from notion_client.errors import APIResponseError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotionClient:
    """Notion API client with External ID upsert pattern for idempotent operations."""

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Notion client.

        Args:
            api_token: Notion API token. Defaults to NOTION_API_TOKEN env var.
        """
        self.api_token = api_token or os.getenv("NOTION_API_TOKEN")
        if not self.api_token:
            raise ValueError("Notion API token required (NOTION_API_TOKEN env var)")

        self.client = Client(auth=self.api_token)
        logger.info("Notion client initialized")

    def find_by_external_id(self, database_id: str, external_id: str) -> Optional[str]:
        """
        Find page by external ID in database.

        Args:
            database_id: Notion database ID
            external_id: External ID to search for

        Returns:
            Page ID if found, None otherwise
        """
        try:
            response = self.client.databases.query(
                database_id=database_id,
                filter={
                    "property": "External ID",
                    "rich_text": {"equals": external_id},
                },
            )

            if response.get("results"):
                page_id = response["results"][0]["id"]
                logger.info(
                    f"Found existing page: {page_id} (external_id={external_id})"
                )
                return page_id

            logger.info(f"No existing page found (external_id={external_id})")
            return None

        except APIResponseError as e:
            logger.error(f"Error querying database: {e}")
            return None

    def upsert_page(
        self,
        database_id: str,
        external_id: str,
        properties: Dict[str, Any],
        children: Optional[List[Dict]] = None,
    ) -> str:
        """
        Create or update page using External ID pattern.

        Args:
            database_id: Notion database ID
            external_id: Unique external ID (e.g., 'bir_Form_1601-C_RIM_2025_01')
            properties: Page properties dict
            children: Optional list of block children

        Returns:
            Page ID of created/updated page
        """
        # Add External ID to properties
        properties["External ID"] = {"rich_text": [{"text": {"content": external_id}}]}

        # Add timestamp
        properties["Last Synced"] = {"date": {"start": datetime.now().isoformat()}}

        # Check if page already exists
        existing_page_id = self.find_by_external_id(database_id, external_id)

        if existing_page_id:
            # Update existing page
            logger.info(f"Updating page: {existing_page_id}")
            self.client.pages.update(page_id=existing_page_id, properties=properties)
            return existing_page_id
        else:
            # Create new page
            logger.info(f"Creating new page (external_id={external_id})")
            response = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties,
                children=children or [],
            )
            return response["id"]

    def create_database_schema(
        self, parent_page_id: str, title: str, properties: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Create new database with schema.

        Args:
            parent_page_id: Parent page ID
            title: Database title
            properties: Database properties schema

        Returns:
            Database ID
        """
        # Ensure External ID and Last Synced columns exist
        if "External ID" not in properties:
            properties["External ID"] = {"rich_text": {}}
        if "Last Synced" not in properties:
            properties["Last Synced"] = {"date": {}}

        response = self.client.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": title}}],
            properties=properties,
        )

        database_id = response["id"]
        logger.info(f"Created database: {title} ({database_id})")
        return database_id

    def bulk_upsert(
        self,
        database_id: str,
        items: List[Dict[str, Any]],
        external_id_field: str = "external_id",
    ) -> List[str]:
        """
        Bulk upsert multiple pages.

        Args:
            database_id: Notion database ID
            items: List of items with external_id and properties
            external_id_field: Field name containing external ID

        Returns:
            List of page IDs
        """
        page_ids = []

        for item in items:
            external_id = item.get(external_id_field)
            if not external_id:
                logger.warning(f"Skipping item without external ID: {item}")
                continue

            properties = item.get("properties", {})
            children = item.get("children")

            try:
                page_id = self.upsert_page(
                    database_id=database_id,
                    external_id=external_id,
                    properties=properties,
                    children=children,
                )
                page_ids.append(page_id)
            except Exception as e:
                logger.error(f"Error upserting item {external_id}: {e}")

        logger.info(f"Bulk upsert complete: {len(page_ids)}/{len(items)} successful")
        return page_ids

    def get_database_items(
        self, database_id: str, filter_params: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Retrieve all items from database.

        Args:
            database_id: Notion database ID
            filter_params: Optional filter parameters

        Returns:
            List of page objects
        """
        query_params = {"database_id": database_id}
        if filter_params:
            query_params["filter"] = filter_params

        results = []
        has_more = True
        next_cursor = None

        while has_more:
            if next_cursor:
                query_params["start_cursor"] = next_cursor

            response = self.client.databases.query(**query_params)
            results.extend(response.get("results", []))

            has_more = response.get("has_more", False)
            next_cursor = response.get("next_cursor")

        logger.info(f"Retrieved {len(results)} items from database")
        return results


def create_notion_property(prop_type: str, value: Any) -> Dict[str, Any]:
    """
    Helper function to create Notion property objects.

    Args:
        prop_type: Property type (title, rich_text, number, select, date, etc.)
        value: Property value

    Returns:
        Notion property object
    """
    if prop_type == "title":
        return {"title": [{"text": {"content": str(value)}}]}
    elif prop_type == "rich_text":
        return {"rich_text": [{"text": {"content": str(value)}}]}
    elif prop_type == "number":
        return {"number": float(value)}
    elif prop_type == "select":
        return {"select": {"name": str(value)}}
    elif prop_type == "multi_select":
        return {"multi_select": [{"name": item} for item in value]}
    elif prop_type == "date":
        return {"date": {"start": value}}
    elif prop_type == "checkbox":
        return {"checkbox": bool(value)}
    elif prop_type == "url":
        return {"url": str(value)}
    else:
        raise ValueError(f"Unsupported property type: {prop_type}")


if __name__ == "__main__":
    # Example usage
    client = NotionClient()

    # Example: Create BIR Compliance database schema
    # bir_db_id = client.create_database_schema(
    #     parent_page_id='your_parent_page_id',
    #     title='BIR Compliance Calendar',
    #     properties={
    #         'Form Code': {'title': {}},
    #         'Agency': {'select': {}},
    #         'Deadline': {'date': {}},
    #         'Status': {'select': {}},
    #         'External ID': {'rich_text': {}},
    #         'Last Synced': {'date': {}}
    #     }
    # )

    # Example: Upsert BIR entry
    # client.upsert_page(
    #     database_id=bir_db_id,
    #     external_id='bir_Form_1601-C_RIM_2025_01',
    #     properties={
    #         'Form Code': create_notion_property('title', '1601-C'),
    #         'Agency': create_notion_property('select', 'RIM'),
    #         'Deadline': create_notion_property('date', '2025-01-10'),
    #         'Status': create_notion_property('select', 'Pending')
    #     }
    # )

    logger.info("Notion client ready")
