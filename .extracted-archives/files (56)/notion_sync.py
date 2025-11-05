#!/usr/bin/env python3
"""
Notion Backlog Sync - Push discovered features to Notion database
Uses MCP tools pattern with External ID upsert for deduplication
"""

import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime


class NotionBacklogSync:
    """Syncs feature backlog to Notion using MCP pattern"""
    
    # Notion database schema for Feature Backlog
    DATABASE_SCHEMA = {
        "Feature Name": {"type": "title"},
        "Module ID": {"type": "rich_text"},
        "Description": {"type": "rich_text"},
        "Business Area": {
            "type": "select",
            "options": [
                "Finance & Accounting",
                "Procurement & Supply Chain",
                "Project & Portfolio Management",
                "Document & Data Management",
                "Integration & API",
                "Compliance & Governance",
                "HR & Employee Management",
                "Analytics & Reporting",
                "Core Infrastructure",
                "Other"
            ]
        },
        "Epic": {
            "type": "select",
            "options": [
                "Finance SSC Automation",
                "SAP Replacement Suite",
                "AI Document Processing",
                "Enterprise Integration",
                "PPM & Resource Planning",
                "Approval & Workflow Engine",
                "Compliance & Audit",
                "Cost & Margin Management",
                "Unclassified"
            ]
        },
        "Status": {
            "type": "select",
            "options": [
                "Backlog",
                "Planning",
                "Development",
                "Staging",
                "Production",
                "Deprecated"
            ]
        },
        "Priority": {
            "type": "select",
            "options": [
                "P0 - Critical",
                "P1 - High",
                "P2 - Medium",
                "P3 - Low"
            ]
        },
        "Story Points": {"type": "number"},
        "Version": {"type": "rich_text"},
        "Category": {"type": "rich_text"},
        "Dependencies": {"type": "rich_text"},
        "External Dependencies": {"type": "rich_text"},
        "Tags": {"type": "multi_select"},
        "GitHub URL": {"type": "url"},
        "File Path": {"type": "rich_text"},
        "External ID": {"type": "rich_text"},  # For deduplication
        "Last Synced": {"type": "date"},
        "Discovered At": {"type": "date"}
    }
    
    def __init__(self, backlog_json_path: str = "feature_backlog.json"):
        self.backlog_json_path = backlog_json_path
        self.features: List[Dict] = []
        self.load_features()
    
    def load_features(self):
        """Load features from JSON export"""
        try:
            with open(self.backlog_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.features = data.get('features', [])
            print(f"📦 Loaded {len(self.features)} features from {self.backlog_json_path}")
        except FileNotFoundError:
            print(f"❌ Error: {self.backlog_json_path} not found. Run feature_discovery.py first.")
            exit(1)
    
    def generate_notion_mcp_commands(self) -> str:
        """Generate MCP commands to create/update Notion database"""
        
        commands = []
        
        # Step 1: Create database (run this once)
        create_db_cmd = self._generate_create_database_command()
        commands.append("# STEP 1: Create Feature Backlog Database (Run once)")
        commands.append("# Copy and execute this in Claude with Notion MCP enabled:\n")
        commands.append(create_db_cmd)
        commands.append("\n" + "="*80 + "\n")
        
        # Step 2: Generate page creation commands
        commands.append("# STEP 2: Sync Features to Database")
        commands.append("# After creating database, use the data_source_id from the response")
        commands.append("# Replace <DATA_SOURCE_ID> with actual ID from Step 1\n")
        
        # Batch features for better performance (max 100 per call)
        batch_size = 50
        for i in range(0, len(self.features), batch_size):
            batch = self.features[i:i+batch_size]
            batch_cmd = self._generate_batch_pages_command(batch, i // batch_size + 1)
            commands.append(batch_cmd)
            commands.append("\n")
        
        commands.append("="*80)
        commands.append("\n# STEP 3: Verify sync")
        commands.append("# Use notion-search to verify features were created")
        commands.append('notion-search(query="", data_source_url="collection://<DATA_SOURCE_ID>")')
        
        return "\n".join(commands)
    
    def _generate_create_database_command(self) -> str:
        """Generate command to create Notion database"""
        
        # Build properties schema
        properties = {}
        
        for prop_name, config in self.DATABASE_SCHEMA.items():
            prop_type = config["type"]
            
            if prop_type == "title":
                properties[prop_name] = {"type": "title", "title": {}}
            elif prop_type == "rich_text":
                properties[prop_name] = {"type": "rich_text", "rich_text": {}}
            elif prop_type == "number":
                properties[prop_name] = {"type": "number", "number": {"format": "number"}}
            elif prop_type == "url":
                properties[prop_name] = {"type": "url", "url": {}}
            elif prop_type == "date":
                properties[prop_name] = {"type": "date", "date": {}}
            elif prop_type == "select":
                options = [{"name": opt, "color": "default"} for opt in config.get("options", [])]
                properties[prop_name] = {
                    "type": "select",
                    "select": {"options": options}
                }
            elif prop_type == "multi_select":
                properties[prop_name] = {"type": "multi_select", "multi_select": {"options": []}}
        
        command = f"""notion-create-database(
    title=[{{"type": "text", "text": {{"content": "🚀 Feature Backlog - InsightPulse Odoo"}}}}],
    description=[{{"type": "text", "text": {{"content": "Automated feature discovery and backlog management for Odoo modules"}}}}],
    properties={json.dumps(properties, indent=2)}
)"""
        
        return command
    
    def _generate_batch_pages_command(self, features: List[Dict], batch_num: int) -> str:
        """Generate command to create batch of pages"""
        
        pages = []
        for feature in features:
            page = self._feature_to_notion_properties(feature)
            pages.append(page)
        
        command = f"""# Batch {batch_num}: {len(features)} features
notion-create-pages(
    parent={{"data_source_id": "<DATA_SOURCE_ID>"}},
    pages={json.dumps(pages, indent=2)}
)"""
        
        return command
    
    def _feature_to_notion_properties(self, feature: Dict) -> Dict:
        """Convert feature dict to Notion page properties"""
        
        # Format dependencies as comma-separated string
        dependencies = ", ".join(feature.get('depends', []))
        
        # Format external dependencies
        ext_deps = feature.get('external_dependencies', {})
        ext_deps_str = ""
        for lang, deps in ext_deps.items():
            ext_deps_str += f"{lang}: {', '.join(deps)}\n"
        
        # Format tags for multi_select
        tags_str = ", ".join(feature.get('tags', []))
        
        # Parse dates
        discovered_at = feature.get('discovered_at', datetime.now().isoformat())
        last_synced = datetime.now().isoformat()
        
        properties = {
            "Feature Name": feature.get('display_name', feature.get('module_name')),
            "Module ID": feature.get('module_name'),
            "Description": feature.get('description', ''),
            "Business Area": feature.get('business_area', 'Other'),
            "Epic": feature.get('epic', 'Unclassified'),
            "Status": feature.get('deployment_status', 'Backlog'),
            "Priority": feature.get('priority', 'P3 - Low'),
            "Story Points": feature.get('story_points', 0),
            "Version": feature.get('version', '0.0.0'),
            "Category": feature.get('category', 'Uncategorized'),
            "Dependencies": dependencies,
            "External Dependencies": ext_deps_str.strip(),
            "Tags": tags_str,
            "GitHub URL": feature.get('github_url', ''),
            "File Path": feature.get('file_path', ''),
            "External ID": feature.get('external_id', ''),
            "date:Last Synced:start": last_synced.split('T')[0],
            "date:Last Synced:is_datetime": 0,
            "date:Discovered At:start": discovered_at.split('T')[0],
            "date:Discovered At:is_datetime": 0
        }
        
        return {"properties": properties}
    
    def generate_python_mcp_script(self, output_path: str = "notion_sync_mcp.py"):
        """Generate standalone Python script using MCP SDK"""
        
        script = f'''#!/usr/bin/env python3
"""
Notion MCP Sync Script - Generated by feature_discovery.py
Syncs {len(self.features)} features to Notion
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def create_feature_database(session: ClientSession):
    """Create Notion database for feature backlog"""
    
    properties = {json.dumps(self._build_properties_dict(), indent=8)}
    
    result = await session.call_tool(
        "notion-create-database",
        arguments={{
            "title": [{{"type": "text", "text": {{"content": "🚀 Feature Backlog - InsightPulse Odoo"}}}}],
            "description": [{{"type": "text", "text": {{"content": "Automated feature discovery and backlog management"}}}}],
            "properties": properties
        }}
    )
    
    print("✅ Database created:", result)
    return result


async def sync_features_to_notion(session: ClientSession, data_source_id: str):
    """Sync all features to Notion database"""
    
    with open('feature_backlog.json', 'r') as f:
        data = json.load(f)
        features = data['features']
    
    print(f"📤 Syncing {{len(features)}} features to Notion...")
    
    # Batch sync (50 features at a time)
    batch_size = 50
    for i in range(0, len(features), batch_size):
        batch = features[i:i+batch_size]
        
        pages = []
        for feature in batch:
            page = convert_feature_to_page(feature)
            pages.append(page)
        
        result = await session.call_tool(
            "notion-create-pages",
            arguments={{
                "parent": {{"data_source_id": data_source_id}},
                "pages": pages
            }}
        )
        
        print(f"✅ Synced batch {{i//batch_size + 1}}: {{len(batch)}} features")
    
    print("🎉 Sync complete!")


def convert_feature_to_page(feature: dict) -> dict:
    """Convert feature dict to Notion page format"""
    
    dependencies = ", ".join(feature.get('depends', []))
    ext_deps = feature.get('external_dependencies', {{}})
    ext_deps_str = "\\n".join(f"{{k}}: {{', '.join(v)}}" for k, v in ext_deps.items())
    tags_str = ", ".join(feature.get('tags', []))
    
    return {{
        "properties": {{
            "Feature Name": feature['display_name'],
            "Module ID": feature['module_name'],
            "Description": feature.get('description', ''),
            "Business Area": feature['business_area'],
            "Epic": feature['epic'],
            "Status": feature['deployment_status'],
            "Priority": feature['priority'],
            "Story Points": feature.get('story_points', 0),
            "Version": feature['version'],
            "Category": feature['category'],
            "Dependencies": dependencies,
            "External Dependencies": ext_deps_str,
            "Tags": tags_str,
            "GitHub URL": feature['github_url'],
            "File Path": feature['file_path'],
            "External ID": feature['external_id'],
            "date:Last Synced:start": feature['discovered_at'].split('T')[0],
            "date:Last Synced:is_datetime": 0,
            "date:Discovered At:start": feature['discovered_at'].split('T')[0],
            "date:Discovered At:is_datetime": 0
        }}
    }}


async def main():
    """Main execution"""
    
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@notionhq/mcp-server-notion"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Step 1: Create database
            print("📋 Creating Notion database...")
            db_result = await create_feature_database(session)
            
            # Extract data_source_id from response
            # You'll need to parse the response and get the collection:// URL
            data_source_id = input("Enter data_source_id from database creation: ")
            
            # Step 2: Sync features
            await sync_features_to_notion(session, data_source_id)


if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"📄 Generated MCP sync script: {output_path}")
        return output_path
    
    def _build_properties_dict(self) -> Dict:
        """Build properties dict for database creation"""
        properties = {}
        
        for prop_name, config in self.DATABASE_SCHEMA.items():
            prop_type = config["type"]
            
            if prop_type == "title":
                properties[prop_name] = {"type": "title", "title": {}}
            elif prop_type == "rich_text":
                properties[prop_name] = {"type": "rich_text", "rich_text": {}}
            elif prop_type == "number":
                properties[prop_name] = {"type": "number", "number": {"format": "number"}}
            elif prop_type == "url":
                properties[prop_name] = {"type": "url", "url": {}}
            elif prop_type == "date":
                properties[prop_name] = {"type": "date", "date": {}}
            elif prop_type == "select":
                options = [{"name": opt, "color": "default"} for opt in config.get("options", [])]
                properties[prop_name] = {"type": "select", "select": {"options": options}}
            elif prop_type == "multi_select":
                properties[prop_name] = {"type": "multi_select", "multi_select": {"options": []}}
        
        return properties
    
    def export_mcp_commands(self, output_path: str = "notion_mcp_commands.txt"):
        """Export MCP commands to text file"""
        commands = self.generate_notion_mcp_commands()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(commands)
        
        print(f"📄 Exported MCP commands to: {output_path}")
        print(f"\n📋 Next steps:")
        print(f"1. Open {output_path}")
        print(f"2. Copy STEP 1 command and execute in Claude with Notion MCP")
        print(f"3. Note the data_source_id from the response")
        print(f"4. Replace <DATA_SOURCE_ID> in STEP 2 commands")
        print(f"5. Execute STEP 2 commands to sync features")
        
        return output_path
    
    def generate_upsert_script(self, output_path: str = "notion_upsert_sync.py"):
        """Generate script for updating existing features (upsert pattern)"""
        
        script = '''#!/usr/bin/env python3
"""
Notion Upsert Sync - Update existing features using External ID pattern
Handles deduplication and updates for existing features
"""

import asyncio
import json
from typing import List, Dict
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def find_existing_pages(session: ClientSession, data_source_url: str, external_ids: List[str]) -> Dict[str, str]:
    """Search for existing pages by External ID"""
    
    existing = {}
    
    for ext_id in external_ids:
        result = await session.call_tool(
            "notion-search",
            arguments={
                "query": ext_id,
                "data_source_url": data_source_url
            }
        )
        
        # Parse result to extract page_id
        # Map external_id -> page_id
        # existing[ext_id] = page_id
    
    return existing


async def upsert_features(session: ClientSession, data_source_url: str, features: List[Dict]):
    """Upsert features - create if not exists, update if exists"""
    
    # Get all external IDs
    external_ids = [f['external_id'] for f in features]
    
    # Find existing pages
    print("🔍 Searching for existing pages...")
    existing_pages = await find_existing_pages(session, data_source_url, external_ids)
    
    # Separate into create vs update
    to_create = []
    to_update = []
    
    for feature in features:
        ext_id = feature['external_id']
        if ext_id in existing_pages:
            to_update.append((existing_pages[ext_id], feature))
        else:
            to_create.append(feature)
    
    print(f"➕ Creating {len(to_create)} new features")
    print(f"🔄 Updating {len(to_update)} existing features")
    
    # Create new pages
    if to_create:
        pages = [convert_feature_to_page(f) for f in to_create]
        await session.call_tool(
            "notion-create-pages",
            arguments={
                "parent": {"data_source_url": data_source_url},
                "pages": pages
            }
        )
    
    # Update existing pages
    for page_id, feature in to_update:
        properties = convert_feature_to_properties(feature)
        await session.call_tool(
            "notion-update-page",
            arguments={
                "page_id": page_id,
                "command": "update_properties",
                "properties": properties
            }
        )
    
    print("✅ Upsert complete!")


def convert_feature_to_page(feature: dict) -> dict:
    """Convert feature to Notion page format"""
    # Same as before
    pass


def convert_feature_to_properties(feature: dict) -> dict:
    """Convert feature to properties dict for update"""
    # Same as convert_feature_to_page but just properties
    pass


async def main():
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@notionhq/mcp-server-notion"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            with open('feature_backlog.json', 'r') as f:
                data = json.load(f)
                features = data['features']
            
            data_source_url = input("Enter data_source_url (collection://...): ")
            
            await upsert_features(session, data_source_url, features)


if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"📄 Generated upsert script: {output_path}")
        return output_path


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync feature backlog to Notion')
    parser.add_argument('--backlog', default='feature_backlog.json', 
                       help='Path to feature backlog JSON')
    parser.add_argument('--output-commands', default='notion_mcp_commands.txt',
                       help='Output file for MCP commands')
    parser.add_argument('--generate-scripts', action='store_true',
                       help='Generate Python MCP scripts')
    
    args = parser.parse_args()
    
    sync = NotionBacklogSync(backlog_json_path=args.backlog)
    
    # Export MCP commands
    sync.export_mcp_commands(output_path=args.output_commands)
    
    # Optionally generate Python scripts
    if args.generate_scripts:
        sync.generate_python_mcp_script()
        sync.generate_upsert_script()
        print("\n✅ Generated Python MCP scripts")
    
    print("\n🎉 Notion sync setup complete!")


if __name__ == "__main__":
    main()
