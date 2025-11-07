# InsightPulse AI Agent Hybrid - Deployment Guide

## Overview

**Odoo Studio × Notion Agent**: Studio handles your data + UI, the agent plans and executes multi-step work.

### Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          User Interaction                            │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐ │
│  │ Odoo Web   │   │   Slack    │   │  Calendar  │   │  Notion    │ │
│  │  Studio    │   │  Commands  │   │  Triggers  │   │   Sync     │ │
│  └─────┬──────┘   └─────┬──────┘   └─────┬──────┘   └─────┬──────┘ │
└────────┼────────────────┼────────────────┼────────────────┼─────────┘
         │                │                │                │
         └────────────────┴────────────────┴────────────────┘
                                 │
┌────────────────────────────────▼──────────────────────────────────────┐
│                   FastAPI Orchestrator (Port 8000)                    │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Agents (LLM Workflows)                                         │ │
│  │  - meeting_to_prd: Meeting → PRD → Tasks → Slack               │ │
│  │  - (add more agents here)                                       │ │
│  └──────────────┬──────────────────────────────────────────────────┘ │
│                 │                                                     │
│  ┌──────────────▼────────┬────────────────┬─────────────────────┐   │
│  │  Tools                │   Memory       │      LLM            │   │
│  │  - odoo_client       │  - kv_store    │   - Claude API      │   │
│  │  - slack_client      │  - team style  │   - Cost tracking   │   │
│  │  - llm_client        │  - templates   │   - Usage tracking  │   │
│  └──────────────┬────────┴────────────────┴─────────────────────┘   │
└─────────────────┼───────────────────────────────────────────────────┘
                  │
         ┌────────┴───────┬──────────────┬──────────────┐
         ↓                ↓              ↓              ↓
  ┌──────────┐     ┌──────────┐   ┌──────────┐  ┌──────────┐
  │   Odoo   │     │  Slack   │   │  Claude  │  │ Supabase │
  │   ERP    │     │   API    │   │   API    │  │    DB    │
  │ (19 CE)  │     │          │   │          │  │ (Memory) │
  └──────────┘     └──────────┘   └──────────┘  └──────────┘
```

---

## Component Overview

### 1. Odoo Module: `ipai_agent_hybrid`

**Models:**
- `ip.page` - Notion-like pages (PRDs, meeting notes, wikis)
- `ip.agent.run` - Agent execution logs with cost tracking
- `ip.memory.kv` - Durable memory (user/team/org scope)
- `ip.page.tag` - Tags for organizing pages

**Features:**
- Markdown/HTML content support
- Source tracking (meeting, notion, github, slack, agent)
- Task integration (link to project.task)
- Full-text search
- Security (public/private, user permissions)
- View count tracking

### 2. FastAPI Service: `ipai-agent`

**Location:** `services/ipai-agent/`

**Components:**
- `main.py` - FastAPI app with endpoints
- `agents/meeting_to_prd.py` - Meeting→PRD workflow
- `tools/odoo_client.py` - Odoo XML-RPC client
- `tools/slack_client.py` - Slack Web API wrapper
- `tools/llm_client.py` - Claude API wrapper
- `memory/kv_store.py` - Memory management

**Endpoints:**
- `GET /health` - Health check
- `POST /agent/meeting-to-prd` - Trigger workflow
- `POST /agent/execute` - Generic agent execution
- `GET/POST /memory/{scope}/{key}` - Memory operations
- `POST /webhook/calendar/event-ended` - Calendar trigger

---

## Prerequisites

### Required Services

1. **Odoo 19 CE** running (https://erp.insightpulseai.net)
2. **Supabase** database (optional, for pg_cron triggers)
3. **Claude API key** (Anthropic)
4. **Slack workspace** with bot token

### Required Credentials

- Odoo admin credentials or API key
- Anthropic API key (`ANTHROPIC_API_KEY`)
- Slack bot token (`SLACK_BOT_TOKEN`)

---

## Installation

### Part 1: Install Odoo Module

#### Step 1: Upload Module

```bash
# SSH to Odoo server
ssh root@165.227.10.178

# Upload module
scp -r addons/ipai_agent_hybrid root@165.227.10.178:/opt/odoo/custom-addons/

# Set permissions
chown -R odoo:odoo /opt/odoo/custom-addons/ipai_agent_hybrid

# Restart Odoo
systemctl restart odoo
```

#### Step 2: Install via Odoo UI

1. Login to Odoo as admin
2. Navigate to **Apps**
3. Click **Update Apps List**
4. Search for "InsightPulse AI Agent Hybrid"
5. Click **Install**

#### Step 3: Verify Installation

Navigate to: **AI Agent** → **Pages**

You should see the page listing view.

---

### Part 2: Deploy FastAPI Service

#### Option A: Local Development

```bash
# Navigate to service directory
cd services/ipai-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env
```

Edit `.env`:
```bash
ODOO_URL=https://erp.insightpulseai.net
ODOO_DB=odoo19
ODOO_USERNAME=admin
ODOO_PASSWORD=your-odoo-password

ANTHROPIC_API_KEY=sk-ant-api03-...

SLACK_BOT_TOKEN=xoxb-...

LOG_LEVEL=INFO
```

```bash
# Run service
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Option B: Production Deployment (Systemd)

```bash
# Create service directory
sudo mkdir -p /opt/ipai-agent
sudo chown odoo:odoo /opt/ipai-agent

# Upload code
scp -r services/ipai-agent/* root@165.227.10.178:/opt/ipai-agent/

# Install dependencies
cd /opt/ipai-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/ipai-agent.service
```

`/etc/systemd/system/ipai-agent.service`:
```ini
[Unit]
Description=InsightPulse AI Agent Orchestrator
After=network.target

[Service]
Type=simple
User=odoo
WorkingDirectory=/opt/ipai-agent
Environment="PATH=/opt/ipai-agent/venv/bin"
EnvironmentFile=/opt/ipai-agent/.env
ExecStart=/opt/ipai-agent/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ipai-agent
sudo systemctl start ipai-agent
sudo systemctl status ipai-agent

# View logs
journalctl -u ipai-agent -f
```

#### Option C: Docker Deployment

```bash
cd services/ipai-agent

# Build image
docker build -t ipai-agent:latest .

# Run container
docker run -d \
  --name ipai-agent \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  ipai-agent:latest

# View logs
docker logs -f ipai-agent
```

#### Option D: DigitalOcean App Platform

```bash
# Create app spec
cat > .do/app.yaml <<EOF
name: ipai-agent
services:
  - name: api
    source_dir: services/ipai-agent
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true
    build_command: pip install -r requirements.txt
    run_command: uvicorn main:app --host 0.0.0.0 --port 8000
    http_port: 8000
    instance_count: 1
    instance_size_slug: basic-xxs
    envs:
      - key: ODOO_URL
        value: https://erp.insightpulseai.net
      - key: ODOO_DB
        value: odoo19
      - key: ODOO_USERNAME
        value: admin
      - key: ODOO_PASSWORD
        scope: SECRET
      - key: ANTHROPIC_API_KEY
        scope: SECRET
      - key: SLACK_BOT_TOKEN
        scope: SECRET
EOF

# Deploy
doctl apps create --spec .do/app.yaml

# Or via UI: Apps → Create App → From GitHub
```

---

## Configuration

### Step 1: Seed Memory

Run this once to populate default memories:

```python
# Python REPL or script
from memory.kv_store import MemoryKVStore
from tools.odoo_client import OdooClient

odoo = OdooClient()
memory = MemoryKVStore(odoo)

# 1. Set PRD template
memory.set_prd_template({
    'sections': [
        'Executive Summary',
        'Background',
        'Goals & Objectives',
        'Requirements',
        'User Stories',
        'Tasks',
        'Success Metrics',
        'Timeline'
    ],
    'style': 'concise and actionable'
})

# 2. Set Slack channel mappings
memory.set_slack_channels({
    'general': 'C01234567',
    'rim-finance': 'C_RIM_FIN',
    'ckvc-finance': 'C_CKVC_FIN',
    'bir-compliance': 'C_BIR_COMP'
})

# 3. Set team writing style (example for team ID 5)
memory.set_writing_style({
    'tone': 'professional yet friendly',
    'format': 'markdown with bullets',
    'length': 'concise (500-1000 words)',
    'structure': 'executive summary first'
}, team_id=5)

# 4. Set database paths
memory.set_db_paths({
    'projects': {
        'model': 'project.project',
        'default_stage_ids': [1, 2, 3]
    },
    'tasks': {
        'model': 'project.task',
        'default_user_id': 2
    }
})

print("✅ Memory seeded successfully!")
```

### Step 2: Configure Nginx (Optional)

If you want to expose the agent API publicly:

```nginx
# /etc/nginx/sites-available/agent.insightpulseai.net
server {
    listen 80;
    server_name agent.insightpulseai.net;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/agent.insightpulseai.net /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d agent.insightpulseai.net
```

---

## Usage

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "ipai-agent",
  "timestamp": "2025-11-06T...",
  "odoo_connected": true,
  "slack_connected": true
}
```

### Test 2: Manual Meeting → PRD Workflow

```bash
curl -X POST http://localhost:8000/agent/meeting-to-prd \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": 123,
    "attendee_emails": ["john@example.com"],
    "user_id": 1
  }'
```

Response:
```json
{
  "run_id": 456,
  "status": "running",
  "message": "PRD generation started. Check agent run for status."
}
```

### Test 3: Check Agent Run Status

Navigate to Odoo: **AI Agent → Agent Runs**

Find run ID 456:
- Status: running → completed
- Input data: meeting_id, attendee_emails
- Output data: page_id, task_ids
- Tokens used: ~3500
- Cost: ~$0.05

### Test 4: View Generated PRD

Navigate to Odoo: **AI Agent → Pages**

Find the PRD:
- Title: "PRD: [Meeting Name]"
- Page Type: PRD
- Source Type: meeting
- Content: Structured PRD with sections
- Related Tasks: 5 tasks extracted

### Test 5: Check Slack Notification

Check your Slack channel (if configured):

You should see:
```
🤖 PRD Generated: Project Kickoff

I've created a PRD from your meeting:
• 5 tasks extracted
• View PRD in Odoo (link)

Meeting: 2025-11-06 | Generated by AI Agent
```

---

## Triggering Workflows

### Method 1: Manual API Call (Development)

```bash
curl -X POST http://localhost:8000/agent/meeting-to-prd \
  -H "Content-Type: application/json" \
  -d '{"meeting_id": 123}'
```

### Method 2: Odoo Server Action (Automated)

Create a server action in Odoo Studio on `calendar.event` model:

**Trigger:** On Write → when `stop` field changes

**Code:**
```python
import requests

# Only trigger if meeting just ended
now = datetime.now()
if record.stop and record.stop < now:
    url = "http://localhost:8000/agent/meeting-to-prd"
    data = {
        "meeting_id": record.id,
        "attendee_emails": [p.email for p in record.partner_ids if p.email],
        "user_id": env.uid
    }
    try:
        requests.post(url, json=data, timeout=5)
    except Exception as e:
        env.log(f"Agent trigger failed: {e}")
```

### Method 3: pg_cron Trigger (Scheduled)

```sql
-- Create function to trigger agent
CREATE OR REPLACE FUNCTION trigger_meeting_prd_workflow()
RETURNS void AS $$
DECLARE
  meeting RECORD;
BEGIN
  -- Find meetings that ended in last 15 minutes
  FOR meeting IN
    SELECT id, name, stop
    FROM calendar_event
    WHERE stop >= NOW() - INTERVAL '15 minutes'
      AND stop < NOW()
      AND NOT EXISTS (
        SELECT 1 FROM ip_page
        WHERE source_type = 'meeting'
          AND source_id = meeting.id::text
      )
  LOOP
    -- Call agent API via pg_net
    PERFORM net.http_post(
      url := 'http://localhost:8000/webhook/calendar/event-ended',
      headers := jsonb_build_object('Content-Type', 'application/json'),
      body := jsonb_build_object(
        'meeting_id', meeting.id,
        'summary', meeting.name
      )
    );
  END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Schedule to run every 15 minutes
SELECT cron.schedule(
  'meeting-prd-trigger',
  '*/15 * * * *',
  'SELECT trigger_meeting_prd_workflow();'
);
```

### Method 4: Slack Slash Command

Setup in Odoo or as standalone webhook:

```
/ipai prd from meeting "Project Kickoff"
```

Handler in `main.py` (already implemented):
```python
@app.post("/webhook/slack/command")
async def slack_command(command_data: Dict[str, Any]):
    # Parse command and trigger workflow
    pass
```

---

## Monitoring

### View Agent Runs in Odoo

Navigate to: **AI Agent → Agent Runs**

**Filters:**
- Status (running, completed, failed)
- Agent slug (meeting-to-prd)
- Date range

**Columns:**
- Run ID, Agent, Status
- Tokens Used, Cost (cents)
- Execution Time
- Created Date
- Error Message (if failed)

### View Logs

```bash
# Systemd service
journalctl -u ipai-agent -f --since "1 hour ago"

# Docker
docker logs -f ipai-agent

# File (if configured)
tail -f /var/log/ipai-agent.log
```

### Cost Tracking

```sql
-- Total cost this month
SELECT
  SUM(cost_cents) / 100.0 AS total_usd,
  COUNT(*) AS run_count,
  AVG(cost_cents) / 100.0 AS avg_cost_per_run
FROM ip_agent_run
WHERE create_date >= DATE_TRUNC('month', NOW())
  AND status = 'completed';

-- Cost by agent
SELECT
  agent_slug,
  SUM(cost_cents) / 100.0 AS total_usd,
  COUNT(*) AS runs,
  SUM(tokens_used) AS total_tokens
FROM ip_agent_run
WHERE create_date >= DATE_TRUNC('month', NOW())
GROUP BY agent_slug
ORDER BY total_usd DESC;
```

---

## Troubleshooting

### Issue: Agent runs fail with "Odoo connection failed"

**Check:**
```bash
# Test Odoo connection
curl -v https://erp.insightpulseai.net/web/database/selector

# Verify credentials in .env
cat /opt/ipai-agent/.env | grep ODOO

# Test XML-RPC manually
python3 << EOF
import xmlrpc.client
url = "https://erp.insightpulseai.net"
db = "odoo19"
username = "admin"
password = "your-password"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
print(f"UID: {uid}")
EOF
```

**Fix:**
- Verify `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD`
- Check Odoo is accessible from agent server
- Verify XML-RPC is enabled in Odoo

### Issue: Slack messages not posting

**Check:**
```bash
# Verify Slack token
cat /opt/ipai-agent/.env | grep SLACK_BOT_TOKEN

# Test Slack API
curl -X POST https://slack.com/api/auth.test \
  -H "Authorization: Bearer xoxb-your-token"
```

**Fix:**
- Verify `SLACK_BOT_TOKEN` is correct
- Check bot is invited to channels: `/invite @InsightPulse Odoo`
- Verify OAuth scopes: `chat:write`, `channels:read`

### Issue: Claude API errors

**Check:**
```bash
# Verify API key
cat /opt/ipai-agent/.env | grep ANTHROPIC_API_KEY

# Test Claude API
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-3-5-sonnet-20241022", "max_tokens": 10, "messages": [{"role": "user", "content": "Hi"}]}'
```

**Fix:**
- Verify `ANTHROPIC_API_KEY` is valid
- Check API key has credits
- Monitor rate limits

### Issue: Memory not persisting

**Check:**
```bash
# Test memory operations
curl http://localhost:8000/memory/org/test_key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"value": "test"}'

curl http://localhost:8000/memory/org/test_key
```

**Verify in Odoo:**
Navigate to: **AI Agent → Configuration → Memory Store**

Should see entry: scope=org, key=test_key

**Fix:**
- Verify Odoo connection
- Check `ip.memory.kv` model exists
- Check user permissions

---

## Next Steps

### 1. Add More Agents

Create new agents in `services/ipai-agent/agents/`:

```python
# agents/github_to_ticket.py
class GitHubToTicketAgent:
    async def execute(self, run_id, github_issue_id, **kwargs):
        # Fetch GitHub issue
        # Create ip.page (page_type='doc')
        # Create helpdesk.ticket
        # Post Slack notification
        pass
```

Register in `main.py`:
```python
from agents.github_to_ticket import GitHubToTicketAgent

github_ticket_agent = GitHubToTicketAgent(odoo, slack, memory, llm)

agents = {
    "meeting-to-prd": meeting_prd_agent,
    "github-to-ticket": github_ticket_agent,
}
```

### 2. Enhance Memory

Add more team-specific memories:
- Writing voice examples
- Project templates
- User preferences
- Agency-specific guidelines

### 3. Improve Slack Integration

- Thread management (one thread per PRD)
- Interactive buttons (approve/reject tasks)
- User mentions (@john for assignments)

### 4. Add Analytics

- Superset dashboard for agent metrics
- Cost tracking over time
- Success rate by agent type
- Average PRD quality scores

### 5. Notion Sync

Create `agents/notion_sync.py`:
- Fetch Notion pages
- Create ip.page records
- Sync comments and updates

---

## Security

### API Authentication

Add authentication to FastAPI:

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if token != os.getenv("API_SECRET_TOKEN"):
        raise HTTPException(status_code=403, detail="Invalid token")
    return token

@app.post("/agent/meeting-to-prd", dependencies=[Depends(verify_token)])
async def run_meeting_to_prd(...):
    pass
```

### Environment Variables

**Never commit**:
- `.env` files
- API keys
- Passwords

Use DigitalOcean App Platform secrets or HashiCorp Vault for production.

### Rate Limiting

Add rate limiting to prevent abuse:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/agent/execute")
@limiter.limit("10/minute")
async def execute_agent(...):
    pass
```

---

## Support

**Issues:** https://github.com/jgtolentino/insightpulse-odoo/issues

**Email:** jgtolentino_rn@yahoo.com

**Documentation:**
- `/docs/IPAI_AGENT_HYBRID_DEPLOYMENT.md` (this file)
- `/services/ipai-agent/README.md` (service docs)
- `/addons/ipai_agent_hybrid/__manifest__.py` (module info)

---

## License

AGPL-3

## Author

Jake Tolentino
