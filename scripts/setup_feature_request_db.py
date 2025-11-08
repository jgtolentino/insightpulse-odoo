#!/usr/bin/env python3
"""
Setup Feature Request Database in Notion

Creates a new Notion database with the correct schema for feature requests.
Run this once to set up your feature request system.

Usage:
    python setup_feature_request_db.py --parent-page-id <notion_page_id>

Environment Variables:
    NOTION_API_TOKEN: Notion API integration token

Dependencies:
    pip install notion-client click
"""

import os
import sys
import click
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from notion_client import Client


@click.command()
@click.option(
    '--parent-page-id',
    required=True,
    help='Notion page ID where database will be created'
)
@click.option(
    '--database-title',
    default='Feature Requests',
    help='Title for the database'
)
def setup_database(parent_page_id: str, database_title: str):
    """
    Create Feature Request database in Notion with proper schema.
    """
    click.echo("\n" + "="*70)
    click.echo("🏗️  SETTING UP FEATURE REQUEST DATABASE IN NOTION")
    click.echo("="*70 + "\n")

    # Validate environment
    api_token = os.getenv('NOTION_API_TOKEN')
    if not api_token:
        click.echo("❌ Error: NOTION_API_TOKEN environment variable not set", err=True)
        sys.exit(1)

    # Initialize Notion client
    try:
        notion = Client(auth=api_token)
        click.echo("✓ Connected to Notion")
    except Exception as e:
        click.echo(f"❌ Failed to connect: {e}", err=True)
        sys.exit(1)

    # Define database schema
    properties = {
        # Title field
        'Title': {
            'title': {}
        },

        # Status select
        'Status': {
            'select': {
                'options': [
                    {'name': '🆕 New', 'color': 'blue'},
                    {'name': '👀 Reviewing', 'color': 'yellow'},
                    {'name': '✅ Approved', 'color': 'green'},
                    {'name': '🚧 In Progress', 'color': 'orange'},
                    {'name': '✅ Done', 'color': 'green'},
                    {'name': '❌ Declined', 'color': 'red'},
                    {'name': '🧊 On Hold', 'color': 'gray'}
                ]
            }
        },

        # Priority select
        'Priority': {
            'select': {
                'options': [
                    {'name': '🔥 Critical', 'color': 'red'},
                    {'name': '⬆️ High', 'color': 'orange'},
                    {'name': '➡️ Medium', 'color': 'yellow'},
                    {'name': '⬇️ Low', 'color': 'gray'}
                ]
            }
        },

        # Category multi-select
        'Category': {
            'multi_select': {
                'options': [
                    {'name': 'Finance', 'color': 'green'},
                    {'name': 'Inventory', 'color': 'blue'},
                    {'name': 'Sales', 'color': 'purple'},
                    {'name': 'HR', 'color': 'pink'},
                    {'name': 'BIR Compliance', 'color': 'red'},
                    {'name': 'Mobile', 'color': 'orange'},
                    {'name': 'Superset', 'color': 'yellow'},
                    {'name': 'Workflow', 'color': 'brown'},
                    {'name': 'Integration', 'color': 'default'},
                    {'name': 'Other', 'color': 'gray'}
                ]
            }
        },

        # Requester person
        'Requester': {
            'people': {}
        },

        # Requester Email
        'Requester Email': {
            'email': {}
        },

        # Votes number
        'Votes': {
            'number': {
                'format': 'number'
            }
        },

        # Use Case rich text
        'Use Case': {
            'rich_text': {}
        },

        # Requested Date
        'Requested Date': {
            'date': {}
        },

        # Target Release
        'Target Release': {
            'select': {
                'options': [
                    {'name': 'v1.0', 'color': 'blue'},
                    {'name': 'v1.1', 'color': 'green'},
                    {'name': 'v2.0', 'color': 'purple'},
                    {'name': 'Backlog', 'color': 'gray'}
                ]
            }
        },

        # Assigned To
        'Assigned To': {
            'people': {}
        },

        # Module
        'Module': {
            'select': {}  # Will be populated as needed
        },

        # Complexity
        'Complexity': {
            'select': {
                'options': [
                    {'name': '🟢 Small (1-2 days)', 'color': 'green'},
                    {'name': '🟡 Medium (3-5 days)', 'color': 'yellow'},
                    {'name': '🔴 Large (1-2 weeks)', 'color': 'orange'},
                    {'name': '🟣 X-Large (>2 weeks)', 'color': 'red'}
                ]
            }
        },

        # External ID (for idempotency)
        'External ID': {
            'rich_text': {}
        },

        # Last Synced
        'Last Synced': {
            'date': {}
        },

        # Tags
        'Tags': {
            'multi_select': {}
        },

        # Dependencies (relation to self)
        # Note: Will need to add this after database is created

        # Discussion URL
        'Discussion URL': {
            'url': {}
        }
    }

    # Create database
    click.echo(f"\n📋 Creating database: '{database_title}'...")

    try:
        database = notion.databases.create(
            parent={
                'type': 'page_id',
                'page_id': parent_page_id
            },
            title=[
                {
                    'type': 'text',
                    'text': {'content': database_title}
                }
            ],
            properties=properties
        )

        database_id = database['id']

        click.echo("\n" + "="*70)
        click.echo("✅ DATABASE CREATED SUCCESSFULLY!")
        click.echo("="*70)
        click.echo(f"\nDatabase ID: {database_id}")
        click.echo(f"Database URL: https://notion.so/{database_id.replace('-', '')}")

        click.echo("\n📝 Next Steps:")
        click.echo("1. Save the Database ID to your environment:")
        click.echo(f"   export NOTION_FEATURE_DB_ID='{database_id}'")
        click.echo("\n2. (Optional) Add self-relation for Dependencies:")
        click.echo("   - Open database in Notion")
        click.echo("   - Add new property 'Dependencies' → Relation → This database")
        click.echo("\n3. (Optional) Add self-relation for Merged From:")
        click.echo("   - Add new property 'Merged From' → Relation → This database")
        click.echo("\n4. Create default views:")
        click.echo("   - All Requests (Table, grouped by Status)")
        click.echo("   - Top Voted (Gallery, sorted by Votes desc)")
        click.echo("   - Backlog (Filtered: Status = Approved)")
        click.echo("   - Current Sprint (Filtered: Status = In Progress)")
        click.echo("   - Roadmap (Board, grouped by Target Release)")
        click.echo("\n5. Test submission:")
        click.echo("   python scripts/submit_feature_request.py interactive")

        click.echo("\n🎉 Feature Request system is ready to use!\n")

        # Create a welcome page in the database
        click.echo("📄 Creating welcome page...")

        welcome_page = notion.pages.create(
            parent={'database_id': database_id},
            properties={
                'Title': {
                    'title': [{'text': {'content': '👋 Welcome to Feature Requests'}}]
                },
                'Status': {
                    'select': {'name': '✅ Done'}
                },
                'Priority': {
                    'select': {'name': '➡️ Medium'}
                },
                'Category': {
                    'multi_select': [{'name': 'Other'}]
                },
                'Use Case': {
                    'rich_text': [{'text': {'content': 'Getting started guide'}}]
                },
                'Requested Date': {
                    'date': {'start': '2025-11-08'}
                },
                'Votes': {'number': 0},
                'External ID': {
                    'rich_text': [{'text': {'content': 'welcome_page'}}]
                }
            },
            children=[
                {
                    'object': 'block',
                    'type': 'heading_1',
                    'heading_1': {
                        'rich_text': [{'text': {'content': '🚀 Welcome to Feature Requests'}}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{'text': {
                            'content': 'This is your simplified feature request system for InsightPulse Odoo.'
                        }}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'heading_2',
                    'heading_2': {
                        'rich_text': [{'text': {'content': 'How to Submit a Request'}}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'numbered_list_item',
                    'numbered_list_item': {
                        'rich_text': [{'text': {
                            'content': 'Use the Python script: python scripts/submit_feature_request.py interactive'
                        }}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'numbered_list_item',
                    'numbered_list_item': {
                        'rich_text': [{'text': {
                            'content': 'Or use the web form (if deployed)'
                        }}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'numbered_list_item',
                    'numbered_list_item': {
                        'rich_text': [{'text': {
                            'content': 'Or manually create a new page in this database'
                        }}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'heading_2',
                    'heading_2': {
                        'rich_text': [{'text': {'content': 'Workflow'}}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'bulleted_list_item',
                    'bulleted_list_item': {
                        'rich_text': [{'text': {
                            'content': '🆕 New → Request submitted'
                        }}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'bulleted_list_item',
                    'bulleted_list_item': {
                        'rich_text': [{'text': {
                            'content': '👀 Reviewing → Team is evaluating'
                        }}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'bulleted_list_item',
                    'bulleted_list_item': {
                        'rich_text': [{'text': {
                            'content': '✅ Approved → Added to backlog'
                        }}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'bulleted_list_item',
                    'bulleted_list_item': {
                        'rich_text': [{'text': {
                            'content': '🚧 In Progress → Currently being built'
                        }}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'bulleted_list_item',
                    'bulleted_list_item': {
                        'rich_text': [{'text': {
                            'content': '✅ Done → Shipped to production'
                        }}]
                    }
                }
            ]
        )

        click.echo(f"✓ Created welcome page: {welcome_page['id']}")

    except Exception as e:
        click.echo(f"\n❌ Error creating database: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    setup_database()
