# InsightPulse AI Agent Orchestrator

FastAPI service that powers the **Odoo Studio × Notion Agent** hybrid system.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   FastAPI Service (Port 8000)                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Agents (LLM-powered workflows)                        │  │
│  │  - meeting_to_prd: Meeting → PRD → Tasks → Slack      │  │
│  │  - (add more agents here)                              │  │
│  └─────────────────┬──────────────────────────────────────┘  │
│                    │                                          │
│  ┌─────────────────▼────────┬──────────────┬──────────────┐  │
│  │  Tools                   │   Memory     │     LLM      │  │
│  │  - odoo_client          │  - kv_store  │  - Claude    │  │
│  │  - slack_client         │              │    API       │  │
│  └─────────────────────────┴──────────────┴──────────────┘  │
└──────────────────────────────────────────────────────────────┘
           │                    │                  │
           ↓                    ↓                  ↓
    ┌──────────┐         ┌──────────┐      ┌──────────┐
    │   Odoo   │         │  Slack   │      │ Claude   │
    │   ERP    │         │   API    │      │   API    │
    └──────────┘         └──────────┘      └──────────┘
```

## Features

### Agents

**1. Meeting → PRD (meeting_to_prd.py)**
- Triggered when calendar meeting ends
- Fetches meeting details from Odoo
- Generates PRD using Claude + team memory
- Creates `ip.page` record
- Extracts tasks → `project.task`
- Posts Slack summary

### Tools

**1. Odoo Client (odoo_client.py)**
- XML-RPC client for Odoo
- CRUD operations on all models
- Agent-specific helpers (create_agent_run, create_page, etc.)
- Memory get/set operations

**2. Slack Client (slack_client.py)**
- Slack Web API wrapper
- Post messages with Block Kit
- Thread management
- Update messages

**3. LLM Client (llm_client.py)**
- Claude API wrapper
- Automatic cost tracking
- JSON output support
- Multiple model support

### Memory

**KV Store (kv_store.py)**
- Scoped memory: user, team, org
- Backed by `ip.memory.kv` in Odoo
- Convenience methods:
  - `get_writing_style(team_id)`
  - `get_prd_template()`
  - `get_user_preferences(user_id)`
  - `get_db_paths()`
  - `get_slack_channels()`

## Setup

### 1. Install Dependencies

```bash
cd services/ipai-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- `ODOO_URL`: Odoo base URL
- `ODOO_DB`: Database name
- `ODOO_USERNAME`: Username (API user)
- `ODOO_PASSWORD`: API key/password
- `ANTHROPIC_API_KEY`: Claude API key
- `SLACK_BOT_TOKEN`: Slack bot token

### 3. Seed Memory (Optional)

Run this once to populate default memories:

```python
from memory.kv_store import MemoryKVStore
from tools.odoo_client import OdooClient

odoo = OdooClient()
memory = MemoryKVStore(odoo)

# Set PRD template
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
    ]
})

# Set Slack channels
memory.set_slack_channels({
    'general': 'C01234567',
    'rim-finance': 'C_RIM_FIN',
    'bir-compliance': 'C_BIR_COMP'
})
```

### 4. Run Service

```bash
# Development
python main.py

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Docker (Alternative)

```bash
docker build -t ipai-agent .
docker run -p 8000:8000 --env-file .env ipai-agent
```

## API Endpoints

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "ipai-agent",
  "timestamp": "2025-11-06T...",
  "odoo_connected": true,
  "slack_connected": true
}
```

### Meeting → PRD
```
POST /agent/meeting-to-prd
```

Request:
```json
{
  "meeting_id": 123,
  "attendee_emails": ["john@example.com"],
  "summary": "Optional meeting summary",
  "user_id": 1
}
```

Response:
```json
{
  "run_id": 456,
  "status": "running",
  "message": "PRD generation started. Check agent run for status."
}
```

### Generic Agent Execution
```
POST /agent/execute
```

Request:
```json
{
  "agent_slug": "meeting-to-prd",
  "input_data": {
    "meeting_id": 123
  },
  "user_id": 1
}
```

### Memory Operations
```
GET /memory/{scope}/{key}?owner_id=123
POST /memory/{scope}/{key}
```

Example:
```bash
# Get team writing style
curl http://localhost:8000/memory/team/writing_style?owner_id=5

# Set user preferences
curl -X POST http://localhost:8000/memory/user/preferences \
  -H "Content-Type: application/json" \
  -d '{"notifications": true, "slack_dm": false}'
```

### Webhook: Calendar Event Ended
```
POST /webhook/calendar/event-ended
```

Request:
```json
{
  "meeting_id": 123,
  "attendee_emails": ["john@example.com"],
  "summary": "Project Kickoff"
}
```

## Triggering from Odoo

### Option 1: Manual Trigger (Odoo Action)

Create a server action in Odoo Studio:
```python
import requests

url = "http://localhost:8000/agent/meeting-to-prd"
data = {
    "meeting_id": record.id,
    "attendee_emails": [p.email for p in record.partner_ids],
    "user_id": env.uid
}
requests.post(url, json=data)
```

### Option 2: Automated Trigger (pg_cron)

```sql
-- When meeting ends, trigger agent
SELECT cron.schedule(
  'trigger-meeting-prd',
  '*/15 * * * *',  -- Every 15 minutes
  $$
  -- Find meetings that ended in last 15 minutes
  SELECT * FROM trigger_meeting_prd_workflow();
  $$
);
```

### Option 3: Slack Slash Command

```
/ipai prd from meeting "Project Kickoff"
```

## Adding New Agents

1. **Create agent file** in `agents/`:

```python
# agents/my_agent.py
class MyAgent:
    def __init__(self, odoo_client, slack_client, memory_store, llm_client):
        self.odoo = odoo_client
        self.slack = slack_client
        self.memory = memory_store
        self.llm = llm_client

    async def execute(self, run_id, user_id, **kwargs):
        # Your workflow here
        pass
```

2. **Register in main.py**:

```python
from agents.my_agent import MyAgent

my_agent = MyAgent(odoo, slack, memory, llm)

agents = {
    "meeting-to-prd": meeting_prd_agent,
    "my-agent": my_agent,  # Add here
}
```

3. **Call via API**:

```bash
curl -X POST http://localhost:8000/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_slug": "my-agent",
    "input_data": {...}
  }'
```

## Monitoring

### View Agent Runs in Odoo

Navigate to: **AI Agent → Agent Runs**

See:
- Status (running, completed, failed)
- Input/output data
- Token usage
- Cost tracking
- Execution time
- Error messages

### Logs

```bash
# Service logs
tail -f /var/log/ipai-agent.log

# Or via journalctl (if systemd)
journalctl -u ipai-agent -f
```

## Production Deployment

### 1. Systemd Service

Create `/etc/systemd/system/ipai-agent.service`:

```ini
[Unit]
Description=InsightPulse AI Agent
After=network.target

[Service]
Type=simple
User=odoo
WorkingDirectory=/opt/ipai-agent
Environment="PATH=/opt/ipai-agent/venv/bin"
ExecStart=/opt/ipai-agent/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ipai-agent
sudo systemctl start ipai-agent
sudo systemctl status ipai-agent
```

### 2. Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name agent.insightpulseai.net;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. DigitalOcean App Platform (Alternative)

```yaml
# .do/app.yaml
name: ipai-agent
services:
  - name: api
    source_dir: services/ipai-agent
    build_command: pip install -r requirements.txt
    run_command: uvicorn main:app --host 0.0.0.0 --port 8000
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
```

Deploy:
```bash
doctl apps create --spec .do/app.yaml
```

## Troubleshooting

### Odoo connection failed
- Check `ODOO_URL`, `ODOO_USERNAME`, `ODOO_PASSWORD`
- Verify Odoo is accessible
- Check XML-RPC is enabled in Odoo

### Slack messages not posting
- Check `SLACK_BOT_TOKEN`
- Verify bot is invited to channels
- Check OAuth scopes: `chat:write`, `channels:read`

### LLM API errors
- Check `ANTHROPIC_API_KEY`
- Verify API key is valid
- Check rate limits

### Agent runs failing
- Check logs in Odoo (AI Agent → Agent Runs)
- View error messages
- Check token usage (may have hit limits)

## Cost Tracking

Agent runs automatically track:
- Input tokens
- Output tokens
- Cost in cents (USD)

View costs in Odoo: **AI Agent → Agent Runs**

Filter by date range and sum `cost_cents` to get total spend.

## Next Steps

1. **Add more agents**:
   - GitHub issue → Odoo ticket
   - Notion sync → Odoo pages
   - BIR deadline → Compliance PRD

2. **Enhance memory**:
   - Team voice/tone examples
   - Project-specific templates
   - User-specific preferences

3. **Improve Slack integration**:
   - Thread management
   - Interactive buttons
   - User mentions

4. **Add monitoring**:
   - Prometheus metrics
   - Error alerting
   - Performance tracking

## License

AGPL-3

## Author

Jake Tolentino (jgtolentino_rn@yahoo.com)
