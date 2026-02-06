"""
Field Documentation Notion Sync

Syncs Odoo field metadata to Notion database.
Uses External ID pattern for idempotent sync.

Usage:
    python scripts/notion_field_docs_sync.py --metadata docs/fields/metadata.json

External ID Format:
    field_{module}_{model}_{field}
    Example: field_hr_payroll_hr.employee_salary
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from notion_client import NotionClient, create_notion_property

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class FieldDocsNotionSync:
    """Sync Odoo field documentation to Notion."""

    def __init__(self, notion_token: str, database_id: str):
        self.client = NotionClient(api_token=notion_token)
        self.database_id = database_id

    def generate_external_id(self, field: dict) -> str:
        """Generate External ID for field."""
        module = (
            Path(field["file"]).parts[1]
            if len(Path(field["file"]).parts) > 1
            else "unknown"
        )
        return f"field_{module}_{field['model']}_{field['field_name']}"

    def sync_field(self, field: dict) -> str:
        """Sync single field to Notion."""
        external_id = self.generate_external_id(field)

        properties = {
            "Field Name": create_notion_property(
                "title", f"{field['model']}.{field['field_name']}"
            ),
            "Model": create_notion_property("rich_text", field["model"]),
            "Field Type": create_notion_property("select", field["field_type"]),
            "Label": create_notion_property(
                "rich_text", field["params"].get("label", "")
            ),
            "Help Text": create_notion_property(
                "rich_text", field["params"].get("help", "")
            ),
            "Required": create_notion_property(
                "checkbox", field["params"].get("required", False)
            ),
            "Readonly": create_notion_property(
                "checkbox", field["params"].get("readonly", False)
            ),
            "Source File": create_notion_property("rich_text", field["file"]),
        }

        page_id = self.client.upsert_page(
            database_id=self.database_id, external_id=external_id, properties=properties
        )

        logger.info(f"Synced: {field['model']}.{field['field_name']} → {page_id}")
        return page_id

    def sync_metadata(self, metadata_file: str) -> dict:
        """Sync all field metadata to Notion."""
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        fields = metadata.get("fields", [])
        logger.info(f"Syncing {len(fields)} fields...")

        page_ids = []
        for field in fields:
            try:
                page_id = self.sync_field(field)
                page_ids.append(page_id)
            except Exception as e:
                logger.error(f"Error syncing field {field.get('field_name')}: {e}")

        return {"total": len(fields), "synced": len(page_ids)}


def main():
    parser = argparse.ArgumentParser(description="Sync field documentation to Notion")
    parser.add_argument("--metadata", required=True, help="Path to field metadata JSON")
    parser.add_argument(
        "--database-id", help="Notion database ID (or use NOTION_FIELDS_DB_ID)"
    )
    args = parser.parse_args()

    notion_token = os.getenv("NOTION_API_TOKEN")
    database_id = args.database_id or os.getenv("NOTION_FIELDS_DB_ID")

    if not notion_token or not database_id:
        logger.error("❌ Missing credentials")
        sys.exit(1)

    syncer = FieldDocsNotionSync(notion_token, database_id)
    stats = syncer.sync_metadata(args.metadata)
    logger.info(f"✅ Synced {stats['synced']}/{stats['total']} fields")


if __name__ == "__main__":
    main()
