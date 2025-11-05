# 🚢 Deployment Guide for InsightPulse Stack

Production deployment guide for automated backlog management integrated with your existing infrastructure.

## 🏗️ Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Repository                            │
│              jgtolentino/insightpulse-odoo                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GitHub Actions                                 │
│  • Daily scheduled runs (2 AM PHT)                              │
│  • Automated feature discovery                                  │
│  • Diff analysis & reports                                      │
└────────────┬───────────────────────────┬─────────────────────────┘
             │                           │
             ▼                           ▼
┌────────────────────────┐    ┌────────────────────────────┐
│   DigitalOcean App     │    │   Supabase Database        │
│   Project ID:          │    │   Project: spdtwktxd...    │
│   29cde7a1-8280...     │    │   • feature_backlog table  │
│   • Automation service │    │   • Analytics views        │
│   • Cron jobs          │    │   • RLS policies           │
└────────────┬───────────┘    └────────┬───────────────────┘
             │                         │
             └────────────┬────────────┘
                          ▼
            ┌──────────────────────────┐
            │    Notion Workspace      │
            │  • Feature Backlog DB    │
            │  • Sprint boards         │
            │  • Epic tracking         │
            └──────────────────────────┘
```

## 🔧 Setup Steps

### 1. Repository Setup

```bash
# Clone your repo
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo

# Create automation directory
mkdir -p automation
cd automation

# Copy automation files
# (These should be in your repo already from previous step)

# Commit to repo
git add .
git commit -m "feat: Add automated backlog management"
git push origin main
```

### 2. GitHub Actions Setup

#### a. Create Workflow File

```bash
mkdir -p .github/workflows
cp automation/github-actions-workflow.yml .github/workflows/backlog-sync.yml
```

#### b. Configure Secrets

Go to GitHub → Settings → Secrets and Variables → Actions

Add these secrets:

```
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_KEY=your-service-role-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL (optional)
EMAIL_USERNAME=your-email@gmail.com (optional)
EMAIL_PASSWORD=your-app-password (optional)
```

#### c. Test Workflow

```bash
# Trigger manual run
# GitHub → Actions → Automated Backlog Sync → Run workflow

# Or commit to trigger
git commit --allow-empty -m "test: Trigger backlog sync"
git push
```

### 3. Supabase Database Setup

#### a. Create Table

```sql
-- Connect to Supabase SQL Editor
-- https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/editor

CREATE TABLE IF NOT EXISTS feature_backlog (
    id BIGSERIAL PRIMARY KEY,
    external_id TEXT UNIQUE NOT NULL,
    module_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    version TEXT,
    author TEXT,
    category TEXT,
    depends JSONB,
    external_dependencies JSONB,
    file_path TEXT,
    business_area TEXT,
    deployment_status TEXT,
    priority TEXT,
    story_points INTEGER,
    epic TEXT,
    tags TEXT[],
    github_url TEXT,
    discovered_at TIMESTAMPTZ,
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_feature_business_area ON feature_backlog(business_area);
CREATE INDEX idx_feature_deployment_status ON feature_backlog(deployment_status);
CREATE INDEX idx_feature_epic ON feature_backlog(epic);
CREATE INDEX idx_feature_priority ON feature_backlog(priority);
CREATE INDEX idx_feature_external_id ON feature_backlog(external_id);
CREATE INDEX idx_feature_tags ON feature_backlog USING GIN(tags);

-- Enable Row Level Security
ALTER TABLE feature_backlog ENABLE ROW LEVEL SECURITY;

-- Create policy (allow all operations for service role)
CREATE POLICY "Allow all for service role"
    ON feature_backlog
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_feature_backlog_updated_at
    BEFORE UPDATE ON feature_backlog
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

#### b. Create Analytics Views

```sql
-- Feature count by business area
CREATE OR REPLACE VIEW v_features_by_area AS
SELECT 
    business_area,
    COUNT(*) as feature_count,
    SUM(story_points) as total_story_points,
    AVG(story_points) as avg_story_points
FROM feature_backlog
GROUP BY business_area
ORDER BY feature_count DESC;

-- Feature count by epic
CREATE OR REPLACE VIEW v_features_by_epic AS
SELECT 
    epic,
    COUNT(*) as feature_count,
    SUM(story_points) as total_story_points,
    string_agg(DISTINCT deployment_status, ', ') as statuses
FROM feature_backlog
GROUP BY epic
ORDER BY total_story_points DESC;

-- Deployment pipeline metrics
CREATE OR REPLACE VIEW v_deployment_metrics AS
SELECT 
    deployment_status,
    COUNT(*) as count,
    SUM(story_points) as story_points,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM feature_backlog
GROUP BY deployment_status
ORDER BY 
    CASE deployment_status
        WHEN 'Production' THEN 1
        WHEN 'Staging' THEN 2
        WHEN 'Development' THEN 3
        WHEN 'Planning' THEN 4
        WHEN 'Backlog' THEN 5
        ELSE 6
    END;

-- Priority distribution
CREATE OR REPLACE VIEW v_priority_distribution AS
SELECT 
    priority,
    COUNT(*) as feature_count,
    SUM(story_points) as story_points,
    json_agg(
        json_build_object(
            'module', module_name,
            'name', display_name,
            'status', deployment_status
        )
    ) as features
FROM feature_backlog
GROUP BY priority
ORDER BY priority;
```

#### c. Test Supabase Connection

```python
# test_supabase.py
from supabase import create_client
import os

supabase = create_client(
    "https://spdtwktxdalcfigzeqrz.supabase.co",
    os.environ.get("SUPABASE_KEY")
)

# Test query
result = supabase.table('feature_backlog').select("*").limit(5).execute()
print(f"✅ Connected! Found {len(result.data)} features")
```

### 4. DigitalOcean Deployment

#### Option A: Deploy as DO App

Create `backlog-automation.yaml`:

```yaml
name: backlog-automation
region: sgp1  # Singapore (closest to Philippines)

services:
  - name: automation
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true
    
    source_dir: /automation
    
    run_command: python3 backlog_automation.py --auto
    
    envs:
      - key: SUPABASE_URL
        value: https://spdtwktxdalcfigzeqrz.supabase.co
      - key: SUPABASE_KEY
        scope: RUN_TIME
        type: SECRET
    
    instance_count: 1
    instance_size_slug: basic-xxs
    
    jobs:
      - name: daily-sync
        kind: CRON
        schedule: "0 2 * * *"  # 2 AM UTC = 10 AM PHT
        run_command: python3 backlog_automation.py --auto
```

Deploy:

```bash
# Install doctl
brew install doctl  # macOS
# or: snap install doctl  # Linux

# Authenticate
doctl auth init

# Create app
doctl apps create --spec backlog-automation.yaml

# Get app ID
doctl apps list

# Monitor deployment
doctl apps logs <app-id> --type RUN
```

#### Option B: Deploy as Cron Job on Existing Server

If you already have a DigitalOcean droplet running Odoo:

```bash
# SSH to your droplet
ssh root@your-droplet-ip

# Clone repo
cd /opt
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo/automation

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment variables
cat > .env << EOF
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_KEY=your-key-here
EOF

# Test run
python3 backlog_automation.py

# Setup cron
crontab -e

# Add this line:
0 2 * * * cd /opt/insightpulse-odoo/automation && source venv/bin/activate && python3 backlog_automation.py --auto >> /var/log/backlog.log 2>&1
```

### 5. Notion Integration

#### a. Get Notion API Key

1. Go to https://www.notion.so/my-integrations
2. Create new integration: "InsightPulse Backlog Sync"
3. Copy the Internal Integration Token
4. Give it access to your workspace

#### b. Setup Notion MCP

If using Claude Desktop:

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
// %APPDATA%\Claude\claude_desktop_config.json (Windows)
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/mcp-server-notion"]
    }
  }
}
```

#### c. Create Database

Use the generated Notion commands from `backlog_output/notion_commands_*.txt`

### 6. Monitoring & Alerts

#### a. Slack Notifications

Create Slack webhook:
1. Go to https://api.slack.com/apps
2. Create app → Incoming Webhooks
3. Add webhook to your channel
4. Copy webhook URL to GitHub secrets

#### b. Supabase Logs

```sql
-- Create audit log table
CREATE TABLE IF NOT EXISTS backlog_sync_logs (
    id BIGSERIAL PRIMARY KEY,
    sync_timestamp TIMESTAMPTZ DEFAULT NOW(),
    features_synced INTEGER,
    new_features INTEGER,
    modified_features INTEGER,
    removed_features INTEGER,
    total_story_points INTEGER,
    status TEXT,
    error_message TEXT,
    execution_time_ms INTEGER
);

-- Create function to log sync
CREATE OR REPLACE FUNCTION log_backlog_sync(
    p_features_synced INTEGER,
    p_new_features INTEGER,
    p_modified_features INTEGER,
    p_removed_features INTEGER,
    p_total_story_points INTEGER,
    p_status TEXT,
    p_error_message TEXT DEFAULT NULL,
    p_execution_time_ms INTEGER DEFAULT NULL
)
RETURNS void AS $$
BEGIN
    INSERT INTO backlog_sync_logs (
        features_synced,
        new_features,
        modified_features,
        removed_features,
        total_story_points,
        status,
        error_message,
        execution_time_ms
    ) VALUES (
        p_features_synced,
        p_new_features,
        p_modified_features,
        p_removed_features,
        p_total_story_points,
        p_status,
        p_error_message,
        p_execution_time_ms
    );
END;
$$ LANGUAGE plpgsql;
```

### 7. Multi-Agency Support

For your agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB):

```sql
-- Create agency table
CREATE TABLE IF NOT EXISTS agencies (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    active BOOLEAN DEFAULT true
);

INSERT INTO agencies (code, name) VALUES
    ('RIM', 'RIM Agency'),
    ('CKVC', 'CKVC Agency'),
    ('BOM', 'BOM Agency'),
    ('JPAL', 'JPAL Agency'),
    ('JLI', 'JLI Agency'),
    ('JAP', 'JAP Agency'),
    ('LAS', 'LAS Agency'),
    ('RMQB', 'RMQB Agency');

-- Link features to agencies
CREATE TABLE IF NOT EXISTS feature_agency_mapping (
    id BIGSERIAL PRIMARY KEY,
    feature_id BIGINT REFERENCES feature_backlog(id),
    agency_code TEXT REFERENCES agencies(code),
    UNIQUE(feature_id, agency_code)
);

-- View features by agency
CREATE OR REPLACE VIEW v_features_by_agency AS
SELECT 
    a.code,
    a.name as agency_name,
    COUNT(f.id) as feature_count,
    SUM(f.story_points) as total_story_points
FROM agencies a
LEFT JOIN feature_agency_mapping fam ON a.code = fam.agency_code
LEFT JOIN feature_backlog f ON fam.feature_id = f.id
GROUP BY a.code, a.name
ORDER BY feature_count DESC;
```

## 🔍 Verification

### Test End-to-End Flow

```bash
# 1. Trigger GitHub Action
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/jgtolentino/insightpulse-odoo/actions/workflows/backlog-sync.yml/dispatches \
  -d '{"ref":"main"}'

# 2. Check Supabase
curl "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/feature_backlog?select=count" \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"

# 3. Verify Notion sync
# Check Notion database manually

# 4. Check logs
tail -f /var/log/backlog.log
```

## 📊 Metrics Dashboard

Create Superset dashboard connected to Supabase:

```python
# superset_config.py
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres'

# Create charts:
# 1. Feature count by business area (pie chart)
# 2. Story points by epic (bar chart)
# 3. Deployment pipeline (funnel chart)
# 4. Priority distribution (stacked bar)
# 5. Sync history (line chart from backlog_sync_logs)
```

## 🚨 Troubleshooting

### GitHub Action Fails

```bash
# Check workflow logs
gh run list --workflow=backlog-sync.yml
gh run view <run-id> --log
```

### Supabase Connection Issues

```python
# Test connection
python3 << EOF
from supabase import create_client
supabase = create_client("https://spdtwktxdalcfigzeqrz.supabase.co", "key")
print(supabase.table('feature_backlog').select("count").execute())
EOF
```

### Notion Sync Fails

- Verify Notion integration has access to workspace
- Check data_source_id is correct
- Ensure no rate limit hit (max 3 requests/second)

## 📚 Maintenance

### Weekly Tasks

- Review diff reports
- Validate feature classification
- Update Notion board views

### Monthly Tasks

- Analyze metrics trends
- Archive old backlog files
- Review and update epics
- Clean up deprecated features

### Quarterly Tasks

- Review business area distribution
- Update classification rules
- Audit External ID consistency
- Performance optimization

---

## 🔗 Related Resources

- [DigitalOcean Project](https://cloud.digitalocean.com/projects/29cde7a1-8280-46ad-9fdf-dea7b21a7825)
- [Supabase Dashboard](https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz)
- [GitHub Actions](https://github.com/jgtolentino/insightpulse-odoo/actions)
- [Notion Workspace](https://notion.so/)

## 🎯 Success Metrics

- ✅ Daily automated discovery runs
- ✅ <5 minute sync to Notion
- ✅ 100% feature coverage
- ✅ Real-time backlog visibility
- ✅ Zero manual data entry
- ✅ Multi-agency support enabled

---

**Deployment Time:** ~2 hours
**Maintenance:** ~15 minutes/week
**ROI:** Eliminates 5-10 hours/week of manual backlog management
