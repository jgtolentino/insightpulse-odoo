# 🚀 Automated Feature Discovery & Backlog Management

Complete automation system for discovering Odoo modules, classifying features, and syncing to Notion for backlog management.

## 🎯 Features

- **Automated Discovery**: Scans `__manifest__.py` files across your Odoo codebase
- **Smart Classification**: Categorizes features by business area, epic, and deployment status
- **Story Point Estimation**: Automatically estimates complexity using Fibonacci scale
- **Priority Assignment**: Assigns priorities based on strategic importance and dependencies
- **Notion Integration**: Syncs backlog to Notion database with External ID deduplication
- **Diff Analysis**: Tracks changes between runs (new/modified/removed features)
- **Scheduled Automation**: Supports cron jobs for daily automated runs

## 📋 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Odoo Repository                            │
│  (addons/, odoo_addons/, custom/)                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Feature Discovery Engine                        │
│  • Scans __manifest__.py files                              │
│  • Extracts metadata (name, version, deps, etc.)            │
│  • Classifies by business area & epic                       │
│  • Estimates story points & assigns priority                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backlog JSON Export                         │
│  • feature_backlog.json                                     │
│  • Summary report (MD)                                      │
│  • Diff report (MD)                                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Notion MCP Integration                          │
│  • Creates database with proper schema                      │
│  • Syncs features with External ID deduplication            │
│  • Supports upsert pattern for updates                      │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ Architecture

### Core Components

1. **`feature_discovery.py`** - Feature discovery engine
   - Scans repository for `__manifest__.py` files
   - Parses module metadata
   - Classifies features by business domain
   - Exports to JSON

2. **`notion_sync.py`** - Notion integration
   - Generates Notion database schema
   - Creates MCP commands for sync
   - Handles External ID-based deduplication

3. **`backlog_automation.py`** - Workflow orchestration
   - Runs complete end-to-end workflow
   - Diff analysis between runs
   - Cleanup of old files
   - Supports cron automation

## 🛠️ Setup

### Prerequisites

```bash
# Python 3.9+
python3 --version

# Git (for repository access)
git --version

# Optional: Node.js for MCP tools
node --version
```

### Installation

```bash
# Clone or navigate to your Odoo repository
cd /path/to/insightpulse-odoo

# Create automation directory
mkdir -p automation
cd automation

# Copy the scripts
cp /path/to/feature_discovery.py .
cp /path/to/notion_sync.py .
cp /path/to/backlog_automation.py .

# Make scripts executable
chmod +x *.py

# Install Python dependencies (if any)
# pip install -r requirements.txt
```

## 🚀 Usage

### Quick Start

```bash
# Run complete workflow
python3 backlog_automation.py

# Output will be in backlog_output/ directory:
# - backlog_YYYYMMDD_HHMMSS.json
# - backlog_latest.json (symlink)
# - summary_YYYYMMDD_HHMMSS.md
# - notion_commands_YYYYMMDD_HHMMSS.txt
# - diff_YYYYMMDD_HHMMSS.md (if previous run exists)
```

### Manual Steps

#### Step 1: Discover Features

```bash
python3 feature_discovery.py --repo-path . --output feature_backlog.json
```

This will:
- Scan all `__manifest__.py` files
- Classify features by business area
- Estimate story points
- Export to JSON

#### Step 2: Generate Notion Sync Commands

```bash
python3 notion_sync.py --backlog feature_backlog.json --output-commands notion_commands.txt
```

This generates MCP commands that you can execute in Claude with Notion MCP enabled.

#### Step 3: Execute Notion Sync

1. Open `notion_commands.txt`
2. Copy STEP 1 command (creates database)
3. Execute in Claude chat with Notion MCP
4. Note the `data_source_id` from response
5. Replace `<DATA_SOURCE_ID>` in STEP 2 commands
6. Execute STEP 2 commands to sync features

### Advanced Usage

```bash
# Custom repository path
python3 backlog_automation.py --repo-path /path/to/odoo

# Custom GitHub repo name
python3 backlog_automation.py --github-repo myorg/myrepo

# Disable cleanup of old files
python3 backlog_automation.py --no-cleanup

# Keep only last 5 runs
python3 backlog_automation.py --keep-last 5

# Show cron setup instructions
python3 backlog_automation.py --setup-cron
```

## ⏰ Automated Scheduling

### Setup Daily Automation

```bash
# Show cron instructions
python3 backlog_automation.py --setup-cron

# Edit crontab
crontab -e

# Add entry (runs daily at 2 AM):
0 2 * * * cd /path/to/automation && python3 backlog_automation.py --auto >> /var/log/backlog.log 2>&1
```

### Webhook Trigger (GitHub Actions)

```yaml
# .github/workflows/backlog-sync.yml
name: Automated Backlog Sync

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Run Backlog Automation
        run: |
          cd automation
          python3 backlog_automation.py --auto
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: backlog-output
          path: automation/backlog_output/
```

## 📊 Classification System

### Business Areas

Features are automatically classified into these areas:

- **Finance & Accounting**: Accounting, invoicing, tax, BIR compliance
- **Procurement & Supply Chain**: Purchase orders, vendors, Ariba integration
- **Project & Portfolio Management**: PPM, projects, tasks, resources
- **Document & Data Management**: OCR, document AI, attachments
- **Integration & API**: MCP, connectors, sync tools
- **Compliance & Governance**: GDPR, audit, approvals, workflows
- **HR & Employee Management**: HR, payroll, attendance
- **Analytics & Reporting**: BI, dashboards, Superset, Tableau
- **Core Infrastructure**: Base modules, frameworks, utilities

### Epics

Strategic themes for organizing features:

- **Finance SSC Automation**: BIR, tax, month-end closing
- **SAP Replacement Suite**: Ariba, Concur, Clarity alternatives
- **AI Document Processing**: OCR, entity extraction, automation
- **Enterprise Integration**: MCP, API connectors, sync
- **PPM & Resource Planning**: Projects, portfolios, resources
- **Approval & Workflow Engine**: Multi-level approvals, escalations
- **Compliance & Audit**: GDPR, consent, audit trails
- **Cost & Margin Management**: Cost sheets, pricing, margins

### Deployment Status

- **Backlog**: Not yet started
- **Planning**: Requirements gathering
- **Development**: Active development
- **Staging**: Testing phase
- **Production**: Deployed to production
- **Deprecated**: No longer maintained

### Priority Levels

- **P0 - Critical**: Production issues, Finance SSC, SAP replacements
- **P1 - High**: Core dependencies, staging modules
- **P2 - Medium**: Development modules
- **P3 - Low**: Backlog, experimental features

## 📁 Output Files

### JSON Backlog

```json
{
  "discovered_at": "2025-11-04T10:30:00",
  "repository": "jgtolentino/insightpulse-odoo",
  "total_features": 45,
  "features": [
    {
      "module_name": "ipai_doc_ai",
      "display_name": "InsightPulse Document AI",
      "description": "OCR to entity mapping, Odoo draft generation",
      "version": "1.0.0",
      "business_area": "Document & Data Management",
      "epic": "AI Document Processing",
      "deployment_status": "Production",
      "priority": "P0 - Critical",
      "story_points": 13,
      "tags": ["AI/ML", "OCR", "PaddleOCR"],
      "github_url": "https://github.com/...",
      "external_id": "odoo_module_ipai_doc_ai"
    }
  ]
}
```

### Summary Report (Markdown)

```markdown
# Feature Backlog Summary
**Generated:** 2025-11-04 10:30:00
**Repository:** jgtolentino/insightpulse-odoo

## Overview
- **Total Features:** 45
- **Total Story Points:** 287

## By Business Area
- **Finance & Accounting:** 12
- **Document & Data Management:** 8
...
```

### Diff Report

Shows changes between runs:
- New features added
- Features removed
- Modified features (version, status, priority changes)

## 🔧 Configuration

### Custom Classification Rules

Edit `feature_discovery.py` to customize classification:

```python
class FeatureClassifier:
    BUSINESS_AREAS = {
        'My Custom Area': ['keyword1', 'keyword2'],
        # Add your custom areas
    }
    
    EPICS = {
        'My Custom Epic': ['keyword1', 'keyword2'],
        # Add your custom epics
    }
```

### Custom Story Point Estimation

Modify the estimation logic:

```python
@staticmethod
def estimate_story_points(manifest_data: Dict, description: str) -> int:
    points = 3  # Base points
    
    # Add your custom complexity logic
    if 'integration' in description.lower():
        points += 3
    
    return min([f for f in [1, 2, 3, 5, 8, 13] if f >= points], default=13)
```

## 🎯 Use Cases

### 1. Sprint Planning

```bash
# Discover features
python3 backlog_automation.py

# Review summary report
cat backlog_output/summary_*.md

# Import to Notion for sprint planning
# Follow Notion sync commands
```

### 2. Portfolio Management

```bash
# Generate backlog with custom repo
python3 backlog_automation.py --github-repo myorg/myrepo

# Review by epic and business area
# Use Notion views to filter by epic
```

### 3. Continuous Integration

```bash
# Setup in CI/CD pipeline
# .gitlab-ci.yml
backlog-discovery:
  script:
    - python3 automation/backlog_automation.py --auto
  artifacts:
    paths:
      - automation/backlog_output/
```

## 🔍 Troubleshooting

### No Features Discovered

```bash
# Check if __manifest__.py files exist
find . -name "__manifest__.py"

# Verify repo path
python3 feature_discovery.py --repo-path /correct/path
```

### Notion Sync Fails

```bash
# Ensure Notion MCP is enabled in Claude
# Check that you have Notion permissions
# Verify data_source_id is correct
```

### Parse Errors

```bash
# Some __manifest__.py files may have syntax errors
# Check the error output for specific file
# Fix syntax in problematic manifest file
```

## 📚 Integration with Jake's Stack

This system integrates with your existing tools:

### MCP Integration Module

```python
# Use your existing mcp_integration module
from addons.mcp_integration import MCPCoordinator

coordinator = MCPCoordinator()
coordinator.sync_to_notion(backlog_data)
```

### Supabase Sync

```python
# Store backlog in Supabase for analytics
from supabase import create_client

supabase = create_client(
    "https://spdtwktxdalcfigzeqrz.supabase.co",
    "your-key"
)

supabase.table('feature_backlog').upsert(features)
```

### DigitalOcean Deployment

```bash
# Deploy automation as DO App
doctl apps create --spec backlog-automation.yaml
```

## 🎓 Best Practices

1. **Run Regularly**: Schedule daily runs to track changes
2. **Review Diffs**: Check diff reports before syncing to Notion
3. **Custom Tags**: Add agency-specific tags (RIM, CKVC, etc.)
4. **Version Control**: Commit backlog JSONs to track history
5. **Notion Views**: Create views by epic, status, priority
6. **Sprint Boards**: Use Notion board view for sprints

## 📦 Dependencies

```
# Python standard library only
# No external dependencies required for core functionality

# Optional dependencies for advanced features:
# - supabase (for Supabase sync)
# - mcp (for direct MCP SDK usage)
```

## 🤝 Contributing

To add new classification rules or improve the system:

1. Edit classification rules in `feature_discovery.py`
2. Run discovery on test repo
3. Validate output JSON
4. Test Notion sync

## 📝 License

Same as InsightPulse Odoo project

## 🔗 Related Projects

- [InsightPulse Odoo](https://github.com/jgtolentino/insightpulse-odoo)
- [MCP Integration Module](https://github.com/jgtolentino/insightpulse-odoo/tree/main/addons/mcp_integration)
- [Finance SSC Automation](docs/finance-ssc.md)

---

**Need Help?** Check existing issues or create a new one on GitHub.
