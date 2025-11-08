# AI Gateway - Unified MCP + REST API for FinServ Operations

**Exposes FinServ operations to Claude Desktop (MCP), ChatGPT Custom GPTs (REST), and Claude Web (REST).**

---

## 🎯 What This Does

### Supported AI Platforms

| Platform | Protocol | Config File | Use Case |
|----------|----------|-------------|----------|
| **Claude Desktop** | MCP (JSON-RPC) | `claude-desktop-config.json` | Power users, developers |
| **ChatGPT Custom GPT** | REST (OpenAPI) | `chatgpt-custom-gpt.md` | Team collaboration |
| **Claude Web (Projects)** | REST | Direct HTTP calls | One-off queries |

### Available Operations

**1. Odoo ERP** (`/mcp/odoo` or `/api/*`)
- Get sale orders, invoices, expenses
- Create project tasks
- Search customers/vendors
- Filter by agency (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)

**2. Month-End Close** (`/mcp/close` or `/api/close/*`)
- Get close status (all entities or specific)
- View checklists with task status
- Track exceptions/blockers
- Analyze close cycle metrics

**3. Policy QA** (`/mcp/policy` or `/api/policy/*`)
- Ask questions about SOPs, policies, compliance
- Semantic search with RAG (pgVector + Claude)
- Returns answers with citations
- Covers accounting, finance, HR, procurement, BIR

---

## 🚀 Quick Start

### 1. Deploy the Gateway

**Option A: Docker Compose (Recommended)**

```bash
cd services/ai-gateway

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env

# Start service
docker compose up -d

# Check health
curl http://localhost:8080/health
```

**Option B: Docker Run**

```bash
docker build -t ai-gateway .

docker run -d \
  -p 8080:8080 \
  --env-file .env \
  --name ai-gateway \
  ai-gateway
```

**Option C: Local Development**

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
export ODOO_URL=https://erp.insightpulseai.net
export ODOO_API_KEY=your-key
# ... (see .env.example for all vars)

# Run
python main.py
# or
uvicorn main:app --reload
```

---

### 2. Configure Claude Desktop

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

Copy contents from `claude-desktop-config.json`:

```json
{
  "mcpServers": {
    "finserv-odoo": {
      "url": "https://api.insightpulseai.net/mcp/odoo"
    },
    "finserv-close": {
      "url": "https://api.insightpulseai.net/mcp/close"
    },
    "finserv-policy": {
      "url": "https://api.insightpulseai.net/mcp/policy"
    }
  }
}
```

**Restart Claude Desktop** → Now you can ask:

```
Claude, what's the close status for RIM this month?
Claude, what's our policy on travel expense approval?
Claude, show me sale order SO001
```

---

### 3. Configure ChatGPT Custom GPT

Follow the guide in `chatgpt-custom-gpt.md`:

1. Create Custom GPT in ChatGPT
2. Import OpenAPI schema from `https://api.insightpulseai.net/.well-known/openapi.yaml`
3. Set API Key authentication (`X-API-Key` header)
4. Test with sample queries
5. Publish and share with team

---

## 📚 API Reference

### MCP Endpoints (for Claude Desktop)

All MCP endpoints accept JSON-RPC requests:

```json
{
  "method": "tools/list",
  "params": {}
}
```

or

```json
{
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {...}
  }
}
```

| Endpoint | Description | Tools |
|----------|-------------|-------|
| `/mcp/odoo` | Odoo ERP operations | `odoo_get_sale_order`, `odoo_list_expenses`, `odoo_create_task`, etc. |
| `/mcp/close` | Close operations | `close_get_status`, `close_get_checklist`, `close_mark_task_complete`, etc. |
| `/mcp/policy` | Policy Q&A | `policy_qa`, `policy_search`, `policy_get_document`, etc. |

---

### REST API Endpoints (for ChatGPT / Claude Web)

All REST endpoints require `X-API-Key` header.

**Close Operations**:

```bash
# Get close status
GET /api/close/status?entity_code=RIM&period=2025-01

# Get checklist
GET /api/close/checklist?entity_code=RIM&period=2025-01

# Get exceptions
GET /api/close/exceptions?severity=critical

# Get metrics
GET /api/close/metrics?last_n_periods=6
```

**Policy QA**:

```bash
# Ask a question
POST /api/policy/qa
{
  "question": "What's the expense approval threshold for managers?",
  "category": "finance",
  "top_k": 6
}

# Search documents
POST /api/policy/search
{
  "query": "BIR deadline 2550Q",
  "limit": 10
}

# List categories
GET /api/policy/categories
```

**Odoo Operations**:

```bash
# List expenses
GET /api/expenses?agency_code=RIM&state=approved&limit=20

# Get expense details
GET /api/expenses/EXP-2025-00123

# List invoices
GET /api/invoices?overdue=true&limit=10

# Get sale order
GET /api/sale-orders/SO001

# Create task
POST /api/tasks
{
  "name": "Review Q4 accruals",
  "description": "Verify all accruals are posted",
  "priority": "2"
}
```

---

## 🔐 Authentication

### API Keys

The gateway supports three types of API keys (configured in `.env`):

| Key | Purpose | Usage |
|-----|---------|-------|
| `API_KEY_CHATGPT` | ChatGPT Custom GPT | Team-wide access via ChatGPT |
| `API_KEY_CLAUDE` | Claude Web (Projects) | Personal use |
| `API_KEY_INTERNAL` | Internal services | n8n, Mattermost bot, etc. |

**Format**: Include in request header:

```
X-API-Key: your-api-key-here
```

### Security Best Practices

1. **Rotate keys quarterly**
2. **Use separate keys for prod/dev**
3. **Never commit keys to Git**
4. **Store keys in secure vaults** (1Password, Vault, AWS Secrets Manager)
5. **Monitor API usage** via logs

---

## 🧪 Testing

### Test Health Endpoint

```bash
curl http://localhost:8080/health
```

Expected:
```json
{
  "status": "healthy",
  "service": "ai-gateway",
  "version": "1.0.0",
  "endpoints": {
    "mcp": ["/mcp/odoo", "/mcp/close", "/mcp/policy"],
    "rest": ["/api/close/status", "/api/policy/qa", "/api/expenses"]
  }
}
```

---

### Test MCP Endpoint

```bash
curl -X POST http://localhost:8080/mcp/odoo \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/list",
    "params": {}
  }'
```

Expected: List of available Odoo tools

---

### Test REST Endpoint

```bash
curl -X GET "http://localhost:8080/api/close/status?entity_code=RIM" \
  -H "X-API-Key: your-api-key-here"
```

Expected: Close status for RIM

---

### Test Policy QA

```bash
curl -X POST http://localhost:8080/api/policy/qa \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the BIR deadline for 2550Q quarterly VAT?",
    "category": "compliance"
  }'
```

Expected: Answer with citations from policy docs

---

## 🐛 Troubleshooting

### Gateway won't start

**Check**:
1. Environment variables set correctly
2. Required services reachable (Odoo, Supabase, n8n)
3. Port 8080 not in use

**Solution**:
```bash
# Check env
docker compose config

# Check logs
docker compose logs -f ai-gateway

# Test backend services
curl https://erp.insightpulseai.net/health
curl https://n8n.insightpulseai.net/health
```

---

### Claude Desktop not seeing MCP servers

**Check**:
1. Config file location correct
2. Gateway URL accessible from your machine
3. JSON syntax valid

**Solution**:
```bash
# Validate JSON
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq

# Test MCP endpoint
curl -X POST https://api.insightpulseai.net/mcp/odoo \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list", "params": {}}'

# Restart Claude Desktop
```

---

### ChatGPT Custom GPT returns errors

**Check**:
1. OpenAPI schema valid
2. API key set correctly
3. CORS enabled for chat.openai.com

**Solution**:
```bash
# Validate OpenAPI
curl https://api.insightpulseai.net/.well-known/openapi.yaml | yq

# Test with curl (same request ChatGPT makes)
curl -X GET https://api.insightpulseai.net/api/close/status \
  -H "X-API-Key: gpt-xxxx"
```

---

### Policy QA returns no citations

**Check**:
1. Vector DB populated with embeddings
2. `VECTOR_API_URL` correct
3. Category filter not too narrow

**Solution**:
```bash
# Test vector API directly
curl https://mcp.insightpulseai.net/vector/categories

# Check embeddings count
psql $DATABASE_URL -c "SELECT COUNT(*) FROM policy_embeddings;"
```

---

## 📊 Monitoring

### Metrics to Track

1. **Request volume** (by endpoint)
2. **Response times** (p50, p95, p99)
3. **Error rates**
4. **API key usage** (by client)
5. **MCP vs REST traffic**

### Add to n8n for Alerts

Create workflow:

1. **Every 5 minutes**: Query `/health`
2. **If unhealthy**: Post to `#alerts` in Mattermost
3. **If error rate > 5%**: Notify ops team

---

## 🚀 Production Deployment

### Option 1: DigitalOcean App Platform

```yaml
# app.yaml
name: ai-gateway
services:
  - name: api
    source_dir: services/ai-gateway
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true
    build_command: pip install -r requirements.txt
    run_command: uvicorn main:app --host 0.0.0.0 --port 8080
    http_port: 8080
    instance_count: 2
    instance_size_slug: basic-xs
    envs:
      - key: API_KEY_CHATGPT
        scope: SECRET
      - key: API_KEY_CLAUDE
        scope: SECRET
      - key: ODOO_URL
        value: https://erp.insightpulseai.net
      # ... (add all vars from .env)
    health_check:
      http_path: /health
```

Deploy:
```bash
doctl apps create --spec app.yaml
```

---

### Option 2: Docker + Nginx Reverse Proxy

Add to your existing `docker-compose.yml`:

```yaml
services:
  ai-gateway:
    build: ./services/ai-gateway
    env_file: ./services/ai-gateway/.env
    restart: unless-stopped
    networks:
      - finserv

  nginx:
    # Add upstream
    # proxy_pass http://ai-gateway:8080;
```

Nginx config snippet:

```nginx
server {
    listen 443 ssl http2;
    server_name api.insightpulseai.net;

    ssl_certificate /etc/letsencrypt/live/api.insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.insightpulseai.net/privkey.pem;

    location / {
        proxy_pass http://ai-gateway:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📖 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      AI INTERFACES                            │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐      │
│  │   Claude    │  │   ChatGPT    │  │   Claude Web   │      │
│  │   Desktop   │  │  Custom GPT  │  │   (Projects)   │      │
│  └──────┬──────┘  └──────┬───────┘  └────────┬───────┘      │
│         │ MCP             │ REST API          │ REST API     │
└─────────┼─────────────────┼───────────────────┼──────────────┘
          │                 │                   │
┌─────────▼─────────────────▼───────────────────▼──────────────┐
│              AI GATEWAY (api.insightpulseai.net)              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  MCP Servers         │  REST API (FastAPI)             │  │
│  │  - finserv_odoo      │  - /api/close/*                 │  │
│  │  - finserv_close     │  - /api/policy/*                │  │
│  │  - finserv_policy    │  - /api/expenses/*              │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────────┬──────────────────────────────────┘
                             │
┌────────────────────────────▼──────────────────────────────────┐
│                    BACKEND SERVICES                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Odoo    │  │   n8n    │  │  Vector  │  │ Supabase │     │
│  │   ERP    │  │  (Jobs)  │  │    DB    │  │   (PG)   │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└───────────────────────────────────────────────────────────────┘
```

---

## 📝 License

LGPL-3.0 (same as InsightPulse Odoo)

---

## 🤝 Support

- **Issues**: GitHub Issues
- **Slack**: `#ai-gateway` channel
- **Mattermost**: `#alerts`
- **Email**: support@insightpulseai.net

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-11-08
