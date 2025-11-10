# InsightPulse Odoo - System Architecture

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Module Catalog](#module-catalog)
- [Dependency Graph](#dependency-graph)
- [Entity Relationships](#entity-relationships)
- [Integration Contracts](#integration-contracts)
- [Data Flow](#data-flow)
- [Semantic Layer](#semantic-layer)
- [Infrastructure Components](#infrastructure-components)

## System Overview

InsightPulse Odoo is an enterprise-grade ERP system built on Odoo 19.0 CE, enhanced with custom modules for finance, procurement, subscriptions, and business intelligence integration.

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Application** | Odoo Community | 19.0 | Core ERP framework |
| **Runtime** | Python | 3.11 | Application runtime |
| **Database** | PostgreSQL | 16 | Primary data store |
| **Cache** | Redis | 7 | Session cache, queues |
| **Queue** | Redis Queue | Latest | Background jobs |
| **Reverse Proxy** | Nginx | 1.25 | Load balancing, SSL |
| **Container** | Docker | 24.0 | Application containerization |
| **Orchestration** | Kubernetes | 1.28 | Container orchestration |
| **CI/CD** | GitHub Actions | N/A | Automation pipeline |
| **Monitoring** | Grafana + Prometheus | Latest | Observability |
| **BI** | Apache Superset | Latest | Advanced analytics |

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INTERNET / USERS                              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LOAD BALANCER (DigitalOcean)                    │
│                   SSL Termination, DDoS Protection                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER (K8s)                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    INGRESS CONTROLLER                         │   │
│  │                   (nginx-ingress)                             │   │
│  └────────────────────────┬─────────────────────────────────────┘   │
│                           │                                          │
│  ┌────────────────────────┴─────────────────────────────────────┐   │
│  │                                                               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │   │
│  │  │     BLUE     │  │    GREEN     │  │  MAINTENANCE │      │   │
│  │  │  DEPLOYMENT  │  │  DEPLOYMENT  │  │     PAGE     │      │   │
│  │  │              │  │   (Active)   │  │              │      │   │
│  │  │  Odoo Pods   │  │  Odoo Pods   │  │  Static Page │      │   │
│  │  │  (3 replicas)│  │  (3 replicas)│  │  (0 replicas)│      │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────────┘      │   │
│  │         │                  │                                 │   │
│  │         └──────────┬───────┘                                 │   │
│  │                    │                                          │   │
│  │  ┌─────────────────┴──────────────────────────┐             │   │
│  │  │           SERVICE LAYER                     │             │   │
│  │  │      (odoo-service - LoadBalancer)          │             │   │
│  │  └─────────────────┬──────────────────────────┘             │   │
│  └────────────────────┼────────────────────────────────────────┘   │
│                       │                                              │
│  ┌────────────────────┼────────────────────────────────────────┐   │
│  │  SUPPORTING SERVICES│                                        │   │
│  │                     │                                        │   │
│  │  ┌──────────────┐  │  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │  PostgreSQL  │◄─┼──┤    Redis     │  │   Superset   │  │   │
│  │  │   Primary    │  │  │  (Cache/Queue)│  │      BI      │  │   │
│  │  │  StatefulSet │  │  └──────────────┘  └──────────────┘  │   │
│  │  └──────┬───────┘  │                                        │   │
│  │         │           │                                        │   │
│  │  ┌──────▼───────┐  │                                        │   │
│  │  │  PostgreSQL  │  │                                        │   │
│  │  │   Replica    │  │                                        │   │
│  │  │  StatefulSet │  │                                        │   │
│  │  └──────────────┘  │                                        │   │
│  └────────────────────┴────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PERSISTENT STORAGE                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   PV: PgData │  │ PV: Filestore│  │  PV: Backups │             │
│  │   (100GB)    │  │   (50GB)     │  │   (200GB)    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   EXTERNAL INTEGRATIONS                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Supabase   │  │    Notion    │  │   Tableau    │             │
│  │  (External DB)│  │ (Knowledge) │  │     (BI)     │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

## Module Catalog

### Core Odoo Modules (Installed)

| Module | Purpose | Dependencies | Status |
|--------|---------|--------------|--------|
| **base** | Core framework | None | ✅ Active |
| **web** | Web interface | base | ✅ Active |
| **account** | Accounting | base, web | ✅ Active |
| **sale** | Sales management | account | ✅ Active |
| **purchase** | Procurement | account | ✅ Active |
| **hr** | Human resources | base | ✅ Active |
| **project** | Project management | base, web | ✅ Active |
| **mail** | Messaging | base, web | ✅ Active |

### Custom InsightPulse Modules

#### Finance & Accounting

| Module | Code Path | Purpose | Key Models | Dependencies |
|--------|-----------|---------|------------|--------------|
| **IPAI Finance SSC** | `addons/custom/ipai_finance_ssc` | Multi-agency finance management | `finance.ssc.agency`<br>`finance.ssc.month.end.closing`<br>`finance.ssc.bir.form`<br>`finance.ssc.bank.reconciliation`<br>`finance.ssc.consolidation` | `account`<br>`account_reports` |
| **IPAI Expense** | `addons/custom/ipai_expense` | Expense tracking | `ipai.expense`<br>`ipai.expense.category` | `account`<br>`hr` |

#### Procurement

| Module | Code Path | Purpose | Key Models | Dependencies |
|--------|-----------|---------|------------|--------------|
| **IPAI Procure** | `addons/custom/ipai_procure` | Procurement automation | `ipai.procure.request`<br>`ipai.procure.vendor` | `purchase`<br>`stock` |

#### Subscriptions

| Module | Code Path | Purpose | Key Models | Dependencies |
|--------|-----------|---------|------------|--------------|
| **IPAI Subscriptions** | `addons/custom/ipai_subscriptions` | Subscription management | `ipai.subscription`<br>`ipai.subscription.plan` | `sale`<br>`account` |

#### Business Intelligence

| Module | Code Path | Purpose | Key Models | Dependencies |
|--------|-----------|---------|------------|--------------|
| **Superset Connector** | `addons/custom/superset_connector` | Apache Superset integration | `superset.config`<br>`superset.dashboard` | `base`<br>`web` |
| **Tableau Connector** | `addons/custom/tableau_connector` | Tableau integration | `tableau.config`<br>`tableau.dashboard` | `base`<br>`web` |

#### Infrastructure

| Module | Code Path | Purpose | Key Models | Dependencies |
|--------|-----------|---------|------------|--------------|
| **Security Hardening** | `addons/custom/security_hardening` | Security enhancements | `security.audit.log`<br>`security.ip.whitelist` | `base` |
| **Microservices Connector** | `addons/custom/microservices_connector` | External service integration | `microservice.config`<br>`microservice.webhook` | `base` |
| **Apps Admin Enhancements** | `addons/custom/apps_admin_enhancements` | App management UI | `ir.module.module` (extends) | `base` |

#### InsightPulse Framework

| Module | Code Path | Purpose | Key Models | Dependencies |
|--------|-----------|---------|------------|--------------|
| **InsightPulse** | `addons/insightpulse/insightpulse` | Core InsightPulse framework | Various | `base`<br>`web` |
| **App Sources** | `addons/insightpulse/insightpulse_app_sources` | App source management | `ir.module.module` (extends) | `insightpulse` |
| **Pulser Hub Sync** | `addons/custom/pulser_hub_sync` | Sync with Pulser Hub | `pulser.hub.sync` | `insightpulse` |

## Dependency Graph

### Module Dependencies

```
┌──────────────────────────────────────────────────────────────────┐
│                          BASE LAYER                               │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐              │
│  │ base │  │ web  │  │ mail │  │ bus  │  │ http │              │
│  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘              │
└─────┼─────────┼─────────┼─────────┼─────────┼───────────────────┘
      │         │         │         │         │
      ▼         ▼         ▼         ▼         ▼
┌──────────────────────────────────────────────────────────────────┐
│                     CORE BUSINESS LAYER                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ account │  │  sale   │  │purchase │  │   hr    │            │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘            │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌──────────────────────────────────────────────────────────────────┐
│                 INSIGHTPULSE FRAMEWORK LAYER                      │
│  ┌──────────────┐  ┌──────────────────┐                         │
│  │ insightpulse │  │ app_sources      │                         │
│  └──────┬───────┘  └──────┬───────────┘                         │
└─────────┼──────────────────┼──────────────────────────────────────┘
          │                  │
          ▼                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                  CUSTOM MODULES LAYER                             │
│                                                                   │
│  FINANCE MODULES:                                                 │
│  ┌────────────────────┐  ┌──────────────┐                       │
│  │ ipai_finance_ssc   │  │ ipai_expense │                       │
│  │ ├─ agency          │  │              │                       │
│  │ ├─ month_end       │  │              │                       │
│  │ ├─ bir_forms       │  │              │                       │
│  │ ├─ bank_recon      │  │              │                       │
│  │ └─ consolidation   │  │              │                       │
│  └────────────────────┘  └──────────────┘                       │
│                                                                   │
│  PROCUREMENT MODULES:                                             │
│  ┌────────────────────┐                                          │
│  │ ipai_procure       │                                          │
│  └────────────────────┘                                          │
│                                                                   │
│  SUBSCRIPTION MODULES:                                            │
│  ┌────────────────────┐                                          │
│  │ ipai_subscriptions │                                          │
│  └────────────────────┘                                          │
│                                                                   │
│  BI CONNECTORS:                                                   │
│  ┌────────────────────┐  ┌──────────────────┐                   │
│  │ superset_connector │  │ tableau_connector│                   │
│  └────────────────────┘  └──────────────────┘                   │
│                                                                   │
│  INFRASTRUCTURE:                                                  │
│  ┌────────────────────┐  ┌──────────────────────┐               │
│  │security_hardening  │  │microservices_connector│              │
│  └────────────────────┘  └──────────────────────┘               │
│                                                                   │
│  ADMIN TOOLS:                                                     │
│  ┌────────────────────────┐  ┌──────────────────┐               │
│  │apps_admin_enhancements │  │ pulser_hub_sync  │               │
│  └────────────────────────┘  └──────────────────┘               │
└──────────────────────────────────────────────────────────────────┘
```

### Python Package Dependencies

```
odoo==19.0                      # Core ERP framework
├── psycopg2-binary==2.9.9     # PostgreSQL adapter
├── python-dateutil==2.8.2      # Date utilities
├── Werkzeug==3.0.1            # WSGI utility library
├── lxml==5.1.0                # XML processing
├── Pillow==10.2.0             # Image processing
├── reportlab==4.0.9           # PDF generation
├── PyPDF2==3.0.1              # PDF manipulation
└── requests==2.31.0           # HTTP library

# Development Dependencies
black==24.3.0                   # Code formatting
ruff==0.3.0                     # Fast Python linter
pylint==3.1.0                   # Comprehensive linter
pytest==8.1.0                   # Testing framework
pytest-cov==5.0.0              # Code coverage
pytest-odoo==0.9.0             # Odoo-specific test utils

# Security
bandit==1.7.8                   # Security linter
safety==3.1.0                   # Dependency vulnerability scanner

# Integrations
supabase==2.3.4                # Supabase client
notion-client==2.2.1           # Notion API client
requests-oauthlib==1.3.1       # OAuth support

# Background Jobs
redis==5.0.1                   # Redis client
rq==1.16.1                     # Redis Queue

# Monitoring
prometheus-client==0.19.0      # Prometheus metrics
sentry-sdk==1.40.0            # Error tracking
```

## Entity Relationships

### IPAI Finance SSC Module

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENCY (Root Entity)                      │
│  finance.ssc.agency                                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Fields:                                                     │ │
│  │ • code: Char (PK: RIM, CKVC, BOM, etc.)                   │ │
│  │ • name: Char (Agency full name)                           │ │
│  │ • tin: Char (Tax Identification Number)                   │ │
│  │ • rdo_code: Char (Revenue District Office)                │ │
│  │ • contact_person: Char                                     │ │
│  │ • supabase_synced: Boolean                                │ │
│  │ • notion_synced: Boolean                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
└────┬──────────────────────┬────────────────────┬────────────────┘
     │                      │                    │
     │ One2Many             │ One2Many           │ One2Many
     │                      │                    │
     ▼                      ▼                    ▼
┌──────────────────┐  ┌─────────────────┐  ┌──────────────────┐
│ MONTH-END CLOSING│  │   BIR FORMS     │  │ BANK RECON       │
│ finance.ssc.     │  │ finance.ssc.    │  │ finance.ssc.     │
│ month.end.closing│  │ bir.form        │  │ bank.recon       │
├──────────────────┤  ├─────────────────┤  ├──────────────────┤
│ • agency_id      │  │ • agency_id     │  │ • agency_id      │
│ • period (Date)  │  │ • form_type     │  │ • statement_date │
│ • state          │  │   - 1601-C      │  │ • bank_lines     │
│ • trial_balance  │  │   - 2550Q       │  │ • odoo_lines     │
│ • variance_report│  │   - 1702-RT     │  │ • match_status   │
│ • checklist_items│  │ • filing_period │  │ • auto_match %   │
└────────┬─────────┘  │ • amount_payable│  └──────────────────┘
         │            │ • filed_date    │
         │            └─────────────────┘
         │
         │ Many2Many (via consolidation)
         │
         ▼
┌──────────────────────────────────────────┐
│          CONSOLIDATION                    │
│  finance.ssc.consolidation                │
├──────────────────────────────────────────┤
│ • period: Date                            │
│ • agency_ids: Many2Many                   │
│ • consolidated_trial_balance: Binary      │
│ • elimination_entries: One2Many           │
│ • financial_ratios: Text                  │
│ • state: Selection                        │
│   - draft                                 │
│   - consolidated                          │
│   - approved                              │
└──────────────────────────────────────────┘
```

### Cross-Module Relationships

```
┌───────────────────────────────────────────────────────────────────┐
│                     ODOO CORE ENTITIES                             │
│                                                                    │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐             │
│  │res.partner │    │account.move│    │ sale.order │             │
│  │  (Contact) │    │  (Journal) │    │   (Sale)   │             │
│  └─────┬──────┘    └─────┬──────┘    └─────┬──────┘             │
└────────┼─────────────────┼─────────────────┼────────────────────┘
         │                 │                 │
         │ Many2One        │ Many2One        │ Many2One
         │                 │                 │
┌────────┴─────────────────┴─────────────────┴────────────────────┐
│                  CUSTOM MODULE ENTITIES                           │
│                                                                   │
│  ┌──────────────────┐   ┌──────────────────┐                    │
│  │ finance.ssc.     │   │ ipai.subscription│                    │
│  │ agency           ├───┤ (Subscription)   │                    │
│  │                  │   │                  │                    │
│  │ • partner_id ────┼───┤ • partner_id     │                    │
│  └──────────────────┘   └──────┬───────────┘                    │
│                                 │                                 │
│                                 │ Many2One                        │
│                                 │                                 │
│  ┌──────────────────┐           │                                │
│  │ ipai.expense     │◄──────────┘                                │
│  │ (Expense)        │                                            │
│  │                  │                                            │
│  │ • agency_id ─────┼─► finance.ssc.agency                      │
│  │ • move_id ───────┼─► account.move                            │
│  └──────────────────┘                                            │
│                                                                   │
│  ┌──────────────────┐                                            │
│  │ ipai.procure     │                                            │
│  │ (Procurement)    │                                            │
│  │                  │                                            │
│  │ • agency_id ─────┼─► finance.ssc.agency                      │
│  │ • partner_id ────┼─► res.partner                             │
│  │ • purchase_id ───┼─► purchase.order                          │
│  └──────────────────┘                                            │
└──────────────────────────────────────────────────────────────────┘
```

## Integration Contracts

### External Service Integrations

#### Supabase Integration

**Contract**: Real-time data synchronization

```python
# Interface: addons/custom/ipai_finance_ssc/models/finance_ssc_agency.py

class FinanceSscAgency(models.Model):
    """
    Integration: Supabase real-time sync
    Direction: Bidirectional (Odoo ⟷ Supabase)
    Frequency: On-change + Cron (hourly)
    """

    def action_sync_to_supabase(self):
        """
        Endpoint: https://[project].supabase.co/rest/v1/agencies
        Method: POST/PATCH
        Authentication: Bearer token (API key)

        Payload:
        {
            "code": "RIM",
            "name": "Research Institute for Mindanao",
            "tin": "123-456-789-000",
            "rdo_code": "116",
            "odoo_id": 42,
            "last_synced": "2025-11-10T10:00:00Z"
        }

        Response:
        {
            "id": "uuid",
            "synced": true,
            "conflicts": []
        }
        """
        pass

# Cron Job: data/bir_forms_data.xml
<record id="cron_sync_agencies_supabase" model="ir.cron">
    <field name="name">Sync Agencies to Supabase</field>
    <field name="model_id" ref="model_finance_ssc_agency"/>
    <field name="state">code</field>
    <field name="code">model.search([]).action_sync_to_supabase()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">hours</field>
</record>
```

#### Notion Integration

**Contract**: Knowledge base synchronization

```python
# Interface: addons/custom/ipai_finance_ssc/models/finance_ssc_month_end_closing.py

class MonthEndClosing(models.Model):
    """
    Integration: Notion database sync
    Direction: Odoo → Notion (one-way)
    Frequency: On month-end finalize
    """

    def action_sync_to_notion(self):
        """
        Endpoint: https://api.notion.com/v1/pages
        Method: POST
        Authentication: Bearer token (Integration secret)

        Payload:
        {
            "parent": {"database_id": "notion_db_id"},
            "properties": {
                "Agency": {"title": [{"text": {"content": "RIM"}}]},
                "Period": {"date": {"start": "2025-10-01"}},
                "Status": {"select": {"name": "Finalized"}},
                "Trial Balance": {"files": [{"url": "..."}]},
                "Variance %": {"number": 0.02}
            }
        }

        Response:
        {
            "id": "page_id",
            "url": "https://notion.so/page_id"
        }
        """
        pass
```

#### Apache Superset Integration

**Contract**: BI dashboard embedding

```python
# Interface: addons/custom/superset_connector/models/superset_config.py

class SupersetDashboard(models.Model):
    """
    Integration: Superset dashboard embedding
    Direction: Odoo → Superset (read-only)
    Authentication: Guest token (OAuth)
    """

    def _compute_embed_url(self):
        """
        Endpoint: {base_url}/api/v1/security/guest_token/
        Method: POST
        Authentication: Bearer token (Superset API key)

        Request:
        {
            "user": {
                "username": "odoo_user_42",
                "first_name": "John",
                "last_name": "Doe"
            },
            "resources": [{
                "type": "dashboard",
                "id": "dashboard_id"
            }],
            "rls": [{
                "clause": "agency_code = 'RIM'"  # Row-level security
            }]
        }

        Response:
        {
            "token": "eyJ...",
            "expires_at": "2025-11-10T12:00:00Z"
        }

        Embed URL:
        {base_url}/superset/dashboard/{dashboard_id}/?guest_token={token}
        """
        pass
```

### Internal Service Contracts

#### Background Job Processing

**Contract**: Redis Queue task execution

```python
# Queue: default
# Interface: addons/custom/ipai_finance_ssc/models/finance_ssc_bank_reconciliation.py

def action_auto_match_lines(self):
    """
    Queue: 'default'
    Priority: Normal
    Timeout: 600 seconds

    Job Description:
    - Fetch all unmatched bank lines
    - Fetch all unmatched Odoo move lines
    - Calculate Jaccard similarity for each pair
    - Auto-match if similarity > 90%
    - Create suggestion if similarity 70-90%

    Result:
    {
        "matched": 45,
        "suggested": 12,
        "unmatched": 3,
        "match_rate": 0.75
    }
    """
    # This would be queued to Redis Queue
    pass
```

#### Email Notifications

**Contract**: SMTP email sending

```python
# Interface: Odoo mail system

def send_month_end_notification(self):
    """
    Service: SMTP (smtp.gmail.com:587)
    Template: email_template_month_end_closing

    Recipients:
    - Agency contact person
    - Finance manager
    - Accountant (if assigned)

    Variables:
    {
        "agency_name": "Research Institute for Mindanao",
        "period": "October 2025",
        "status": "Finalized",
        "trial_balance_url": "https://...",
        "variance_percentage": "2.5%"
    }
    """
    pass
```

## Data Flow

### Month-End Closing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. INITIATION                                                    │
│    User clicks "Month-End Closing" → Wizard opens               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. DATA COLLECTION                                               │
│    • Fetch all journal entries for period                       │
│    • Fetch all move lines (debit/credit)                        │
│    • Calculate trial balance                                    │
│    • Generate financial reports                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. VALIDATION                                                    │
│    • Check debit/credit balance                                 │
│    • Validate required journal entries                          │
│    • Check for unposted entries                                 │
│    • Variance analysis (compare to budget/previous period)      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. REPORT GENERATION                                             │
│    • Trial Balance PDF                                          │
│    • Variance Report PDF                                        │
│    • Checklist PDF                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. APPROVAL WORKFLOW                                             │
│    Draft → Under Review → Approved → Finalized                  │
│    • Email notifications at each stage                          │
│    • Notion sync on finalize                                    │
│    • Lock period (prevent backdated entries)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. INTEGRATION SYNC                                              │
│    • Sync to Supabase (analytics database)                      │
│    • Sync to Notion (knowledge base)                            │
│    • Update Superset dashboards (refresh cache)                 │
└─────────────────────────────────────────────────────────────────┘
```

### BIR Form Filing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. FORM GENERATION                                               │
│    Cron (monthly) → Auto-generate BIR forms for all agencies    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. DATA POPULATION                                               │
│    • Fetch withholding tax entries                              │
│    • Fetch income tax entries                                   │
│    • Calculate totals per form type                             │
│    • Populate form fields                                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. VALIDATION                                                    │
│    • Check required fields                                      │
│    • Validate TIN format                                        │
│    • Validate RDO code                                          │
│    • Cross-check with general ledger                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. PDF GENERATION                                                │
│    • Generate BIR form PDF (form-specific template)             │
│    • Attach supporting schedules                                │
│    • Generate payment form                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. FILING WORKFLOW                                               │
│    Generated → Reviewed → E-Filed → Paid → Archived             │
│    • Email notification to agency contact                       │
│    • Track filing deadline                                      │
│    • Alert if approaching deadline                              │
└─────────────────────────────────────────────────────────────────┘
```

## Semantic Layer

### Domain Concepts

| Domain | Entity | Meaning | Business Rule |
|--------|--------|---------|---------------|
| **Finance** | Agency | Legal entity (non-profit/foundation) | Each agency has unique TIN and RDO |
| **Finance** | Month-End Closing | Financial period closing process | One per agency per month |
| **Tax** | BIR Form | Philippine tax form | Due dates: 10th (1601-C), 60 days after quarter (2550Q), April 15 (1702-RT) |
| **Finance** | Bank Reconciliation | Match bank statement with Odoo entries | Target: 80%+ auto-match |
| **Finance** | Consolidation | Multi-agency financial reporting | Eliminations required for inter-agency transactions |
| **BI** | Dashboard | Visual analytics interface | Row-level security per agency |
| **BI** | Data Source | Odoo data exported for analytics | Incremental sync, 1-hour lag |

### Naming Conventions

#### Module Names
- **Pattern**: `{org}_{domain}[_{feature}]`
- **Examples**:
  - `ipai_finance_ssc` - InsightPulse AI, Finance, Shared Service Center
  - `ipai_expense` - InsightPulse AI, Expense tracking
  - `superset_connector` - Third-party integration (no org prefix)

#### Model Names
- **Pattern**: `{module}.{entity}[.{sub_entity}]`
- **Examples**:
  - `finance.ssc.agency` - Main entity
  - `finance.ssc.month.end.closing` - Compound entity
  - `finance.ssc.bir.form` - Hierarchical entity

#### Field Names
- **Pattern**: `{descriptor}[_{relation}]`
- **Examples**:
  - `agency_id` - Many2One relation (always ends with `_id`)
  - `agency_ids` - Many2Many relation (always ends with `_ids`)
  - `name` - Char field (primary display name)
  - `state` - Selection field (workflow state)
  - `active` - Boolean field (archive flag)

#### View Names
- **Pattern**: `view_{model}_{type}`
- **Examples**:
  - `view_finance_ssc_agency_form`
  - `view_finance_ssc_agency_tree`
  - `view_finance_ssc_agency_kanban`

#### Menu Names
- **Pattern**: `menu_{module}_{section}[_{subsection}]`
- **Examples**:
  - `menu_finance_ssc_root` - Top-level menu
  - `menu_finance_ssc_operations` - Section menu
  - `menu_finance_ssc_agency` - Action menu

## Infrastructure Components

### File Structure

```
insightpulse-odoo/
├── addons/
│   ├── custom/                    # Custom modules
│   │   ├── ipai_finance_ssc/
│   │   │   ├── __init__.py
│   │   │   ├── __manifest__.py   # Module metadata
│   │   │   ├── models/           # Business logic
│   │   │   │   ├── __init__.py
│   │   │   │   ├── finance_ssc_agency.py
│   │   │   │   ├── finance_ssc_month_end_closing.py
│   │   │   │   ├── finance_ssc_bir_form.py
│   │   │   │   ├── finance_ssc_bank_reconciliation.py
│   │   │   │   └── finance_ssc_consolidation.py
│   │   │   ├── views/            # UI definitions
│   │   │   │   ├── agency_views.xml
│   │   │   │   ├── month_end_closing_views.xml
│   │   │   │   ├── bir_forms_views.xml
│   │   │   │   ├── bank_reconciliation_views.xml
│   │   │   │   ├── consolidation_views.xml
│   │   │   │   └── menus.xml
│   │   │   ├── wizards/          # Wizard models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── month_end_closing_wizard.py
│   │   │   │   ├── bir_filing_wizard.py
│   │   │   │   └── bank_match_wizard.py
│   │   │   ├── security/         # Access control
│   │   │   │   ├── finance_ssc_security.xml
│   │   │   │   └── ir.model.access.csv
│   │   │   ├── data/             # Master data
│   │   │   │   ├── agencies_data.xml
│   │   │   │   └── bir_forms_data.xml
│   │   │   ├── reports/          # Report templates
│   │   │   │   ├── trial_balance_report.xml
│   │   │   │   └── bir_forms_report.xml
│   │   │   └── static/           # Static assets
│   │   │       ├── src/
│   │   │       │   ├── js/
│   │   │       │   └── css/
│   │   │       └── description/
│   │   │           ├── icon.png
│   │   │           └── index.html
│   │   ├── ipai_expense/
│   │   ├── ipai_procure/
│   │   ├── ipai_subscriptions/
│   │   ├── superset_connector/
│   │   ├── tableau_connector/
│   │   ├── security_hardening/
│   │   ├── microservices_connector/
│   │   ├── apps_admin_enhancements/
│   │   └── pulser_hub_sync/
│   └── insightpulse/             # InsightPulse framework
│       ├── insightpulse/
│       └── insightpulse_app_sources/
├── config/
│   ├── odoo/
│   │   └── odoo.conf             # Odoo configuration
│   └── nginx/
│       └── nginx.conf            # Reverse proxy config
├── scripts/
│   ├── odoo-reinstall-module.sh
│   ├── reinstall-ipai-knowledge.sh
│   └── apps-truth-sync.sh
├── .github/
│   └── workflows/                # CI/CD workflows
│       ├── comprehensive-cicd.yml
│       ├── rollback.yml
│       ├── quality-gate.yml
│       └── README.md
├── docs/
│   ├── ARCHITECTURE.md           # This file
│   ├── SUPERSET_INTEGRATION.md
│   └── IMPLEMENTATION_SUMMARY_*.md
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

### Configuration Files

#### Odoo Configuration (`config/odoo/odoo.conf`)

```ini
[options]
# Core
addons_path = /mnt/extra-addons/custom,/mnt/extra-addons/insightpulse,/usr/lib/python3/dist-packages/odoo/addons
data_dir = /var/lib/odoo
admin_passwd = ${ODOO_MASTER_PASSWORD}

# Database
db_host = postgres
db_port = 5432
db_user = odoo
db_password = ${POSTGRES_PASSWORD}
db_name = odoo
db_maxconn = 64
db_sslmode = prefer

# Network
xmlrpc_interface = 0.0.0.0
xmlrpc_port = 8069
proxy_mode = True
web.base.url = https://insightpulseai.net

# Performance
workers = 4
max_cron_threads = 2
limit_time_cpu = 600
limit_time_real = 1200
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648

# Logging
log_level = info
log_handler = :INFO
logfile = /var/log/odoo/odoo.log

# Security
list_db = False
dbfilter = ^odoo$

# Email
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_ssl = False
smtp_user = ${EMAIL_USERNAME}
smtp_password = ${EMAIL_PASSWORD}
```

#### Docker Compose (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: odoo
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  odoo:
    image: ghcr.io/${GITHUB_REPOSITORY}:${VERSION}
    depends_on:
      - postgres
      - redis
    ports:
      - "8069:8069"
    volumes:
      - ./addons/custom:/mnt/extra-addons/custom
      - ./addons/insightpulse:/mnt/extra-addons/insightpulse
      - ./config/odoo/odoo.conf:/etc/odoo/odoo.conf
      - filestore:/var/lib/odoo
      - logs:/var/log/odoo
    environment:
      HOST: postgres
      USER: odoo
      PASSWORD: ${POSTGRES_PASSWORD}
    restart: always

volumes:
  pgdata:
  filestore:
  logs:
```

### Environment Variables

| Variable | Purpose | Example | Required |
|----------|---------|---------|----------|
| `POSTGRES_PASSWORD` | PostgreSQL password | `secure_password_123` | ✅ |
| `ODOO_MASTER_PASSWORD` | Odoo admin password | `admin_password_456` | ✅ |
| `EMAIL_USERNAME` | SMTP username | `noreply@insightpulseai.net` | ✅ |
| `EMAIL_PASSWORD` | SMTP password | `smtp_token_789` | ✅ |
| `SUPABASE_URL` | Supabase project URL | `https://xyz.supabase.co` | ❌ |
| `SUPABASE_KEY` | Supabase API key | `eyJ...` | ❌ |
| `NOTION_TOKEN` | Notion integration token | `secret_...` | ❌ |
| `GITHUB_REPOSITORY` | GitHub repo path | `jgtolentino/insightpulse-odoo` | ✅ |
| `VERSION` | Image version tag | `v1.2.3` | ✅ |

---

**Last Updated**: 2025-11-10
**Maintained by**: InsightPulseAI DevOps Team
**License**: AGPL-3.0
