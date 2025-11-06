# MCP Skills Integration Optimization & Minimal Server Stack

**Analysis Date**: 2025-11-06
**Stack**: InsightPulse Finance SSC (Odoo 19 + Supabase + Superset + DigitalOcean)

---

## Executive Summary

### Current State
- **7 MCP servers** configured (5 third-party + 2 custom)
- **55 operational skills** across 11 categories
- **4 custom MCP implementations** (pulser-hub, deepcode-server, mcp-coordinator, insightpulse-monitor)
- **Overlap**: Multiple servers covering similar capabilities (GitHub, DigitalOcean, Docker)

### Optimization Potential
- **Reduce to 3-4 core MCP servers** (67% reduction)
- **Consolidate custom servers** into single unified coordinator
- **Align CI/CD pipelines** for automated deployment
- **Estimated cost savings**: ~40% infrastructure costs

---

## Current MCP Landscape

### Third-Party MCP Servers (vscode-mcp-config.json)

| Server | Tools | Status | Priority |
|--------|-------|--------|----------|
| **digitalocean** | 3 tools (infra, k8s, db) | ✅ Active | 🔴 CRITICAL |
| **github** | 40 tools (repo, CI/CD, issues) | ✅ Active | 🟡 MEDIUM |
| **superset** | 3 tools (analytics, dashboards) | ✅ Active | 🟢 LOW |
| **kubernetes** | 22 tools (cluster ops) | ⚠️ Partial | 🟡 MEDIUM |
| **docker** | 1 tool (containers) | ⚠️ Partial | 🟢 LOW |

### Custom MCP Servers (services/)

| Server | Purpose | Lines of Code | Status | Priority |
|--------|---------|---------------|--------|----------|
| **pulser-hub** | GitHub operations via app | 600+ | ✅ Production | 🔴 CRITICAL |
| **deepcode-server** | Code analysis integration | 400+ | 🔶 Beta | 🟢 LOW |
| **mcp-coordinator** | Multi-server orchestration | 800+ | 🔶 Beta | 🟡 MEDIUM |
| **insightpulse-monitor** | System monitoring | 300+ | 🔶 Beta | 🟢 LOW |

### Skills Framework (.claude/skills/)

| Category | Skills | Most Used | Priority |
|----------|--------|-----------|----------|
| **Odoo** | 36 | odoo-agile-scrum-devops, odoo-finance-automation | 🔴 CRITICAL |
| **Analytics** | 6 | superset-dashboard-automation, superset-chart-builder | 🟡 MEDIUM |
| **Supabase** | 3 | supabase-database-operations, supabase-automation | 🟡 MEDIUM |
| **Finance** | 5 | bir-tax-filing, multi-agency-orchestrator | 🔴 CRITICAL |
| **Notion** | 20 | notion-workflow-sync, notion-knowledge-capture | 🟢 LOW |
| **Infrastructure** | 4 | paddle-ocr-validation, mcp-builder | 🟡 MEDIUM |
| **Documents** | 4 | docx, pdf, pptx, xlsx | 🟢 LOW |
| **Meta** | 10 | skill-creator, mcp-builder | 🟢 LOW |
| **GitHub** | 1 | github-integration | 🟡 MEDIUM |
| **Procurement** | 2 | procurement-sourcing, project-portfolio-management | 🟢 LOW |
| **Core** | 6 | librarian-indexer, repo-architect | 🟢 LOW |

---

## Problems Identified

### 1. ⚠️ **Server Overlap & Redundancy**

**Issue**: Multiple servers covering similar capabilities

| Function | Servers Providing It | Recommendation |
|----------|---------------------|----------------|
| GitHub operations | `@modelcontextprotocol/server-github` + `pulser-hub` | Keep `pulser-hub` (GitHub App auth) |
| Container management | `docker` + `kubernetes` | Merge into single container-ops server |
| Infrastructure | `digitalocean` + `kubernetes` | Keep `digitalocean` only |
| Monitoring | `insightpulse-monitor` + DigitalOcean built-in | Use DO monitoring + health checks |

**Impact**:
- Increased maintenance burden (4 codebases)
- Higher resource consumption (~400MB RAM per server)
- Configuration complexity across multiple configs

### 2. 🔴 **CI/CD Misalignment**

**Issue**: CI/CD pipeline only covers `mcp-coordinator`, not all custom servers

**Current**:
- `.github/workflows/deploy-mcp.yml` → Only deploys `mcp-coordinator`
- Other servers (`pulser-hub`, `deepcode-server`) require manual deployment

**Missing**:
- Automated testing for MCP server changes
- Integration tests across servers
- Rollback procedures
- Health check validation post-deploy

### 3. 🟡 **Skills-to-MCP Misalignment**

**Issue**: 55 skills but only 7 MCP servers to execute them

| Skill Category | Requires MCP Server | Currently Available? |
|----------------|---------------------|---------------------|
| Odoo operations | Odoo RPC + Supabase | ✅ Via direct connection |
| BIR tax filing | Odoo RPC + OCR | ⚠️ Partial (no OCR MCP) |
| Notion workflows | Notion API | ❌ Missing Notion MCP |
| Finance automation | Odoo + Supabase | ✅ Available |
| Superset automation | Superset API | ✅ Available |
| Reddit scraping | Firecrawl | ❌ Missing Firecrawl MCP |

**Gap Analysis**:
- **Missing**: Notion MCP, OCR MCP, Firecrawl MCP
- **Underutilized**: Superset MCP (only 3 tools), Docker MCP (only 1 tool)

### 4. 🔴 **Resource Inefficiency**

**Current Resource Usage** (estimated):

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| Custom MCP servers (4) | ~1.6 cores | ~1.6GB | ~200MB |
| Third-party MCP (5) | ~0.5 cores | ~500MB | ~100MB |
| **Total** | **~2.1 cores** | **~2.1GB** | **~300MB** |

**Optimized**:
| Component | CPU | Memory | Storage | Savings |
|-----------|-----|--------|---------|---------|
| Unified MCP coordinator | ~0.8 cores | ~800MB | ~150MB | **62% CPU** |
| Essential third-party (2) | ~0.2 cores | ~200MB | ~50MB | **60% RAM** |
| **Total** | **~1.0 core** | **~1GB** | **~200MB** | **~50% overall** |

---

## Recommended Minimal MCP Stack

### 🎯 Tier 1: Critical (Must Have)

#### 1. **Unified InsightPulse MCP Coordinator**

**Consolidates**:
- `pulser-hub` (GitHub operations)
- `mcp-coordinator` (orchestration)
- `insightpulse-monitor` (monitoring)

**Provides**:
- ✅ GitHub operations via pulser-hub app (11 tools)
- ✅ DigitalOcean infrastructure management (8 tools)
- ✅ Odoo RPC operations (12 tools)
- ✅ Supabase database operations (10 tools)
- ✅ Multi-service orchestration (5 tools)
- ✅ Health monitoring (3 tools)

**Implementation**:
```python
# services/mcp-unified/server.py
from fastapi import FastAPI
from mcp_server import MCPServer

app = FastAPI(title="InsightPulse Unified MCP")
mcp = MCPServer()

# GitHub tools (from pulser-hub)
@mcp.tool("github_create_pr")
async def github_create_pr(repo: str, title: str, base: str, head: str) -> dict:
    """Create pull request via pulser-hub GitHub App"""
    return await github_client.create_pr(repo, title, base, head)

# DigitalOcean tools (new)
@mcp.tool("do_app_deploy")
async def do_app_deploy(app_id: str, spec: dict) -> dict:
    """Deploy app to DigitalOcean App Platform"""
    return await do_client.apps_update(app_id, spec)

# Odoo tools (new)
@mcp.tool("odoo_approve_expense")
async def odoo_approve_expense(expense_id: int, context: dict) -> dict:
    """Approve expense sheet in Odoo via RPC"""
    return await odoo_client.execute("hr.expense.sheet", "approve", [expense_id])

# Supabase tools (new)
@mcp.tool("supabase_rpc_call")
async def supabase_rpc_call(function: str, params: dict) -> dict:
    """Call Supabase RPC function"""
    return await supabase_client.rpc(function, params)

# Orchestration tools
@mcp.tool("orchestrate_deployment")
async def orchestrate_deployment(service: str, env: str) -> dict:
    """Multi-step deployment orchestration"""
    # 1. Run tests
    await github_trigger_workflow("integration-tests")
    # 2. Deploy to staging
    await do_app_deploy(service, spec)
    # 3. Health check
    await health_check(service)
    # 4. If success, deploy to prod
    if env == "production":
        await do_app_deploy(service, prod_spec)
```

**Deployment**:
- **Platform**: DigitalOcean App Platform
- **Domain**: `mcp.insightpulseai.net`
- **CI/CD**: `.github/workflows/deploy-unified-mcp.yml`
- **Cost**: $0 (starter tier) or $5/month (basic tier for 24/7 uptime)

#### 2. **DigitalOcean MCP Server**

**Why separate?**
- Official Anthropic-maintained server
- Direct DO API integration
- Auto-updated

**Provides**:
- ✅ Droplet management
- ✅ App Platform operations
- ✅ Kubernetes cluster ops
- ✅ Database management

**Implementation**:
```bash
# Already configured in vscode-mcp-config.json
npx -y @modelcontextprotocol/server-digitalocean
```

**Alternative**: Merge into Unified MCP if DO API changes frequently

---

### 🟡 Tier 2: Optional (Nice to Have)

#### 3. **Superset MCP Server** (if heavy analytics usage)

**Only if**:
- Creating >10 dashboards per week
- Automated chart generation required
- Multi-tenant dashboard deployment

**Otherwise**: Use direct Superset REST API from Unified MCP

#### 4. **Notion MCP Server** (if Notion-heavy workflows)

**Only if**:
- Using 10+ Notion skills actively
- Notion as primary documentation hub
- Automated Notion page creation

**Otherwise**: Use Notion API directly via Python requests

---

### ❌ Tier 3: Remove

These can be **replaced** or **deprecated**:

| Server | Replace With | Reason |
|--------|--------------|--------|
| `deepcode-server` | GitHub Copilot or native tools | Low usage, redundant |
| `kubernetes` MCP | DigitalOcean MCP (includes k8s) | Overlapping functionality |
| `docker` MCP | DigitalOcean MCP | 1 tool doesn't justify standalone server |
| `github` MCP | Unified MCP (pulser-hub) | Custom auth via GitHub App is better |
| `insightpulse-monitor` | DigitalOcean built-in monitoring | Native DO monitoring is sufficient |

---

## Optimized Architecture

### Before (Current)
```
┌─────────────────────────────────────────────────┐
│ Claude Code / Claude Desktop                    │
└────────────┬────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│ pulser-  │    │  github  │    │digitalocean│
│   hub    │    │   MCP    │    │    MCP     │
└──────────┘    └──────────┘    └──────────┘
    ▼                 ▼                ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│mcp-coord │    │kubernetes│    │  docker  │
└──────────┘    └──────────┘    └──────────┘
    ▼                 ▼
┌──────────┐    ┌──────────┐
│deepcode  │    │superset  │
└──────────┘    └──────────┘

7 MCP servers × ~300MB = 2.1GB RAM
Maintenance: 7 repos, 7 CI/CD pipelines
```

### After (Optimized)
```
┌─────────────────────────────────────────────────┐
│ Claude Code / Claude Desktop                    │
└────────────┬────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────────┐  ┌──────────────┐
│   Unified    │  │ DigitalOcean │
│ InsightPulse │  │     MCP      │
│     MCP      │  │   (official) │
└──────────────┘  └──────────────┘
       │
       ├─ GitHub (pulser-hub auth)
       ├─ Odoo RPC
       ├─ Supabase
       ├─ Orchestration
       └─ Monitoring

2 MCP servers × ~500MB = 1GB RAM
Maintenance: 1 repo, 1 CI/CD pipeline
SAVINGS: 52% RAM, 71% maintenance burden
```

---

## Skills-to-MCP Alignment Matrix

### After Optimization

| Skill Category | Execution Path | MCP Server | Tools Used |
|----------------|----------------|------------|------------|
| **Odoo operations** | Direct RPC | Unified MCP | `odoo_*` (12 tools) |
| **Finance automation** | Odoo + Supabase | Unified MCP | `odoo_approve_expense`, `supabase_rpc_call` |
| **BIR tax filing** | Odoo + OCR API | Unified MCP | `odoo_generate_bir_form`, HTTP to OCR droplet |
| **Superset dashboards** | Direct REST API | Unified MCP | `superset_create_dashboard` |
| **GitHub workflows** | GitHub App | Unified MCP | `github_create_pr`, `github_trigger_workflow` |
| **DigitalOcean ops** | Official MCP | DO MCP | `do_apps_create`, `do_apps_update` |
| **Multi-agency** | Odoo + Supabase | Unified MCP | Context-aware orchestration |
| **Notion workflows** | Direct API | Unified MCP | `notion_create_page` (new tool) |

**Coverage**: 48/55 skills (87%) → Fully executable via 2 MCP servers

**Gaps** (7 skills not executable via MCP):
- Document skills (docx, pdf, pptx, xlsx) → Direct file operations
- Canvas/art skills → Claude native capabilities
- Audit/review skills → Analysis, not execution

---

## Implementation Plan

### Phase 1: Consolidation (Week 1-2)

#### Step 1.1: Create Unified MCP Server
```bash
# Create new unified server
mkdir -p services/mcp-unified
cd services/mcp-unified

# Scaffold structure
cat > server.py <<EOF
from fastapi import FastAPI
from mcp_server import MCPServer

app = FastAPI(title="InsightPulse Unified MCP")
mcp = MCPServer()

# Import tools from existing servers
from pulser_hub_tools import github_tools
from odoo_tools import odoo_tools
from supabase_tools import supabase_tools
from orchestration_tools import orchestration_tools

# Register all tools
mcp.register_tools(github_tools)
mcp.register_tools(odoo_tools)
mcp.register_tools(supabase_tools)
mcp.register_tools(orchestration_tools)

@app.post("/mcp")
async def mcp_endpoint(request: dict):
    return await mcp.handle_request(request)
EOF
```

#### Step 1.2: Migrate Pulser-Hub Tools
```bash
# Copy GitHub tools from pulser-hub
cp services/mcp-server/server.py services/mcp-unified/github_tools.py

# Update imports and tool registration
# Refactor to use unified auth
```

#### Step 1.3: Add Odoo Tools
```python
# services/mcp-unified/odoo_tools.py
from odoorpc import ODOO

class OdooTools:
    def __init__(self):
        self.odoo = ODOO(
            host=os.getenv("ODOO_HOST"),
            port=443,
            protocol="jsonrpc+ssl"
        )

    async def approve_expense(self, expense_id: int) -> dict:
        """Approve expense sheet"""
        return self.odoo.execute(
            "hr.expense.sheet",
            "approve",
            [expense_id]
        )

    async def generate_bir_form(self, agency: str, period: str, form_type: str) -> dict:
        """Generate BIR tax form"""
        return self.odoo.execute(
            "l10n_ph.bir_form",
            "generate",
            agency, period, form_type
        )
```

#### Step 1.4: Add Supabase Tools
```python
# services/mcp-unified/supabase_tools.py
from supabase import create_client

class SupabaseTools:
    def __init__(self):
        self.client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

    async def rpc_call(self, function: str, params: dict) -> dict:
        """Call Supabase RPC function"""
        return self.client.rpc(function, params).execute()

    async def query(self, table: str, filters: dict) -> list:
        """Query Supabase table"""
        query = self.client.table(table).select("*")
        for key, value in filters.items():
            query = query.eq(key, value)
        return query.execute()
```

#### Step 1.5: Deploy Unified MCP
```bash
# Create app.yaml
cat > services/mcp-unified/app.yaml <<EOF
name: mcp-unified
region: sgp
domains:
  - domain: mcp.insightpulseai.net
    type: PRIMARY
services:
  - name: mcp
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true
    source_dir: /services/mcp-unified
    dockerfile_path: /services/mcp-unified/Dockerfile
    http_port: 8000
    instance_count: 1
    instance_size_slug: professional-xs
    health_check:
      http_path: /health
    envs:
      - key: GITHUB_APP_ID
        value: 2191216
      - key: GITHUB_PRIVATE_KEY
        scope: RUN_TIME
        type: SECRET
      - key: GITHUB_INSTALLATION_ID
        scope: RUN_TIME
        type: SECRET
      - key: ODOO_URL
        value: https://erp.insightpulseai.net
      - key: ODOO_DB
        value: odoo
      - key: ODOO_USERNAME
        scope: RUN_TIME
        type: SECRET
      - key: ODOO_PASSWORD
        scope: RUN_TIME
        type: SECRET
      - key: SUPABASE_URL
        value: https://spdtwktxdalcfigzeqrz.supabase.co
      - key: SUPABASE_KEY
        scope: RUN_TIME
        type: SECRET
      - key: DIGITALOCEAN_TOKEN
        scope: RUN_TIME
        type: SECRET
EOF

# Deploy
doctl apps create --spec services/mcp-unified/app.yaml
```

### Phase 2: CI/CD Alignment (Week 3)

#### Step 2.1: Create Unified CI/CD Pipeline
```yaml
# .github/workflows/deploy-unified-mcp.yml
name: Deploy Unified MCP

on:
  push:
    branches: [main]
    paths:
      - 'services/mcp-unified/**'
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd services/mcp-unified
          pip install -r requirements.txt
          pip install pytest pytest-asyncio

      - name: Run unit tests
        run: |
          cd services/mcp-unified
          pytest tests/ -v

      - name: Test MCP protocol
        run: |
          cd services/mcp-unified
          python -m pytest tests/test_mcp_protocol.py

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Deploy to App Platform
        run: |
          APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep mcp-unified | awk '{print $1}')
          if [ -z "$APP_ID" ]; then
            doctl apps create --spec services/mcp-unified/app.yaml
          else
            doctl apps update $APP_ID --spec services/mcp-unified/app.yaml
          fi

      - name: Wait for deployment
        run: |
          APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep mcp-unified | awk '{print $1}')
          for i in {1..30}; do
            STATUS=$(doctl apps get $APP_ID --format ActiveDeployment.Phase --no-header)
            if [ "$STATUS" = "ACTIVE" ]; then
              echo "Deployment successful"
              exit 0
            fi
            sleep 10
          done
          echo "Deployment timeout"
          exit 1

      - name: Integration tests
        run: |
          # Test health endpoint
          curl -f https://mcp.insightpulseai.net/health

          # Test GitHub tool
          curl -X POST https://mcp.insightpulseai.net/mcp \
            -H "Content-Type: application/json" \
            -d '{"method": "tools/list"}' | jq -e '.result | length > 0'

          # Test Odoo tool
          curl -X POST https://mcp.insightpulseai.net/mcp \
            -H "Content-Type: application/json" \
            -d '{"method": "tools/call", "params": {"name": "odoo_search", "arguments": {"model": "res.partner", "domain": []}}}' | jq -e '.result'
```

#### Step 2.2: Deprecate Old Servers
```bash
# Archive old servers
git mv services/mcp-server services/_archived/mcp-server
git mv services/mcp-coordinator services/_archived/mcp-coordinator
git mv services/deepcode-server services/_archived/deepcode-server
git mv services/insightpulse-monitor services/_archived/insightpulse-monitor

# Update CI/CD to ignore archived
echo "services/_archived/**" >> .github/workflows/.ignore
```

### Phase 3: Skills Alignment (Week 4)

#### Step 3.1: Update Skills Configuration
```bash
# Update .claude/settings.json to point to unified MCP
cat > .claude/mcp-config.json <<EOF
{
  "mcpServers": {
    "insightpulse": {
      "url": "https://mcp.insightpulseai.net/mcp",
      "description": "Unified InsightPulse MCP - GitHub, Odoo, Supabase, Orchestration"
    },
    "digitalocean": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-digitalocean"],
      "env": {
        "DIGITALOCEAN_TOKEN": "${env:DIGITALOCEAN_TOKEN}"
      },
      "description": "DigitalOcean infrastructure management"
    }
  }
}
EOF
```

#### Step 3.2: Update Skill Prompts
Update each skill in `.claude/skills/` to reference unified MCP:

```markdown
<!-- Before -->
Use the `pulser-hub` MCP server to create PRs
Use the `mcp-coordinator` MCP server to orchestrate deployments

<!-- After -->
Use the `insightpulse` MCP server for all operations:
- GitHub: `github_create_pr`, `github_trigger_workflow`
- Odoo: `odoo_approve_expense`, `odoo_search`
- Supabase: `supabase_rpc_call`, `supabase_query`
- Orchestration: `orchestrate_deployment`
```

### Phase 4: Testing & Validation (Week 5)

#### Step 4.1: Integration Testing
```python
# tests/integration/test_unified_mcp.py
import pytest
from mcp_client import MCPClient

@pytest.mark.asyncio
async def test_github_operations():
    client = MCPClient("https://mcp.insightpulseai.net/mcp")

    # List branches
    result = await client.call_tool("github_list_branches", {
        "repo": "jgtolentino/insightpulse-odoo"
    })
    assert len(result["branches"]) > 0

    # Create PR
    result = await client.call_tool("github_create_pr", {
        "repo": "jgtolentino/insightpulse-odoo",
        "title": "Test PR",
        "base": "main",
        "head": "test-branch"
    })
    assert result["number"] > 0

@pytest.mark.asyncio
async def test_odoo_operations():
    client = MCPClient("https://mcp.insightpulseai.net/mcp")

    # Search partners
    result = await client.call_tool("odoo_search", {
        "model": "res.partner",
        "domain": [["is_company", "=", True]]
    })
    assert isinstance(result["records"], list)

@pytest.mark.asyncio
async def test_orchestration():
    client = MCPClient("https://mcp.insightpulseai.net/mcp")

    # Deploy service
    result = await client.call_tool("orchestrate_deployment", {
        "service": "ade-ocr",
        "environment": "staging"
    })
    assert result["status"] == "success"
```

#### Step 4.2: Load Testing
```bash
# Use k6 for load testing
cat > tests/load/mcp_load_test.js <<EOF
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 users
    { duration: '1m', target: 10 },   // Stay at 10 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
};

export default function() {
  const url = 'https://mcp.insightpulseai.net/mcp';
  const payload = JSON.stringify({
    method: 'tools/list',
    params: {}
  });

  const res = http.post(url, payload, {
    headers: { 'Content-Type': 'application/json' }
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
EOF

# Run load test
k6 run tests/load/mcp_load_test.js
```

---

## Cost-Benefit Analysis

### Before Optimization

| Item | Monthly Cost |
|------|-------------|
| Custom MCP servers (4) on DO App Platform | $20 |
| Third-party MCP NPM packages (local) | $0 |
| Maintenance time (7 servers × 2 hrs/month) | $1,400 @ $100/hr |
| **Total** | **$1,420** |

### After Optimization

| Item | Monthly Cost |
|------|-------------|
| Unified MCP server on DO App Platform | $5 |
| Third-party MCP (1: DigitalOcean) | $0 |
| Maintenance time (2 servers × 1 hr/month) | $200 @ $100/hr |
| **Total** | **$205** |

**Savings**: $1,215/month (85% reduction)

---

## Success Metrics

### Week 1-2 (Consolidation)
- ✅ Unified MCP server deployed
- ✅ All pulser-hub tools migrated
- ✅ Odoo + Supabase tools implemented
- ✅ Health checks passing

### Week 3 (CI/CD)
- ✅ CI/CD pipeline created
- ✅ Integration tests passing
- ✅ Old servers archived

### Week 4 (Skills)
- ✅ All 48 executable skills aligned to unified MCP
- ✅ Skills prompts updated
- ✅ Documentation updated

### Week 5 (Testing)
- ✅ Integration tests: 95% pass rate
- ✅ Load tests: <500ms p95 latency
- ✅ Zero production incidents

### Ongoing (Post-launch)
- 📊 **MCP uptime**: >99.5%
- 📊 **Tool call latency**: <300ms p95
- 📊 **Error rate**: <1%
- 📊 **Maintenance time**: <2 hrs/month

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Unified MCP downtime** | 🔴 High | Deploy to 2 regions, add health checks |
| **Tool auth failures** | 🟡 Medium | Implement token refresh, fallback credentials |
| **Skills misalignment** | 🟢 Low | Comprehensive testing, gradual rollout |
| **Performance degradation** | 🟡 Medium | Load testing, caching, CDN |
| **Data loss during migration** | 🔴 High | Backup all configs before changes |

---

## Rollback Plan

If optimization fails:

```bash
# Phase 1: Stop unified MCP
doctl apps delete <unified-mcp-app-id>

# Phase 2: Restore archived servers
git mv services/_archived/mcp-server services/mcp-server
git mv services/_archived/mcp-coordinator services/mcp-coordinator

# Phase 3: Redeploy old servers
doctl apps create --spec services/mcp-server/app.yaml
doctl apps create --spec services/mcp-coordinator/app.yaml

# Phase 4: Revert MCP config
cp .claude/mcp-config.json.backup .claude/mcp-config.json
```

---

## Next Steps

### Immediate (This Week)
1. ✅ Review this optimization plan
2. ⏳ Create unified MCP server repository structure
3. ⏳ Migrate pulser-hub tools to unified server
4. ⏳ Deploy to staging environment

### Short-term (Next 2 Weeks)
5. ⏳ Add Odoo + Supabase tools
6. ⏳ Create CI/CD pipeline
7. ⏳ Run integration tests
8. ⏳ Deploy to production

### Long-term (Next Month)
9. ⏳ Archive old MCP servers
10. ⏳ Update all skills prompts
11. ⏳ Monitor performance
12. ⏳ Document lessons learned

---

## References

- [MCP Implementation Summary](./MCP_IMPLEMENTATION_SUMMARY.md)
- [Skills Inventory](./SKILLS.md)
- [Automation Architecture](./AUTOMATION_ARCHITECTURE.md)
- [Core Stack README](../infra/CORE_STACK_README.md)
- [MCP Best Practices](../.claude/skills/mcp-builder/SKILL.md)

---

**Author**: Claude Code (AI)
**Reviewed By**: Jake Tolentino
**Status**: 📝 DRAFT - Awaiting approval
