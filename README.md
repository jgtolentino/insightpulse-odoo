# 🚀 InsightPulse Odoo - Enterprise SaaS Replacement Suite

[![CI Status](https://github.com/jgtolentino/insightpulse-odoo/workflows/CI/badge.svg)](https://github.com/jgtolentino/insightpulse-odoo/actions)
[![Deploy Status](https://github.com/jgtolentino/insightpulse-odoo/workflows/Deploy/badge.svg)](https://github.com/jgtolentino/insightpulse-odoo/actions)
[![Stack Validation](https://github.com/jgtolentino/insightpulse-odoo/workflows/Stack%20Validation/badge.svg)](https://github.com/jgtolentino/insightpulse-odoo/actions)
[![SaaS Parity](https://img.shields.io/badge/SaaS%20Parity-87%25-green)](docs/saas-parity/)
[![Test Coverage](https://img.shields.io/badge/tests-134%20methods-blue)](tests/)
[![License](https://img.shields.io/badge/license-LGPL--3.0-blue)](LICENSE)

> **Enterprise-grade multi-tenant SaaS platform** built on Odoo 18.0 CE + OCA modules with embedded BI and AI capabilities.
>
> Replicate key enterprise processes in an open, modular framework optimized for mid-market services businesses at **< $20/month** (87-91% cost reduction vs traditional enterprise stacks).

---

## 📊 SaaS Replacement Matrix

Replace $60K+/year in SaaS subscriptions with self-hosted alternatives:

| SaaS Product | Annual Cost | InsightPulse Equivalent | Parity | Savings |
|--------------|-------------|-------------------------|--------|---------|
| Notion Enterprise (50 users) | $12,000 | Odoo Knowledge + Custom | 87% | $12,000 |
| SAP Concur | $18,000 | `ipai_expense` + OCR | 85% | $18,000 |
| SAP Ariba | $15,000 | `ipai_procure` + OCA | 90% | $15,000 |
| Tableau | $8,400 | Apache Superset | 110% | $8,400 |
| Slack Business+ | $3,600 | Mattermost (optional) | 95% | $3,600 |
| Jira Software | $4,200 | `ipai_ppm` + Odoo Project | 95% | $4,200 |
| **TOTAL** | **$61,200/yr** | **$240/yr** (hosting) | **87%** | **$58,800/yr** 🎉 |

**3-Year Savings: $176,400** | **Annual Infrastructure: $240** (DigitalOcean droplet)

📈 **[Detailed Parity Analysis](docs/saas-parity/)** - Feature comparison matrices, gap tracking, migration guides

---

## 🎯 What Is This?

A complete **Finance Shared Service Center** platform built on:
- **Odoo 18.0 CE** (open-source ERP core)
- **OCA Modules** (community-maintained extensions)
- **Custom Modules** (10 enterprise modules, 134 test methods, 2,771 lines of tests)
- **Self-Hosted Tools** (Superset, n8n, Authentik, MinIO, Qdrant)

**Designed For:**
- ✅ Multi-company consolidation (8 affiliated agencies: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- ✅ Philippines BIR compliance (Forms 1601-C, 1702-RT, 2550Q, ATP)
- ✅ Month-end closing workflows with audit trail
- ✅ AI-powered document processing (PaddleOCR + OpenAI)
- ✅ Advanced analytics (5 pre-built Superset dashboards)
- ✅ Semantic search + AI assistant (pgVector + GPT-4o-mini)

---

## 🚀 Quick Start

### Prerequisites
- Docker 24+ & Docker Compose 2.20+
- 8GB RAM minimum (16GB recommended)
- 50GB disk space

### 1-Command Local Deploy (2 minutes)
```bash
git clone --recursive https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo
make init && make dev
```

🌐 **Odoo**: http://localhost:8069 (admin / admin)
📊 **Superset**: http://localhost:8088
🔧 **n8n**: http://localhost:5678

### Production Deploy (DigitalOcean Droplet - 10 minutes)
```bash
# SSH into fresh Ubuntu 24.04 droplet (4GB/2vCPU, $24/month)
ssh root@your-droplet-ip

# Clone and deploy
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo/scripts/deploy
chmod +x *.sh && bash deploy-all.sh
```

**Includes**: Odoo 19 + PostgreSQL 16 + Nginx + Let's Encrypt SSL + S3 backups

📚 **[Full Deployment Guide](docs/deployment/digitalocean-production.md)**

### Repository Structure

This repository follows a **Supabase-first monorepo layout** with clear separation of concerns:
- **`supabase/`** - Canonical deploy surface (migrations, edge functions)
- **`runtime/`** - Execution scaffolding (Odoo 19, local dev)
- **`addons/`** - Custom Odoo modules
- **`vendor/`** - External dependencies (Odoo source, OCA modules)
- **`tools/claude-plugin/`** - AI agents, skills, and automation

📐 **[Detailed Structure Documentation](MONOREPO_STRUCTURE.md)** - Directory layout, integration patterns, deployment strategies

---

## 📦 What's Included

### ✅ Wave 1-3 Complete - Production Ready

**10 Enterprise Modules** | **134 Test Methods** | **2,771 Lines of Tests**

| Category | Modules | Purpose |
|----------|---------|---------|
| **Finance** | 6 modules | Rate calculation, project costing, procurement, subscriptions, expenses, approvals |
| **SaaS Ops** | 1 module | Multi-tenant provisioning, backups, usage tracking |
| **Analytics** | 2 modules | Apache Superset integration (5 dashboards), BI connector |
| **AI/Knowledge** | 1 module | Semantic search + /ask API (pgVector + OpenAI) |

---

## 🧩 Core Modules - Business Capabilities

### Finance & Operations

#### 1. **Rate Policy Automation** (`ipai_rate_policy`)
**Purpose**: Automated rate calculation with P60 + 25% markup logic
- Configurable rate cards (hourly, daily, project-based)
- P60 compliance calculations
- Multi-currency support with real-time conversion
- Rate approval workflows with audit trail

**Usage**: `Finance → Rate Policies → Create Policy`
**Docs**: [ipai_rate_policy/README.md](addons/insightpulse/finance/ipai_rate_policy/README.md)

---

#### 2. **Program & Project Management** (`ipai_ppm`)
**Purpose**: Enterprise program/roadmap/budget/risk management (Jira replacement)
- Multi-level project hierarchy (Program → Project → Task)
- Budget tracking with variance analysis
- Risk register with mitigation planning
- Gantt charts and timeline visualizations

**Usage**: `Projects → Programs → Create Program`
**Docs**: [ipai_ppm/README.md](addons/insightpulse/finance/ipai_ppm/README.md)

---

#### 3. **Cost Sheet Analysis** (`ipai_ppm_costsheet`)
**Purpose**: Tax-aware project costing with role-based visibility
- Detailed project cost breakdown by resource/category
- Role-based rate redaction (Account Manager vs Finance Director)
- Tax-inclusive/exclusive margin calculations
- Real-time cost vs budget tracking with alerts

**Usage**: `Projects → Project → Cost Sheet`
**Docs**: [ipai_ppm_costsheet/README.md](insightpulse_odoo/addons/insightpulse/finance/ipai_ppm_costsheet/README.md)

---

#### 4. **Procurement & Supplier Management** (`ipai_procure`)
**Purpose**: Strategic sourcing with multi-round RFQ workflows (SAP Ariba replacement)
- Multi-vendor RFQ comparison matrices
- Supplier scorecards and performance tracking
- Contract management with renewal alerts
- Automated PO generation from approved RFQs

**Usage**: `Procurement → RFQs → Create RFQ`
**Docs**: [ipai_procure/README.md](insightpulse_odoo/addons/insightpulse/ops/ipai_procure/README.md)

---

#### 5. **OCR Expense Automation** (`ipai_expense`)
**Purpose**: AI-powered receipt OCR with policy validation (SAP Concur replacement)
- Upload receipt → Auto-extract vendor, date, amount, tax
- PaddleOCR-VL integration (external service)
- Policy validation (amount limits, category restrictions)
- OpenAI GPT-4o-mini post-processing for accuracy

**Integration**: `https://ade-ocr-backend-d9dru.ondigitalocean.app`
**Usage**: `Expenses → Upload Receipt → Auto-Fill`
**Docs**: [ipai_expense/README.md](insightpulse_odoo/addons/insightpulse/finance/ipai_expense/README.md)

---

#### 6. **Subscription Management** (`ipai_subscriptions`)
**Purpose**: Recurring revenue (MRR/ARR) lifecycle management
- Recurring billing cycles (monthly, quarterly, annual)
- Automated invoice generation with payment reminders
- Revenue recognition (deferred → recognized)
- Subscription analytics dashboard (churn, expansion, renewal)

**Usage**: `Subscriptions → Create Subscription`
**Docs**: [ipai_subscriptions/README.md](insightpulse_odoo/addons/insightpulse/finance/ipai_subscriptions/README.md)

---

### Approval & Governance

#### 7. **Multi-Stage Approval Workflows** (`ipai_approvals`)
**Purpose**: Escalation-aware approval routing for expenses/POs/invoices
- Configurable approval rules (amount thresholds, departments, roles)
- Multi-level approval chains with parallel/sequential routing
- 3-day escalation triggers (timeout, threshold breach)
- Audit trail with user + timestamp + reason logging

**Usage**: `Approvals → Configure Rules → Apply to Documents`
**Docs**: [ipai_approvals/README.md](insightpulse_odoo/addons/insightpulse/finance/ipai_approvals/README.md)

---

### SaaS Operations

#### 8. **Tenant Management** (`ipai_saas_ops`)
**Purpose**: Multi-tenant provisioning, backups, usage metering
- Self-service tenant creation with resource quotas
- Automated backup scheduling (daily, weekly, on-demand)
- Usage tracking and billing integration
- Tenant isolation and security controls

**Usage**: `Operations → SaaS Tenants → Create Tenant`
**Docs**: [ipai_saas_ops/README.md](addons/insightpulse/ops/ipai_saas_ops/README.md)

---

### Analytics & Business Intelligence

#### 9. **Apache Superset Integration** (`superset_connector`)
**Purpose**: BI dashboards with row-level security (Tableau replacement)
- **5 Pre-built Dashboards**: Sales Executive, Financial Performance, Inventory Ops, HR Analytics, Procurement Insights
- Row-level security (RLS) for multi-company/multi-tenant
- Real-time data sync with Odoo
- Drill-down analytics and custom chart builder

**Usage**: `BI → Superset → Open Dashboard`
**Docs**: [superset_connector/README.md](insightpulse_odoo/addons/insightpulse/ops/superset_connector/README.md)

---

### AI & Knowledge Management

#### 10. **AI Knowledge Workspace** (`ipai_knowledge_ai`)
**Purpose**: Semantic search + /ask API powered by pgVector + OpenAI (Notion replacement)
- Vector embeddings for documentation (pgVector via Supabase)
- `/ask_ai` API endpoint with GPT-4o-mini responses
- Auto-embedding generation (~200ms per block)
- Performance: <50ms search latency, ~2s E2E response time

**Usage**: `Knowledge → AI Workspaces → Ask AI`
**Quickstart**: [ipai_knowledge_ai/QUICKSTART.md](insightpulse_odoo/addons/insightpulse/knowledge/ipai_knowledge_ai/QUICKSTART.md)
**Docs**: [ipai_knowledge_ai/README.md](insightpulse_odoo/addons/insightpulse/knowledge/ipai_knowledge_ai/README.md)

---

## 🏗️ Architecture

### Technology Stack
- **Odoo**: 19.0 CE + OCA modules (Python 3.11)
- **Database**: PostgreSQL 16 + pgVector (Supabase pooler, port 6543)
- **Container**: Docker 24.0+ (multi-stage build, 512MB RAM optimized)
- **BI**: Apache Superset 3.0+ (open-source)
- **Workflow**: n8n (workflow automation, Zapier alternative)
- **SSO**: Authentik (SAML/OAuth provider)
- **Storage**: MinIO (S3-compatible object storage)
- **Vector DB**: Qdrant (alternative to pgVector for AI search)
- **AI**: OpenAI GPT-4o-mini + PaddleOCR-VL (document understanding)
- **Deployment**: DigitalOcean (Droplet or App Platform)

### Production Architecture
```
┌─────────────────────────────────────────────────────────┐
│               Nginx (Reverse Proxy + SSL)               │
│                  Let's Encrypt SSL/TLS                   │
└────────────┬─────────────────────────────────┬──────────┘
             │                                 │
    ┌────────▼────────┐               ┌───────▼────────┐
    │   Odoo 19 CE    │               │  Apache         │
    │   (8 Companies) │               │  Superset       │
    │                 │               │  (BI Analytics) │
    │  - Finance SSC  │               └─────────────────┘
    │  - Procurement  │
    │  - Expense Mgmt │               ┌─────────────────┐
    │  - Knowledge    │               │  n8n            │
    │  - AI Services  │               │  (Workflows)    │
    └────────┬────────┘               └─────────────────┘
             │
    ┌────────▼────────┐               ┌─────────────────┐
    │  PostgreSQL 16  │               │  Authentik      │
    │  + pgvector     │               │  (SSO/SAML)     │
    │  + TimescaleDB  │               └─────────────────┘
    └────────┬────────┘
             │                        ┌─────────────────┐
    ┌────────▼────────┐               │  MinIO          │
    │    Supabase     │               │  (S3 Storage)   │
    │   (Backups)     │               └─────────────────┘
    └─────────────────┘
```

**Memory Budget Optimization**:
- Odoo workers: 2 (optimized from 4)
- Cron threads: 1
- Max DB connections: 8
- Memory limits: 400MB hard, 320MB soft
- Asset bundling: Production mode

---

## 💰 Cost Optimization - Enterprise for SME Budget

### Infrastructure Costs

| Item | Traditional (Azure) | InsightPulse (DO) | Savings |
|------|---------------------|-------------------|---------|
| **App Platform** | $50-100/month | $5/month | 90-95% |
| **Database** | $25-50/month | $0 (Supabase free) | 100% |
| **OCR Service** | $30/month (Azure AI) | $5/month (PaddleOCR) | 83% |
| **AI/LLM** | $20/month (Azure OpenAI) | $10/month (OpenAI direct) | 50% |
| **BI Platform** | $25/month (Power BI) | $0 (Superset OSS) | 100% |
| **Total** | **$150-225/month** | **< $20/month** | **87-91%** |

**Annual Infrastructure Savings**: $1,560-2,460 per deployment

### Total Cost of Ownership (3 Years)

| Category | Enterprise SaaS | InsightPulse | Savings |
|----------|----------------|--------------|---------|
| **Software Licenses** | $183,600 | $0 | $183,600 |
| **Infrastructure** | $5,400 | $720 | $4,680 |
| **Implementation** | $30,000 | $10,000 | $20,000 |
| **Support** | $18,000 | $0 (self) | $18,000 |
| **Total (3 years)** | **$237,000** | **$10,720** | **$226,280** |

**ROI: 95.5% cost reduction**

---

## 🧪 Test Coverage - Wave 3 Validation

**Test Suite Statistics**:
- **17 test files** across modules
- **134 test methods** (unit + integration + E2E)
- **2,771 lines** of test code
- **Coverage**: Unit tests, integration tests, E2E workflows, performance benchmarks

**Test Categories**:
```
tests/
├── unit/
│   ├── test_finance_ssc/
│   ├── test_expense_management/
│   └── test_procurement/
├── integration/
│   ├── test_rate_policy_costsheet_integration.py
│   └── test_approval_expense_integration.py
├── e2e/
│   ├── playwright/
│   └── test_procurement_workflow.py
└── performance/
    └── test_performance_benchmarks.py
```

**Run Tests**:
```bash
# Full test suite
make test

# Specific test categories
python -m pytest tests/integration/ -v
python -m pytest tests/e2e/ -v
python -m pytest tests/performance/ -v
```

---

## 📚 Documentation

### Quick Start & Deployment
- **[Main README](README.md)** - This file
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute deployment (local, DigitalOcean, custom Docker)
- **[docs/deployment/local-development.md](docs/deployment/local-development.md)** - Dev environment setup
- **[docs/deployment/digitalocean-production.md](docs/deployment/digitalocean-production.md)** - Production deployment guide
- **[scripts/deploy/README.md](scripts/deploy/README.md)** - Automated deployment scripts

### Architecture & Design
- **[docs/architecture/README.md](docs/architecture/)** - System architecture overview
- **[docs/architecture/tech-stack.md](docs/architecture/tech-stack.md)** - Complete tech stack
- **[docs/architecture/decisions/](docs/architecture/decisions/)** - Architecture Decision Records (ADRs)
- **[docs/architecture/integrations/](docs/architecture/integrations/)** - Third-party service integration guides

### SaaS Parity & Gap Analysis
- **[docs/saas-parity/README.md](docs/saas-parity/)** - SaaS feature equivalence overview
- **[docs/saas-parity/notion-enterprise.md](docs/saas-parity/notion-enterprise.md)** - Notion → Odoo Knowledge mapping
- **[docs/saas-parity/sap-concur.md](docs/saas-parity/sap-concur.md)** - Concur → ipai_expense mapping
- **[docs/saas-parity/sap-ariba.md](docs/saas-parity/sap-ariba.md)** - Ariba → ipai_procure mapping
- **[docs/saas-parity/tableau.md](docs/saas-parity/tableau.md)** - Tableau → Superset mapping
- **[docs/saas-parity/gap-matrix.csv](docs/saas-parity/gap-matrix.csv)** - Automated gap tracking

### User Guides
- **[docs/user-guides/finance-team/](docs/user-guides/finance-team/)** - Finance team workflows
- **[docs/user-guides/admin/](docs/user-guides/admin/)** - System administration
- **[docs/user-guides/developer/](docs/user-guides/developer/)** - Developer guides

### Compliance & Security
- **[docs/compliance/bir-requirements.md](docs/compliance/bir-requirements.md)** - Philippines BIR compliance
- **[docs/compliance/gdpr.md](docs/compliance/gdpr.md)** - GDPR compliance checklist
- **[docs/compliance/soc2.md](docs/compliance/soc2.md)** - SOC 2 controls mapping
- **[SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)** - Complete security audit

### Repository Operations & CI/CD
- **[docs/REPO_STATE_OF_UNION_2025-11.md](docs/REPO_STATE_OF_UNION_2025-11.md)** - 📊 Current state of CI/CD, SRE, and AI infrastructure
- **[docs/ISSUE_RESOLUTION_SUMMARY.md](docs/ISSUE_RESOLUTION_SUMMARY.md)** - Historic issue cleanup and resolution guidance
- **[.github/workflows/README.md](.github/workflows/README.md)** - Complete workflow inventory (~76 workflows)
- **[docs/CI_CD_FIXES_SUMMARY.md](docs/CI_CD_FIXES_SUMMARY.md)** - Recent CI/CD improvements
- **[docs/CANARY_DEPLOYMENT_GUIDE.md](docs/CANARY_DEPLOYMENT_GUIDE.md)** - Canary deployment strategy
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines and development workflow

### Module-Specific Documentation
- **Finance Modules**: [ipai_rate_policy](addons/insightpulse/finance/ipai_rate_policy/README.md), [ipai_ppm](addons/insightpulse/finance/ipai_ppm/README.md), [ipai_ppm_costsheet](insightpulse_odoo/addons/insightpulse/finance/ipai_ppm_costsheet/README.md)
- **Operations**: [ipai_procure](insightpulse_odoo/addons/insightpulse/ops/ipai_procure/README.md), [ipai_saas_ops](addons/insightpulse/ops/ipai_saas_ops/README.md), [ipai_approvals](insightpulse_odoo/addons/insightpulse/finance/ipai_approvals/README.md)
- **Analytics & AI**: [superset_connector](insightpulse_odoo/addons/insightpulse/ops/superset_connector/README.md), [ipai_knowledge_ai](insightpulse_odoo/addons/insightpulse/knowledge/ipai_knowledge_ai/README.md)
- **Expense Management**: [ipai_expense](insightpulse_odoo/addons/insightpulse/finance/ipai_expense/README.md), [ipai_subscriptions](insightpulse_odoo/addons/insightpulse/finance/ipai_subscriptions/README.md)

---

## 🔧 Common Tasks

```bash
# Start all services
make up

# View logs
make logs

# Run tests
make test

# Deploy to production
make deploy-prod

# Backup database
make backup

# Update OCA modules
make update-oca

# Create new custom module
make create-module NAME=my_new_module

# Open Odoo shell
make shell

# Open PostgreSQL shell
make psql
```

---

## 🤖 Development Agent Capabilities

This repository includes **AI agent skills** for automated operations:

### OpenAI Cookbook Automation Stack
- **`ai_stack/`** reusable Python package following [OpenAI Cookbook](https://cookbook.openai.com/) patterns
- **CLI**: `python3 agents/issue-classifier.py --title "..." --body-file issue.md`
- Generates JSON analysis and `plan.yaml` for implementation
- Validates LLM structured outputs with Pydantic before execution

### Odoo Module Development Skills
- **odoo-vendor-management**: Privacy-first vendor portals
- **odoo-expense-automation**: OCR-powered expense workflows
- **odoo-analytics-bridge**: BI dashboard integration
- **odoo-module-generator**: OCA-compliant module scaffolding

**Skills Catalog**: `~/.claude/superclaude/skills/odoo/SKILLS_INDEX.md`

### Agent Usage Examples

**Create a Custom Module**:
```
Create a sales commission module that calculates tiered commissions
for salespeople based on monthly revenue targets.
```

**Design BI Dashboard**:
```
Design a Superset dashboard for CFO showing cash flow, AR aging,
and P&L trends with drill-down by department.
```

**Implement Integration**:
```
Implement a webhook connector to sync Odoo invoices with
QuickBooks Online using their REST API.
```

---

## 🔐 Security & Compliance

### Built-in Security Features
- **RLS (Row-Level Security)**: All Supabase tables enforce tenant isolation
- **Service Role Keys**: Backend-only (never exposed to frontend)
- **API Authentication**: Bearer token with rate limiting
- **Secret Management**: Environment variables only (zero secrets in database/repo)
- **Encrypted Connections**: SSL/TLS enforced for PostgreSQL and all API calls
- **Audit Logs**: All approval actions logged (user + timestamp + reason)
- **SAML SSO**: Authentik integration for enterprise single sign-on
- **2FA**: TOTP support via OCA `auth_totp` module

### Compliance
- **LGPL-3.0 License**: All custom modules
- **OCA Guidelines**: Module structure and coding standards
- **GDPR Ready**: Data privacy controls and RLS policies
- **SOC 2 Type II**: DigitalOcean infrastructure compliance
- **Philippines BIR**: Tax compliance modules and reporting

**Full Audit**: [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)

---

## 🚀 Deployment Options

### 1. Local Development (2 minutes)
```bash
make init && make dev
open http://localhost:8069
```

### 2. Production Droplet - Automated (10 minutes)
```bash
# SSH into fresh Ubuntu 24.04 droplet (4GB/2vCPU, $24/month)
ssh root@your-droplet-ip

# Clone and deploy
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo/scripts/deploy
chmod +x *.sh && bash deploy-all.sh
```

**Infrastructure**: Odoo 19 + PostgreSQL 16 + Nginx + Let's Encrypt SSL + S3 backups
**Full Guide**: [docs/deployment/digitalocean-production.md](docs/deployment/digitalocean-production.md)

### 3. DigitalOcean App Platform (5 minutes)
```bash
# Deploy via doctl
doctl apps create --spec infra/do/odoo-app.yaml

# Or automated
./scripts/deploy-to-production.sh
```

**Cost**: $5-10/month (basic-xs instance + Supabase free tier)

### 4. Custom Docker Build
```bash
# Build production image
docker build -t insightpulse-odoo:19.0 .

# Run with environment variables
docker run -d \
  -e ODOO_DB_HOST=your-db-host \
  -e ODOO_DB_USER=odoo \
  -e ODOO_DB_PASSWORD=secret \
  -p 8069:8069 \
  insightpulse-odoo:19.0
```

---

## 📁 Repository Structure

```
insightpulse-odoo/
├── .github/workflows/              # CI/CD automation
│   ├── ci-odoo.yml                # Test Odoo modules
│   ├── cd-deploy.yml              # Deploy to DigitalOcean
│   ├── oca-update.yml             # Auto-update OCA modules
│   ├── backup-schedule.yml        # Daily backups to Supabase
│   └── security-scan.yml          # Trivy/Snyk security scans
│
├── docs/                          # Documentation hub
│   ├── architecture/              # System architecture & ADRs
│   ├── saas-parity/               # SaaS feature equivalence
│   ├── deployment/                # Deployment guides
│   ├── user-guides/               # End-user documentation
│   └── compliance/                # Compliance & security
│
├── odoo/                          # Odoo core (submodule)
├── addons/                        # OCA community modules
│   ├── oca-server-tools/          # OCA server utilities
│   ├── oca-account-*/             # OCA accounting modules
│   ├── oca-knowledge/             # OCA knowledge management
│   └── ...
│
├── custom/                        # Custom modules (your IP)
│   ├── insightpulse_base/         # Base module
│   ├── finance_ssc/               # Finance Shared Service Center
│   ├── expense_management/        # SAP Concur replacement
│   ├── procurement/               # SAP Ariba replacement
│   ├── knowledge_base/            # Notion replacement
│   ├── ai_services/               # InsightPulse AI
│   ├── analytics_connector/       # Superset integration
│   └── philippines_localization/  # PH-specific modules
│
├── third_party/                   # 3rd party self-hosted services
│   ├── superset/                  # Apache Superset (BI)
│   ├── n8n/                       # n8n (workflow automation)
│   ├── minio/                     # MinIO (S3-compatible storage)
│   ├── authentik/                 # Authentik (SSO/SAML provider)
│   ├── mattermost/                # Mattermost (Slack alternative)
│   └── qdrant/                    # Qdrant (vector database)
│
├── infrastructure/                # Infrastructure as Code
│   ├── docker/                    # Docker configs
│   ├── terraform/                 # DigitalOcean provisioning
│   ├── ansible/                   # Configuration management
│   └── kubernetes/                # K8s manifests (future)
│
├── scripts/                       # Automation scripts
│   ├── setup/                     # Initial setup scripts
│   ├── deployment/                # Deployment automation
│   ├── maintenance/               # Backup, update, health check
│   ├── development/               # Dev tools (create-module, test, lint)
│   └── migration/                 # Data migration scripts
│
├── tests/                         # Test suites
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   ├── e2e/                       # End-to-end tests
│   └── performance/               # Performance benchmarks
│
├── config/                        # Configuration files
│   ├── odoo.conf                  # Odoo configuration
│   ├── .env.example               # Environment variables template
│   ├── logging/                   # Logging configs
│   └── monitoring/                # Prometheus, Grafana
│
├── data/                          # Initial data & fixtures
│   ├── demo/                      # Demo data (8 agencies)
│   ├── migration/                 # Legacy data import
│   └── localization/              # PH chart of accounts
│
├── tools/                         # Development tools
│   ├── oca-module-finder/         # Find OCA modules
│   ├── gap-analyzer/              # Auto-generate gap reports
│   └── saas-feature-tracker/      # Track SaaS parity
│
├── Makefile                       # Common commands
├── docker-compose.yml             # Main orchestration
├── README.md                      # This file
├── LICENSE                        # LGPL-3.0
└── CONTRIBUTING.md                # Contribution guidelines
```

---

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes following OCA guidelines
4. Write tests (unit + integration minimum)
5. Run validation: `make test`
6. Commit: `git commit -m 'feat: add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open Pull Request

### Code Quality Standards
- ✅ OCA module structure compliance
- ✅ Python type hints (3.11+)
- ✅ Google-style docstrings
- ✅ Unit + integration tests for new features
- ✅ Documentation updates (README + CHANGELOG)
- ✅ Security audit passed (no hardcoded secrets)
- ✅ Performance validation (no N+1 queries)

**Full Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📝 License

This project is licensed under the **LGPL-3.0 License** - see the [LICENSE](LICENSE) file for details.

---

## 🤖 For AI Assistants

This repository includes AI assistant instructions for code generation and architectural guidance. See [claude.md](claude.md) for:
- Multi-tenant architecture rules
- BIR compliance patterns
- Code generation guardrails
- Security best practices
- Conditional deployment triggers

**For operational tasks** (installation, monitoring, troubleshooting), refer to this README.

---

## 🙏 Acknowledgments

- [Odoo Community Association (OCA)](https://github.com/OCA) - Community modules and development standards
- [Apache Superset](https://superset.apache.org/) - Open-source business intelligence platform
- [Supabase](https://supabase.com/) - PostgreSQL + pgVector managed database
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - Document OCR engine
- [OpenAI](https://openai.com/) - GPT-4o-mini API and embeddings
- [n8n](https://n8n.io/) - Workflow automation (Zapier alternative)
- [Authentik](https://goauthentik.io/) - SSO/SAML provider
- [MinIO](https://min.io/) - S3-compatible object storage

---

## 📧 Support & Community

- **Issues**: [GitHub Issues](https://github.com/jgtolentino/insightpulse-odoo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jgtolentino/insightpulse-odoo/discussions)
- **Email**: support@insightpulseai.net
- **Documentation**: [docs/](docs/) directory

---

## 🗺️ Roadmap

- [x] **Wave 1**: Finance & Operations Foundation (4 modules) ✅
- [x] **Wave 2**: Advanced Operations & Analytics (6 modules) ✅
- [x] **Wave 3**: Testing & Documentation (134 test methods) ✅
- [ ] **Wave 4**: Enterprise Repository Structure (docs, third_party, infrastructure)
- [ ] **Wave 5**: Kubernetes deployment templates + Helm charts
- [ ] **Wave 6**: Multi-language localization (ES, FR, DE, PT)
- [ ] **Wave 7**: Mobile app (React Native) for expense submission
- [ ] **Wave 8**: GraphQL API layer for headless integrations
- [ ] **Wave 9**: Predictive analytics with MindsDB integration

**Detailed Roadmap**: [docs/ROADMAP.md](docs/ROADMAP.md)

---

**Version**: 4.0.0 (Enterprise Structure)
**Last Updated**: 2025-11-05
**Odoo Version**: 19.0 CE + OCA
**Status**: Production Ready ✅
**Test Coverage**: 134 test methods, 2,771 lines of tests
**Modules**: 10 enterprise modules + OCA community modules
**Monthly Cost**: < $20 USD (87-91% reduction vs enterprise stacks)
**SaaS Parity**: 87% feature equivalence
**Annual Savings**: $58,800 in SaaS costs + $1,560-2,460 in infrastructure
