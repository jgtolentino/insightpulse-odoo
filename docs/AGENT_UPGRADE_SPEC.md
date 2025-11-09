# AI Agent Upgrade Specification

**Agent Gateway:** `https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run`
**Current Model:** Claude 3.5 Sonnet
**Current Tools:** 13
**Target Tools:** 25+
**Upgrade Date:** 2025-11-09

---

## Current Agent Capabilities (Baseline)

### Existing Tools (13)

1. **BIR Tax Q&A** - Philippine tax compliance question answering
2. **RMC Citation Retrieval** - Revenue Memorandum Circular lookup
3. **Tax Calendar** - Filing deadlines and schedules
4. **Withholding Tax Calculator** - WHT computation (5%, 10%, 15%)
5. **VAT Compliance Checker** - Quarterly VAT (2550Q) validation
6. **Form Generator** - BIR forms (1601-C, 2307, 2316)
7. **Document Understanding** - Receipt/invoice OCR integration
8. **Multi-Agency Routing** - 8-entity expense routing
9. **Approval Workflow** - Multi-level approval orchestration
10. **Database Query** - Supabase PostgreSQL direct queries
11. **Vector Search** - pgvector similarity search for RAG
12. **Embedding Generation** - OpenAI text-embedding-3-small
13. **Session Memory** - Conversation context retention

### Knowledge Base (Current)

**Vector Storage (Supabase pgvector):**
- `scout.bir_documents` (1,250 documents, 1536-dim embeddings)
- `scout.ocr_results` (5,400 receipts, embeddings for similarity matching)
- `scout.agent_memory` (3,800 conversation turns)

**Indexed Content:**
- BIR Revenue Memorandum Circulars (RMCs): 145 documents
- Revenue Regulations (RRs): 78 documents
- BIR Form Instructions: 32 documents
- Tax Calendar 2023-2025: 12 documents
- OCA Odoo Guidelines: 250 documents
- Custom Odoo Module Docs: 38 README files

**Embedding Model:** OpenAI text-embedding-3-small (1536 dimensions)

---

## Upgrade Plan: New Tools & Capabilities

### Phase 1: Extended BIR Compliance (6 New Tools)

**Tool 14: E-Invoicing Validator**
- **Purpose:** Validate JSON structure for upcoming BIR e-invoicing requirements
- **Inputs:** Invoice JSON, validation schema
- **Outputs:** Validation report, compliance score
- **Knowledge Source:** BIR e-invoicing specs (when released), RMC updates

**Tool 15: Multi-Form Batch Generator**
- **Purpose:** Generate multiple BIR forms for month-end closing
- **Inputs:** Month, agency code, transaction data
- **Outputs:** 1601-C, 2550Q, 2307 batch files
- **Integration:** Supabase transactions table, Odoo journal entries

**Tool 16: Tax Deadline Forecaster**
- **Purpose:** Predict upcoming tax deadlines with risk scoring
- **Inputs:** Current date, agency, filing history
- **Outputs:** Deadline calendar with risk alerts (red/yellow/green)
- **Knowledge Source:** BIR tax calendar, historical compliance data

**Tool 17: WHT Rate Lookup (Advanced)**
- **Purpose:** Context-aware withholding tax rate determination
- **Inputs:** Vendor type, service category, amount, treaty applicability
- **Outputs:** Correct WHT rate, BIR reference, computation
- **Knowledge Source:** Tax treaties, RMCs, Revenue Regulations

**Tool 18: BIR Audit Trail Generator**
- **Purpose:** Generate immutable audit trails for BIR compliance
- **Inputs:** Document ID, change history
- **Outputs:** Tamper-proof audit log with digital signatures
- **Integration:** Odoo chatter logs, mail.activity records

**Tool 19: Cross-Reference Validator**
- **Purpose:** Verify consistency across BIR forms (1601-C vs 2307)
- **Inputs:** Multiple forms for same period
- **Outputs:** Discrepancy report, reconciliation suggestions
- **Knowledge Source:** BIR validation rules, cross-form requirements

### Phase 2: Odoo ERP Integration (5 New Tools)

**Tool 20: Odoo Module Documentation Generator**
- **Purpose:** Auto-generate OCA-compliant module documentation
- **Inputs:** Module path, manifest, models, views
- **Outputs:** README.rst with proper structure and examples
- **Knowledge Source:** OCA guidelines, existing module patterns

**Tool 21: Odoo RPC Executor**
- **Purpose:** Execute Odoo ORM operations via XML-RPC
- **Inputs:** Model name, method, arguments
- **Outputs:** Operation result, error handling
- **Integration:** Odoo ERP (https://erp.insightpulseai.net)

**Tool 22: Multi-Tenant Data Router**
- **Purpose:** Route operations to correct legal entity (company_id)
- **Inputs:** Agency code, operation type, data
- **Outputs:** Routed operation with proper company context
- **Knowledge Source:** config/environments.yaml agencies list

**Tool 23: Odoo Upgrade Assistant**
- **Purpose:** Guide Odoo module upgrades (18.0 → 19.0)
- **Inputs:** Current version, target version, module list
- **Outputs:** Upgrade roadmap, breaking changes, migration steps
- **Knowledge Source:** Odoo upgrade guides, OCA migration docs

**Tool 24: Record Rule Generator**
- **Purpose:** Generate Odoo security record rules for RLS
- **Inputs:** Model name, access requirements
- **Outputs:** XML file with ir.rule definitions
- **Knowledge Source:** Odoo security best practices

### Phase 3: Advanced Analytics & BI (4 New Tools)

**Tool 25: Superset Dashboard Builder**
- **Purpose:** Generate Superset dashboards from natural language requests
- **Inputs:** Dashboard description, data source, metrics
- **Outputs:** Dashboard JSON spec, chart configurations
- **Integration:** Superset API (https://superset.insightpulseai.net)

**Tool 26: SQL Query Generator**
- **Purpose:** Generate optimized PostgreSQL queries for analytics
- **Inputs:** Natural language query, schema context
- **Outputs:** SQL query, execution plan, performance tips
- **Knowledge Source:** PostgreSQL docs, query optimization patterns

**Tool 27: Financial Reporting Composer**
- **Purpose:** Generate financial reports (P&L, Balance Sheet, Cash Flow)
- **Inputs:** Period, agency, format (PDF/Excel)
- **Outputs:** Formatted report with BIR compliance annotations
- **Integration:** Odoo accounting data, Supabase analytics views

**Tool 28: Expense Pattern Analyzer**
- **Purpose:** Detect anomalies and patterns in expense data
- **Inputs:** Date range, agency, category
- **Outputs:** Pattern insights, anomaly alerts, recommendations
- **Integration:** Scout transaction data, ML-based analysis

### Phase 4: Infrastructure & DevOps (3 New Tools)

**Tool 29: Health Check Orchestrator**
- **Purpose:** Coordinate health checks across all services
- **Inputs:** Service name, check type
- **Outputs:** Aggregated health status, issue diagnosis
- **Integration:** All service /health endpoints

**Tool 30: Deployment Coordinator**
- **Purpose:** Orchestrate canary deployments with rollback capability
- **Inputs:** Service name, version, canary percentage
- **Outputs:** Deployment status, metrics, rollback decision
- **Integration:** DigitalOcean API, GitHub Actions

**Tool 31: Cost Optimizer**
- **Purpose:** Analyze infrastructure costs and suggest optimizations
- **Inputs:** Current usage, service metrics
- **Outputs:** Cost breakdown, optimization recommendations, projected savings
- **Knowledge Source:** DigitalOcean pricing, usage analytics

---

## Knowledge Base Expansion

### New Document Collections

**1. Odoo 19.0 Documentation** (Target: 500 documents)
- Official Odoo 19.0 documentation
- OCA module guidelines for 19.0
- Migration guides from 18.0
- API changes and deprecations

**2. Advanced BIR Regulations** (Target: 200 documents)
- Tax treaties (US-PH, Japan-PH, etc.)
- Industry-specific RMCs
- E-invoicing specifications (when released)
- BIR rulings and circulars

**3. Financial Analysis Patterns** (Target: 150 documents)
- Financial ratio analysis
- Expense benchmarking data
- Industry-specific financial metrics
- Cash flow forecasting models

**4. Infrastructure Documentation** (Target: 100 documents)
- DigitalOcean best practices
- PostgreSQL optimization guides
- Docker deployment patterns
- Kubernetes configuration examples

### Embedding Model Upgrade

**Current:** OpenAI text-embedding-3-small (1536 dimensions)
**Proposed:** OpenAI text-embedding-3-large (3072 dimensions)

**Benefits:**
- Higher semantic precision for complex queries
- Better handling of multilingual content (English/Filipino)
- Improved performance on long-form documents

**Migration Plan:**
1. Generate new embeddings in parallel (new column)
2. A/B test retrieval quality
3. Gradual cutover to new embeddings
4. Archive old embeddings after 30 days

---

## Integration Updates

### MCP Coordinator Integration

**Current MCP Servers:** 7 (pulser-hub, digitalocean, kubernetes, docker, github, superset, tableau)
**New Integrations:**
- **Notion MCP** - Knowledge capture and meeting intelligence
- **Gmail MCP** - Email automation for BIR filing confirmations
- **Slack MCP** - Team notifications and approval workflows

**Total MCP Servers (Target):** 10 servers, 120+ tools

### API Integrations

**New Endpoints:**
1. **BIR eFPS API** (when available) - Electronic filing and payment
2. **OpenAI Assistants API** - Advanced conversation management
3. **Anthropic Claude 4** (when released) - Model upgrade
4. **MindsDB Integration** - Predictive analytics for expense forecasting

---

## Performance Targets

### Response Time SLAs

| Query Type | Current | Target | Improvement |
|------------|---------|--------|-------------|
| Simple Tax Q&A | 2.5s | 1.5s | 40% faster |
| Complex Multi-Form | 5.0s | 3.0s | 40% faster |
| Document Understanding | 8.0s | 5.0s | 38% faster |
| Dashboard Generation | 15.0s | 10.0s | 33% faster |

### Accuracy Metrics

| Capability | Current | Target | Improvement |
|------------|---------|--------|-------------|
| Tax Answer Accuracy | 92% | 98% | +6pp |
| Form Generation Accuracy | 88% | 95% | +7pp |
| OCR Confidence | 85% | 92% | +7pp |
| Multi-Agency Routing | 95% | 99% | +4pp |

### Cost Efficiency

**Current:** $20/month (usage-based)
**Target:** $25/month (25% increase for 100% more tools)
**Cost per Tool:** $0.77 (vs current $1.54) - 50% more cost-efficient

---

## Implementation Roadmap

### Week 1: BIR Compliance Tools (Tools 14-19)
- Day 1-2: E-Invoicing Validator + Multi-Form Batch Generator
- Day 3-4: Tax Deadline Forecaster + WHT Rate Lookup
- Day 5-7: BIR Audit Trail + Cross-Reference Validator

### Week 2: Odoo Integration Tools (Tools 20-24)
- Day 8-9: Module Documentation Generator + Odoo RPC Executor
- Day 10-11: Multi-Tenant Data Router + Upgrade Assistant
- Day 12-14: Record Rule Generator + testing

### Week 3: Analytics & BI Tools (Tools 25-28)
- Day 15-16: Superset Dashboard Builder + SQL Query Generator
- Day 17-18: Financial Reporting Composer + Expense Pattern Analyzer
- Day 19-21: Integration testing + optimization

### Week 4: DevOps Tools + Knowledge Base (Tools 29-31)
- Day 22-23: Health Check Orchestrator + Deployment Coordinator
- Day 24-25: Cost Optimizer
- Day 26-28: Knowledge base expansion + embedding migration
- Day 29-30: Full system testing + documentation

---

## Validation & Testing

### Canary Testing Strategy

**Phase 1 (Week 1):** 10% of agent traffic uses new tools
- Monitor: Error rates, response times, user satisfaction
- Rollback trigger: Error rate >5% or response time >2x baseline

**Phase 2 (Week 2):** 25% traffic to new tools
- A/B testing against baseline agent
- Collect user feedback via post-response surveys

**Phase 3 (Week 3):** 50% traffic to upgraded agent
- Full feature parity validation
- Performance benchmarking

**Phase 4 (Week 4):** 100% cutover
- Deprecate old agent version
- Monitor for 7 days before marking complete

### Quality Gates

**Required Passing Criteria:**
- ✅ All 31 tools passing unit tests (>95% coverage)
- ✅ Integration tests with all MCP servers (100% pass rate)
- ✅ Response time <3s P95 for standard queries
- ✅ BIR compliance validation tests (100% pass rate)
- ✅ Multi-tenant isolation tests (no cross-contamination)
- ✅ Cost per query <$0.05 average

---

## Knowledge Transfer

### Documentation Deliverables

1. **Agent Tool Reference** - Detailed documentation for all 31 tools
2. **Integration Guide** - How to use agent with Odoo, Superset, MCP
3. **BIR Compliance Playbook** - Step-by-step guides for tax filing
4. **Troubleshooting Guide** - Common issues and solutions
5. **API Documentation** - OpenAPI specs for all agent endpoints

### Training Materials

1. **Video Tutorials** (10 videos, 5-10 min each)
   - Getting started with the upgraded agent
   - BIR tax filing automation
   - Multi-agency expense routing
   - Dashboard generation
   - Advanced analytics queries

2. **Interactive Demos** (Loom or similar)
   - Live demonstrations of each new tool
   - Real-world use cases for Finance SSC teams

3. **FAQ & Examples**
   - 50+ example queries with expected outputs
   - Common pitfalls and best practices

---

## Success Metrics

### Adoption Metrics (30 days post-upgrade)

- **Active Users:** >50 unique users/week
- **Query Volume:** >500 queries/week
- **Tool Utilization:** All 31 tools used at least once
- **User Satisfaction:** >4.5/5.0 average rating

### Business Impact (90 days post-upgrade)

- **Time Saved:** 40+ hours/month on BIR filing
- **Error Reduction:** 50% fewer manual entry errors
- **Cost Savings:** $2,000/month (vs manual processing)
- **Compliance Rate:** 100% on-time BIR filings

### Technical Metrics (Continuous)

- **Uptime:** 99.9% (≤8.7 hours downtime/year)
- **Response Time:** P95 <3s
- **Error Rate:** <0.1%
- **Cost per Query:** <$0.05

---

## Risk Mitigation

### Identified Risks

1. **BIR E-Invoicing Spec Changes**
   - **Mitigation:** Pluggable connector architecture, rapid update capability

2. **Knowledge Base Drift**
   - **Mitigation:** Weekly RMC monitoring, automated refresh pipeline

3. **Cost Overruns**
   - **Mitigation:** Query rate limiting, caching, cost alerts at $30/month

4. **Performance Degradation**
   - **Mitigation:** Gradual rollout, A/B testing, immediate rollback capability

5. **Multi-Tenant Data Leakage**
   - **Mitigation:** Comprehensive testing, RLS validation, security audits

---

## Appendix: Agent Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Gateway API                         │
│         https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─► Claude 3.5 Sonnet (LLM Core)
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│   31 Tools   │    │  Knowledge Base  │    │ MCP Servers  │
│              │    │                  │    │              │
│ • BIR (19)   │───►│ pgvector (15K)  │◄───│ 10 servers   │
│ • Odoo (5)   │    │ embeddings      │    │ 120+ tools   │
│ • BI (4)     │    │                  │    │              │
│ • DevOps (3) │    │ OpenAI embed-3  │    │              │
└──────────────┘    └──────────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            ┌───────────────┐   ┌─────────────┐
            │   Supabase    │   │   Odoo ERP  │
            │   PostgreSQL  │   │   18.0 CE   │
            └───────────────┘   └─────────────┘
```

---

**Maintainer:** InsightPulse AI Team
**Contact:** jgtolentino_rn@yahoo.com
**Version:** 2.0.0 (Upgrade Spec)
**Last Updated:** 2025-11-09
