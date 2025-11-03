#!/usr/bin/env python3
"""
BIR Website Monitoring Example
Demonstrates Firecrawl + Supabase + Notion integration
"""

import os
from datetime import datetime
from firecrawl import FirecrawlApp
from supabase import create_client
from notion_client import Client

# Initialize clients
firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
notion = Client(auth=os.getenv("NOTION_TOKEN"))

def scrape_bir_announcements():
    """
    Scrape BIR website for new announcements
    Returns: List of announcements with structured data
    """
    url = "https://bir.gov.ph/index.php/tax-information.html"
    
    result = firecrawl.scrape_url(
        url,
        params={
            "formats": ["extract"],
            "extract": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "announcements": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "Title of the announcement"
                                    },
                                    "date": {
                                        "type": "string",
                                        "description": "Publication date"
                                    },
                                    "category": {
                                        "type": "string",
                                        "description": "Category (e.g., Tax Advisory, Revenue Memo)"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "Brief description"
                                    },
                                    "link": {
                                        "type": "string",
                                        "description": "Full URL to announcement"
                                    },
                                    "affects_agencies": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Which agencies this affects (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)"
                                    }
                                },
                                "required": ["title", "date", "category"]
                            }
                        }
                    }
                }
            }
        }
    )
    
    return result['extract']['announcements']

def store_in_supabase(announcements):
    """
    Store announcements in Supabase with deduplication
    """
    stored_count = 0
    
    for ann in announcements:
        # Check if already exists
        existing = supabase.table("bir_announcements")\
            .select("id")\
            .eq("link", ann['link'])\
            .execute()
        
        if not existing.data:
            # Insert new announcement
            supabase.table("bir_announcements").insert({
                "title": ann['title'],
                "date": ann['date'],
                "category": ann['category'],
                "description": ann.get('description', ''),
                "link": ann['link'],
                "affects_agencies": ann.get('affects_agencies', []),
                "status": "new",
                "scraped_at": datetime.now().isoformat()
            }).execute()
            stored_count += 1
    
    return stored_count

def create_notion_tasks(announcements):
    """
    Create Notion tasks for new announcements
    Assign to all 8 agencies
    """
    created_count = 0
    
    for ann in announcements:
        # Create page in Notion database
        notion.pages.create(
            parent={"database_id": os.getenv("NOTION_BIR_DB_ID")},
            properties={
                "Name": {
                    "title": [{
                        "text": {"content": ann['title'][:100]}  # Notion title limit
                    }]
                },
                "Category": {
                    "select": {"name": ann['category']}
                },
                "Date": {
                    "date": {"start": ann['date']}
                },
                "Status": {
                    "select": {"name": "To Review"}
                },
                "Priority": {
                    "select": {"name": "High"}
                },
                "Source URL": {
                    "url": ann['link']
                },
                "Agencies": {
                    "multi_select": [
                        {"name": "RIM"}, {"name": "CKVC"},
                        {"name": "BOM"}, {"name": "JPAL"},
                        {"name": "JLI"}, {"name": "JAP"},
                        {"name": "LAS"}, {"name": "RMQB"}
                    ]
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"text": {"content": "Description"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "text": {"content": ann.get('description', 'No description available')}
                        }]
                    }
                },
                {
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                },
                {
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"text": {"content": "Review announcement"}}],
                        "checked": False
                    }
                },
                {
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"text": {"content": "Determine impact on agencies"}}],
                        "checked": False
                    }
                },
                {
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"text": {"content": "Update compliance checklist"}}],
                        "checked": False
                    }
                }
            ]
        )
        created_count += 1
    
    return created_count

def main():
    """
    Main execution flow
    """
    print(f"🚀 Starting BIR monitoring at {datetime.now()}")
    print("-" * 50)
    
    # Step 1: Scrape BIR website
    print("📡 Scraping BIR website...")
    try:
        announcements = scrape_bir_announcements()
        print(f"✅ Found {len(announcements)} announcements")
    except Exception as e:
        print(f"❌ Error scraping: {e}")
        return
    
    # Step 2: Store in Supabase
    print("\n💾 Storing in Supabase...")
    try:
        stored = store_in_supabase(announcements)
        print(f"✅ Stored {stored} new announcements")
    except Exception as e:
        print(f"❌ Error storing: {e}")
        return
    
    # Step 3: Get new announcements that need Notion tasks
    print("\n🔍 Checking for new announcements...")
    new_announcements = supabase.table("bir_announcements")\
        .select("*")\
        .eq("status", "new")\
        .execute()
    
    if not new_announcements.data:
        print("✅ No new announcements to process")
        return
    
    # Step 4: Create Notion tasks
    print(f"\n📝 Creating Notion tasks for {len(new_announcements.data)} announcements...")
    try:
        created = create_notion_tasks(new_announcements.data)
        print(f"✅ Created {created} Notion tasks")
        
        # Mark as notified
        for ann in new_announcements.data:
            supabase.table("bir_announcements")\
                .update({"status": "notified"})\
                .eq("id", ann['id'])\
                .execute()
        
    except Exception as e:
        print(f"❌ Error creating Notion tasks: {e}")
        return
    
    print("\n" + "=" * 50)
    print(f"✨ Monitoring complete at {datetime.now()}")
    print(f"📊 Summary:")
    print(f"  - Total announcements found: {len(announcements)}")
    print(f"  - New announcements stored: {stored}")
    print(f"  - Notion tasks created: {created}")

if __name__ == "__main__":
    main()
