# Multi-Agent Orchestrator Deployment Guide

## Prerequisites

### Required Tools
```bash
# DigitalOcean CLI
brew install doctl
doctl auth init

# GitHub CLI (for repository operations)
brew install gh
gh auth login

# PostgreSQL client (for Supabase migrations)
brew install postgresql
```

### Required Credentials
```bash
# DigitalOcean
export DO_ACCESS_TOKEN=<your-token>

# Anthropic (Claude API)
export ANTHROPIC_API_KEY=<your-api-key>

# Supabase
export SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
export SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
export POSTGRES_URL=<your-connection-pooler-url>

# OpenAI (for embeddings)
export OPENAI_API_KEY=<your-api-key>

# GitHub
export GITHUB_TOKEN=<your-github-token>
```

## Phase 1: DNS Configuration

### Step 1: Create Custom Domain
```bash
# Create CNAME record for agent.insightpulseai.net
./scripts/setup-dns.sh wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run

# Verify DNS propagation (may take 5-30 minutes)
dig agent.insightpulseai.net
nslookup agent.insightpulseai.net

# Test endpoint (once propagated)
curl https://agent.insightpulseai.net/health
```

**Expected output**:
```json
{
  "status": "ok",
  "agent": "orchestrator",
  "version": "3.0.0"
}
```

## Phase 2: Deploy Specialist Services

### Step 2: Deploy odoo_developer Agent
```bash
# Validate spec file
doctl apps spec validate infra/do/odoo-developer-agent.yaml

# Deploy service
./scripts/deploy-specialist.sh odoo-developer-agent

# Verify deployment
curl https://odoo-developer-agent.ondigitalocean.app/health
curl https://odoo-developer-agent.ondigitalocean.app/capabilities
```

**Expected output** (health):
```json
{
  "status": "ok",
  "agent": "odoo_developer",
  "version": "1.0.0",
  "model": "claude-sonnet-4-5-20250929",
  "uptime": "Managed by DigitalOcean App Platform"
}
```

**Expected output** (capabilities):
```json
{
  "agent_name": "odoo_developer",
  "specialization": "Odoo 18 CE Enterprise module development",
  "standards": ["OCA compliance", "AGPL-3.0", "PEP8", "Type hints"],
  "capabilities": [
    "Module scaffolding",
    "Model creation (PostgreSQL ORM)",
    "View development (XML)",
    "Security configuration (RLS, access rules)",
    "Workflow automation",
    "API integration",
    "Testing strategy",
    "Deployment guidance"
  ],
  "triggers": ["odoo module", "scaffold", "model", "view", "workflow", "automation", "manifest.py"]
}
```

### Step 3: Deploy finance_ssc_expert Agent
```bash
./scripts/deploy-specialist.sh finance-ssc-expert

# Verify
curl https://finance-ssc-expert.ondigitalocean.app/health
curl https://finance-ssc-expert.ondigitalocean.app/capabilities
```

### Step 4: Deploy bi_architect Agent
```bash
./scripts/deploy-specialist.sh bi-architect

# Verify
curl https://bi-architect.ondigitalocean.app/health
curl https://bi-architect.ondigitalocean.app/capabilities
```

### Step 5: Deploy devops_engineer Agent
```bash
./scripts/deploy-specialist.sh devops-engineer

# Verify
curl https://devops-engineer.ondigitalocean.app/health
curl https://devops-engineer.ondigitalocean.app/capabilities
```

## Phase 3: Knowledge Base Setup

### Step 6: Apply Database Migrations
```bash
# Apply agent domain embeddings schema
psql "$POSTGRES_URL" -f packages/db/sql/05_agent_domain_embeddings.sql

# Verify tables created
psql "$POSTGRES_URL" -c "\dt scout.agent_domain_embeddings"
psql "$POSTGRES_URL" -c "SELECT * FROM scout.agent_knowledge_stats;"
```

**Expected output**:
```
                                    Table "scout.agent_domain_embeddings"
     Column      |           Type            | Collation | Nullable |      Default
-----------------+---------------------------+-----------+----------+-------------------
 id              | uuid                      |           | not null | gen_random_uuid()
 agent_domain    | text                      |           | not null |
 content_type    | text                      |           | not null |
 title           | text                      |           | not null |
 content         | text                      |           | not null |
 embedding       | vector(1536)              |           |          |
 metadata        | jsonb                     |           |          | '{}'::jsonb
 source_url      | text                      |           |          |
 indexed_at      | timestamp with time zone  |           |          | now()
 updated_at      | timestamp with time zone  |           |          | now()
```

### Step 7: Index Agent Knowledge
```bash
# Create sample knowledge base directories
mkdir -p knowledge/{odoo,bir,superset,devops}

# Index Odoo documentation (example with sample data)
./scripts/index_agent_knowledge.py \
  --source knowledge/odoo/ \
  --agent odoo_developer \
  --content-type oca_guideline

# Index BIR regulations
./scripts/index_agent_knowledge.py \
  --source knowledge/bir/ \
  --agent finance_ssc_expert \
  --content-type bir_regulation

# Index Superset documentation
./scripts/index_agent_knowledge.py \
  --source knowledge/superset/ \
  --agent bi_architect \
  --content-type superset_doc

# Index DevOps documentation
./scripts/index_agent_knowledge.py \
  --source knowledge/devops/ \
  --agent devops_engineer \
  --content-type infra_doc

# Verify embeddings
psql "$POSTGRES_URL" -c "SELECT * FROM scout.agent_knowledge_stats;"
```

**Expected output**:
```
  agent_domain   | content_type  | document_count | last_indexed | months_active
-----------------+---------------+----------------+--------------+---------------
 odoo_developer  | oca_guideline |             15 | 2025-11-15   |             1
 finance_ssc_expert | bir_regulation |          25 | 2025-11-15   |             1
 bi_architect    | superset_doc  |             12 | 2025-11-15   |             1
 devops_engineer | infra_doc     |             18 | 2025-11-15   |             1
```

## Phase 4: Orchestrator Upgrade

### Step 8: Add Routing Tools to DO AI Agent

**Via DO AI Agent Platform UI**:
1. Navigate to https://cloud.digitalocean.com/ai
2. Select your AI Agent (wr2azp5dsl6mu6xvxtpglk5v)
3. Go to "Tools" section
4. Add the following 4 routing tools:

**Tool 1: route_to_odoo_developer**
```json
{
  "name": "route_to_odoo_developer",
  "description": "Route Odoo 18 CE module development tasks to specialized agent. Use for: module creation, OCA compliance, Python models, XML views, security configuration, workflow automation.",
  "parameters": {
    "type": "object",
    "properties": {
      "task": {
        "type": "string",
        "description": "Task description for Odoo development"
      },
      "context": {
        "type": "object",
        "description": "Additional context (agency, module_name, dependencies)"
      }
    },
    "required": ["task"]
  },
  "endpoint": {
    "url": "https://odoo-developer-agent.ondigitalocean.app/execute",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

**Tool 2: route_to_finance_ssc_expert**
```json
{
  "name": "route_to_finance_ssc_expert",
  "description": "Route BIR compliance and tax filing tasks to specialized agent. Use for: Forms 1601-C, 1702-RT, 2550Q, 2307, 0605, month-end close, multi-agency consolidation.",
  "parameters": {
    "type": "object",
    "properties": {
      "task": {
        "type": "string",
        "description": "Task description for BIR compliance or finance SSC"
      },
      "context": {
        "type": "object",
        "description": "Additional context (period, agency, form_type)"
      }
    },
    "required": ["task"]
  },
  "endpoint": {
    "url": "https://finance-ssc-expert.ondigitalocean.app/execute",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

**Tool 3: route_to_bi_architect**
```json
{
  "name": "route_to_bi_architect",
  "description": "Route dashboard design and SQL optimization tasks to specialized agent. Use for: Superset dashboards, chart creation, SQL queries, RLS policies, data modeling.",
  "parameters": {
    "type": "object",
    "properties": {
      "task": {
        "type": "string",
        "description": "Task description for BI or analytics"
      },
      "context": {
        "type": "object",
        "description": "Additional context (dashboard_type, data_source)"
      }
    },
    "required": ["task"]
  },
  "endpoint": {
    "url": "https://bi-architect.ondigitalocean.app/execute",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

**Tool 4: route_to_devops_engineer**
```json
{
  "name": "route_to_devops_engineer",
  "description": "Route deployment and infrastructure tasks to specialized agent. Use for: DO App Platform deployments, Docker containerization, CI/CD pipelines, infrastructure automation.",
  "parameters": {
    "type": "object",
    "properties": {
      "task": {
        "type": "string",
        "description": "Task description for DevOps or deployment"
      },
      "context": {
        "type": "object",
        "description": "Additional context (service_name, environment)"
      }
    },
    "required": ["task"]
  },
  "endpoint": {
    "url": "https://devops-engineer.ondigitalocean.app/execute",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

### Step 9: Update Orchestrator System Prompt

**Add to DO AI Agent system prompt** (via Platform UI):
```
## Multi-Agent Orchestration

You have access to 4 specialist agents via routing tools:

1. **route_to_odoo_developer** - Odoo 18 CE module development, OCA compliance
   - Triggers: odoo module, scaffold, model, view, workflow, automation

2. **route_to_finance_ssc_expert** - BIR compliance, tax filing, multi-agency finance
   - Triggers: bir, 1601-c, 2550q, tax, withholding, month-end, agency

3. **route_to_bi_architect** - Superset dashboards, SQL optimization, data modeling
   - Triggers: superset, dashboard, chart, sql, query, analytics

4. **route_to_devops_engineer** - DO App Platform deployments, CI/CD, infrastructure
   - Triggers: deploy, infrastructure, ci/cd, docker, pipeline

**Routing Strategy**:
- Analyze user query for trigger keywords
- Route to specialist when domain expertise required
- Synthesize specialist responses for final answer
- Coordinate multiple specialists for complex workflows

**Multi-Agent Coordination**:
- Sequential: odoo_developer → devops_engineer (create then deploy)
- Parallel: finance_ssc_expert + bi_architect (analyze and visualize)
- Iterative: Multiple specialist calls for refinement
```

## Phase 5: Testing & Validation

### Step 10: Run Integration Tests
```bash
# Install test dependencies
pip install pytest requests

# Run all integration tests
python scripts/test-orchestrator.py

# Run pytest suite
cd tests/integration
pytest test_multi_agent_routing.py -v
```

**Expected output**:
```
=== Multi-Agent Orchestrator Integration Tests ===

Testing health endpoints...
  ✓ odoo_developer_health: Health check passed (model: claude-sonnet-4-5-20250929) (0.15s)
  ✓ finance_ssc_expert_health: Health check passed (model: claude-sonnet-4-5-20250929) (0.13s)
  ✓ bi_architect_health: Health check passed (model: claude-sonnet-4-5-20250929) (0.14s)
  ✓ devops_engineer_health: Health check passed (model: claude-sonnet-4-5-20250929) (0.12s)

Testing capabilities endpoints...
  ✓ odoo_developer_capabilities: Capabilities: 8 items (0.11s)
  ✓ finance_ssc_expert_capabilities: Capabilities: 7 items (0.10s)
  ✓ bi_architect_capabilities: Capabilities: 5 items (0.09s)
  ✓ devops_engineer_capabilities: Capabilities: 5 items (0.08s)

Testing specialist execution...
  ✓ odoo_developer_execution: Execution successful (confidence: 0.95, keywords: 3/3) (2.34s)
  ✓ finance_ssc_expert_execution: Execution successful (confidence: 0.98, keywords: 3/3) (1.89s)
  ✓ bi_architect_execution: Execution successful (confidence: 0.93, keywords: 3/4) (2.15s)
  ✓ devops_engineer_execution: Execution successful (confidence: 0.92, keywords: 3/4) (1.97s)

=== Test Summary ===
Total: 12
Passed: 12
Failed: 0

All tests passed! ✓
```

### Step 11: Manual Testing
```bash
# Test single-agent routing (via DO AI Agent UI or API)
curl -X POST https://agent.insightpulseai.net/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create an Odoo module for tracking employee leave requests",
    "conversation_id": "test_001"
  }'

# Expected: Orchestrator routes to odoo_developer, returns OCA-compliant module structure

# Test multi-agent coordination
curl -X POST https://agent.insightpulseai.net/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create an Odoo module for expense tracking and deploy it to staging",
    "conversation_id": "test_002"
  }'

# Expected: Orchestrator coordinates odoo_developer + devops_engineer
```

## Phase 6: Staged Rollout

### Step 12: Canary Deployment (25% Traffic)
```bash
# Not applicable for DO AI Agent (no traffic splitting)
# Manual testing with subset of users instead

# Monitor for 2-3 days:
# - Response times
# - Error rates
# - User feedback
# - Cost per query
```

### Step 13: Increase to 50% Traffic
```bash
# Continue monitoring for 2-3 days
# Compare metrics vs. baseline
```

### Step 14: Full Cutover (100% Traffic)
```bash
# Full production deployment
# All users now use multi-agent orchestrator
# Monitor for 7 days before declaring success
```

## Quality Gates Checklist

Before each phase, verify:

- [ ] All health endpoints return 200 OK
- [ ] All capabilities endpoints return valid JSON
- [ ] P95 response time < 3 seconds
- [ ] Error rate < 1%
- [ ] Cost per query < $0.10 USD
- [ ] Routing accuracy > 95%
- [ ] Knowledge base has >50 embeddings per agent
- [ ] All secrets properly configured in DO App Platform
- [ ] DNS propagation complete (agent.insightpulseai.net)
- [ ] Integration tests pass 100%

## Rollback Procedure

If any quality gate fails, see `docs/ROLLBACK_PROCEDURE.md` for detailed rollback instructions.

**Quick rollback** (<5 minutes):
```bash
# Revert DNS
./scripts/setup-dns.sh wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run

# Pause specialist services (don't delete)
doctl apps update <odoo-developer-app-id> --pause
doctl apps update <finance-ssc-expert-app-id> --pause
doctl apps update <bi-architect-app-id> --pause
doctl apps update <devops-engineer-app-id> --pause

# Verify old orchestrator serving traffic
curl https://agent.insightpulseai.net/health
```

## Post-Deployment

### Monitoring Setup
```bash
# Set up DO alerts for each specialist service
# - Deployment failures
# - High error rates (>5%)
# - High response times (>5s P95)

# Set up cost alerts
# - Weekly budget: $10
# - Monthly budget: $35
```

### Continuous Improvement
- Review routing accuracy weekly
- Expand knowledge base with new documentation
- Add new specialists as needed (diagram_designer, document_creator)
- Optimize specialist prompts based on user feedback
- A/B test different routing strategies
