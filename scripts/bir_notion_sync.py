"""
BIR Compliance Notion Sync

Syncs BIR compliance calendar entries to Notion database.
Uses External ID pattern to prevent duplicates on repeated runs.

Usage:
    python scripts/bir_notion_sync.py --calendar docs/bir_calendar_2025_01.json

Required Environment Variables:
    NOTION_API_TOKEN - Notion API integration token
    NOTION_BIR_DB_ID - Notion database ID for BIR compliance

External ID Format:
    bir_{FormCode}_{CompanyCode}_{Year}_{Month}
    Example: bir_1601-C_RIM_2025_01
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from notion_client import NotionClient, create_notion_property

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class BIRNotionSync:
    """Sync BIR compliance calendar to Notion."""

    def __init__(self, notion_token: str, database_id: str):
        """
        Initialize BIR Notion sync.

        Args:
            notion_token: Notion API token
            database_id: BIR compliance database ID
        """
        self.client = NotionClient(api_token=notion_token)
        self.database_id = database_id
        logger.info(f"Initialized BIR sync for database: {database_id}")

    def generate_external_id(
        self, form_code: str, company_code: str, deadline: str
    ) -> str:
        """
        Generate External ID for BIR entry.

        Args:
            form_code: BIR form code (1601-C, 2550Q, etc.)
            company_code: Company code (RIM, CKVC, BOM, etc.)
            deadline: Deadline date (YYYY-MM-DD)

        Returns:
            External ID string (bir_{form}_{company_code}_{year}_{month})
        """
        date_obj = datetime.fromisoformat(deadline)
        year = date_obj.year
        month = f"{date_obj.month:02d}"
        return f"bir_{form_code}_{company_code}_{year}_{month}"

    def sync_entry(self, entry: dict) -> str:
        """
        Sync single BIR entry to Notion.

        Args:
            entry: BIR calendar entry dict

        Returns:
            Notion page ID
        """
        external_id = self.generate_external_id(
            form_code=entry["form"],
            company_code=entry["company"],
            deadline=entry["deadline"],
        )

        properties = {
            "Form Code": create_notion_property(
                "title", f"{entry['form']} - {entry['name']}"
            ),
            "Company": create_notion_property("select", entry["company"]),
            "Deadline": create_notion_property("date", entry["deadline"]),
            "Reminder Date": create_notion_property("date", entry["reminder_date"]),
            "Status": create_notion_property("select", "Pending"),
            "Priority": create_notion_property("select", "High"),
        }

        # Create checklist as page children
        children = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Checklist"}}]
                },
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Gather supporting documents"},
                        }
                    ],
                    "checked": False,
                },
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"Prepare {entry['form']} form"},
                        }
                    ],
                    "checked": False,
                },
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Review with Finance Officer"},
                        }
                    ],
                    "checked": False,
                },
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "Submit to BIR"}}
                    ],
                    "checked": False,
                },
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "File copy in company folder"},
                        }
                    ],
                    "checked": False,
                },
            },
        ]

        page_id = self.client.upsert_page(
            database_id=self.database_id,
            external_id=external_id,
            properties=properties,
            children=children,
        )

        logger.info(f"Synced: {entry['form']} - {entry['company']} → {page_id}")
        return page_id

    def sync_calendar(self, calendar_file: str) -> dict:
        """
        Sync entire BIR calendar to Notion.

        Args:
            calendar_file: Path to BIR calendar JSON file

        Returns:
            Sync statistics dict
        """
        if not os.path.exists(calendar_file):
            raise FileNotFoundError(f"Calendar file not found: {calendar_file}")

        with open(calendar_file, "r") as f:
            calendar_entries = json.load(f)

        logger.info(f"Syncing {len(calendar_entries)} BIR entries...")

        page_ids = []
        errors = []

        for entry in calendar_entries:
            try:
                page_id = self.sync_entry(entry)
                page_ids.append(page_id)
            except Exception as e:
                logger.error(
                    f"Error syncing entry {entry.get('form')} - {entry.get('company')}: {e}"
                )
                errors.append({"entry": entry, "error": str(e)})

        stats = {
            "total": len(calendar_entries),
            "synced": len(page_ids),
            "errors": len(errors),
            "success_rate": (
                (len(page_ids) / len(calendar_entries) * 100) if calendar_entries else 0
            ),
        }

        logger.info(
            f"✅ Sync complete: {stats['synced']}/{stats['total']} entries "
            f"({stats['success_rate']:.1f}% success rate)"
        )

        if errors:
            logger.warning(f"⚠️  {len(errors)} errors occurred during sync")

        return stats


def main():
    """Main entry point for BIR Notion sync."""
    parser = argparse.ArgumentParser(
        description="Sync BIR compliance calendar to Notion"
    )
    parser.add_argument(
        "--calendar", required=True, help="Path to BIR calendar JSON file"
    )
    parser.add_argument(
        "--database-id", help="Notion database ID (or use NOTION_BIR_DB_ID env var)"
    )
    parser.add_argument(
        "--token", help="Notion API token (or use NOTION_API_TOKEN env var)"
    )
    args = parser.parse_args()

    # Get credentials
    notion_token = args.token or os.getenv("NOTION_API_TOKEN")
    database_id = args.database_id or os.getenv("NOTION_BIR_DB_ID")

    if not notion_token:
        logger.error(
            "❌ Notion API token required (--token or NOTION_API_TOKEN env var)"
        )
        sys.exit(1)

    if not database_id:
        logger.error(
            "❌ Notion database ID required (--database-id or NOTION_BIR_DB_ID env var)"
        )
        sys.exit(1)

    # Run sync
    try:
        syncer = BIRNotionSync(notion_token=notion_token, database_id=database_id)
        stats = syncer.sync_calendar(args.calendar)

        # Print summary
        print("\n" + "=" * 50)
        print("BIR Compliance Notion Sync - Summary")
        print("=" * 50)
        print(f"Total entries: {stats['total']}")
        print(f"Successfully synced: {stats['synced']}")
        print(f"Errors: {stats['errors']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print("=" * 50 + "\n")

        sys.exit(0 if stats["errors"] == 0 else 1)

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
