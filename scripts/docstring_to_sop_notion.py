"""
SOP (Standard Operating Procedures) Notion Sync

Syncs SOPs extracted from docstrings to Notion database.

Usage:
    python scripts/docstring_to_sop_notion.py --sop-dir docs/sops

External ID Format:
    sop_{module}_{sop_name}
    Example: sop_hr_payroll_month_end_closing
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from notion_client import NotionClient, create_notion_property

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class SOPNotionSync:
    """Sync SOPs to Notion."""

    def __init__(self, notion_token: str, database_id: str):
        self.client = NotionClient(api_token=notion_token)
        self.database_id = database_id

    def sync_sop(self, module: str, sop_name: str, sop_content: str) -> str:
        """Sync single SOP to Notion."""
        external_id = f"sop_{module}_{sop_name}"

        properties = {
            'SOP Name': create_notion_property('title', f"{module} - {sop_name}"),
            'Module': create_notion_property('select', module),
            'Type': create_notion_property('select', 'Procedure')
        }

        # Convert markdown content to Notion blocks
        children = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": sop_content[:2000]}}]
                }
            }
        ]

        page_id = self.client.upsert_page(
            database_id=self.database_id,
            external_id=external_id,
            properties=properties,
            children=children
        )

        logger.info(f"Synced SOP: {module}/{sop_name} → {page_id}")
        return page_id


def main():
    parser = argparse.ArgumentParser(description='Sync SOPs to Notion')
    parser.add_argument('--sop-dir', required=True, help='Path to SOPs directory')
    args = parser.parse_args()

    notion_token = os.getenv('NOTION_API_TOKEN')
    database_id = os.getenv('NOTION_SOP_DB_ID')

    if not notion_token or not database_id:
        logger.error("❌ Missing credentials")
        sys.exit(1)

    syncer = SOPNotionSync(notion_token, database_id)
    logger.info(f"✅ SOP sync initialized")


if __name__ == '__main__':
    main()
