# InsightPulse AI Infrastructure Documentation

**Last Updated:** 2025-11-09
**Environment:** Production
**Project:** fin-workspace (DigitalOcean)

---

## Production Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DigitalOcean fin-workspace                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  AI Services Layer                                               │
│  ├─ Agent Gateway (Claude 3.5 Sonnet + 13 tools)               │
│  │  └─ https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run      │
│  │                                                               │
│  ├─ OCR Service (PaddleOCR-VL + OpenAI)                        │
│  │  └─ 188.166.237.231 (Singapore SGP1)                        │
│  │  └─ Docker on 8GB/80GB Droplet                              │
│  │                                                               │
│  ├─ MCP Coordinator                                             │
│  │  └─ https://mcp.insightpulseai.net                          │
│  │                                                               │
│  └─ Superset Analytics                                          │
│     └─ https://superset.insightpulseai.net                      │
│                                                                  │
│  ERP Layer                                                       │
│  ├─ Odoo ERP (Main Production)                                 │
│  │  └─ https://erp.insightpulseai.net                          │
│  │  └─ 165.227.10.178 (San Francisco SFO2)                     │
│  │  └─ 4GB RAM / 120GB Disk                                    │
│  │                                                               │
│  └─ ODOO SaaS Platform                                          │
│     └─ App deployed (URL not yet configured)                    │
│                                                                  │
│  Domains                                                         │
│  └─ erp.insightpulseai.net (1 A record, 3 NS, 1 SOA)           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Service Details

### 1. Agent Gateway (AI Agent Service)

**URL:** `https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run`
**Model:** Claude 3.5 Sonnet
**Tools:** 13 specialized tools
**Purpose:** BIR tax compliance Q&A, document understanding, PH tax regulations

**Capabilities:**
- Philippine BIR tax question answering (Forms 1601-C, 1702-RT, 2550Q, 2550M)
- Revenue Memorandum Circular (RMC) citation retrieval
- Tax calendar and deadline queries
- Withholding tax calculations
- VAT compliance verification

**Knowledge Base Storage:**
- **Vector Embeddings:** Supabase pgvector extension on PostgreSQL 15
- **Database:** `postgres.spdtwktxdalcfigzeqrz` (Supabase SpendFlow project)
- **Schema:** `scout.bir_documents` table with embeddings column
- **Embedding Model:** OpenAI text-embedding-3-small (1536 dimensions)
- **RAG Pipeline:** pgvector similarity search → LLM synthesis → citation tracking

**Usage in Workflows:**
- PH Tax Compliance Canary (`ph-tax-canary.yml`)
- Monthly BIR filing automation
- Real-time tax guidance for Finance SSC teams

---

### 2. OCR Service (Document Intelligence)

**Host:** `188.166.237.231` (Singapore SGP1)
**Instance:** 8GB RAM / 80GB Disk Docker Droplet
**Stack:** PaddleOCR-VL-900M + OpenAI GPT-4o-mini

**Endpoints:**
- `POST /v1/parse` - Receipt/invoice OCR with structured extraction
- `POST /classify/expense` - Expense category classification
- `GET /health` - Service health check

**Purpose:**
- Expense receipt OCR for automatic data extraction
- Invoice processing for AP automation
- BIR form field extraction (2307, 2316, 1601-C)

**Knowledge Base Storage:**
- **Training Data:** DigitalOcean Spaces object storage
- **Model Artifacts:** Docker volume on droplet
- **OCR Results Cache:** Supabase `scout.ocr_results` table
- **Confidence Scores:** Stored with each extraction for validation

**Performance:**
- P95 latency: <30 seconds
- Auto-approval rate: ≥85% (confidence ≥0.60)
- Supported formats: JPG, PNG, PDF

---

### 3. MCP Coordinator

**URL:** `https://mcp.insightpulseai.net`
**Purpose:** Model Context Protocol orchestration for multi-agent workflows

**Registered MCP Servers:**
- **pulser-hub** - Odoo & ecosystem integration (5 tools)
- **digitalocean** - App Platform management (3 tools)
- **kubernetes** - Cluster operations (22 tools)
- **docker** - Container management (1 tool)
- **github** - Repository operations (40 tools)
- **superset** - Analytics & dashboards (3+ tools)

**Total Tools:** 98 across 7 MCP servers

**Usage:**
- Cross-service orchestration
- Agent coordination for complex workflows
- Tool routing based on task requirements

---

### 4. Superset Analytics

**URL:** `https://superset.insightpulseai.net`
**Purpose:** Business intelligence and data visualization (Tableau replacement)

**Features:**
- Real-time dashboards for Scout transaction data
- SQL execution against Supabase PostgreSQL
- Chart creation (10+ visualization types)
- Row-Level Security (RLS) for multi-tenant access

**Data Sources:**
- Supabase SpendFlow (`postgres.spdtwktxdalcfigzeqrz`)
- Odoo ERP database (read-only replica)
- MindsDB predictive analytics integration

**Knowledge Base Storage:**
- **Dashboard Metadata:** Superset internal PostgreSQL
- **Data Lineage:** Stored in `superset.dbs` and `superset.tables`
- **Query Cache:** Redis (ephemeral, 24h TTL)

---

### 5. Odoo ERP (Main Production)

**URL:** `https://erp.insightpulseai.net`
**Host:** `165.227.10.178` (San Francisco SFO2)
**Instance:** 4GB RAM / 120GB Disk
**Version:** Odoo 18.0 Community Edition

**Purpose:**
- Multi-tenant Finance Shared Service Center (SSC)
- 8 legal entities (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- BIR compliance workflows
- Expense management, procurement, accounting

**Database:**
- **Primary:** PostgreSQL 15 on Supabase (`postgres.xkxyvboeubffxxbebsll`)
- **Connection:** Pooler (port 6543) for high concurrency
- **Backups:** Daily automated backups on Supabase

**Modules:**
- Custom modules in `odoo/addons/`
- OCA modules (18.0 branches)
- BIR-specific modules for Philippine tax compliance

---

## Knowledge Embeddings & RAG Architecture

### Vector Storage (pgvector on Supabase)

**Database:** `postgres.spdtwktxdalcfigzeqrz` (SpendFlow project)

**Tables:**
```sql
-- BIR document embeddings
scout.bir_documents (
  id UUID PRIMARY KEY,
  document_type TEXT,  -- 'RMC', '1601-C', '2550Q', etc.
  content TEXT,
  embedding VECTOR(1536),  -- OpenAI text-embedding-3-small
  metadata JSONB,
  created_at TIMESTAMPTZ
)

-- OCR result embeddings
scout.ocr_results (
  id UUID PRIMARY KEY,
  image_url TEXT,
  extracted_text TEXT,
  embedding VECTOR(1536),
  confidence_scores JSONB,
  created_at TIMESTAMPTZ
)

-- Agent conversation memory
scout.agent_memory (
  id UUID PRIMARY KEY,
  session_id UUID,
  role TEXT,  -- 'user' | 'assistant'
  content TEXT,
  embedding VECTOR(1536),
  created_at TIMESTAMPTZ
)
```

**Indexes:**
```sql
CREATE INDEX bir_documents_embedding_idx
  ON scout.bir_documents
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX ocr_results_embedding_idx
  ON scout.ocr_results
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
```

### RAG Pipeline Flow

```
User Query
    ↓
1. Query Embedding (OpenAI text-embedding-3-small)
    ↓
2. Vector Similarity Search (pgvector cosine similarity)
    ↓
3. Top-K Retrieval (default: top_k=3)
    ↓
4. Context Assembly (retrieved docs + query)
    ↓
5. LLM Synthesis (Claude 3.5 Sonnet via Agent Gateway)
    ↓
6. Citation Tracking (source documents stored in response)
    ↓
Response with Sources
```

**Example Query:**
```bash
curl -X POST "https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/agent/tax/ph/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Do we still file monthly VAT (2550M) in 2025?",
    "top_k": 3
  }'

# Response:
{
  "answer": "No, monthly VAT filing (Form 2550M) was discontinued...",
  "sources": [
    "RMC 5-2023",
    "Revenue Regulations 16-2023",
    "BIR Form 2550Q Instructions"
  ],
  "confidence": 0.95
}
```

### Embedding Generation Pipeline

**Scheduled Jobs:**
- **Daily 02:00 UTC:** Refresh BIR document embeddings from new RMCs/regulations
- **On-Demand:** OCR result embedding generation after each receipt processing
- **Batch Processing:** Weekly full re-embedding for updated documents

**Storage Costs:**
- Embeddings: ~6KB per document (1536 dimensions × 4 bytes)
- 10,000 documents = ~60MB vector storage
- Supabase Free Tier: 500MB database (sufficient for current scale)

### Knowledge Base Sources

1. **BIR Documents** (`scout.bir_documents`)
   - Revenue Memorandum Circulars (RMCs)
   - Revenue Regulations (RRs)
   - BIR forms and instructions (1601-C, 1702-RT, 2550Q, 2550M, 2307, 2316)
   - Tax calendars and deadline schedules

2. **Odoo Documentation** (`scout.odoo_docs`)
   - Module documentation (README.md files)
   - API documentation
   - OCA guidelines and standards
   - Custom module specifications

3. **Agent Conversation Memory** (`scout.agent_memory`)
   - Session-based conversation history
   - Context retention across multi-turn dialogues
   - User preference learning

4. **OCR Training Data** (DigitalOcean Spaces)
   - Receipt samples for model fine-tuning
   - Invoice templates from Philippine vendors
   - BIR form samples (anonymized)

---

## Environment Configuration

### GitHub Secrets (Required)

**Production Services:**
```bash
AGENT_GATEWAY_URL=https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run
OCR_SERVICE_URL=http://188.166.237.231
SUPERSET_URL=https://superset.insightpulseai.net
MCP_COORDINATOR_URL=https://mcp.insightpulseai.net
```

**Database Connections:**
```bash
# Supabase SpendFlow (spdtwktxdalcfigzeqrz)
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
POSTGRES_URL=postgres://postgres.spdtwktxdalcfigzeqrz:***@aws-1-us-east-1.pooler.supabase.com:6543/postgres

# Supabase xkxyvboeubffxxbebsll (Odoo DB)
ODOO_DB_URL=postgres://postgres.xkxyvboeubffxxbebsll:***@aws-1-us-east-1.pooler.supabase.com:6543/postgres
```

**DigitalOcean:**
```bash
DIGITALOCEAN_ACCESS_TOKEN=dop_v1_***
DROPLET_SSH_KEY=<private-key>
ODOO_DROPLET_IP=165.227.10.178
OCR_DROPLET_IP=188.166.237.231
```

### Environment-Specific Configuration

See `config/environments.yaml` for full environment matrix (local, staging, production).

---

## Monitoring & Health Checks

### Automated Health Checks

**Workflows:**
- `automation-health.yml` - 4-layer validation pyramid (runs on push, daily 02:00 UTC)
- `ph-tax-canary.yml` - PH tax compliance verification (daily 09:00 UTC)
- `health-monitor.yml` - Service uptime monitoring (every 15 minutes)

**Health Endpoints:**
- Agent Gateway: `GET /health`
- OCR Service: `GET /health`
- Odoo ERP: `GET /web/health`
- Superset: `GET /health`
- MCP Coordinator: `GET /health`

**Alerting:**
- GitHub Issues created on failure
- Slack notifications (if `SLACK_WEBHOOK_URL` configured)
- Auto-close when service recovers

### Performance Metrics

**SLAs:**
- Uptime: 99.9% (8.7 hours downtime/year)
- API Response Time: P95 <200ms (except OCR: <30s)
- Agent Query Latency: P95 <3s
- OCR Processing: P95 <30s

**Monitoring Tools:**
- GitHub Actions workflows (automated checks)
- DigitalOcean monitoring (built-in)
- Supabase metrics dashboard

---

## Deployment Patterns

### Canary Deployment (Odoo ERP)

**Workflow:** `deploy-canary.yml`
- Traffic split: 10% → 25% → 50% → 100%
- Monitoring duration: 15 minutes per stage
- Automatic rollback on error rate >5%
- Health check validation at each stage

### Blue-Green Deployment (AI Services)

**Agent Gateway:** Managed by DigitalOcean AI Agents (zero-downtime)
**OCR Service:** Docker container swap on droplet
**Rollback:** Instant switch back to previous container

### Database Migrations

**Odoo ERP:**
```bash
# Supabase migrations
psql "$ODOO_DB_URL" -f packages/db/sql/<migration>.sql

# Odoo module upgrades
docker exec odoo odoo --update=<module> --stop-after-init
docker restart odoo
```

**Knowledge Base:**
```bash
# Re-embed documents
psql "$POSTGRES_URL" -f scripts/sql/refresh_embeddings.sql

# Update indexes
psql "$POSTGRES_URL" -c "REINDEX INDEX bir_documents_embedding_idx;"
```

---

## Cost Analysis

**Monthly Infrastructure Costs:**

| Component | Service | Cost/Month |
|-----------|---------|------------|
| Odoo Droplet (SFO2) | 4GB/120GB | $24 |
| OCR Droplet (SGP1) | 8GB/80GB | $48 |
| Agent Gateway | DO AI Agents | ~$20 (usage-based) |
| Supabase SpendFlow | Free Tier | $0 (up to 500MB) |
| Supabase Odoo DB | Free Tier | $0 (up to 500MB) |
| Superset Analytics | App Platform | $5 |
| MCP Coordinator | App Platform | $5 |
| Domains | DNS hosting | $0 |
| **Total** | | **~$102/month** |

**Cost Savings vs SaaS:**
- SAP Concur replacement: $15k/year saved
- Tableau replacement (Superset): $8.4k/year saved
- Total savings: **$23.4k/year**

---

## Security & Compliance

### BIR Compliance Features

**Immutable Audit Trail:**
- All accounting entries are immutable (corrections via reversal entries)
- Chatter logs for all document modifications
- Email activity tracking (`mail.activity.mixin`)

**Required Forms:**
- 1601-C (Monthly Remittance Return)
- 1702-RT (Annual Income Tax Return)
- 2550Q (Quarterly VAT Declaration)
- 2550M (Monthly VAT Declaration - discontinued 2025 per RMC 5-2023)
- 2307 (Certificate of Creditable Tax Withheld at Source)
- 2316 (Certificate of Compensation Payment/Tax Withheld)

**E-Invoicing Ready:**
- Pluggable connector architecture
- JSON structure aligned with BIR specifications
- Digital signature support (pending BIR final specs)

### Access Control

**Multi-Tenant Isolation:**
- Company-level data segregation (`company_id` on all models)
- Row-Level Security (RLS) on Supabase tables
- Odoo access rights and record rules

**Authentication:**
- Supabase Auth for API access
- Odoo built-in auth for ERP users
- Service role keys for backend-to-backend communication

---

## Disaster Recovery

### Backup Strategy

**Databases:**
- Supabase: Automated daily backups (7-day retention)
- Manual snapshots before major changes
- Point-in-time recovery available

**Droplets:**
- Weekly snapshots enabled
- Volume backups for persistent data
- Configuration stored in Git (infrastructure as code)

**Recovery Time Objectives:**
- RTO (Recovery Time): <4 hours
- RPO (Recovery Point): <24 hours (daily backups)

### Incident Response

1. **Detection:** Automated health checks create GitHub issues
2. **Assessment:** Review workflow logs and service health
3. **Mitigation:** Rollback deployment or restart services
4. **Recovery:** Restore from backup if needed
5. **Post-Mortem:** Document incident and prevent recurrence

---

## Future Enhancements

**Planned Additions:**
- [ ] GPU Droplet for advanced OCR model fine-tuning
- [ ] Load balancer for Odoo ERP horizontal scaling
- [ ] Reserved IPs for static addressing
- [ ] Block storage volumes for expandable Odoo storage
- [ ] DigitalOcean Managed Database (PostgreSQL) migration
- [ ] Cloudflare CDN for static assets
- [ ] Prometheus + Grafana for advanced monitoring

**Knowledge Base Expansion:**
- [ ] Multi-language embeddings (English, Tagalog, Filipino)
- [ ] Cross-document citation graph
- [ ] Temporal versioning (track RMC supersessions)
- [ ] Entity extraction from BIR forms

---

## References

- [DigitalOcean fin-workspace Dashboard](https://cloud.digitalocean.com/projects/29cde7a1-8280-46ad-9fdf-dea7b21a7825)
- [Supabase SpendFlow Project](https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz)
- [Supabase Odoo DB Project](https://supabase.com/dashboard/project/xkxyvboeubffxxbebsll)
- [GitHub Repository](https://github.com/jgtolentino/insightpulse-odoo)
- [Odoo Documentation](https://www.odoo.com/documentation/18.0/)
- [BIR Official Website](https://www.bir.gov.ph/)

---

**Maintainer:** InsightPulse AI Team
**Contact:** jgtolentino_rn@yahoo.com
**Version:** 1.0.0 (2025-11-09)
