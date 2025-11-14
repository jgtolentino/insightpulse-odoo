# Multi-Agent Orchestrator Architecture

## Overview

The InsightPulse Odoo Multi-Agent Orchestrator is a **hybrid architecture** that combines:
- **Managed Orchestrator**: DigitalOcean AI Agent (https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run)
- **Specialist Services**: Self-hosted FastAPI microservices on DO App Platform
- **Knowledge Base**: Supabase PostgreSQL with pgvector for RAG

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│          Master Orchestrator (DO AI Agent)                   │
│  https://agent.insightpulseai.net                           │
│  (CNAME → wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run)        │
│                                                              │
│  Model: Claude Sonnet 4.5                                   │
│  Tools: 31 (27 native + 4 routing tools)                    │
│  Knowledge Base: Supabase pgvector (agent-specific)         │
└─────────────────────┬───────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┬───────────────┐
      ▼               ▼               ▼               ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│  odoo_    │  │ finance_  │  │    bi_    │  │  devops_  │
│ developer │  │ ssc_expert│  │ architect │  │ engineer  │
│  (API)    │  │   (API)   │  │   (API)   │  │   (API)   │
│           │  │           │  │           │  │           │
│  FastAPI  │  │  FastAPI  │  │  FastAPI  │  │  FastAPI  │
│  Port:8080│  │  Port:8080│  │  Port:8080│  │  Port:8080│
│  $5/mo    │  │  $5/mo    │  │  $5/mo    │  │  $5/mo    │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │              │
      └──────────────┴──────────────┴──────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │   Supabase   │ │ MCP Servers  │ │  Odoo ERP   │
      │  PostgreSQL  │ │  (10 total)  │ │ (RPC/API)   │
      │  (pgvector)  │ │              │ │             │
      └──────────────┘ └──────────────┘ └──────────────┘
```

## Components

### 1. Master Orchestrator (DO AI Agent)

**URL**: https://agent.insightpulseai.net (CNAME to DO AI Agent URL)

**Responsibilities**:
- Receive user queries
- Analyze intent and route to appropriate specialist
- Synthesize responses from multiple specialists
- Maintain conversation context and session state
- Coordinate multi-agent workflows

**Native Tools** (27 existing):
- BIR compliance queries
- Tax calculation
- OCR processing
- Database queries (Supabase)
- Vector search (pgvector)
- Odoo ERP integration
- File operations
- Web search

**Routing Tools** (4 new):
1. `route_to_odoo_developer` - Odoo development tasks
2. `route_to_finance_ssc_expert` - BIR compliance, tax filing
3. `route_to_bi_architect` - Dashboard design, SQL optimization
4. `route_to_devops_engineer` - Deployment, infrastructure

**Knowledge Base**:
- Agent-specific embeddings in `scout.agent_domain_embeddings`
- Shared knowledge base in existing `scout.bir_documents`
- Vector similarity search with 0.7 threshold

### 2. Specialist Services

#### odoo_developer Agent
**URL**: https://odoo-developer-agent.ondigitalocean.app

**Expertise**:
- Odoo 19.0 Enterprise module development
- OCA (Odoo Community Association) compliance
- Python 3.11+ with type hints
- PostgreSQL ORM modeling
- XML view development
- Security (RLS, access rules)

**Triggers**: odoo module, scaffold, model, view, workflow, automation

**Knowledge Base**: OCA guidelines, Odoo 19 documentation, module patterns

#### finance_ssc_expert Agent
**URL**: https://finance-ssc-expert.ondigitalocean.app

**Expertise**:
- Philippine BIR regulations (Forms 1601-C, 1702-RT, 2550Q, 2307, 0605)
- Multi-agency finance SSC operations
- Month-end close procedures
- Expense approval workflows
- Vendor payment processing

**Triggers**: bir, 1601-c, 2550q, tax, withholding, month-end, agency

**Knowledge Base**: BIR regulations, tax forms, compliance deadlines

#### bi_architect Agent
**URL**: https://bi-architect.ondigitalocean.app

**Expertise**:
- Apache Superset 3.0 dashboard design
- SQL query optimization (PostgreSQL)
- Data modeling (star schema, snowflake)
- Row-Level Security (RLS) policies
- Data visualization best practices

**Triggers**: superset, dashboard, chart, sql, query, analytics, visualization

**Knowledge Base**: Superset documentation, SQL patterns, RLS examples

#### devops_engineer Agent
**URL**: https://devops-engineer.ondigitalocean.app

**Expertise**:
- DigitalOcean App Platform deployments
- Docker containerization
- GitHub Actions CI/CD
- Deployment automation (doctl CLI)
- Monitoring and observability

**Triggers**: deploy, infrastructure, ci/cd, docker, digitalocean, pipeline

**Knowledge Base**: DO App Platform docs, deployment patterns, CI/CD workflows

### 3. Knowledge Base Layer

**Database**: Supabase PostgreSQL (spdtwktxdalcfigzeqrz)

**Schema**: `scout.agent_domain_embeddings`
```sql
CREATE TABLE scout.agent_domain_embeddings (
    id UUID PRIMARY KEY,
    agent_domain TEXT NOT NULL,  -- Which specialist agent
    content_type TEXT NOT NULL,  -- Document classification
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),      -- OpenAI text-embedding-3-small
    metadata JSONB,
    source_url TEXT,
    indexed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

**Embedding Model**: OpenAI `text-embedding-3-small` (1536 dimensions)

**Search Functions**:
- `scout.search_agent_knowledge(agent_domain, query_embedding, threshold, count)` - Agent-specific search
- `scout.search_all_agent_knowledge(query_embedding, threshold, count)` - Cross-agent search

**Indexing**: Run `scripts/index_agent_knowledge.py` to populate embeddings

## Request Flow

### Single-Agent Request
```
1. User → "Create Odoo module for expense reports"
2. Orchestrator → Analyze intent → route_to_odoo_developer
3. odoo_developer API → Claude Sonnet 4.5 with specialist system prompt
4. Claude → Generate OCA-compliant module structure
5. odoo_developer API → Return response with code artifacts
6. Orchestrator → Synthesize final response
7. User ← Complete implementation guidance
```

### Multi-Agent Request
```
1. User → "Create Odoo module and deploy to staging"
2. Orchestrator → Analyze intent → Requires 2 agents
3a. route_to_odoo_developer → Create module
3b. route_to_devops_engineer → Wait for module creation
4. odoo_developer → Returns module structure
5. devops_engineer → Create deployment spec using module context
6. Orchestrator → Synthesize responses from both agents
7. User ← Complete workflow (module + deployment instructions)
```

## Cost Structure

| Component | Monthly Cost | Notes |
|-----------|--------------|-------|
| DO AI Agent (Orchestrator) | $5-10 | Usage-based (Claude API calls) |
| odoo_developer (basic-xxs) | $5 | App Platform service |
| finance_ssc_expert (basic-xxs) | $5 | App Platform service |
| bi_architect (basic-xxs) | $5 | App Platform service |
| devops_engineer (basic-xxs) | $5 | App Platform service |
| Supabase PostgreSQL | $0 | Free tier (up to 500MB) |
| OpenAI Embeddings | ~$2 | text-embedding-3-small ($0.02/1M tokens) |
| **TOTAL** | **$27-32/month** | 80x ROI ($2,000/month automation savings) |

## Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Response Time (P95) | <3 seconds | User experience requirement |
| Cost per Query | <$0.10 USD | Economic viability |
| Error Rate | <1% | Reliability requirement |
| Uptime | 99.9% | Business continuity (8.7h/year downtime) |
| Routing Accuracy | >95% | Correct specialist selection |

## Deployment Strategy

See `docs/DEPLOYMENT_GUIDE.md` for step-by-step deployment instructions.

**Phases**:
1. **Week 1-2**: Design validation (this phase - no deployment)
2. **Week 3**: Deploy specialist services to DO App Platform
3. **Week 4**: Upgrade orchestrator with routing tools, staged rollout (25% → 50% → 100%)

## Rollback Procedure

See `docs/ROLLBACK_PROCEDURE.md` for detailed rollback steps.

**Quick Rollback** (<5 minutes):
1. Revert DNS: `agent.insightpulseai.net` → old DO AI Agent URL
2. Pause specialist services (don't delete)
3. Verify old orchestrator is serving traffic

## Security

**Authentication**:
- Orchestrator → Specialist: Optional `X-Orchestrator-Key` header (production only)
- Specialist → Claude API: `ANTHROPIC_API_KEY` (DO secret)
- Specialist → Supabase: `SUPABASE_SERVICE_ROLE_KEY` (DO secret)

**Secrets Management**:
- All secrets stored as DO App Platform environment variables
- Never hardcoded in code or committed to git
- Masked in logs and error messages

**Network Security**:
- All communication over HTTPS
- Specialists only accept requests from orchestrator (optional firewall rule)
- Supabase RLS policies enforce data access control

## Monitoring & Observability

**Health Checks**:
- All specialists expose `/health` endpoint
- DO App Platform monitors health every 30 seconds
- Auto-restart on 3 consecutive failures

**Metrics**:
- Response times (P50, P95, P99)
- Error rates by specialist
- Cost per query
- Routing accuracy

**Logging**:
- Structured JSON logs to DO App Platform
- Supabase audit trail for all agent operations
- Claude API usage tracking

## Future Enhancements

1. **Agent Caching**: Cache frequent queries to reduce API costs
2. **Agent Learning**: Improve routing accuracy based on success metrics
3. **Agent Scaling**: Add more specialists (diagram_designer, document_creator)
4. **Agent Parallelization**: Coordinate multiple specialists simultaneously
5. **Agent Versioning**: A/B test new specialist versions before full rollout
