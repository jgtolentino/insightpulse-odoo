# 🚀 Quick Start Guide

Get your automated feature backlog running in 5 minutes!

## Step 1: Download Scripts (2 min)

```bash
# Create automation directory in your Odoo repo
cd ~/insightpulse-odoo  # or your repo path
mkdir -p automation
cd automation

# If using Claude Desktop, files should already be in /home/claude/
# Copy them to your automation directory:
cp /home/claude/feature_discovery.py .
cp /home/claude/notion_sync.py .
cp /home/claude/backlog_automation.py .
chmod +x *.py
```

## Step 2: Run Discovery (1 min)

```bash
# Simple one-liner
python3 backlog_automation.py

# Or step by step:
python3 feature_discovery.py --repo-path .. --github-repo jgtolentino/insightpulse-odoo
```

**Expected Output:**
```
🔍 Starting feature discovery...
Found 47 manifest files
✅ Discovered: MCP Integration (Integration & API)
✅ Discovered: IPAI Core (Core Infrastructure)
✅ Discovered: IPAI Approvals (Compliance & Governance)
...
🎉 Discovery complete! Found 47 features
📄 Exported to feature_backlog.json

📊 FEATURE BACKLOG SUMMARY
================================================================================
Total Features: 47
Total Story Points: 312

📂 By Business Area:
  • Finance & Accounting: 14
  • Document & Data Management: 9
  • Integration & API: 8
...
```

## Step 3: Review Output (1 min)

```bash
# Check generated files
ls -lh backlog_output/

# View summary
cat backlog_output/summary_*.md

# View JSON
cat backlog_output/backlog_latest.json | jq '.features[] | {name: .display_name, area: .business_area}'
```

## Step 4: Sync to Notion (1 min setup)

### Option A: Manual Sync via Claude Chat

```bash
# View Notion commands
cat backlog_output/notion_commands_*.txt
```

Copy the commands and execute in Claude chat with Notion MCP enabled:

**Step 1 - Create Database:**
```
notion-create-database(
    title=[{"type": "text", "text": {"content": "🚀 Feature Backlog - InsightPulse Odoo"}}],
    description=[{"type": "text", "text": {"content": "Automated feature discovery and backlog management"}}],
    properties={...}
)
```

**Step 2 - Sync Features:**
After Step 1, you'll get a response with `data_source_id`. Use it here:

```
notion-create-pages(
    parent={"data_source_id": "YOUR_DATA_SOURCE_ID_HERE"},
    pages=[...]
)
```

### Option B: Automated Sync (Advanced)

```bash
# Generate Python MCP script
python3 notion_sync.py --backlog backlog_output/backlog_latest.json --generate-scripts

# Run the script
python3 notion_sync_mcp.py
```

## 🎯 What You Get

### 1. JSON Backlog
Complete feature inventory with metadata:
```json
{
  "module_name": "ipai_doc_ai",
  "display_name": "InsightPulse Document AI",
  "business_area": "Document & Data Management",
  "epic": "AI Document Processing",
  "deployment_status": "Production",
  "priority": "P0 - Critical",
  "story_points": 13
}
```

### 2. Markdown Summary
Human-readable report for quick review

### 3. Notion Database
Organized backlog with:
- Business area grouping
- Epic tracking
- Status board (Backlog → Planning → Dev → Staging → Prod)
- Priority filtering
- Story point tracking

## 🔄 Daily Automation

```bash
# Setup cron for daily 2 AM runs
crontab -e

# Add this line:
0 2 * * * cd ~/insightpulse-odoo/automation && python3 backlog_automation.py --auto >> /var/log/backlog.log 2>&1
```

## 📊 Example Use Cases

### Sprint Planning
```bash
# Discover features
python3 backlog_automation.py

# Filter by epic in Notion
# View by status (Backlog, Planning, Development)
# Assign story points
# Plan sprint capacity
```

### Month-End Closing Prep (Finance SSC)
```bash
# Find Finance SSC features
cat backlog_output/backlog_latest.json | jq '.features[] | select(.epic == "Finance SSC Automation")'

# Output:
# - ipai_bir_filing
# - ipai_month_end_closing
# - ipai_vat_returns
# - ipai_withholding_tax
```

### BIR Compliance Tracking
```bash
# Find all BIR-related modules
cat backlog_output/backlog_latest.json | jq '.features[] | select(.tags[] | contains("BIR"))'
```

### SAP Replacement Roadmap
```bash
# View SAP alternatives
cat backlog_output/backlog_latest.json | jq '.features[] | select(.epic == "SAP Replacement Suite")'

# Output:
# - ipai_ariba_cxml (Procurement)
# - ipai_concur_expense (Travel & Expense)
# - ipai_clarity_ppm_sync (PPM)
```

## 🎨 Customization

### Add Your Agency Tags

Edit `feature_discovery.py`:

```python
# Add your agencies to the classifier
agencies = ['RIM', 'CKVC', 'BOM', 'JPAL', 'JLI', 'JAP', 'LAS', 'RMQB']

# Features with these in their name get auto-tagged
# e.g., "ipai_rim_expense" → Tagged: "Agency-RIM"
```

### Custom Business Areas

```python
BUSINESS_AREAS = {
    'Philippine Compliance': ['bir', 'dole', 'sss', 'philhealth', 'pagibig'],
    'Multi-Agency Operations': ['rim', 'ckvc', 'bom', 'jpal'],
    # Add your custom areas
}
```

### Custom Story Point Rules

```python
def estimate_story_points(manifest_data, description):
    points = 3
    
    # BIR modules are complex
    if 'bir' in description.lower():
        points += 5
    
    # MCP integrations need API work
    if 'mcp' in description.lower():
        points += 3
    
    return min([1,2,3,5,8,13], key=lambda x: abs(x-points))
```

## 🔍 Troubleshooting

### Issue: No features found
```bash
# Verify manifest files exist
find .. -name "__manifest__.py" | head -5

# Check repo path
python3 feature_discovery.py --repo-path /correct/path
```

### Issue: Parse errors
```bash
# Some manifests may have syntax errors
# Check error message for file path
# Fix syntax in that __manifest__.py
```

### Issue: Notion sync fails
```bash
# Ensure Notion MCP is connected
# Check permissions in Notion
# Verify data_source_id format: collection://...
```

## 📈 Metrics You'll Track

After setup, you can track:

- **Feature Velocity**: Features moved from Backlog → Production
- **Epic Progress**: % complete for each epic
- **Business Area Coverage**: Investment by business area
- **Technical Debt**: Old versions, deprecated modules
- **Dependency Graph**: Most depended-on modules
- **Story Point Burn**: Sprint progress tracking

## 🎓 Pro Tips

1. **Tag Strategically**: Use tags for agencies (RIM, CKVC), technologies (AI/ML, MCP), compliance (BIR)

2. **Create Notion Views**:
   - Board by Status
   - Table grouped by Epic
   - Calendar by Sprint
   - Gallery by Business Area

3. **Link to GitHub**: Each feature has GitHub URL for easy navigation

4. **Diff Analysis**: Run daily to catch module additions/changes

5. **External ID Pattern**: Uses `odoo_module_{name}` for clean deduplication

## 🚨 Common Gotchas

### Don't forget data_source_id
When syncing to Notion, you MUST replace `<DATA_SOURCE_ID>` with the actual ID from Step 1

### Python version
Requires Python 3.9+. Check: `python3 --version`

### Notion permissions
Ensure your Notion token has access to create databases

## 🎉 Success Checklist

- [ ] Scripts downloaded and executable
- [ ] Discovery runs successfully
- [ ] JSON backlog generated
- [ ] Summary report looks good
- [ ] Notion database created
- [ ] Features synced to Notion
- [ ] Notion views configured
- [ ] Cron job scheduled (optional)

## 📞 Next Steps

After setup:

1. **Review Summary**: Check business area distribution
2. **Validate Classification**: Adjust if needed
3. **Setup Notion Board**: Create sprint board view
4. **Schedule Automation**: Setup cron for daily runs
5. **Integrate with Workflow**: Use for sprint planning

## 🔗 Helpful Links

- [Full Documentation](README.md)
- [Notion MCP Setup](https://github.com/notionhq/mcp-server-notion)
- [GitHub Repo](https://github.com/jgtolentino/insightpulse-odoo)

---

**Time to Value: ~5 minutes** ⚡

**Questions?** Open an issue or check the full README.md
