# InsightPulse Odoo - SaaS Parity Platform

**Enterprise-grade multi-tenant SaaS platform** built on Odoo 19.0 CE + OCA modules with embedded BI and AI capabilities.

Replicate key enterprise processes in an open, modular framework optimized for mid-market services businesses at **< $20/month** (87% cost reduction vs traditional enterprise stacks).

---

## 🚀 Quick Start - 5 Minutes to Production

```bash
# Clone repository with submodules
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo
git submodule update --init --recursive

# Start with Docker
docker compose up -d

# Access Odoo
open http://localhost:8069
# Default: admin / admin
```

**Full deployment guide**: See [QUICKSTART.md](QUICKSTART.md) for local, DigitalOcean, and custom Docker options.

---

## ✅ Wave 1-3 Complete - Production Ready

**10 Enterprise Modules** | **134 Test Methods** | **2,771 Lines of Tests**

### What's Included

| Category | Modules | Purpose |
|----------|---------|---------|
| **Finance** | 6 modules | Rate calculation, project costing, procurement, subscriptions, expenses, approvals |
| **SaaS Ops** | 1 module | Multi-tenant provisioning, backups, usage tracking |
| **Analytics** | 2 modules | Apache Superset integration (5 dashboards), BI connector |
| **AI/Knowledge** | 1 module | Semantic search + /ask API (pgVector + OpenAI) |

---

## 📦 Core Modules - Business Capabilities

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
**Purpose**: Enterprise program/roadmap/budget/risk management
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
**Purpose**: Strategic sourcing with multi-round RFQ workflows
- Multi-vendor RFQ comparison matrices
- Supplier scorecards and performance tracking
- Contract management with renewal alerts
- Automated PO generation from approved RFQs

**Usage**: `Procurement → RFQs → Create RFQ`
**Docs**: [ipai_procure/README.md](insightpulse_odoo/addons/insightpulse/ops/ipai_procure/README.md)

---

#### 5. **OCR Expense Automation** (`ipai_expense`)
**Purpose**: AI-powered receipt OCR with policy validation
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
**Purpose**: BI dashboards with row-level security
- **5 Pre-built Dashboards**: Sales Executive, Financial Performance, Inventory Ops, HR Analytics, Procurement Insights
- Row-level security (RLS) for multi-company/multi-tenant
- Real-time data sync with Odoo
- Drill-down analytics and custom chart builder

**Usage**: `BI → Superset → Open Dashboard`
**Docs**: [superset_connector/README.md](insightpulse_odoo/addons/insightpulse/ops/superset_connector/README.md)

---

### AI & Knowledge Management

#### 10. **AI Knowledge Workspace** (`ipai_knowledge_ai`)
**Purpose**: Semantic search + /ask API powered by pgVector + OpenAI
- Vector embeddings for documentation (pgVector via Supabase)
- `/ask_ai` API endpoint with GPT-4o-mini responses
- Auto-embedding generation (~200ms per block)
- Performance: <50ms search latency, ~2s E2E response time

**Usage**: `Knowledge → AI Workspaces → Ask AI`
**Quickstart**: [ipai_knowledge_ai/QUICKSTART.md](insightpulse_odoo/addons/insightpulse/knowledge/ipai_knowledge_ai/QUICKSTART.md)
**Docs**: [ipai_knowledge_ai/README.md](insightpulse_odoo/addons/insightpulse/knowledge/ipai_knowledge_ai/README.md)

---

## 💰 Cost Optimization - Enterprise for SME Budget

| Item | Traditional (Azure) | InsightPulse (DO) | Savings |
|------|---------------------|-------------------|---------|
| **App Platform** | $50-100/month | $5/month | 90-95% |
| **Database** | $25-50/month | $0 (Supabase free) | 100% |
| **OCR Service** | $30/month (Azure AI) | $5/month (PaddleOCR) | 83% |
| **AI/LLM** | $20/month (Azure OpenAI) | $10/month (OpenAI direct) | 50% |
| **BI Platform** | $25/month (Power BI) | $0 (Superset OSS) | 100% |
| **Total** | **$150-225/month** | **< $20/month** | **87-91%** |

**Annual Savings**: $1,560-2,460 per deployment

---

## 🏗️ Architecture

### Technology Stack
- **Odoo**: 19.0 CE + OCA modules (Python 3.11)
- **Database**: PostgreSQL 16 (Supabase pooler, port 6543)
- **Container**: Docker 24.0+ (multi-stage build, 512MB RAM optimized)
- **BI**: Apache Superset 3.0+ (open-source)
- **Vector DB**: pgVector extension (via Supabase)
- **AI**: OpenAI GPT-4o-mini + PaddleOCR-VL (document understanding)
- **Deployment**: DigitalOcean App Platform (Singapore region)

### Production Architecture
```
┌─────────────────────────────────────────────────┐
│ DigitalOcean App Platform (basic-xs)           │
│  ├─ Odoo 19.0 (512MB RAM, 2 workers, 1 cron)  │
│  ├─ PaddleOCR-VL Service (OCR endpoint)        │
│  └─ Supabase PostgreSQL (AWS us-east-1)        │
│     ├─ Connection pooler (port 6543)           │
│     ├─ pgVector extension (embeddings)         │
│     └─ RLS policies (multi-tenant security)    │
└─────────────────────────────────────────────────┘
           ↓ External Integrations
┌─────────────────────────────────────────────────┐
│  ├─ Apache Superset (BI dashboards)            │
│  ├─ OpenAI API (GPT-4o-mini, ~$10/month)       │
│  └─ GitHub Actions (CI/CD automation)          │
└─────────────────────────────────────────────────┘
```

**Memory Budget Optimization**:
- Odoo workers: 2 (optimized from 4)
- Cron threads: 1
- Max DB connections: 8
- Memory limits: 400MB hard, 320MB soft
- Asset bundling: Production mode

---

## 🧪 Test Coverage - Wave 3 Validation

**Test Suite Statistics**:
- **17 test files** across modules
- **134 test methods** (unit + integration + E2E)
- **2,771 lines** of test code
- **Coverage**: Unit tests, integration tests, E2E workflows, performance benchmarks

**Test Categories**:
```
insightpulse_odoo/addons/insightpulse/tests/
├── integration/
│   ├── test_rate_policy_costsheet_integration.py
│   └── test_approval_expense_integration.py
├── e2e/
│   └── test_procurement_workflow.py
├── performance/
│   └── test_performance_benchmarks.py
└── unit tests in each module
```

**Run Tests**:
```bash
# Full test suite
python -m pytest insightpulse_odoo/addons/insightpulse/tests/ -v

# Integration tests only
python -m pytest insightpulse_odoo/addons/insightpulse/tests/integration/ -v

# E2E tests
python -m pytest insightpulse_odoo/addons/insightpulse/tests/e2e/ -v

# Performance benchmarks
python -m pytest insightpulse_odoo/addons/insightpulse/tests/performance/ -v
```

---

## 📚 Documentation

### Quick Start & Deployment
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute deployment (local, DigitalOcean, custom Docker)
- **[docs/PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md)** - Complete production deployment guide for Odoo 19
- **[scripts/deploy/README.md](scripts/deploy/README.md)** - Automated deployment scripts reference
- **[MODULES.md](MODULES.md)** - Comprehensive module reference and dependency guide
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - 13-point pre-deployment validation
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Docker containerization and CI/CD pipeline

### Infrastructure & Networking
- **[docs/NETWORK_CONFIGURATION.md](docs/NETWORK_CONFIGURATION.md)** - Network architecture, DNS, SSL/TLS, and firewall configuration
- **[scripts/deploy/](scripts/deploy/)** - Production deployment automation scripts

### Security & Architecture
- **[SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)** - Complete security compliance audit
- **[ARCHITECTURE_IMPLEMENTATION_SUMMARY.md](ARCHITECTURE_IMPLEMENTATION_SUMMARY.md)** - System architecture overview
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes

### Module-Specific Documentation
- **Finance Modules**: [ipai_rate_policy](addons/insightpulse/finance/ipai_rate_policy/README.md), [ipai_ppm](addons/insightpulse/finance/ipai_ppm/README.md), [ipai_ppm_costsheet](insightpulse_odoo/addons/insightpulse/finance/ipai_ppm_costsheet/README.md), [ipai_procure](insightpulse_odoo/addons/insightpulse/ops/ipai_procure/README.md), [ipai_expense](insightpulse_odoo/addons/insightpulse/finance/ipai_expense/README.md), [ipai_subscriptions](insightpulse_odoo/addons/insightpulse/finance/ipai_subscriptions/README.md)
- **Operations**: [ipai_saas_ops](addons/insightpulse/ops/ipai_saas_ops/README.md), [ipai_approvals](insightpulse_odoo/addons/insightpulse/finance/ipai_approvals/README.md)
- **Analytics & AI**: [superset_connector](insightpulse_odoo/addons/insightpulse/ops/superset_connector/README.md), [ipai_knowledge_ai](insightpulse_odoo/addons/insightpulse/knowledge/ipai_knowledge_ai/README.md)

---

## 🤖 Development Agent Capabilities

This repository includes **SuperClaude agent skills** for AI-assisted operations:

### OpenAI Cookbook Automation Stack
- **`ai_stack/`** reusable Python package that follows the [OpenAI Cookbook](https://cookbook.openai.com/) stack for hybrid automation
  (Responses API + rule-based fallbacks)
- **CLI**: `python3 agents/issue-classifier.py --title "..." --body-file path/to/issue.md` generates JSON analysis and `plan.yaml`

### Odoo Module Development Skills
- **odoo-vendor-management**: Privacy-first vendor portals with role-based access
- **odoo-expense-automation**: OCR-powered expense workflows with policy validation
- **odoo-analytics-bridge**: BI dashboard integration patterns
- **odoo-module-generator**: OCA-compliant module scaffolding

**Skills Catalog**: `~/.claude/superclaude/skills/odoo/SKILLS_INDEX.md`

### Agent Usage Patterns

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

**Troubleshoot Performance**:
```
Our project cost sheet calculations are slow (>5s).
Help diagnose and optimize the query performance.
```

**Implement Integration**:
```
Implement a webhook connector to sync Odoo invoices with
QuickBooks Online using their REST API.
```

See [docs/AGENT.md](docs/AGENT.md) for complete agent usage guide.

---

## 🔐 Security & Compliance

### Built-in Security Features
- **RLS (Row-Level Security)**: All Supabase tables enforce tenant isolation
- **Service Role Keys**: Backend-only (never exposed to frontend)
- **API Authentication**: Bearer token with rate limiting
- **Secret Management**: Environment variables only (zero secrets in database/repo)
- **Encrypted Connections**: SSL/TLS enforced for PostgreSQL and all API calls
- **Audit Logs**: All approval actions logged (user + timestamp + reason)

### Compliance
- **LGPL-3.0 License**: All custom modules
- **OCA Guidelines**: Module structure and coding standards
- **GDPR Ready**: Data privacy controls and RLS policies
- **SOC 2 Type II**: DigitalOcean infrastructure compliance

**Full Audit**: [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)

---

## 🚀 Deployment Options

### 1. Local Development (2 minutes)
```bash
docker compose up -d
open http://localhost:8069
```

### 2. Production Droplet - Automated (10 minutes)
**NEW**: Complete automated deployment to DigitalOcean droplet with Odoo 19, PostgreSQL 16, Nginx, and SSL/TLS:

```bash
# SSH into fresh Ubuntu 24.04 droplet
ssh root@your-droplet-ip

# Clone repository
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo/scripts/deploy

# Make scripts executable
chmod +x *.sh

# Run automated deployment (prompts for domain/email)
bash deploy-all.sh
```

**Infrastructure**:
- Odoo 19 with systemd service
- PostgreSQL 16 (local)
- Nginx reverse proxy with Let's Encrypt SSL
- Automated backups to S3
- Health monitoring endpoints

**Cost**: $24/month (4GB/2vCPU droplet)

**Full Guide**: [docs/PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md)

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

**Deployment Guide**: [QUICKSTART.md](QUICKSTART.md)

---

## 📁 Repository Structure

```
insightpulse-odoo/
├── .github/workflows/       # CI/CD automation
│   ├── ci.yml              # Fast checks (linting, validation)
│   ├── odoo-ci.yml         # Odoo module tests
│   └── parity-live-sync.yml # Wave parity validation
├── addons/
│   ├── insightpulse/       # Wave 1-2 enterprise modules
│   │   ├── finance/
│   │   │   ├── ipai_rate_policy/
│   │   │   ├── ipai_ppm/
│   │   │   └── ipai_ppm_costsheet/
│   │   └── ops/
│   │       ├── ipai_saas_ops/
│   │       └── ipai_procure/
│   ├── custom/             # Legacy modules (pre-Wave)
│   │   ├── ipai_approvals/
│   │   └── ipai_core/
│   ├── oca/                # OCA community modules
│   ├── bi_superset_agent/  # Superset integration
│   └── knowledge_notion_clone/  # UI knowledge base
├── insightpulse_odoo/      # Git submodule
│   └── addons/insightpulse/
│       ├── knowledge/ipai_knowledge_ai/
│       ├── finance/ipai_expense/
│       ├── finance/ipai_subscriptions/
│       └── ops/superset_connector/
├── scripts/
│   ├── deploy-check.sh     # Pre-deployment validation
│   ├── deploy-to-production.sh  # Deployment automation
│   └── odoo-reinstall-module.sh  # Module management
├── infra/do/               # DigitalOcean app specs
├── Dockerfile              # Production-optimized build
├── docker-compose.yml      # Local development stack
└── [Documentation files]
```

---

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes following OCA guidelines
4. Write tests (unit + integration minimum)
5. Run validation: `./scripts/deploy-check.sh --full`
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

---

## 📝 License

This project is licensed under the **LGPL-3.0 License** - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- [Odoo Community Association (OCA)](https://github.com/OCA) for community modules and development standards
- [Apache Superset](https://superset.apache.org/) for open-source business intelligence platform
- [Supabase](https://supabase.com/) for PostgreSQL + pgVector managed database
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for document OCR engine
- [OpenAI](https://openai.com/) for GPT-4o-mini API and embeddings
- [SuperClaude Framework](https://github.com/anthropics/claude-code) for agent automation capabilities

---

## 📧 Support & Community

- **Issues**: [GitHub Issues](https://github.com/jgtolentino/insightpulse-odoo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jgtolentino/insightpulse-odoo/discussions)
- **Email**: support@insightpulse.ai
- **Documentation**: [docs/](docs/) directory

---

## 🗺️ Roadmap - Post Wave 3

- [x] **Wave 1**: Finance & Operations Foundation (4 modules) ✅
- [x] **Wave 2**: Advanced Operations & Analytics (6 modules) ✅
- [x] **Wave 3**: Testing & Documentation (134 test methods) ✅
- [ ] **Wave 4**: Kubernetes deployment templates + Helm charts
- [ ] **Wave 5**: Multi-language localization (ES, FR, DE, PT)
- [ ] **Wave 6**: Mobile app (React Native) for expense submission
- [ ] **Wave 7**: GraphQL API layer for headless integrations
- [ ] **Wave 8**: Predictive analytics with MindsDB integration

---

**Version**: 3.0.0 (Wave 1-3 Complete)
**Last Updated**: 2025-10-30
**Odoo Version**: 19.0 CE + OCA
**Status**: Production Ready ✅
**Test Coverage**: 134 test methods, 2,771 lines of tests
**Modules**: 10 enterprise modules + OCA community modules
**Monthly Cost**: < $20 USD (87-91% reduction vs enterprise stacks)
**Deployment Time**: 2-5 minutes
