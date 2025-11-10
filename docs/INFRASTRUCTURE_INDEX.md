# InsightPulse Odoo - Infrastructure Index & Catalog

## 📋 Quick Navigation

- [Custom Modules](#custom-modules)
- [Scripts & Utilities](#scripts--utilities)
- [CI/CD Workflows](#cicd-workflows)
- [Configuration Files](#configuration-files)
- [Documentation](#documentation)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Integration Points](#integration-points)
- [Monitoring & Observability](#monitoring--observability)

---

## Custom Modules

### 📊 Finance & Accounting Modules

#### IPAI Finance SSC
**Path**: `addons/custom/ipai_finance_ssc/`
**Version**: 19.0.251110.1
**Purpose**: Multi-agency finance shared service center
**Status**: ✅ Active

**Key Components**:
- **Models** (5): agency, month_end_closing, bir_form, bank_reconciliation, consolidation
- **Views** (6): agency, month_end_closing, bir_forms, bank_reconciliation, consolidation, menus
- **Wizards** (3): month_end_closing_wizard, bir_filing_wizard, bank_match_wizard
- **Reports** (2): trial_balance_report, bir_forms_report
- **Security Groups** (3): User, Accountant, Manager
- **Cron Jobs** (5): Month-end auto-generation, BIR form generation, Supabase sync, Notion sync

**Dependencies**:
```python
'depends': ['account', 'account_reports', 'base', 'web']
```

**Integration Points**:
- ✅ Supabase (real-time sync)
- ✅ Notion (knowledge base)
- ✅ Superset (analytics dashboards)

**Documentation**:
- Manifest: `addons/custom/ipai_finance_ssc/__manifest__.py`
- Architecture: `docs/ARCHITECTURE.md#ipai-finance-ssc-module`

---

#### IPAI Expense
**Path**: `addons/custom/ipai_expense/`
**Version**: 19.0.251027.1
**Purpose**: Expense tracking and management
**Status**: ✅ Active

**Key Components**:
- **Models** (2): ipai_expense, ipai_expense_category
- **Views** (2): expense_views, menu
- **Security Groups** (2): User, Manager

**Dependencies**:
```python
'depends': ['account', 'hr', 'base']
```

**Integration Points**:
- ✅ Accounting (journal entries)
- ✅ HR (employee expense claims)

**Documentation**:
- Manifest: `addons/custom/ipai_expense/__manifest__.py`
- Website: https://insightpulseai.net/apps/ipai_expense

---

### 🛒 Procurement Modules

#### IPAI Procure
**Path**: `addons/custom/ipai_procure/`
**Version**: 19.0.251027.1
**Purpose**: Procurement automation and vendor management
**Status**: ✅ Active

**Key Components**:
- **Models** (3): procure_request, procure_vendor, procure_approval
- **Views** (3): request_views, vendor_views, menu
- **Workflows**: 3-level approval (User → Manager → Director)

**Dependencies**:
```python
'depends': ['purchase', 'stock', 'account', 'base']
```

**Integration Points**:
- ✅ Purchase Orders
- ✅ Inventory Management
- ✅ Accounting

**Documentation**:
- Manifest: `addons/custom/ipai_procure/__manifest__.py`
- Website: https://insightpulseai.net/apps/ipai_procure

---

### 💳 Subscription Management Modules

#### IPAI Subscriptions
**Path**: `addons/custom/ipai_subscriptions/`
**Version**: 19.0.251027.1
**Purpose**: Recurring subscription management
**Status**: ✅ Active

**Key Components**:
- **Models** (4): subscription, subscription_plan, subscription_invoice, subscription_analytics
- **Views** (4): subscription_views, plan_views, analytics_views, menu
- **Cron Jobs** (3): Invoice generation, Renewal reminders, Churn analysis

**Dependencies**:
```python
'depends': ['sale', 'account', 'base']
```

**Integration Points**:
- ✅ Sales Orders (recurring)
- ✅ Invoicing (automated)
- ✅ Payment Gateways

**Documentation**:
- Manifest: `addons/custom/ipai_subscriptions/__manifest__.py`
- Website: https://insightpulseai.net/apps/ipai_subscriptions

---

### 📈 Business Intelligence Modules

#### Superset Connector
**Path**: `addons/custom/superset_connector/`
**Version**: 19.0.251027.1
**Purpose**: Apache Superset dashboard integration
**Status**: ✅ Active

**Key Components**:
- **Models** (2): superset_config, superset_dashboard
- **Views** (2): config_views, dashboard_templates
- **Security**: CVSS 6.5 URL injection fix applied

**Dependencies**:
```python
'depends': ['base', 'web']
```

**Integration Points**:
- ✅ Apache Superset (OAuth/Guest token)
- ✅ Row-Level Security (RLS) per agency

**Documentation**:
- Manifest: `addons/custom/superset_connector/__manifest__.py`
- Integration Guide: `docs/SUPERSET_INTEGRATION.md`
- Website: https://insightpulseai.net/apps/superset_connector

---

#### Tableau Connector
**Path**: `addons/custom/tableau_connector/`
**Version**: 19.0.251027.1
**Purpose**: Tableau dashboard integration
**Status**: ✅ Active

**Key Components**:
- **Models** (2): tableau_config, tableau_dashboard
- **Views** (2): config_views, dashboard_embed

**Dependencies**:
```python
'depends': ['base', 'web']
```

**Integration Points**:
- ✅ Tableau Server/Online
- ✅ Embedded analytics

**Documentation**:
- Manifest: `addons/custom/tableau_connector/__manifest__.py`
- Website: https://insightpulseai.net/apps/tableau_connector

---

### 🔒 Security & Infrastructure Modules

#### Security Hardening
**Path**: `addons/custom/security_hardening/`
**Version**: 19.0.251027.1
**Purpose**: Enhanced security features
**Status**: ✅ Active

**Key Components**:
- **Models** (3): security_audit_log, security_ip_whitelist, security_2fa
- **Views** (2): audit_views, whitelist_views
- **Features**:
  - IP whitelisting
  - 2FA enforcement
  - Audit logging
  - Session management

**Dependencies**:
```python
'depends': ['base', 'web']
```

**Security Features**:
- ✅ Failed login tracking
- ✅ Brute force protection
- ✅ IP-based access control
- ✅ Session timeout enforcement

**Documentation**:
- Manifest: `addons/custom/security_hardening/__manifest__.py`
- Website: https://insightpulseai.net/apps/security_hardening

---

#### Microservices Connector
**Path**: `addons/custom/microservices_connector/`
**Version**: 19.0.251027.1
**Purpose**: External microservice integration
**Status**: ✅ Active

**Key Components**:
- **Models** (3): microservice_config, microservice_webhook, microservice_log
- **Views** (2): config_views, webhook_views
- **Supported Protocols**: HTTP, REST, GraphQL, gRPC

**Dependencies**:
```python
'depends': ['base', 'web']
```

**Integration Points**:
- ✅ Webhook handlers
- ✅ OAuth2 authentication
- ✅ API key management

**Documentation**:
- Manifest: `addons/custom/microservices_connector/__manifest__.py`
- Website: https://insightpulseai.net/apps/microservices_connector

---

#### Apps Admin Enhancements
**Path**: `addons/custom/apps_admin_enhancements/`
**Version**: 19.0.251027.1
**Purpose**: Enhanced app management UI
**Status**: ✅ Active

**Key Components**:
- **Models** (1): ir.module.module (extends)
- **Views** (2): module_enhanced_views, menu
- **Features**:
  - Module dependency graph
  - Installation wizard
  - Bulk operations
  - Module health checks

**Dependencies**:
```python
'depends': ['base']
```

**Documentation**:
- Manifest: `addons/custom/apps_admin_enhancements/__manifest__.py`
- Website: https://insightpulseai.net/apps/apps_admin_enhancements

---

### 🔗 Integration & Sync Modules

#### Pulser Hub Sync
**Path**: `addons/custom/pulser_hub_sync/`
**Version**: 19.0.251027.1
**Purpose**: Synchronization with Pulser Hub
**Status**: ✅ Active

**Key Components**:
- **Models** (2): pulser_hub_sync, pulser_hub_log
- **Views** (2): sync_views, log_views
- **Sync Frequency**: Every 15 minutes

**Dependencies**:
```python
'depends': ['insightpulse', 'base']
```

**Integration Points**:
- ✅ Pulser Hub API
- ✅ Real-time notifications

**Documentation**:
- Manifest: `addons/custom/pulser_hub_sync/__manifest__.py`
- API Usage: `addons/custom/pulser_hub_sync/API_USAGE.md`
- Website: https://insightpulseai.net/apps/pulser_hub_sync

---

### 🧠 InsightPulse Framework

#### InsightPulse Core
**Path**: `addons/insightpulse/insightpulse/`
**Version**: 19.0.1.0
**Purpose**: Core InsightPulse framework
**Status**: ✅ Active

**Dependencies**:
```python
'depends': ['base', 'web']
```

---

#### InsightPulse App Sources
**Path**: `addons/insightpulse/insightpulse_app_sources/`
**Version**: 19.0.1.0
**Purpose**: App source management
**Status**: ✅ Active

**Key Components**:
- **Models** (1): ir.module.module (extends)
- **Features**: App source tracking, version management

**Dependencies**:
```python
'depends': ['insightpulse', 'base']
```

---

## Scripts & Utilities

### Module Management Scripts

#### Reinstall IPAI Knowledge
**Path**: `scripts/reinstall-ipai-knowledge.sh`
**Purpose**: Reinstall ipai_knowledge module
**Usage**:
```bash
./scripts/reinstall-ipai-knowledge.sh
```

**Actions**:
1. Uninstall existing module
2. Update module list
3. Install latest version
4. Restart Odoo

---

#### Odoo Reinstall Module
**Path**: `scripts/odoo-reinstall-module.sh`
**Purpose**: Generic module reinstall script
**Usage**:
```bash
./scripts/odoo-reinstall-module.sh <module_name>
```

**Parameters**:
- `module_name`: Technical name of module (e.g., `ipai_finance_ssc`)

**Actions**:
1. Check if module exists
2. Uninstall if installed
3. Update module list
4. Install module
5. Run upgrade if needed

---

#### Apps Truth Sync
**Path**: `scripts/apps-truth-sync.sh`
**Purpose**: Sync app metadata with source of truth
**Usage**:
```bash
./scripts/apps-truth-sync.sh
```

**Actions**:
1. Fetch latest app metadata from API
2. Compare with local state
3. Update module manifests
4. Generate sync report

---

### OCA Vendor Scripts

#### OCA Fetch Script
**Path**: `scripts/vendor_oca_enhanced.py`
**Purpose**: Fetch and vendor OCA modules
**Usage**:
```bash
python3 scripts/vendor_oca_enhanced.py <module_name> [--version 19.0]
```

**Parameters**:
- `module_name`: OCA module name
- `--version`: Odoo version (default: 19.0)

**Actions**:
1. Clone OCA repository
2. Extract specific module
3. Copy to `addons/custom/`
4. Update dependencies
5. Create vendor manifest

**Example**:
```bash
# Fetch account_reports module from OCA
python3 scripts/vendor_oca_enhanced.py account_reports --version 19.0
```

---

## CI/CD Workflows

### Production Workflows

#### Comprehensive CI/CD
**Path**: `.github/workflows/comprehensive-cicd.yml`
**Triggers**: Push to main/develop, PR
**Duration**: ~15-20 minutes

**Stages**:
1. **Code Quality** (3 min)
   - Python linting (Ruff, Pylint, Black)
   - XML validation
   - YAML validation

2. **Security Scanning** (4 min)
   - Bandit (code security)
   - Safety (dependency audit)
   - TruffleHog (secret scanning)

3. **Testing** (5 min)
   - Unit tests (pytest)
   - Integration tests (Docker)
   - Module validation

4. **Build** (3 min)
   - Docker multi-platform build
   - Trivy container scan
   - Image signing (Cosign)

5. **Deployment** (5 min)
   - Staging (auto)
   - Production (manual approval)
   - Blue-green strategy

6. **Validation** (5 min)
   - Smoke tests
   - E2E tests (Playwright)
   - Performance tests (k6)

**Environment Variables**:
- `ODOO_VERSION`: 19.0
- `PYTHON_VERSION`: 3.11
- `POSTGRES_VERSION`: 16

**Secrets Required**:
- `DOCKER_USERNAME`, `DOCKER_PASSWORD`
- `KUBE_CONFIG_STAGING`, `KUBE_CONFIG_PRODUCTION`
- `SLACK_WEBHOOK_URL`

---

#### Emergency Rollback
**Path**: `.github/workflows/rollback.yml`
**Triggers**: Manual dispatch
**Duration**: ~10 minutes

**Inputs**:
- `environment`: staging | production
- `rollback_type`: blue_green_swap | previous_image | specific_version
- `version`: (optional) specific version tag
- `reason`: (required) rollback reason

**Stages**:
1. **Validate** (1 min)
   - Get current deployment
   - Determine rollback target
   - Verify image exists

2. **Snapshot** (3 min)
   - Backup PostgreSQL database
   - Snapshot Kubernetes state
   - Upload to S3/GCS

3. **Execute** (4 min)
   - Enable maintenance mode
   - Execute rollback
   - Health checks
   - Disable maintenance mode

4. **Notify** (2 min)
   - Slack notification
   - Email incident report
   - Create GitHub issue

**Example**:
```bash
# Rollback production to previous image
gh workflow run rollback.yml \
  -f environment=production \
  -f rollback_type=previous_image \
  -f reason="Critical bug in payment processing"
```

---

### Quality Assurance Workflows

#### Quality Gate
**Path**: `.github/workflows/quality-gate.yml`
**Triggers**: PR creation/update
**Duration**: ~5 minutes

**Checks**:
- ✅ Code formatting (Black)
- ✅ Linting (Ruff, Pylint)
- ✅ Security (Bandit)
- ✅ Test coverage >80%
- ✅ No TODO/FIXME comments
- ✅ Commit message format
- ✅ PR template filled

**Blocking**: Yes (PR cannot merge if fails)

---

#### Odoo CI
**Path**: `.github/workflows/odoo-ci.yml`
**Triggers**: PR to main/develop
**Duration**: ~8 minutes

**Checks**:
- ✅ Module structure validation
- ✅ Manifest validation
- ✅ Python syntax check
- ✅ XML validation
- ✅ CSV validation
- ✅ Dependency check
- ✅ Upgrade test

---

### Automation Workflows

#### OCA Bot Automation
**Path**: `.github/workflows/oca-bot-automation.yml`
**Triggers**: Schedule (daily), Manual
**Duration**: ~20 minutes

**Actions**:
1. Fetch new OCA modules
2. Check for updates
3. Create PR if changes
4. Run tests on new modules
5. Auto-merge if tests pass

---

#### OCA Fetch Test
**Path**: `.github/workflows/oca-fetch-test.yml`
**Triggers**: Manual dispatch
**Duration**: ~10 minutes

**Inputs**:
- `module_name`: OCA module to fetch
- `odoo_version`: Target Odoo version

**Actions**:
1. Fetch specified OCA module
2. Run tests
3. Generate report

---

#### Parity Live Sync
**Path**: `.github/workflows/parity-live-sync.yml`
**Triggers**: Schedule (hourly)
**Duration**: ~5 minutes

**Actions**:
1. Compare staging vs production
2. Identify drift
3. Create sync report
4. Alert if drift exceeds threshold

---

### Deployment Workflows

#### Production Deploy
**Path**: `.github/workflows/production-deploy.yml`
**Triggers**: Manual dispatch
**Duration**: ~10 minutes

**Inputs**:
- `version`: Image tag to deploy
- `environment`: staging | production

**Actions**:
1. Pre-deployment checks
2. Database backup
3. Blue-green deployment
4. Health checks
5. Notification

---

#### DigitalOcean Deploy
**Path**: `.github/workflows/digitalocean-deploy.yml`
**Triggers**: Push to main
**Duration**: ~12 minutes

**Actions**:
1. Build Docker image
2. Push to DO Container Registry
3. Deploy to DO Kubernetes
4. Update load balancer
5. Health checks

---

#### InsightPulse Monitor Deploy
**Path**: `.github/workflows/insightpulse-monitor-deploy.yml`
**Triggers**: Push to monitoring config
**Duration**: ~8 minutes

**Actions**:
1. Deploy Grafana dashboards
2. Deploy Prometheus config
3. Deploy alert rules
4. Restart monitoring stack

---

### Utility Workflows

#### AI Code Review
**Path**: `.github/workflows/ai-code-review.yml`
**Triggers**: PR creation/update
**Duration**: ~3 minutes

**Actions**:
1. Fetch PR changes
2. Send to Claude API
3. Get code review feedback
4. Post as PR comment

---

#### Docker Image Build
**Path**: `.github/workflows/docker-image.yml`
**Triggers**: Push, PR
**Duration**: ~6 minutes

**Actions**:
1. Build Docker image (AMD64, ARM64)
2. Tag image
3. Push to GHCR
4. Security scan (Trivy)

---

#### DockerHub Publish
**Path**: `.github/workflows/dockerhub-publish.yml`
**Triggers**: Release published
**Duration**: ~8 minutes

**Actions**:
1. Build production image
2. Tag with version
3. Push to DockerHub
4. Update README

---

### Monitoring Workflows

#### Agent Eval
**Path**: `.github/workflows/agent-eval.yml`
**Triggers**: Manual dispatch
**Duration**: ~5 minutes

**Purpose**: Test AI agent performance

---

#### Auto Close Resolved
**Path**: `.github/workflows/auto-close-resolved.yml`
**Triggers**: Schedule (daily)
**Duration**: ~2 minutes

**Actions**:
1. Find issues with "resolved" label
2. Check if older than 7 days
3. Close with comment

---

#### Issue Validation
**Path**: `.github/workflows/issue-validation.yml`
**Triggers**: Issue creation
**Duration**: ~1 minute

**Actions**:
1. Check template compliance
2. Validate required fields
3. Auto-label based on content

---

#### Triage
**Path**: `.github/workflows/triage.yml`
**Triggers**: Issue creation
**Duration**: ~1 minute

**Actions**:
1. Auto-label by keywords
2. Assign to team members
3. Set priority

---

## Configuration Files

### Odoo Configuration

#### Main Config
**Path**: `config/odoo/odoo.conf`
**Purpose**: Odoo server configuration

**Key Settings**:
```ini
[options]
addons_path = /mnt/extra-addons/custom,/mnt/extra-addons/insightpulse,/usr/lib/python3/dist-packages/odoo/addons
db_host = postgres
db_port = 5432
workers = 4
max_cron_threads = 2
web.base.url = https://insightpulseai.net
```

**Environment Variables Used**:
- `ODOO_MASTER_PASSWORD`
- `POSTGRES_PASSWORD`
- `EMAIL_USERNAME`
- `EMAIL_PASSWORD`

---

### Docker Configuration

#### Docker Compose
**Path**: `docker-compose.yml`
**Purpose**: Local development environment

**Services**:
- `postgres`: PostgreSQL 16
- `redis`: Redis 7
- `odoo`: Odoo 19.0 CE

**Volumes**:
- `pgdata`: PostgreSQL data
- `filestore`: Odoo filestore
- `logs`: Application logs

---

#### Dockerfile
**Path**: `Dockerfile`
**Purpose**: Production Docker image

**Base Image**: `odoo:19.0`
**Custom Layers**:
- Install system dependencies
- Copy custom addons
- Install Python requirements
- Configure Odoo

---

### Nginx Configuration

#### Nginx Config
**Path**: `config/nginx/nginx.conf`
**Purpose**: Reverse proxy and load balancer

**Features**:
- SSL termination
- Load balancing
- Static file serving
- Gzip compression
- Security headers

---

### Python Configuration

#### Requirements
**Path**: `requirements.txt`
**Purpose**: Python package dependencies

**Key Packages**:
- `odoo==19.0`
- `psycopg2-binary==2.9.9`
- `redis==5.0.1`
- `supabase==2.3.4`
- `notion-client==2.2.1`

---

#### Development Requirements
**Path**: `requirements-dev.txt`
**Purpose**: Development and testing dependencies

**Key Packages**:
- `black==24.3.0`
- `ruff==0.3.0`
- `pylint==3.1.0`
- `pytest==8.1.0`
- `pytest-cov==5.0.0`

---

## Documentation

### Technical Documentation

| Document | Path | Purpose |
|----------|------|---------|
| **Architecture** | `docs/ARCHITECTURE.md` | System architecture, dependencies, entity relationships |
| **Infrastructure Index** | `docs/INFRASTRUCTURE_INDEX.md` | Complete catalog of all components (this file) |
| **Workflows README** | `.github/workflows/README.md` | CI/CD workflows documentation |
| **Superset Integration** | `docs/SUPERSET_INTEGRATION.md` | Superset integration guide |
| **GitHub Deployment Status** | `docs/GITHUB_APP_DEPLOYMENT_STATUS.md` | GitHub App deployment tracking |
| **Implementation Summary** | `docs/IMPLEMENTATION_SUMMARY_GITHUB_AUTOMATION.md` | GitHub automation implementation details |

---

### API Documentation

| Document | Path | Purpose |
|----------|------|---------|
| **Pulser Hub API** | `addons/custom/pulser_hub_sync/API_USAGE.md` | Pulser Hub API usage guide |

---

### Module Documentation

Each custom module has embedded documentation:

**Standard Structure**:
```
addons/custom/{module_name}/
├── __manifest__.py          # Module metadata and description
├── README.md               # Module-specific README (if exists)
└── static/description/
    └── index.html          # Module description page (shown in Apps)
```

**Access**: Settings → Apps → Select module → More Info

---

## Database Schema

### Core Tables

| Table | Purpose | Key Fields | Indexes |
|-------|---------|------------|---------|
| `res_partner` | Contacts/Companies | `name`, `email`, `phone` | `name`, `email` |
| `res_users` | Users | `login`, `partner_id` | `login`, `active` |
| `ir_model` | Model definitions | `model`, `name` | `model` |
| `ir_model_fields` | Field definitions | `model_id`, `name`, `ttype` | `model_id`, `name` |
| `ir_module_module` | Installed modules | `name`, `state` | `name`, `state` |

---

### Finance SSC Tables

| Table | Purpose | Key Fields | Indexes |
|-------|---------|------------|---------|
| `finance_ssc_agency` | Agencies | `code`, `name`, `tin` | `code`, `tin` |
| `finance_ssc_month_end_closing` | Month-end closings | `agency_id`, `period`, `state` | `agency_id`, `period`, `state` |
| `finance_ssc_bir_form` | BIR tax forms | `agency_id`, `form_type`, `filing_period` | `agency_id`, `form_type`, `filing_period` |
| `finance_ssc_bank_reconciliation` | Bank reconciliations | `agency_id`, `statement_date`, `state` | `agency_id`, `statement_date` |
| `finance_ssc_consolidation` | Consolidations | `period`, `state` | `period`, `state` |

---

### Accounting Tables

| Table | Purpose | Key Fields | Indexes |
|-------|---------|------------|---------|
| `account_account` | Chart of accounts | `code`, `name`, `account_type` | `code`, `account_type` |
| `account_move` | Journal entries | `name`, `date`, `state` | `name`, `date`, `state` |
| `account_move_line` | Journal entry lines | `move_id`, `account_id`, `debit`, `credit` | `move_id`, `account_id` |
| `account_journal` | Journals | `name`, `type` | `type` |

---

## API Endpoints

### REST API Endpoints

#### Authentication
```
POST   /web/session/authenticate
POST   /web/session/logout
GET    /web/session/get_session_info
```

#### CRUD Operations
```
POST   /web/dataset/call_kw/{model}/{method}
POST   /web/dataset/search_read
POST   /web/dataset/call_button
```

#### Finance SSC Endpoints
```
POST   /finance_ssc/agency/sync_to_supabase
POST   /finance_ssc/month_end/finalize
POST   /finance_ssc/bir_form/generate_pdf
POST   /finance_ssc/bank_recon/auto_match
GET    /finance_ssc/consolidation/report/{id}
```

---

### XML-RPC Endpoints

```python
# Common endpoint
url = 'https://insightpulseai.net/xmlrpc/2/common'
# Object endpoint
url = 'https://insightpulseai.net/xmlrpc/2/object'
```

**Example Usage**:
```python
import xmlrpc.client

# Authenticate
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

# Execute
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
records = models.execute_kw(db, uid, password,
    'finance.ssc.agency', 'search_read',
    [[['active', '=', True]]],
    {'fields': ['code', 'name', 'tin']}
)
```

---

## Integration Points

### External Services

| Service | Purpose | Protocol | Authentication |
|---------|---------|----------|----------------|
| **Supabase** | Real-time analytics DB | REST | API Key |
| **Notion** | Knowledge base | REST | Integration Token |
| **Apache Superset** | BI dashboards | REST, OAuth | Guest Token |
| **Tableau** | BI dashboards | REST, OAuth | Access Token |
| **GitHub** | Source control, CI/CD | REST | GitHub App |
| **Slack** | Notifications | Webhook | Webhook URL |
| **SMTP** | Email notifications | SMTP | Username/Password |

---

### Webhook Endpoints

```
POST   /webhook/github
POST   /webhook/slack
POST   /webhook/supabase
POST   /webhook/notion
```

---

## Monitoring & Observability

### Metrics

**Prometheus Metrics Endpoint**:
```
GET    /metrics
```

**Key Metrics**:
- `odoo_http_requests_total` - Total HTTP requests
- `odoo_http_request_duration_seconds` - Request duration
- `odoo_cron_job_duration_seconds` - Cron job duration
- `odoo_database_connections` - Active DB connections
- `odoo_workers_active` - Active worker processes

---

### Logs

**Log Locations**:
```
/var/log/odoo/odoo.log              # Main application log
/var/log/odoo/odoo-server.log       # Server log
/var/log/nginx/access.log           # Nginx access log
/var/log/nginx/error.log            # Nginx error log
/var/log/postgresql/postgres.log    # PostgreSQL log
```

**Log Levels**:
- `DEBUG` - Detailed debug information
- `INFO` - General information
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

---

### Dashboards

**Grafana Dashboards**:
1. **Odoo Overview** - System health, request rates, error rates
2. **Database Performance** - Query performance, connection pool
3. **Finance SSC Metrics** - Month-end closing stats, BIR form filing
4. **User Activity** - Active users, session duration
5. **Integration Health** - Supabase sync status, Notion sync status

**Access**: https://monitoring.insightpulseai.net

---

### Alerts

**Alert Rules**:
- High error rate (>5% of requests)
- Database connection pool exhausted
- Worker process crashes
- Cron job failures
- Integration sync failures
- Disk space low (<10% free)
- Memory usage high (>90%)

**Notification Channels**:
- Slack: #alerts channel
- Email: ops@insightpulseai.net
- PagerDuty: Critical alerts only

---

## Quick Reference

### Common Commands

```bash
# Start Odoo
docker-compose up -d odoo

# Restart Odoo
docker-compose restart odoo

# View logs
docker-compose logs -f odoo

# Access Odoo shell
docker-compose exec odoo odoo shell -d odoo

# Update module list
docker-compose exec odoo odoo -d odoo -u all --stop-after-init

# Install module
docker-compose exec odoo odoo -d odoo -i ipai_finance_ssc --stop-after-init

# Upgrade module
docker-compose exec odoo odoo -d odoo -u ipai_finance_ssc --stop-after-init

# Backup database
docker-compose exec postgres pg_dump -U odoo odoo > backup.sql

# Restore database
docker-compose exec -T postgres psql -U odoo odoo < backup.sql

# Run tests
docker-compose exec odoo pytest tests/

# Check code quality
docker-compose exec odoo black --check addons/custom/
docker-compose exec odoo ruff check addons/custom/
```

---

### Environment URLs

| Environment | URL | Purpose |
|-------------|-----|---------|
| **Production** | https://insightpulseai.net | Live production system |
| **Staging** | https://staging.insightpulseai.net | Pre-production testing |
| **Monitoring** | https://monitoring.insightpulseai.net | Grafana dashboards |
| **Superset** | https://analytics.insightpulseai.net | Apache Superset |

---

### Support Contacts

| Team | Contact | Responsibility |
|------|---------|----------------|
| **DevOps** | devops@insightpulseai.net | Infrastructure, deployments |
| **Development** | dev@insightpulseai.net | Module development, bugs |
| **Finance** | finance@insightpulseai.net | Finance SSC module support |
| **Security** | security@insightpulseai.net | Security incidents |

---

**Last Updated**: 2025-11-10
**Maintained by**: InsightPulseAI DevOps Team
**License**: AGPL-3.0
**Version**: 1.0.0
