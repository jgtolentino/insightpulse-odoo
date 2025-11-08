#!/usr/bin/env python3
"""
Feature Request Submission Script for Notion

Simplified alternative to Odoo community feature request form.
Submits feature requests directly to Notion database.

Usage:
    python submit_feature_request.py \
        --title "Add multi-currency support" \
        --category "Finance" \
        --use-case "We operate in 3 countries..." \
        --priority "High" \
        --requester "john@company.com"

Environment Variables:
    NOTION_API_TOKEN: Notion API integration token
    NOTION_FEATURE_DB_ID: Feature Requests database ID

Dependencies:
    pip install notion-client click
"""

import os
import sys
import click
from datetime import datetime
from typing import Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from notion_client import NotionClient


# Feature request categories
CATEGORIES = [
    "Finance",
    "Inventory",
    "Sales",
    "HR",
    "BIR Compliance",
    "Mobile",
    "Superset",
    "Workflow",
    "Integration",
    "Other"
]

# Priority levels
PRIORITIES = ["Critical", "High", "Medium", "Low"]

# Status options (initial status is always "New")
STATUS = "🆕 New"


def validate_category(ctx, param, value):
    """Validate category selection."""
    if value and value not in CATEGORIES:
        raise click.BadParameter(
            f"Category must be one of: {', '.join(CATEGORIES)}"
        )
    return value


def validate_priority(ctx, param, value):
    """Validate priority selection."""
    if value and value not in PRIORITIES:
        raise click.BadParameter(
            f"Priority must be one of: {', '.join(PRIORITIES)}"
        )
    return value


@click.command()
@click.option(
    '--title',
    required=True,
    prompt='Feature title',
    help='Short, descriptive feature title'
)
@click.option(
    '--category',
    required=True,
    type=click.Choice(CATEGORIES, case_sensitive=False),
    prompt='Category',
    help='Feature category'
)
@click.option(
    '--use-case',
    required=True,
    prompt='Use case (describe the problem)',
    help='Detailed use case: What problem does this solve? Who benefits?'
)
@click.option(
    '--priority',
    type=click.Choice(PRIORITIES, case_sensitive=False),
    default='Medium',
    prompt='Priority',
    help='Business priority level'
)
@click.option(
    '--requester',
    prompt='Your email',
    help='Email address of requester'
)
@click.option(
    '--proposed-solution',
    default='',
    help='(Optional) Proposed solution or approach'
)
@click.option(
    '--module',
    default='',
    help='(Optional) Target Odoo module name'
)
@click.option(
    '--tags',
    default='',
    help='(Optional) Comma-separated tags'
)
@click.option(
    '--discussion-url',
    default='',
    help='(Optional) Link to Slack thread, GitHub issue, etc.'
)
def submit_feature_request(
    title: str,
    category: str,
    use_case: str,
    priority: str,
    requester: str,
    proposed_solution: str,
    module: str,
    tags: str,
    discussion_url: str
):
    """
    Submit a feature request to Notion database.

    This is a simplified alternative to the Odoo community feature request form.
    """
    click.echo("\n" + "="*70)
    click.echo("📝 INSIGHTPULSE FEATURE REQUEST SUBMISSION")
    click.echo("="*70 + "\n")

    # Validate environment variables
    api_token = os.getenv('NOTION_API_TOKEN')
    database_id = os.getenv('NOTION_FEATURE_DB_ID')

    if not api_token or not database_id:
        click.echo("❌ Error: Missing required environment variables:", err=True)
        click.echo("   - NOTION_API_TOKEN", err=True)
        click.echo("   - NOTION_FEATURE_DB_ID", err=True)
        click.echo("\nSet these in your .env file or export them.", err=True)
        sys.exit(1)

    # Initialize Notion client
    try:
        client = NotionClient(api_token=api_token)
        click.echo("✓ Connected to Notion")
    except Exception as e:
        click.echo(f"❌ Failed to connect to Notion: {e}", err=True)
        sys.exit(1)

    # Generate external ID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    category_slug = category.lower().replace(' ', '_')
    external_id = f"feature_{category_slug}_{timestamp}"

    # Build page content (use case + proposed solution)
    content_blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Use Case"}}]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": use_case}}]
            }
        }
    ]

    if proposed_solution:
        content_blocks.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Proposed Solution"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": proposed_solution}}]
                }
            }
        ])

    # Add metadata section
    metadata = f"Submitted by: {requester}\nSubmitted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if module:
        metadata += f"\nTarget Module: {module}"

    content_blocks.append({
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": metadata}}],
            "icon": {"emoji": "ℹ️"}
        }
    })

    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(',')] if tags else []

    # Build Notion properties
    properties = {
        'Title': {
            'title': [{'text': {'content': title}}]
        },
        'Status': {
            'select': {'name': STATUS}
        },
        'Priority': {
            'select': {'name': f"{'🔥' if priority == 'Critical' else '⬆️' if priority == 'High' else '➡️' if priority == 'Medium' else '⬇️'} {priority}"}
        },
        'Category': {
            'multi_select': [{'name': category}]
        },
        'Requester Email': {
            'email': requester
        },
        'Use Case': {
            'rich_text': [{'text': {'content': use_case[:2000]}}]  # Notion limit
        },
        'Requested Date': {
            'date': {'start': datetime.now().isoformat()}
        },
        'Votes': {
            'number': 0
        }
    }

    # Optional properties
    if module:
        properties['Module'] = {
            'select': {'name': module}
        }

    if tag_list:
        properties['Tags'] = {
            'multi_select': [{'name': tag} for tag in tag_list if tag]
        }

    if discussion_url:
        properties['Discussion URL'] = {
            'url': discussion_url
        }

    # Submit to Notion
    click.echo("\n📤 Submitting feature request...")
    click.echo(f"   Title: {title}")
    click.echo(f"   Category: {category}")
    click.echo(f"   Priority: {priority}")
    click.echo(f"   Requester: {requester}")

    try:
        page_id = client.upsert_page(
            database_id=database_id,
            external_id=external_id,
            properties=properties,
            children=content_blocks
        )

        click.echo("\n" + "="*70)
        click.echo("✅ FEATURE REQUEST SUBMITTED SUCCESSFULLY!")
        click.echo("="*70)
        click.echo(f"\nNotion Page ID: {page_id}")
        click.echo(f"External ID: {external_id}")
        click.echo("\nWhat happens next:")
        click.echo("1. Product team will review within 2-3 business days")
        click.echo("2. Community can vote on your request in Notion")
        click.echo("3. You'll be notified of status updates")
        click.echo("\nThank you for helping improve InsightPulse! 🚀\n")

    except Exception as e:
        click.echo(f"\n❌ Error submitting feature request: {e}", err=True)
        click.echo("\nPlease try again or contact support.", err=True)
        sys.exit(1)


@click.command()
def list_categories():
    """List available feature request categories."""
    click.echo("\n📋 Available Categories:\n")
    for i, category in enumerate(CATEGORIES, 1):
        click.echo(f"  {i}. {category}")
    click.echo()


@click.command()
def interactive():
    """Interactive mode for submitting feature requests."""
    click.echo("\n" + "="*70)
    click.echo("📝 FEATURE REQUEST - INTERACTIVE MODE")
    click.echo("="*70 + "\n")

    click.echo("Let's gather information about your feature request.\n")

    title = click.prompt("Feature title", type=str)

    click.echo("\nAvailable categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        click.echo(f"  {i}. {cat}")
    category_idx = click.prompt("Select category", type=click.IntRange(1, len(CATEGORIES)))
    category = CATEGORIES[category_idx - 1]

    use_case = click.prompt("\nDescribe the use case (what problem does this solve?)", type=str)

    click.echo("\nPriority levels:")
    for i, pri in enumerate(PRIORITIES, 1):
        click.echo(f"  {i}. {pri}")
    priority_idx = click.prompt("Select priority", type=click.IntRange(1, len(PRIORITIES)), default=3)
    priority = PRIORITIES[priority_idx - 1]

    requester = click.prompt("\nYour email", type=str)

    proposed_solution = click.prompt(
        "\n(Optional) Proposed solution",
        type=str,
        default='',
        show_default=False
    )

    module = click.prompt(
        "\n(Optional) Target Odoo module",
        type=str,
        default='',
        show_default=False
    )

    tags = click.prompt(
        "\n(Optional) Tags (comma-separated)",
        type=str,
        default='',
        show_default=False
    )

    discussion_url = click.prompt(
        "\n(Optional) Discussion URL (Slack, GitHub, etc.)",
        type=str,
        default='',
        show_default=False
    )

    # Confirm submission
    click.echo("\n" + "="*70)
    click.echo("REVIEW YOUR SUBMISSION")
    click.echo("="*70)
    click.echo(f"\nTitle: {title}")
    click.echo(f"Category: {category}")
    click.echo(f"Priority: {priority}")
    click.echo(f"Use Case: {use_case[:100]}...")
    if proposed_solution:
        click.echo(f"Proposed Solution: {proposed_solution[:100]}...")
    click.echo(f"Requester: {requester}")

    if click.confirm("\nSubmit this feature request?"):
        # Call the main submission function
        ctx = click.Context(submit_feature_request)
        ctx.invoke(
            submit_feature_request,
            title=title,
            category=category,
            use_case=use_case,
            priority=priority,
            requester=requester,
            proposed_solution=proposed_solution,
            module=module,
            tags=tags,
            discussion_url=discussion_url
        )
    else:
        click.echo("\n❌ Submission cancelled.")


@click.group()
def cli():
    """Feature Request Submission Tool for Notion"""
    pass


cli.add_command(submit_feature_request, name='submit')
cli.add_command(list_categories, name='categories')
cli.add_command(interactive, name='interactive')


if __name__ == '__main__':
    cli()
