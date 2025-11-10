# Product Requirements Document (PRD)
**InsightPulse Odoo – Enterprise SaaS Parity Platform**

**Last Updated**: 2025-11-09
**Version**: 4.0.0
**Status**: Wave 4 (85% complete)
**Product Owner**: InsightPulse AI Team
**Target Release**: Q1 2027 (Wave 9 completion)

---

## 0. Executive Summary

### Product Vision
Build a complete, self-hosted **Enterprise SaaS Parity Platform** providing 95% feature parity with enterprise stacks (SAP Concur, SAP Ariba, Tableau, Odoo Enterprise) at **<5% of the cost** using Odoo CE 18 + OCA modules + AI automation.

### Value Proposition
- **Cost Savings**: $46,400/year net savings (88% cost reduction)
- **Open Source**: 100% AGPL-3.0, no vendor lock-in
- **BIR Compliance**: Philippine tax regulations (Forms 2307, 2316, e-invoicing)
- **Multi-Tenant**: Strict legal entity isolation with row-level security
- **AI-Powered**: PaddleOCR-VL, OpenAI GPT-4o-mini, pgvector semantic search
- **Production Grade**: >80% test coverage, <200ms P95 CRUD, 99.5%+ uptime

### Target Market
- **Primary**: Finance Shared Service Centers (Philippines)
- **Secondary**: Multi-agency government operations, SMEs, international corporations with Philippine operations
- **Agencies**: 8 agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)

### Success Criteria
- Replace $52,700/year in SaaS tools with <$6,300/year infrastructure
- Achieve BIR compliance for 100% of transactions
- Maintain 99.5%+ uptime in production
- Complete Waves 1-9 by Q1 2027

---

## 1. Product Overview

### What We're Building
A **complete enterprise operations platform** built on Odoo CE 18 that replaces:

| SaaS Tool | Annual Cost | InsightPulse Replacement | Module |
|-----------|-------------|-------------------------|--------|
| **SAP Concur** | $15,000 | Travel & Expense with OCR | `ipai_expense` |
| **SAP Ariba** | $12,000 | Procurement & SRM | `ipai_procure` |
| **Tableau** | $8,400 | Apache Superset | `superset_connector` |
| **Slack Enterprise** | $12,600 | Mattermost/Rocket.Chat | (External) |
| **Odoo Enterprise** | $4,700 | Odoo CE + OCA | Base platform |
| **Total** | **$52,700/year** | **$6,300/year** | **88% savings** |

### Core Modules (10 modules across Waves 1-3)

#### Wave 1: Finance Foundation (4 modules)
1. **`ipai_core`** - Foundation module with multi-tenant framework
2. **`ipai_approvals`** - Multi-stage approval workflows
3. **`ipai_rate_policy`** - Automated rate calculation (P60 + 25% markup)
4. **`ipai_saas_ops`** - Multi-tenant provisioning and operations

#### Wave 2: Advanced Operations (6 modules)
5. **`ipai_ppm`** - Program/Project/Budget/Risk management
6. **`ipai_ppm_costsheet`** - Tax-aware project costing with privacy controls
7. **`ipai_procure`** - Procurement & supplier relationship management
8. **`ipai_expense`** - OCR-powered expense automation
9. **`ipai_subscriptions`** - Recurring revenue (MRR/ARR) management
10. **`superset_connector`** - Apache Superset BI integration

#### Wave 3: Quality & AI (2 modules)
11. **`ipai_knowledge_ai`** - AI knowledge workspace (pgvector + GPT-4o-mini)
12. **Test Suite** - 134 test methods, 2,771 lines of test coverage

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **ERP Platform** | Odoo Community Edition | 18.0 | Core business logic |
| **Database** | PostgreSQL + Supabase | 15.6 | Data persistence + pgvector |
| **Analytics** | Apache Superset | 3.0 | BI dashboards |
| **OCR** | PaddleOCR-VL | 900M | Receipt processing |
| **LLM** | OpenAI GPT-4o-mini | Latest | Post-processing + AI workspace |
| **Orchestration** | Pulser v4.0.0 | 4.0.0 | Multi-agent coordination |
| **Infrastructure** | DigitalOcean App Platform | - | Deployment |
| **CI/CD** | GitHub Actions | - | Automation (76 workflows) |

---

## 2. User Personas & Use Cases

### Primary Personas

#### 1. Finance Director (FD)
**Role**: Strategic finance oversight, compliance, budget management

**Goals**:
- Ensure BIR compliance (Forms 2307, 2316)
- Monitor budget vs actual across 8 agencies
- Approve high-value expenses and procurement
- Generate financial reports for executives

**Pain Points**:
- Manual BIR form generation (error-prone)
- Lack of real-time budget visibility
- Scattered vendor data across agencies
- Time-consuming month-end closing

**Use Cases**:
1. Generate BIR Form 2307 for all agencies (monthly)
2. Review and approve cost sheets with vendor details
3. Monitor budget variance across programs
4. Approve expenses >₱50,000

#### 2. Account Manager (AM)
**Role**: Client project management, cost estimation, delivery

**Goals**:
- Create accurate cost sheets with role/rate (vendor hidden)
- Track project budgets and margins
- Submit expense reports quickly
- Manage project timelines and resources

**Pain Points**:
- Shouldn't see vendor rates (privacy concern)
- Manual cost sheet creation (slow, error-prone)
- Delayed expense reimbursements
- Lack of project profitability visibility

**Use Cases**:
1. Create cost sheet with role/rate (vendor masked)
2. Submit expense report with OCR receipt scanning
3. Track project budget vs actual
4. Request rate quotes for new roles

#### 3. Procurement Officer
**Role**: Vendor management, RFQ processing, contract administration

**Goals**:
- Onboard new vendors efficiently
- Manage multi-round RFQ bidding
- Track vendor scorecards (quality, delivery, pricing)
- Ensure 3-way match (PO → GRN → Invoice)

**Pain Points**:
- Manual vendor onboarding (slow)
- Spreadsheet-based RFQ comparison
- No vendor performance tracking
- Invoice discrepancies (manual reconciliation)

**Use Cases**:
1. Onboard new vendor with KYC documents
2. Issue RFQ to 5 vendors, receive bids, compare
3. Generate PO from approved RFQ
4. Validate 3-way match before invoice payment

#### 4. Employee (Expense Submitter)
**Role**: Field operations, travel, client meetings

**Goals**:
- Submit expense reports quickly (mobile)
- Get reimbursed within 5 days
- Auto-fill expense details from receipt photos

**Pain Points**:
- Manual expense entry (tedious)
- Lost receipts (no audit trail)
- Delayed approvals and reimbursements
- Policy violations (after submission)

**Use Cases**:
1. Snap receipt photo, auto-fill expense details
2. Submit expense report for approval
3. Track approval status in real-time
4. Receive reimbursement notification

---

## 3. Functional Requirements

### 3.1 Multi-Tenancy & Security

**REQ-001: Legal Entity Isolation** (Priority: Critical)
- System MUST support multiple legal entities with strict data isolation
- Each entity (company_id) MUST have separate:
  - Chart of accounts
  - Tax configurations
  - Numbering sequences
  - User access controls
- Row-level security (RLS) enforced at database level
- No cross-entity data leakage

**Acceptance Criteria**:
- User in Company A cannot view/edit Company B records
- Database queries auto-filter by company_id
- Supabase RLS policies enforce isolation
- Security audit shows no data leakage

**REQ-002: Role-Based Access Control** (Priority: Critical)
- System MUST support role-based field visibility
- Account Manager: See role/rate, vendor HIDDEN
- Finance Director: See all fields including vendor/cost
- Employee: See own expenses only

**Acceptance Criteria**:
- Record rules enforce field-level security
- HttpCase tests validate RLS enforcement
- Security audit shows proper access control

### 3.2 BIR Compliance (Philippines)

**REQ-003: BIR Form Generation** (Priority: Critical)
- System MUST generate BIR Forms 2307, 2316 automatically
- Forms MUST be immutable after submission
- All corrections MUST use reversal entries (no in-place edits)
- Audit trail MUST track all form generations

**Acceptance Criteria**:
- BIR Form 2307 generated monthly for all withholding taxes
- BIR Form 2316 generated annually for employee income
- Posted forms cannot be edited (ValidationError raised)
- Audit log shows all form generations with timestamp + user

**REQ-004: Immutable Accounting** (Priority: Critical)
- System MUST NOT allow editing of posted journal entries
- All corrections MUST use reversal + rebook pattern
- Audit trail MUST be immutable

**Acceptance Criteria**:
- Posted moves raise ValidationError on edit attempt
- Correction wizard creates reversal + new entry
- Audit trail shows clear correction chain

### 3.3 Expense Management

**REQ-005: OCR Receipt Processing** (Priority: High)
- System MUST auto-extract vendor, date, amount, tax from receipts
- OCR confidence MUST be ≥60% for auto-approval
- Low-confidence OCR MUST flag for manual review

**Acceptance Criteria**:
- PaddleOCR-VL extracts fields with JSON output
- OpenAI GPT-4o-mini post-processes for accuracy
- P95 processing time <30 seconds
- Auto-approval rate ≥85%

**REQ-006: Expense Policy Validation** (Priority: High)
- System MUST validate expenses against policies (amount limits, categories)
- Policy violations MUST be flagged before approval
- Employees MUST be notified of violations

**Acceptance Criteria**:
- Amount limits enforced per expense category
- Category restrictions enforced per employee role
- Violation notifications sent via email + in-app

### 3.4 Procurement & Sourcing

**REQ-007: Multi-Vendor RFQ** (Priority: High)
- System MUST support multi-round bidding
- Comparison matrix MUST show all vendor bids side-by-side
- Automated PO generation from approved RFQ

**Acceptance Criteria**:
- RFQ issued to ≥3 vendors
- Bidding rounds: initial → clarification → final
- Comparison matrix sortable by price, delivery, quality
- PO auto-generated from selected bid

**REQ-008: 3-Way Match** (Priority: High)
- System MUST validate PO → GRN → Invoice consistency
- Discrepancies MUST be flagged and resolved before payment

**Acceptance Criteria**:
- Quantity variance ≤2%
- Price variance ≤1%
- Discrepancies create exception workflow
- Payment blocked until resolution

### 3.5 Analytics & Reporting

**REQ-009: Real-Time Dashboards** (Priority: Medium)
- System MUST provide real-time dashboards via Superset
- Dashboards MUST load in <5 seconds
- Row-level security MUST filter data per company/agency

**Acceptance Criteria**:
- 5 key dashboards: Finance, PPM, Procurement, Expenses, Retainers
- Dashboard load time P95 <5 seconds
- Superset RLS policies enforce multi-company isolation
- Drill-down to transaction level enabled

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-001: Response Time** (Priority: High)
- CRUD operations: P95 <500ms
- Database queries: P95 <200ms
- Dashboard load: P95 <5 seconds
- OCR processing: P95 <30 seconds

**NFR-002: Scalability** (Priority: Medium)
- Support 1,000 concurrent users
- Support 10 million transactions/year
- Support 100 companies (multi-tenant)

### 4.2 Reliability

**NFR-003: Uptime** (Priority: Critical)
- System uptime: >99.5% (43 hours downtime/year max)
- Zero data loss on failures
- Automated backups: Daily (retained 30 days)

**NFR-004: Error Handling** (Priority: High)
- Queue job success rate: >99%
- API error rate: <0.1%
- Graceful degradation on external service failures

### 4.3 Security

**NFR-005: Security Standards** (Priority: Critical)
- OWASP Top 10 compliance (no Critical/High vulnerabilities)
- SQL injection prevention (ORM only, no raw SQL)
- XSS prevention (t-esc in templates)
- CSRF tokens on all forms
- SSL/TLS enforced for all connections

**NFR-006: Data Protection** (Priority: Critical)
- Secrets in environment variables (never in code/DB)
- RLS on all Supabase tables
- Service role keys backend-only
- Audit logs for all sensitive operations

### 4.4 Testing & Quality

**NFR-007: Test Coverage** (Priority: High)
- Unit test coverage: >80%
- Integration test coverage: >70%
- E2E test coverage: Critical user journeys
- Performance benchmarks: All critical operations

**NFR-008: Code Quality** (Priority: Medium)
- Pylint score: >8.0
- Flake8: Zero violations
- Black formatting: Enforced
- OCA conventions: 100% compliance

---

## 5. Epic Breakdown & Acceptance Criteria

### Wave 4: Enterprise Repository Structure (Current - 85% complete)

**EPIC-000: Professional Documentation & CI/CD Automation**
- **Goal**: Transform repository into enterprise-grade structure
- **Status**: 🚧 In Progress (Sprint 5, Nov 9-15, 2025)
- **Acceptance Criteria**:
  - [x] CLAUDE.md v2025-11-09 (24 sections, Spec-Kit compliant)
  - [x] TASKS.md restructured with task IDs and dependencies
  - [x] PLANNING.md with Wave milestones and KPIs
  - [x] CHANGELOG.md with semantic versioning
  - [x] PRD.md for main project (this document)
  - [ ] Pulser v4.0.0 documentation suite (5 files)
  - [ ] CI/CD workflows (cd-odoo-prod.yml, supabase-migration-test.yml)
  - [ ] Bootstrap GitHub secrets script
  - [ ] Root Makefile for DX
  - [ ] Docker compose for full stack
  - [ ] DigitalOcean App Platform specs (3 services)
  - [ ] Documentation index (docs/INDEX.md)

### Waves 1-3: Complete (See CHANGELOG.md v3.0.0)

**Detailed epic breakdown** available in:
- [docs/PRD_ENTERPRISE_SAAS_PARITY.md](docs/PRD_ENTERPRISE_SAAS_PARITY.md) (10 epics, acceptance criteria)
- [TASKS.md](TASKS.md) (EPIC-001 through EPIC-010)

**Summary**:
- EPIC-001: Unified Approvals Engine (70% complete)
- EPIC-002: Vendor-Privacy Cost Sheets (60% complete)
- EPIC-003: Rate Policy Automation (40% complete)
- EPIC-004: Procurement & SRM (30% complete)
- EPIC-005: Travel & Expense (65% complete)
- EPIC-006: PPM Core (20% complete)
- EPIC-007: Retainers & Subscriptions (10% complete)
- EPIC-008: Knowledge Workspace (15% complete)
- EPIC-009: Analytics & Dashboards (75% complete)
- EPIC-010: SaaS Ops & Multi-Tenancy (100% complete)

---

## 6. Success Metrics & KPIs

### Business KPIs

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **SaaS Cost Savings** | $52.7k/year | $0 (not deployed) | 🔴 |
| **Estimate → Invoice cycle** | ≤5 days | TBD | 🔴 |
| **Vendor approval lead time** | -40% | TBD | 🔴 |
| **Retainer overage detection** | ≥95% | TBD | 🔴 |
| **Margin variance** | ≤±2% | TBD | 🔴 |
| **AI workspace answer precision** | ≥0.9 F1 | TBD | 🔴 |

### Technical KPIs

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Response time P95** | <500ms | TBD | 🔴 |
| **Database query time P95** | <200ms | TBD | 🔴 |
| **Queue job success rate** | >99% | TBD | 🔴 |
| **API error rate** | <0.1% | TBD | 🔴 |
| **Test coverage** | >80% | 75% | 🟡 |
| **System uptime** | >99.5% | 99.8% | 🟢 |

### Wave 4 Progress Metrics (Current)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Wave 4 Completion** | 100% | 85% | 🟡 In Progress |
| **Documentation Suite** | 100% Spec-Kit | 90% | 🟡 In Progress |
| **CI/CD Automation** | Fully automated | 90% | 🟡 In Progress |
| **Documentation Freshness** | <7 days | 1 day | 🟢 Excellent |

---

## 7. Technical Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Vercel Frontend (Web UI)                    │
│                    https://atomic-crm.vercel.app                │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTPS
┌─────────────────────┴───────────────────────────────────────────┐
│              DigitalOcean App Platform (Services)                │
│  ┌──────────────────┬──────────────────┬──────────────────┐    │
│  │  Odoo CE 18.0    │  OCR Backend     │  Pulser v4.0.0   │    │
│  │  (ERP Core)      │  (PaddleOCR-VL)  │  (Orchestrator)  │    │
│  └──────────────────┴──────────────────┴──────────────────┘    │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Connection Pooler
┌─────────────────────┴───────────────────────────────────────────┐
│              Supabase PostgreSQL 15.6                            │
│  ┌──────────────────┬──────────────────┬──────────────────┐    │
│  │  RLS Policies    │  pgvector        │  Edge Functions  │    │
│  │  (Multi-tenant)  │  (AI embeddings) │  (Webhooks)      │    │
│  └──────────────────┴──────────────────┴──────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────────┐
│              Apache Superset 3.0 (Analytics)                    │
│              https://insightpulseai.net/superset                │
└──────────────────────────────────────────────────────────────────┘
```

### Multi-Agent Orchestration (Pulser v4.0.0)

```
┌────────────────────────────────────────────────────────────────┐
│                  Pulser Orchestrator (24/7)                   │
│              FastAPI + Celery + Redis + MCP Servers            │
└───┬───┬───┬───┬───┬───┬──────────────────────────────────────┘
    │   │   │   │   │   │
    ▼   ▼   ▼   ▼   ▼   ▼
  Dash Maya Echo Data Arkie Learn
        Fabcon         Bot
```

**Agents**:
- **Dash** (BI Architect) - Superset dashboards, SQL optimization
- **Maya** (Documentation) - Technical writing, API docs
- **Echo** (QA Engineer) - Test automation, quality gates
- **Data Fabcon** (Data Engineer) - ETL pipelines, migrations
- **Arkie** (Architect) - System design, deployment
- **LearnBot** (Knowledge) - Skills mining, error analysis
- **Pulser** (Orchestrator) - Agent coordination

### Data Layer

```
Supabase PostgreSQL 15.6
├── scout.* (transaction data)
├── public.* (Odoo tables with company_id RLS)
├── analytics.* (materialized views for Superset)
└── embeddings.* (pgvector for AI workspace)
```

**RLS Policies**: Enforced on all tables for multi-tenant isolation

**Connections**:
- Direct (port 5432): Low-latency admin operations
- Pooler (port 6543): High-concurrency application queries

---

## 8. Dependencies & Integration Points

### OCA Module Dependencies

**Required OCA Modules** (Odoo 18.0 branches):
- `queue_job` - Async job processing
- `base_tier_validation` - Multi-level approvals
- `server_environment` - Environment configuration
- `report_xlsx` - Excel report generation
- `contract` - Subscription management
- `contract_sale` - Sales integration
- `contract_invoice` - Invoicing integration

**Installation Order**:
1. `ipai_core` (foundation)
2. `ipai_approvals` (workflow engine)
3. All other modules (see DEPLOYMENT_CHECKLIST.md)

### External Service Integration

| Service | Purpose | Endpoint | Auth |
|---------|---------|----------|------|
| **OpenAI API** | GPT-4o-mini (LLM) | https://api.openai.com/v1 | API Key |
| **PaddleOCR-VL** | OCR processing | https://ade-ocr-backend-d9dru.ondigitalocean.app | None (internal) |
| **Supabase** | PostgreSQL + pgvector | aws-1-us-east-1.pooler.supabase.com:6543 | Service role key |
| **Apache Superset** | BI dashboards | https://insightpulseai.net/superset | OAuth |
| **DigitalOcean** | App Platform | https://api.digitalocean.com | Access token |

### MCP Server Integration

**7 MCP Servers** (98 total tools):
- `pulser-hub` - Odoo & ecosystem integration
- `digitalocean` - App Platform management
- `kubernetes` - Cluster operations (22 tools)
- `docker` - Container management
- `github` - Repository management (40 tools)
- `superset` - Analytics operations (3+ tools)

---

## 9. Release Strategy

### Wave Timeline (52 weeks total)

| Wave | Duration | Focus | Status |
|------|----------|-------|--------|
| **Wave 1** | Weeks 1-8 | Finance Foundation | ✅ 100% |
| **Wave 2** | Weeks 9-16 | Operations & Workflows | ✅ 100% |
| **Wave 3** | Weeks 17-20 | Testing & Quality | ✅ 100% |
| **Wave 4** | Weeks 21-26 | Enterprise Repository | 🚧 85% |
| **Wave 5** | Weeks 27-32 | Kubernetes & Cloud (Q1 2026) | 📋 Planned |
| **Wave 6** | Weeks 33-36 | Multi-Language (Q2 2026) | 📋 Planned |
| **Wave 7** | Weeks 37-42 | Mobile App (Q3 2026) | 📋 Planned |
| **Wave 8** | Weeks 43-46 | GraphQL API (Q4 2026) | 📋 Planned |
| **Wave 9** | Weeks 47-52 | Predictive Analytics (Q1 2027) | 📋 Planned |

### Version Strategy

**Semantic Versioning**: MAJOR.MINOR.PATCH

- **MAJOR** (X.0.0): Wave completion (breaking changes)
- **MINOR** (4.X.0): New features, non-breaking changes
- **PATCH** (4.0.X): Bug fixes, documentation updates

**Current**: v4.0.0 (Wave 4 - Enterprise Repository Structure)

### Deployment Strategy

**Continuous Deployment**:
- GitHub Actions workflows (76 existing, 4 new in Wave 4)
- Automated testing (unit, integration, E2E)
- Automated deployment to DigitalOcean App Platform
- Zero-downtime deployments (blue-green strategy)

**Environments**:
- Development: Local Docker compose
- Staging: DigitalOcean App Platform (staging)
- Production: DigitalOcean App Platform (production)

---

## 10. Risk Assessment

### High Risk

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **OCA module compatibility issues** | Medium | High | Pin specific OCA versions; test in staging |
| **User adoption resistance** | Medium | High | Phased rollout; training; change management |
| **Scope creep beyond timeline** | High | Medium | Sprint reviews; MVP focus; backlog prioritization |

### Medium Risk

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **AI workspace accuracy <0.9 F1** | Medium | Medium | Iterative prompt engineering; pgvector tuning |
| **Key developer departure** | Medium | High | Documentation; code reviews; knowledge transfer |

### Low Risk

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Performance degradation (>100 modules)** | Low | High | Database optimization; connection pooling; caching |
| **Multi-tenancy security breach** | Low | Critical | Rigorous RLS testing; security audit |

---

## 11. Glossary

**Terms & Definitions**:

- **BIR**: Bureau of Internal Revenue (Philippines)
- **Form 2307**: Certificate of Creditable Tax Withheld at Source
- **Form 2316**: Certificate of Compensation Payment/Tax Withheld
- **RLS**: Row-Level Security (database access control)
- **OCA**: Odoo Community Association
- **CE**: Community Edition (Odoo)
- **SaaS**: Software as a Service
- **PPM**: Program/Project Management
- **SRM**: Supplier Relationship Management
- **MRR**: Monthly Recurring Revenue
- **ARR**: Annual Recurring Revenue
- **P60**: 60th percentile (rate calculation)
- **RFQ**: Request for Quotation
- **PO**: Purchase Order
- **GRN**: Goods Receipt Note
- **OCR**: Optical Character Recognition
- **LLM**: Large Language Model
- **MCP**: Model Context Protocol
- **Spec-Kit**: GitHub documentation specification standard

**Agency Abbreviations**:
- **RIM**: Research Institute Manila
- **CKVC**: Corporate Knowledge & Value Creation
- **BOM**: Business Operations Management
- **JPAL**: J-PAL Southeast Asia
- **JLI**: Joint Learning Initiative
- **JAP**: Joint Advocacy Program
- **LAS**: Legal Advisory Services
- **RMQB**: Research Methods & Quality Bureau

**Roles**:
- **FD**: Finance Director
- **AM**: Account Manager
- **PO**: Procurement Officer

---

## 12. Related Documents

### Core Documentation (Spec-Kit Compliant)
- **CLAUDE.md**: [CLAUDE.md](CLAUDE.md) (AI assistant context, v2025-11-09, 24 sections)
- **TASKS.md**: [TASKS.md](TASKS.md) (Sprint 5 tasks, dependencies, epic tracking)
- **PLANNING.md**: [PLANNING.md](PLANNING.md) (Wave milestones, KPIs, resource allocation)
- **CHANGELOG.md**: [CHANGELOG.md](CHANGELOG.md) (Semantic versioning, migration notes)
- **PRD.md**: [PRD.md](PRD.md) (This document)

### Pulser Orchestrator Documentation (v4.0.0)
- **PRD_PULSER.md**: `docs/pulser/PRD_PULSER.md` (Pending - TSK-007)
- **Tasks**: `docs/pulser/tasks.md` (Pending - TSK-007)
- **Planning**: `docs/pulser/planning.md` (Pending - TSK-007)
- **Changelog**: `docs/pulser/CHANGELOG_PULSER.md` (Pending - TSK-007)
- **Spec-Kit Metadata**: `docs/pulser/doc.yaml` (Pending - TSK-007)

### Architecture & Design
- **PRD (Enterprise SaaS)**: [docs/PRD_ENTERPRISE_SAAS_PARITY.md](docs/PRD_ENTERPRISE_SAAS_PARITY.md) (Detailed epic-level PRD)
- **Roadmap**: [docs/ROADMAP.md](docs/ROADMAP.md) (Waves 1-9 overview)
- **Architecture**: `ARCHITECTURE.md` (To be consolidated - Issue-002)
- **SuperClaude Architecture**: [docs/SUPERCLAUDE_ARCHITECTURE.md](docs/SUPERCLAUDE_ARCHITECTURE.md)

### Infrastructure & Deployment
- **Deployment Checklist**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Quickstart Guide**: [QUICKSTART.md](QUICKSTART.md)
- **Security Audit**: [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)
- **Module Reference**: [MODULES.md](MODULES.md)

### Navigation
- **Documentation Index**: `docs/INDEX.md` (Pending - TSK-015)

---

**Maintainer**: InsightPulse AI Team
**Repository**: https://github.com/jgtolentino/insightpulse-odoo
**License**: AGPL-3.0
**Odoo Version**: 18 CE (consistent across project)
**Last Updated**: 2025-11-09 (Wave 4, Sprint 5 - Spec-Kit compliance)
**Document Version**: 4.0.0
