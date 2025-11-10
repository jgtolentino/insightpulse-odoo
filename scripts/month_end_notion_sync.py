"""
Month-End Tasks Notion Sync

Syncs month-end closing tasks to Notion database.
Uses External ID pattern to prevent duplicates.

Usage:
    python scripts/month_end_notion_sync.py --tasks docs/month_end_tasks_2025_01.json

Required Environment Variables:
    NOTION_API_TOKEN - Notion API integration token
    NOTION_MONTHEND_DB_ID - Notion database ID for month-end tasks

External ID Format:
    monthend_{Agency}_{Task}_{Year}_{Month}
    Example: monthend_RIM_BankReconciliation_2025_01
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


class MonthEndNotionSync:
    """Sync month-end tasks to Notion."""

    def __init__(self, notion_token: str, database_id: str):
        self.client = NotionClient(api_token=notion_token)
        self.database_id = database_id
        logger.info(f"Initialized month-end sync for database: {database_id}")

    def generate_external_id(self, agency: str, task: str, deadline: str) -> str:
        """Generate External ID for month-end task."""
        task_key = task.replace(" ", "")  # Remove spaces
        year_month = deadline[:7].replace("-", "_")  # 2025-01 → 2025_01
        return f"monthend_{agency}_{task_key}_{year_month}"

    def get_priority_emoji(self, priority: str) -> str:
        """Get emoji for priority level."""
        priority_map = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}
        return priority_map.get(priority.lower(), "⚪")

    def sync_task(self, task: dict) -> str:
        """Sync single month-end task to Notion."""
        external_id = self.generate_external_id(
            agency=task["agency"], task=task["task"], deadline=task["deadline"]
        )

        priority_emoji = self.get_priority_emoji(task["priority"])

        properties = {
            "Task": create_notion_property(
                "title", f"{priority_emoji} {task['task']} - {task['agency']}"
            ),
            "Agency": create_notion_property("select", task["agency"]),
            "Month": create_notion_property("rich_text", task["month"]),
            "Deadline": create_notion_property("date", task["deadline"]),
            "Priority": create_notion_property("select", task["priority"].capitalize()),
            "Status": create_notion_property("select", "Pending"),
        }

        # Create subtask checklist
        children = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Checklist"}}]
                },
            }
        ]

        for subtask in task.get("subtasks", []):
            children.append(
                {
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": subtask}}],
                        "checked": False,
                    },
                }
            )

        # Add notes section
        children.extend(
            [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "Notes"}}]
                    },
                },
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Complete all subtasks before marking as done"
                                },
                            }
                        ]
                    },
                },
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Attach supporting documents in comments"
                                },
                            }
                        ]
                    },
                },
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Tag Finance Officer for approval when ready"
                                },
                            }
                        ]
                    },
                },
            ]
        )

        page_id = self.client.upsert_page(
            database_id=self.database_id,
            external_id=external_id,
            properties=properties,
            children=children,
        )

        logger.info(f"Synced: {task['task']} - {task['agency']} → {page_id}")
        return page_id

    def sync_tasks(self, tasks_file: str) -> dict:
        """Sync all month-end tasks to Notion."""
        if not os.path.exists(tasks_file):
            raise FileNotFoundError(f"Tasks file not found: {tasks_file}")

        with open(tasks_file, "r") as f:
            tasks = json.load(f)

        logger.info(f"Syncing {len(tasks)} month-end tasks...")

        page_ids = []
        errors = []

        for task in tasks:
            try:
                page_id = self.sync_task(task)
                page_ids.append(page_id)
            except Exception as e:
                logger.error(
                    f"Error syncing task {task.get('task')} - {task.get('agency')}: {e}"
                )
                errors.append({"task": task, "error": str(e)})

        stats = {
            "total": len(tasks),
            "synced": len(page_ids),
            "errors": len(errors),
            "success_rate": (len(page_ids) / len(tasks) * 100) if tasks else 0,
        }

        logger.info(
            f"✅ Sync complete: {stats['synced']}/{stats['total']} tasks "
            f"({stats['success_rate']:.1f}% success rate)"
        )

        return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Sync month-end tasks to Notion")
    parser.add_argument(
        "--tasks", required=True, help="Path to month-end tasks JSON file"
    )
    parser.add_argument(
        "--database-id",
        help="Notion database ID (or use NOTION_MONTHEND_DB_ID env var)",
    )
    parser.add_argument(
        "--token", help="Notion API token (or use NOTION_API_TOKEN env var)"
    )
    args = parser.parse_args()

    notion_token = args.token or os.getenv("NOTION_API_TOKEN")
    database_id = args.database_id or os.getenv("NOTION_MONTHEND_DB_ID")

    if not notion_token:
        logger.error("❌ Notion API token required")
        sys.exit(1)

    if not database_id:
        logger.error("❌ Notion database ID required")
        sys.exit(1)

    try:
        syncer = MonthEndNotionSync(notion_token=notion_token, database_id=database_id)
        stats = syncer.sync_tasks(args.tasks)

        print("\n" + "=" * 50)
        print("Month-End Tasks Notion Sync - Summary")
        print("=" * 50)
        print(f"Total tasks: {stats['total']}")
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
