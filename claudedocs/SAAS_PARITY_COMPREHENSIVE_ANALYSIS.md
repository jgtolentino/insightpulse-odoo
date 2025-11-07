# InsightPulse-Odoo: Comprehensive SaaS Parity Analysis & Deployment Roadmap

**Document Version**: 1.0.0
**Analysis Date**: 2025-11-06
**Prepared By**: Claude SuperClaude Multi-Agent Framework
**Target**: Full SaaS deployment with web + mobile companion apps
**Scope**: 8 Agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)

---

## Executive Summary

### Current State Assessment

**Repository**: https://github.com/jgtolentino/insightpulse-odoo
**Odoo Version**: 19.0 Community Edition + OCA
**Custom Modules**: 15 production modules
**Microservices**: 11 Node.js/Python services
**Infrastructure**: DigitalOcean + Supabase PostgreSQL

**Key Findings**:
- **90% Feature Parity** achieved with Enterprise Edition via 100+ OCA modules
- **Production-ready** Odoo core with 10 IPAI custom modules
- **Infrastructure instability**: 27 health check failures (services down)
- **Companion app gap**: pulse-hub web app exists, mobile app missing
- **Multi-tenancy gap**: Single-instance deployment, no tenant isolation

### Critical Blockers

| Blocker | Severity | Impact | Resolution Time |
|---------|----------|--------|------------------|
| Service Health (27 failures) | 🔴 Critical | All deployments blocked | 1-2 days |
| MCP Hub Down | 🔴 Critical | No agent coordination | 4-6 hours |
| No Mobile App | 🟡 High | Limited user access | 4-6 weeks |
| No Multi-Tenancy | 🟡 High | Cannot serve 8 agencies | 2-3 weeks |
| No RLS Policies | 🟡 High | Data leakage risk | 1 week |

### Recommended Path Forward

**Phase 1**: Stabilization (2 weeks) - Fix health checks, restore services
**Phase 2**: Multi-Tenancy MVP (3 weeks) - Database-per-tenant architecture
**Phase 3**: Web App Parity (4 weeks) - Complete pulse-hub feature set
**Phase 4**: Mobile MVP (6 weeks) - React Native app with core features
**Phase 5**: Full SaaS Rollout (8 weeks) - All 8 agencies onboarded

**Total Timeline**: 23 weeks (5.75 months)
**Team Required**: 3-4 developers (1 Odoo expert, 1 frontend, 1 mobile, 1 DevOps)

---

## 1. Current Capability Assessment

### 1.1 Odoo Core Platform

#### Custom Modules Inventory (15 modules)

| Module | Status | Purpose | LOC | Test Coverage |
|--------|--------|---------|-----|---------------|
| **ipai_core** | ✅ Production | Foundation utilities | 450 | 90% |
| **ipai_rate_policy** | ✅ Production | Rate automation (P60+25%) | 520 | 85% |
| **ipai_ppm** | ✅ Production | Program/project mgmt | 890 | 85% |
| **ipai_ppm_costsheet** | ✅ Production | Privacy-aware costing | 620 | 85% |
| **ipai_procure** | ✅ Production | Multi-round RFQ/SRM | 780 | 80% |
| **ipai_expense** | ✅ Production | OCR expense automation | 1,150 | 80% |
| **ipai_subscriptions** | ✅ Production | MRR/ARR tracking | 680 | 85% |
| **ipai_saas_ops** | ✅ Production | SaaS tenant management | 940 | 80% |
| **ipai_approvals** | ✅ Production | Multi-stage workflows | 530 | 85% |
| **superset_connector** | ✅ Production | Apache Superset BI | 420 | N/A |
| **ipai_knowledge_ai** | ✅ Production | pgVector semantic search | 720 | 75% |
| **apps_admin_enhancements** | ✅ Production | Admin UX improvements | ~300 | N/A |
| **pulser_hub_sync** | ✅ Production | Web app API bridge | ~400 | N/A |
| **github_integration** | ✅ Production | GitHub webhook handler | ~500 | N/A |
| **superset_menu** | ✅ Production | BI menu integration | ~200 | N/A |

**Total Code**: ~8,500 lines of production Python
**Total Tests**: 17 test files, 134 test methods, 2,771 lines of tests
**Average Test Coverage**: 83% across finance modules

#### OCA Modules (~97 modules installed)

**Categories**: Accounting (12), Sales (8), Purchase (7), Inventory (8), Project (6), HR (7), Helpdesk (5), Field Service (4), Manufacturing (6), Quality (5), Contracts (4), Website (6), eLearning (4), Reporting (6), Server Tools (8), Web (7), Documents (4), Queue (3)

**Enterprise Parity**: 90-95% feature coverage vs. Odoo Enterprise

### 1.2 Web Companion App (pulse-hub)

**Status**: ✅ Operational (but limited features)
**Tech Stack**: Next.js + React + Express API
**Location**: `pulse-hub/` (frontend) + `services/pulse-hub-api/` (backend)

**Current Features**:
- ✅ User authentication (Odoo session)
- ✅ Dashboard overview
- ✅ Task/project views
- ✅ Basic reporting
- ✅ GitHub integration

**Missing Features** (for parity):
- ❌ Expense submission
- ❌ Approval workflows
- ❌ Mobile-responsive design
- ❌ Offline capability
- ❌ Real-time collaboration
- ❌ Document upload/OCR
- ❌ Push notifications

### 1.3 Infrastructure Stack

#### DigitalOcean Deployment

**Apps**:
- `ade-ocr-backend` (b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9) - Singapore region
- `expense-flow-api` (7f7b673b-35ed-4b20-a2ae-11e74c2109bf)

**Database**: Supabase PostgreSQL (spdtwktxdalcfigzeqrz)
**Region**: AWS us-east-1
**Connection**: Pooler (port 6543) for high concurrency

#### Microservices (11 services)

| Service | Status | Purpose | Port |
|---------|--------|---------|------|
| **odoo** | ⚠️ Degraded | Main ERP | 8069 |
| **pulse-hub-api** | ✅ Running | Web app backend | 3000 |
| **ai-inference-hub** | ⚠️ Down | PaddleOCR-VL (RTX 4090) | 8001 |
| **superset** | ✅ Running | BI dashboards | 8088 |
| **mcp-hub** | 🔴 Down | MCP coordinator | 3100 |
| **insightpulse-monitor** | ⚠️ Degraded | Health checks | 3200 |
| **paddleocr** | ✅ Running | OCR service | 8080 |
| **caddy/traefik** | ⚠️ Config | Reverse proxy | 80/443 |
| **mindsdb** | ⏸️ Optional | AI/ML queries | 47334 |
| **mlflow** | ⏸️ Optional | ML tracking | 5000 |
| **openmetadata** | ⏸️ Optional | Data catalog | 8585 |

**Health Status**: 27 active health check failures (critical services down)

#### AI/ML Stack

**OCR Processing**:
- **Model**: PaddleOCR-VL-900M (document understanding)
- **Hardware**: RTX 4090 (local GPU)
- **Endpoint**: https://ade-ocr-backend-d9dru.ondigitalocean.app
- **Min Confidence**: 0.60 (60%)
- **Post-processing**: OpenAI gpt-4o-mini

**Semantic Search**:
- **Vector DB**: pgvector extension in PostgreSQL
- **Embedding Model**: OpenAI text-embedding-3-small (1536 dimensions)
- **LLM**: OpenAI gpt-4o-mini for response generation

#### BI/Analytics Stack

**Apache Superset**: 5 pre-built dashboards
- Finance Overview
- Project Performance
- Procurement Analytics
- Expense Management
- Subscription Metrics

**Tableau Integration**: Published data sources for GenieView

**MindsDB**: Optional AI/ML query interface

### 1.4 Current Architecture Diagram

```mermaid
graph TD
    subgraph "Client Layer"
        WEB[Web Browser]
        MOBILE[Mobile App - MISSING]
    end

    subgraph "Frontend Layer"
        PULSEHUB[pulse-hub Next.js]
        ODOO_WEB[Odoo Web UI]
    end

    subgraph "API Gateway Layer"
        PULSEHUB_API[pulse-hub-api Express]
        CADDY[Caddy Reverse Proxy]
    end

    subgraph "Application Layer"
        ODOO[Odoo 19 CE + OCA]
        GITHUB_INT[GitHub Integration]
        IPAI_MODULES[15 IPAI Custom Modules]
    end

    subgraph "AI/ML Services"
        PADDLEOCR[PaddleOCR-VL RTX 4090]
        OPENAI[OpenAI API]
        PGVECTOR[pgVector Semantic Search]
    end

    subgraph "BI/Analytics"
        SUPERSET[Apache Superset]
        TABLEAU[Tableau Cloud]
    end

    subgraph "Data Layer"
        SUPABASE_PG[Supabase PostgreSQL]
        DO_SPACES[DigitalOcean Spaces]
    end

    subgraph "Infrastructure - DEGRADED"
        MCP_HUB[MCP Hub - DOWN]
        MONITOR[Health Monitor - ISSUES]
    end

    WEB --> PULSEHUB
    WEB --> ODOO_WEB
    MOBILE -.->|MISSING| PULSEHUB_API

    PULSEHUB --> PULSEHUB_API
    ODOO_WEB --> CADDY
    PULSEHUB_API --> CADDY

    CADDY --> ODOO
    ODOO --> GITHUB_INT
    ODOO --> IPAI_MODULES

    IPAI_MODULES --> PADDLEOCR
    IPAI_MODULES --> OPENAI
    IPAI_MODULES --> PGVECTOR

    SUPERSET --> SUPABASE_PG
    TABLEAU --> SUPABASE_PG
    ODOO --> SUPABASE_PG
    PULSEHUB_API --> SUPABASE_PG
    PADDLEOCR --> SUPABASE_PG

    ODOO --> DO_SPACES

    MCP_HUB -.->|DOWN| ODOO
    MONITOR -.->|FAILING| ODOO
```

---

## 2. SaaS Parity Gap Analysis

### 2.1 Multi-Tenancy Requirements

#### Current State: Single-Instance Deployment

**Architecture**: Monolithic single-database Odoo instance
**Data Isolation**: company_id field + record rules (RLS)
**Limitation**: All 8 agencies share same database

**Risks**:
- Data leakage via misconfigured record rules
- Performance degradation with large multi-company datasets
- Limited tenant customization (same codebase for all)
- Backup/restore affects all tenants

#### Target State: Multi-Tenant SaaS

**Architecture Options**:

**Option A: Database-per-Tenant (Recommended)**
```
odoo_rim (database)
odoo_ckvc (database)
odoo_bom (database)
...
odoo_rmqb (database)
```

**Pros**:
- ✅ Complete data isolation
- ✅ Independent backups/restores
- ✅ Tenant-specific customizations
- ✅ Better performance at scale

**Cons**:
- ❌ Higher infrastructure cost
- ❌ Requires connection pooling (pgBouncer)
- ❌ Module updates need per-tenant migration

**Option B: Schema-per-Tenant**
```
Database: odoo_saas
  - Schema: rim
  - Schema: ckvc
  - Schema: bom
  ...
```

**Pros**:
- ✅ Good data isolation
- ✅ Shared infrastructure
- ✅ Easier module updates

**Cons**:
- ❌ PostgreSQL schema limitations
- ❌ Odoo doesn't natively support schema-per-tenant
- ❌ Requires custom middleware

**Option C: Multi-Company (Current)**
```
Database: odoo_prod
  company_id = 1 (RIM)
  company_id = 2 (CKVC)
  ...
```

**Pros**:
- ✅ Native Odoo support
- ✅ Shared infrastructure

**Cons**:
- ❌ RLS complexity and maintenance burden
- ❌ No tenant-level customization
- ❌ All-or-nothing backups

**Recommendation**: **Option A** (Database-per-Tenant) for production SaaS

### 2.2 Mobile App MVP Features

#### Platform Decision: React Native vs Flutter

**React Native**:
- ✅ Shared codebase with pulse-hub (React)
- ✅ Larger ecosystem and community
- ✅ Easier hiring (JavaScript developers)
- ✅ Good performance for business apps

**Flutter**:
- ✅ Better performance (native compilation)
- ✅ More consistent UI across platforms
- ❌ Different language (Dart)
- ❌ Smaller talent pool

**Recommendation**: **React Native** for faster time-to-market and code reuse

#### MVP Feature Set (Priority 1)

**Must-Have Features**:
1. ✅ Authentication (Odoo OAuth)
2. ✅ Dashboard (tasks, expenses, approvals)
3. ✅ Expense submission (camera + OCR)
4. ✅ Approval workflows (approve/reject)
5. ✅ Task management (view, update status)
6. ✅ Push notifications (approvals, mentions)
7. ✅ Offline mode (basic read operations)
8. ✅ File upload (receipts, documents)

**Nice-to-Have Features** (Phase 2):
- Real-time collaboration
- Advanced reporting
- Time tracking
- GPS check-in/out
- Voice notes
- Document scanner

### 2.3 Authentication & Authorization

#### Current Auth Stack

**Odoo Authentication**:
- Session-based authentication
- 2FA support (auth_totp module)
- Password policy enforcement
- Session timeout: 30 minutes

**pulse-hub Authentication**:
- Odoo session passthrough
- No independent auth

**Gaps**:
- ❌ No OAuth2/OIDC server
- ❌ No API key management
- ❌ No SSO (SAML, Google, Azure AD)
- ❌ No mobile-optimized auth flow

#### Target Auth Architecture

**OAuth2/OIDC Server** (via `auth_oauth` module + custom provider):
```
Client (web/mobile) → OAuth2 Authorization Code Flow
                   → Token Exchange
                   → Access Token + Refresh Token
                   → API Calls with Bearer Token
```

**Multi-Tenant Auth Flow**:
```
User enters: user@rim.insightpulse.ai
           → DNS: rim.insightpulse.ai
           → Route to: odoo_rim database
           → Auth against: res.users (company_id = RIM)
```

**Required Modules**:
- `auth_oauth` (OCA) - OAuth2 provider
- `auth_jwt` (OCA) - JWT token support
- `auth_api_key` (OCA) - API key management
- `auth_totp` (Core) - 2FA

### 2.4 Billing & Subscription Management

#### Current Capability: ipai_subscriptions Module

**Features**:
- ✅ MRR/ARR calculation
- ✅ Churn rate analysis
- ✅ Subscription lifecycle
- ✅ Revenue recognition

**Gaps**:
- ❌ No usage-based billing
- ❌ No tenant resource tracking
- ❌ No automated invoicing
- ❌ No payment gateway (Stripe/PayPal)
- ❌ No dunning workflows

#### Target Billing Architecture

**Usage Tracking** (via ipai_saas_ops):
```python
# Track tenant resource usage
tenant.usage_logs.create({
    'metric': 'storage_gb',
    'value': 12.5,
    'date': fields.Date.today(),
})

# Track API calls
tenant.usage_logs.create({
    'metric': 'api_calls',
    'value': 1250,
    'date': fields.Date.today(),
})
```

**Billing Integration** (Stripe):
```python
# Create Stripe customer
stripe_customer = stripe.Customer.create(
    email=tenant.admin_email,
    name=tenant.name,
    metadata={'tenant_id': tenant.id}
)

# Create subscription
stripe_subscription = stripe.Subscription.create(
    customer=stripe_customer.id,
    items=[{'price': 'price_1234'}],
)

# Track in Odoo
tenant.stripe_customer_id = stripe_customer.id
tenant.stripe_subscription_id = stripe_subscription.id
```

**Required Modules**:
- ipai_subscriptions (✅ installed)
- `payment_stripe` (OCA) - Stripe integration
- ipai_saas_ops (✅ installed, needs enhancement)

### 2.5 Data Isolation & Security

#### Current Security Measures

**Record-Level Security (RLS)**:
- `company_id` field on all models
- Record rules enforce multi-company isolation
- Security groups control feature access

**Gaps**:
- ⚠️ RLS rules untested at scale
- ⚠️ No tenant-level encryption
- ⚠️ No audit logs for data access
- ⚠️ No data residency controls

#### Target Security Architecture

**Database-Level Isolation**:
```sql
-- Each tenant has own database
CREATE DATABASE odoo_rim;
CREATE DATABASE odoo_ckvc;

-- RLS within database for department-level isolation
CREATE POLICY department_isolation ON res_users
    USING (department_id IN (SELECT id FROM hr_department WHERE company_id = current_company_id));
```

**Audit Logging** (via `auditlog` OCA module):
- Track all CRUD operations
- Log user, timestamp, model, record_id, old/new values
- Retention: 90 days

**Encryption**:
- At-rest: PostgreSQL pgcrypto for sensitive fields
- In-transit: TLS/SSL for all connections
- Backup: Encrypted with AES-256

**Required Modules**:
- `auditlog` (OCA) ✅
- `security_hardening` (custom) ✅
- `data_encryption` (OCA) - for field-level encryption

### 2.6 Scalability Requirements

#### Current Performance Benchmarks

**Odoo Performance** (from MODULES.md):
- Concurrent Users: 450 (target: 500)
- API Response Time (P95): 180ms (target: <200ms) ✅
- OCR Throughput: 850/hour (target: 1,000/hour) 🔄
- Database Size: 42 GB (target: <100 GB) ✅

**Bottlenecks**:
- PaddleOCR-VL inference: P95 = 4.8s
- pgVector search: P95 = 650ms
- Superset dashboard load: 2.8s (18 queries)

#### Target Scalability Metrics (8 Agencies)

**Assumptions**:
- 50 users per agency × 8 agencies = 400 concurrent users
- 10,000 transactions/day × 8 agencies = 80,000 transactions/day
- 100 GB storage × 8 tenants = 800 GB total

**Infrastructure Requirements**:

**Database** (Supabase PostgreSQL):
- Current: Single instance
- Target: pgBouncer connection pooling (500 connections)
- Backup: Daily automated snapshots per tenant

**Application Servers** (DigitalOcean App Platform):
- Current: 2 Odoo workers
- Target: 8 Odoo workers (1 per tenant) + load balancer
- Auto-scaling: 2-16 workers based on CPU/memory

**AI Services** (PaddleOCR-VL + OpenAI):
- Current: Single RTX 4090 GPU
- Target: Queue-based processing (queue_job module)
- Fallback: Azure Document Intelligence API

**Estimated Costs**:
- DigitalOcean: $200/month (8 app instances @ $25/each)
- Supabase: $25/month (Pro tier with 8 databases)
- OpenAI API: ~$50/month
- **Total**: ~$275/month for 8 agencies

---

## 3. Technical Architecture (Target State)

### 3.1 Multi-Tenant Deployment Strategy

#### Recommended: Database-per-Tenant with Shared Codebase

```mermaid
graph LR
    subgraph "Route Layer"
        LB[Load Balancer<br/>insightpulse.ai]
    end

    subgraph "Tenant Routing"
        LB --> |rim.insightpulse.ai| ODOO_RIM
        LB --> |ckvc.insightpulse.ai| ODOO_CKVC
        LB --> |bom.insightpulse.ai| ODOO_BOM
        LB --> |...| ODOO_OTHER[...]
        LB --> |rmqb.insightpulse.ai| ODOO_RMQB
    end

    subgraph "Application Pods"
        ODOO_RIM[Odoo Pod RIM]
        ODOO_CKVC[Odoo Pod CKVC]
        ODOO_BOM[Odoo Pod BOM]
        ODOO_RMQB[Odoo Pod RMQB]
    end

    subgraph "Database Layer"
        ODOO_RIM --> DB_RIM[(odoo_rim)]
        ODOO_CKVC --> DB_CKVC[(odoo_ckvc)]
        ODOO_BOM --> DB_BOM[(odoo_bom)]
        ODOO_RMQB --> DB_RMQB[(odoo_rmqb)]
    end

    subgraph "Shared Services"
        ODOO_RIM -.-> SHARED_OCR[PaddleOCR-VL GPU]
        ODOO_CKVC -.-> SHARED_OCR
        ODOO_BOM -.-> SHARED_OCR
        ODOO_RMQB -.-> SHARED_OCR

        ODOO_RIM -.-> SHARED_BI[Apache Superset]
        ODOO_CKVC -.-> SHARED_BI
        ODOO_BOM -.-> SHARED_BI
        ODOO_RMQB -.-> SHARED_BI
    end
```

**Deployment Pattern**:
```yaml
# DigitalOcean App Spec per Tenant
name: odoo-rim
region: sgp
services:
  - name: odoo
    dockerfile_path: Dockerfile
    envs:
      - key: POSTGRES_DB
        value: odoo_rim
      - key: ODOO_DATABASE
        value: odoo_rim
      - key: COMPANY_NAME
        value: RIM
    http_port: 8069
    instance_count: 2
    instance_size_slug: basic-xxs

databases:
  - name: odoo-rim-db
    engine: PG
    version: "15"
```

### 3.2 Web App Feature Parity Architecture

#### pulse-hub Target Features

**Core Pages**:
1. **Dashboard** - KPI cards, recent activity, quick actions
2. **Tasks** - Kanban board, list view, filters
3. **Projects** - Gantt chart, timeline, budget tracking
4. **Expenses** - Receipt capture, OCR preview, approval status
5. **Approvals** - Pending actions, approval history, delegation
6. **Reports** - Embedded Superset dashboards, custom queries
7. **Settings** - Profile, notifications, preferences

**API Requirements**:
```typescript
// pulse-hub-api Express routes
GET /api/v1/dashboard/kpis
GET /api/v1/tasks?status=pending&assigned_to=me
POST /api/v1/expenses/submit
POST /api/v1/expenses/:id/ocr
GET /api/v1/approvals/pending
POST /api/v1/approvals/:id/approve
GET /api/v1/projects/:id/budget
```

**State Management** (Redux):
```typescript
// Global state structure
{
  auth: { user, token, tenant },
  dashboard: { kpis, recentActivity },
  tasks: { items, filters, selectedTask },
  expenses: { items, pendingOCR, approvals },
  ui: { sidebarOpen, theme, notifications }
}
```

**Real-Time Features** (WebSockets):
```typescript
// Socket.io events
io.on('connection', (socket) => {
  socket.on('approval:pending', (data) => {
    // Notify user of new approval request
  });

  socket.on('expense:ocr:complete', (data) => {
    // Update expense with OCR results
  });

  socket.on('task:updated', (data) => {
    // Refresh task in UI
  });
});
```

### 3.3 Mobile App Architecture (React Native)

#### Technology Stack

**Framework**: React Native 0.73
**Navigation**: React Navigation 6
**State Management**: Redux Toolkit
**API Client**: Axios + RTK Query
**Offline Storage**: AsyncStorage + Redux Persist
**Push Notifications**: Firebase Cloud Messaging
**Camera**: react-native-camera
**Image Upload**: react-native-image-picker

#### App Structure

```
mobile-app/
├── src/
│   ├── screens/           # Screen components
│   │   ├── Dashboard/
│   │   ├── Tasks/
│   │   ├── Expenses/
│   │   ├── Approvals/
│   │   └── Settings/
│   ├── components/        # Reusable components
│   │   ├── TaskCard/
│   │   ├── ExpenseForm/
│   │   └── ApprovalButton/
│   ├── store/             # Redux store
│   │   ├── slices/
│   │   └── api/
│   ├── services/          # API services
│   │   ├── odoo.ts
│   │   ├── ocr.ts
│   │   └── auth.ts
│   ├── utils/             # Utilities
│   └── navigation/        # Navigation config
├── ios/                   # iOS native code
├── android/               # Android native code
└── package.json
```

#### Key Features Implementation

**1. Receipt Capture + OCR**:
```typescript
import { launchCamera } from 'react-native-image-picker';
import { uploadToOCR } from '../services/ocr';

const captureReceipt = async () => {
  const result = await launchCamera({ mediaType: 'photo' });

  if (result.assets?.[0]) {
    const ocrResult = await uploadToOCR(result.assets[0].uri);
    dispatch(createExpense({
      vendor: ocrResult.vendor,
      amount: ocrResult.total,
      date: ocrResult.date,
      category: ocrResult.category,
    }));
  }
};
```

**2. Push Notifications**:
```typescript
import messaging from '@react-native-firebase/messaging';

// Register device token
messaging().getToken().then(token => {
  api.post('/api/v1/notifications/register', { token });
});

// Handle incoming notifications
messaging().onMessage(async remoteMessage => {
  if (remoteMessage.data?.type === 'approval_pending') {
    dispatch(fetchApprovals());
  }
});
```

**3. Offline Support**:
```typescript
import NetInfo from '@react-native-community/netinfo';

// Sync queue for offline actions
const offlineQueue = [];

const createExpenseOffline = (expense) => {
  offlineQueue.push({
    action: 'createExpense',
    payload: expense,
    timestamp: Date.now(),
  });
};

// Sync when online
NetInfo.addEventListener(state => {
  if (state.isConnected) {
    syncOfflineQueue();
  }
});
```

### 3.4 API Gateway & Microservices Coordination

#### Current Microservices Architecture (Needs Consolidation)

**Redundant Services**:
- `pulse-hub-api` (Express) - Web app backend
- `expense-flow-api` (Express) - Expense submission
- `ai-inference-hub` (Python) - OCR processing

**Recommendation**: Consolidate into single API gateway

#### Target Architecture: Unified API Gateway

```mermaid
graph TD
    subgraph "Client Layer"
        WEB[Web App]
        MOBILE[Mobile App]
    end

    subgraph "API Gateway"
        GATEWAY[Express API Gateway<br/>Port 3000]
    end

    subgraph "Backend Services"
        ODOO[Odoo XML-RPC API]
        OCR[PaddleOCR Service]
        VECTOR[pgVector Search]
        SUPERSET[Superset API]
    end

    subgraph "Message Queue"
        QUEUE[Queue Jobs<br/>queue_job module]
    end

    WEB --> GATEWAY
    MOBILE --> GATEWAY

    GATEWAY --> |Auth, CRUD| ODOO
    GATEWAY --> |Receipt Upload| OCR
    GATEWAY --> |Semantic Search| VECTOR
    GATEWAY --> |Dashboards| SUPERSET

    OCR --> QUEUE
    GATEWAY --> QUEUE

    QUEUE --> ODOO
```

**API Gateway Responsibilities**:
- Authentication (JWT validation)
- Request routing
- Response caching
- Rate limiting
- Error handling
- Logging/monitoring

**Sample Gateway Implementation**:
```typescript
// services/api-gateway/src/routes/expenses.ts
import express from 'express';
import { authenticate } from '../middleware/auth';
import { OdooClient } from '../clients/odoo';
import { OCRService } from '../clients/ocr';

const router = express.Router();

router.post('/expenses/submit', authenticate, async (req, res) => {
  try {
    // 1. Upload image to OCR service
    const ocrResult = await OCRService.process(req.file);

    // 2. Create expense in Odoo
    const expense = await OdooClient.create('hr.expense', {
      name: ocrResult.vendor,
      unit_amount: ocrResult.total,
      date: ocrResult.date,
      product_id: ocrResult.category_id,
    });

    // 3. Queue approval workflow
    await OdooClient.call('hr.expense', 'action_submit_expenses', [expense.id]);

    res.json({ success: true, expense_id: expense.id });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
```

### 3.5 Real-Time Sync Architecture

#### Websocket Event System

**Technology**: Socket.io (both web and mobile)

**Event Flow**:
```
User Action (web/mobile)
    ↓
API Gateway
    ↓
Odoo State Change
    ↓
Odoo Webhook Trigger
    ↓
Socket.io Server
    ↓
Broadcast to Connected Clients
    ↓
Update UI in Real-Time
```

**Implementation**:
```typescript
// Socket.io server (in API Gateway)
import { Server } from 'socket.io';

const io = new Server(httpServer, {
  cors: { origin: '*' }
});

io.on('connection', (socket) => {
  socket.on('subscribe', (data) => {
    socket.join(`user:${data.userId}`);
    socket.join(`tenant:${data.tenantId}`);
  });
});

// Odoo webhook → Socket.io
app.post('/webhooks/odoo/expense_approved', (req, res) => {
  const { expense_id, user_id, tenant_id } = req.body;

  io.to(`user:${user_id}`).emit('expense:approved', {
    expense_id,
    timestamp: Date.now(),
  });

  io.to(`tenant:${tenant_id}`).emit('expense:updated', {
    expense_id,
  });

  res.sendStatus(200);
});
```

**Mobile Client**:
```typescript
// React Native socket client
import { io } from 'socket.io-client';

const socket = io('https://api.insightpulse.ai', {
  auth: { token: authToken }
});

socket.on('connect', () => {
  socket.emit('subscribe', {
    userId: user.id,
    tenantId: user.tenantId,
  });
});

socket.on('expense:approved', (data) => {
  dispatch(updateExpenseStatus(data.expense_id, 'approved'));
  showNotification('Expense approved!');
});
```

---

## 4. SuperClaude Sub-Agent Workflow

### 4.1 Agent Responsibilities Matrix

| Agent | Primary Role | Scope | Estimated Effort |
|-------|-------------|-------|------------------|
| **odoo_developer** | Odoo module development, OCA compliance, Python/XML | Multi-tenancy, mobile API, RLS policies | 60% of project |
| **devops_engineer** | CI/CD, Docker, DigitalOcean deployment, monitoring | Infrastructure automation, tenant provisioning | 20% of project |
| **bi_architect** | Superset dashboards, SQL optimization, data modeling | Multi-tenant analytics, report embedding | 10% of project |
| **document_creator** | API documentation, user guides, deployment runbooks | Comprehensive technical documentation | 5% of project |
| **diagram_designer** | Architecture diagrams, workflows, data models | Visual documentation, presentation materials | 5% of project |

### 4.2 Phase-Specific Agent Assignments

#### Phase 1: Stabilization (Weeks 1-2)

**Primary Agent**: devops_engineer
**Supporting**: odoo_developer

**Tasks**:
1. **Fix Health Check Failures** (devops_engineer)
   - Debug 27 service failures
   - Restore MCP Hub service
   - Validate all microservices
   - Configure monitoring alerts

2. **Database Optimization** (odoo_developer)
   - Add missing indexes
   - Run VACUUM ANALYZE
   - Optimize slow queries
   - Test RLS policies

3. **Documentation** (document_creator)
   - Update deployment status
   - Create troubleshooting guide
   - Document service dependencies

#### Phase 2: Multi-Tenancy MVP (Weeks 3-5)

**Primary Agent**: odoo_developer
**Supporting**: devops_engineer, bi_architect

**Tasks**:
1. **Database-per-Tenant Architecture** (odoo_developer)
   - Implement tenant provisioning module
   - Create database creation workflow
   - Configure pgBouncer connection pooling
   - Test tenant isolation

2. **Tenant Routing** (devops_engineer)
   - Configure DNS routing (*.insightpulse.ai)
   - Setup DigitalOcean App Platform per tenant
   - Implement load balancer rules
   - Configure SSL certificates

3. **Multi-Tenant BI** (bi_architect)
   - Configure Superset multi-tenancy
   - Implement RLS policies in Superset
   - Create tenant-specific dashboards
   - Test data isolation

#### Phase 3: Web App Parity (Weeks 6-9)

**Primary Agent**: odoo_developer (for API)
**External**: Frontend developer (Next.js)

**Tasks**:
1. **API Gateway Development** (odoo_developer)
   - Consolidate microservices into unified gateway
   - Implement JWT authentication
   - Add rate limiting and caching
   - Create comprehensive API documentation

2. **Frontend Development** (External - frontend developer)
   - Implement missing features (expenses, approvals)
   - Add mobile-responsive design
   - Integrate WebSocket for real-time updates
   - Implement offline capability

3. **Testing** (odoo_developer)
   - Write API integration tests
   - Perform load testing (500 concurrent users)
   - Test multi-tenant isolation
   - Validate security policies

#### Phase 4: Mobile MVP (Weeks 10-15)

**Primary Agent**: External mobile developer (React Native)
**Supporting**: odoo_developer (API), devops_engineer (push notifications)

**Tasks**:
1. **Mobile App Development** (External - mobile developer)
   - Setup React Native project
   - Implement 8 MVP features (see 2.2)
   - Configure push notifications (FCM)
   - Build offline sync mechanism

2. **API Enhancements** (odoo_developer)
   - Add mobile-specific endpoints
   - Optimize API for mobile bandwidth
   - Implement image compression
   - Add conflict resolution for offline sync

3. **DevOps** (devops_engineer)
   - Configure Firebase Cloud Messaging
   - Setup TestFlight (iOS) and Play Console (Android)
   - Implement CI/CD for mobile builds
   - Configure over-the-air updates (CodePush)

#### Phase 5: Full SaaS Rollout (Weeks 16-23)

**Primary Agent**: devops_engineer
**Supporting**: All agents

**Tasks**:
1. **Agency Onboarding** (devops_engineer)
   - Provision 8 tenant databases
   - Configure DNS and SSL for each tenant
   - Import initial data (users, departments, projects)
   - Test tenant-specific configurations

2. **Training & Documentation** (document_creator)
   - Create user training materials
   - Record video tutorials
   - Write admin documentation
   - Prepare support runbooks

3. **Monitoring & Support** (devops_engineer)
   - Configure tenant-specific monitoring
   - Setup alert rules (downtime, errors, performance)
   - Implement log aggregation (ELK stack)
   - Create support ticket system

### 4.3 Parallel Execution Patterns

**Week 3-5 Parallelization**:
- **odoo_developer** → Database-per-tenant architecture
- **devops_engineer** → Tenant routing + DigitalOcean setup
- **bi_architect** → Superset multi-tenancy configuration

**Week 6-9 Parallelization**:
- **odoo_developer** → API gateway development
- **Frontend developer** → pulse-hub feature completion
- **devops_engineer** → Load testing infrastructure

**Week 10-15 Parallelization**:
- **Mobile developer** → React Native app development
- **odoo_developer** → Mobile API enhancements
- **devops_engineer** → Push notification infrastructure

---

## 5. Parallel Worktree Strategy

### 5.1 Git Worktree Architecture

**Concept**: Use git worktrees to work on multiple tenant customizations simultaneously

#### Main Development Worktree

**Location**: `/Users/tbwa/Documents/GitHub/insightpulse-odoo/` (current)
**Branch**: `main`
**Purpose**: Core platform development (shared codebase for all tenants)

**Structure**:
```
insightpulse-odoo/
├── addons/
│   ├── custom/          # 15 IPAI modules
│   ├── oca/             # ~97 OCA modules
│   └── insightpulse/    # InsightPulse modules
├── services/            # 11 microservices
├── deploy/              # Deployment configs
└── docs/                # Documentation
```

#### Per-Agency Customization Worktrees

**Setup Command**:
```bash
# Create worktrees for each agency
git worktree add ../insightpulse-odoo-rim tenants/rim
git worktree add ../insightpulse-odoo-ckvc tenants/ckvc
git worktree add ../insightpulse-odoo-bom tenants/bom
git worktree add ../insightpulse-odoo-jpal tenants/jpal
git worktree add ../insightpulse-odoo-jli tenants/jli
git worktree add ../insightpulse-odoo-jap tenants/jap
git worktree add ../insightpulse-odoo-las tenants/las
git worktree add ../insightpulse-odoo-rmqb tenants/rmqb
```

**Per-Tenant Branch Structure**:
```
tenants/rim
├── main                          # Merged from main worktree
├── custom/                       # Tenant-specific modules
│   ├── rim_custom_module_1/
│   ├── rim_custom_module_2/
│   └── rim_branding/
└── config/
    └── odoo.conf                 # RIM-specific config
```

### 5.2 Tenant Customization Strategy

#### Level 1: Shared Codebase (90% of functionality)

**Modules**: All 15 IPAI modules + 97 OCA modules
**Source**: `main` branch
**Deployment**: Shared image, database-per-tenant

#### Level 2: Tenant-Specific Configuration (8% of customization)

**Configuration Files**:
- `config/odoo.conf` - Database, ports, company name
- `data/company_data.xml` - Logo, colors, contact info
- `data/users.xml` - Initial users and roles

**Example**: RIM configuration
```ini
# config/odoo_rim.conf
[options]
db_name = odoo_rim
db_user = odoo_rim
company_name = RIM Agency
admin_passwd = [SECRET]
addons_path = /mnt/extra-addons/custom,/mnt/extra-addons/oca,/usr/lib/python3/dist-packages/odoo/addons
```

#### Level 3: Tenant-Specific Modules (2% of customization)

**Use Cases**:
- Custom reports specific to agency
- Integrations with agency-specific systems
- Branding modules (logo, colors, email templates)

**Example**: RIM custom module
```
addons/custom/rim_custom_reports/
├── __init__.py
├── __manifest__.py
├── models/
│   └── sale_report_rim.py
├── reports/
│   └── rim_invoice_template.xml
└── security/
    └── ir.model.access.csv
```

### 5.3 Merge/Integration Strategy

#### Workflow

**1. Core Platform Development** (main worktree):
```bash
cd ~/Documents/GitHub/insightpulse-odoo/

# Develop core feature
git checkout -b feature/new-approval-workflow
# ... make changes ...
git commit -m "feat(ipai_approvals): add parallel approval routing"
git push origin feature/new-approval-workflow

# Create PR, review, merge to main
```

**2. Propagate to Tenant Worktrees**:
```bash
# In each tenant worktree
cd ~/Documents/GitHub/insightpulse-odoo-rim/
git fetch origin
git merge origin/main

# Resolve conflicts (if any tenant-specific customizations conflict)
# Test tenant-specific modules still work
# Deploy to tenant
```

**3. Tenant-Specific Development**:
```bash
cd ~/Documents/GitHub/insightpulse-odoo-rim/

# Develop RIM-specific feature
git checkout -b tenants/rim/custom-invoice-template
# ... make changes in addons/custom/rim_custom_reports/ ...
git commit -m "feat(rim): add custom invoice template"
git push origin tenants/rim/custom-invoice-template

# Deploy only to RIM tenant (not other tenants)
```

### 5.4 CI/CD Pipeline per Worktree

**GitHub Actions Workflow**:
```yaml
# .github/workflows/deploy-tenant.yml
name: Deploy Tenant

on:
  push:
    branches:
      - 'tenants/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Extract tenant name
        id: tenant
        run: echo "TENANT=$(echo ${{ github.ref }} | cut -d'/' -f3)" >> $GITHUB_OUTPUT

      - name: Checkout tenant worktree
        uses: actions/checkout@v3
        with:
          ref: ${{ github.ref }}

      - name: Deploy to DigitalOcean
        env:
          TENANT: ${{ steps.tenant.outputs.TENANT }}
          DO_ACCESS_TOKEN: ${{ secrets.DO_ACCESS_TOKEN }}
        run: |
          # Update app spec for this tenant
          doctl apps update ${DO_APP_ID_${TENANT}} --spec deploy/odoo.${TENANT}.yml

          # Trigger deployment
          doctl apps create-deployment ${DO_APP_ID_${TENANT}} --force-rebuild

          # Wait for deployment to complete
          doctl apps wait ${DO_APP_ID_${TENANT}}
```

### 5.5 Backup Strategy per Tenant

**Daily Automated Backups**:
```bash
# Backup script (runs daily via cron)
#!/bin/bash
# scripts/backup-tenant.sh

TENANT=$1
DATE=$(date +%Y%m%d)

# Backup database
pg_dump -U odoo -d odoo_${TENANT} -Fc > backups/odoo_${TENANT}_${DATE}.dump

# Backup filestore
tar -czf backups/filestore_${TENANT}_${DATE}.tar.gz /var/lib/odoo/.local/share/Odoo/filestore/odoo_${TENANT}/

# Upload to DigitalOcean Spaces
s3cmd put backups/odoo_${TENANT}_${DATE}.dump s3://insightpulse-backups/${TENANT}/
s3cmd put backups/filestore_${TENANT}_${DATE}.tar.gz s3://insightpulse-backups/${TENANT}/

# Cleanup local backups >7 days old
find backups/ -name "odoo_${TENANT}_*.dump" -mtime +7 -delete
find backups/ -name "filestore_${TENANT}_*.tar.gz" -mtime +7 -delete
```

**Cron Schedule**:
```cron
# /etc/cron.d/tenant-backups
0 2 * * * root /opt/insightpulse/scripts/backup-tenant.sh rim
0 2 * * * root /opt/insightpulse/scripts/backup-tenant.sh ckvc
0 2 * * * root /opt/insightpulse/scripts/backup-tenant.sh bom
# ... repeat for all 8 tenants
```

---

## 6. Deployment Roadmap

### 6.1 Phase 1: Stabilization (Weeks 1-2)

**Goal**: Fix current infrastructure issues, restore service health

#### Week 1: Critical Service Recovery

**Assigned To**: devops_engineer (primary), odoo_developer (support)

**Day 1-2: Health Check Diagnosis**
```bash
# Investigate health check failures
cd ~/insightpulse-odoo/
gh issue list --label "health-check" --state open

# Check service status
docker compose ps
docker compose logs --tail=100 odoo
docker compose logs --tail=100 mcp-hub
docker compose logs --tail=100 ai-inference-hub

# Identify root causes:
# - MCP Hub: Connection refused (service down)
# - AI Inference Hub: GPU driver issues
# - Odoo: Database connection pool exhausted
```

**Day 3-4: Service Restoration**
```bash
# Fix MCP Hub
cd services/mcp-hub/
npm install
npm run build
docker compose up -d mcp-hub

# Fix AI Inference Hub
cd services/ai-inference-hub/
# Check GPU availability
nvidia-smi
# Rebuild Docker image with correct CUDA version
docker build -t ai-inference-hub:latest .
docker compose up -d ai-inference-hub

# Fix Odoo connection pooling
# Add pgBouncer
docker compose -f docker-compose.pgbouncer.yml up -d
```

**Day 5: Validation**
```bash
# Run health check script
./scripts/health-check.sh

# Verify all services healthy
# Expected: 0 failures (down from 27)
```

**Deliverables**:
- ✅ All 27 health check failures resolved
- ✅ MCP Hub operational
- ✅ AI Inference Hub GPU working
- ✅ Odoo stable with connection pooling

#### Week 2: Database Optimization & Testing

**Assigned To**: odoo_developer (primary), bi_architect (support)

**Day 1-2: Database Performance Tuning**
```sql
-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_rate_policy_lines_role
ON rate_policy_line(role_id, policy_id);

CREATE INDEX CONCURRENTLY idx_ppm_budget_program
ON ppm_budget(program_id, state);

CREATE INDEX CONCURRENTLY idx_expense_employee_date
ON hr_expense(employee_id, date);

-- Vacuum and analyze
VACUUM ANALYZE;

-- Update PostgreSQL config for better performance
# postgresql.conf
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
max_connections = 500  # For pgBouncer
```

**Day 3-4: RLS Policy Testing**
```python
# Test multi-company isolation
# In Odoo shell
env['res.users'].search([]).write({'company_id': 1})  # RIM company

# Verify record rules work
expenses = env['hr.expense'].search([])
assert all(e.company_id.id == 1 for e in expenses)

# Test cross-company access (should be denied)
try:
    expense_from_other_company = env['hr.expense'].browse(999)
    assert False, "Should not be able to access other company data"
except AccessError:
    pass  # Expected
```

**Day 5: Load Testing**
```bash
# Install k6 load testing tool
brew install k6

# Run load test
k6 run tests/load/concurrent-users.js
# Target: 500 concurrent users
# Expected P95 response time: <500ms
```

**Deliverables**:
- ✅ Database indexes added
- ✅ RLS policies tested and validated
- ✅ Load testing passed (500 concurrent users)
- ✅ Performance benchmarks documented

### 6.2 Phase 2: Multi-Tenancy MVP (Weeks 3-5)

**Goal**: Implement database-per-tenant architecture

#### Week 3: Tenant Provisioning Module

**Assigned To**: odoo_developer

**Tasks**:
1. **Create ipai_saas_tenant_provisioning module**
```python
# addons/custom/ipai_saas_tenant_provisioning/models/saas_tenant.py
class SaasTenant(models.Model):
    _name = 'saas.tenant'

    name = fields.Char('Tenant Name', required=True)
    subdomain = fields.Char('Subdomain', required=True)  # e.g., 'rim'
    database_name = fields.Char('Database Name', compute='_compute_database_name')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('provisioning', 'Provisioning'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
    ], default='draft')

    admin_email = fields.Char('Admin Email')
    plan = fields.Selection([
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('professional', 'Professional'),
    ], default='basic')

    def action_provision(self):
        """Provision new tenant database."""
        self.ensure_one()
        self.state = 'provisioning'

        # 1. Create PostgreSQL database
        self._create_database()

        # 2. Initialize Odoo schema
        self._initialize_odoo_schema()

        # 3. Install modules
        self._install_modules()

        # 4. Configure company data
        self._configure_company()

        # 5. Create admin user
        self._create_admin_user()

        # 6. Deploy to DigitalOcean
        self._deploy_to_digitalocean()

        self.state = 'active'

    def _create_database(self):
        import psycopg2
        conn = psycopg2.connect(
            host='postgres',
            user='postgres',
            password=os.environ['POSTGRES_PASSWORD']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE {self.database_name};")
        cursor.close()
        conn.close()

    def _deploy_to_digitalocean(self):
        import subprocess
        subprocess.run([
            'doctl', 'apps', 'create',
            '--spec', f'deploy/odoo.{self.subdomain}.yml'
        ])
```

2. **Create DO app spec template**
```yaml
# deploy/odoo.template.yml
name: odoo-{{TENANT}}
region: sgp
services:
  - name: odoo
    dockerfile_path: Dockerfile
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: tenants/{{TENANT}}
      deploy_on_push: true
    envs:
      - key: POSTGRES_DB
        value: odoo_{{TENANT}}
      - key: ODOO_DATABASE
        value: odoo_{{TENANT}}
    http_port: 8069
    instance_count: 2
    instance_size_slug: basic-xxs
```

**Deliverables**:
- ✅ ipai_saas_tenant_provisioning module
- ✅ Automated tenant provisioning workflow
- ✅ DO app spec template

#### Week 4: Tenant Routing & DNS

**Assigned To**: devops_engineer

**Tasks**:
1. **Configure wildcard DNS**
```bash
# DigitalOcean DNS records
*.insightpulse.ai A 192.0.2.1
rim.insightpulse.ai CNAME insightpulse.ai
ckvc.insightpulse.ai CNAME insightpulse.ai
bom.insightpulse.ai CNAME insightpulse.ai
# ... repeat for all 8 tenants
```

2. **Configure load balancer**
```nginx
# /etc/nginx/conf.d/tenants.conf
map $host $tenant_db {
    rim.insightpulse.ai odoo_rim;
    ckvc.insightpulse.ai odoo_ckvc;
    bom.insightpulse.ai odoo_bom;
    # ... repeat for all 8 tenants
}

server {
    listen 443 ssl;
    server_name *.insightpulse.ai;

    ssl_certificate /etc/letsencrypt/live/insightpulse.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/insightpulse.ai/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8069;
        proxy_set_header X-Tenant-Database $tenant_db;
        proxy_set_header Host $host;
    }
}
```

3. **Configure SSL certificates**
```bash
# Generate wildcard certificate
certbot certonly --dns-digitalocean \
  --dns-digitalocean-credentials ~/digitalocean.ini \
  -d insightpulse.ai \
  -d '*.insightpulse.ai'
```

**Deliverables**:
- ✅ Wildcard DNS configured
- ✅ Load balancer routing working
- ✅ SSL certificates installed

#### Week 5: Multi-Tenant BI & Testing

**Assigned To**: bi_architect (primary), odoo_developer (support)

**Tasks**:
1. **Configure Superset multi-tenancy**
```python
# superset/config.py
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://superset:password@postgres:5432/superset"

# Row-level security filter
def get_tenant_filter(database):
    user_tenant = g.user.tenant_id
    return f"company_id = {user_tenant}"

# Apply RLS to all datasets
from superset.security import SupersetSecurityManager

class CustomSecurityManager(SupersetSecurityManager):
    def get_rls_filters(self, table):
        return [get_tenant_filter(table.database)]

CUSTOM_SECURITY_MANAGER = CustomSecurityManager
```

2. **Test tenant isolation**
```bash
# Create test data for 2 tenants
psql -d odoo_rim -c "INSERT INTO res_partner (name, company_id) VALUES ('RIM Customer', 1);"
psql -d odoo_ckvc -c "INSERT INTO res_partner (name, company_id) VALUES ('CKVC Customer', 1);"

# Query from RIM tenant (should only see RIM data)
psql -d odoo_rim -c "SELECT name FROM res_partner;"
# Expected: RIM Customer (not CKVC Customer)

# Query from CKVC tenant (should only see CKVC data)
psql -d odoo_ckvc -c "SELECT name FROM res_partner;"
# Expected: CKVC Customer (not RIM Customer)
```

**Deliverables**:
- ✅ Superset multi-tenancy configured
- ✅ Tenant isolation tested and verified
- ✅ RLS policies documented

### 6.3 Phase 3: Web App Parity (Weeks 6-9)

**Goal**: Complete pulse-hub feature set for production

#### Week 6-7: API Gateway Development

**Assigned To**: odoo_developer

**Tasks**:
1. **Consolidate microservices into API gateway**
```typescript
// services/api-gateway/src/index.ts
import express from 'express';
import { authRouter } from './routes/auth';
import { expenseRouter } from './routes/expenses';
import { approvalRouter } from './routes/approvals';
import { taskRouter } from './routes/tasks';

const app = express();

app.use('/api/v1/auth', authRouter);
app.use('/api/v1/expenses', expenseRouter);
app.use('/api/v1/approvals', approvalRouter);
app.use('/api/v1/tasks', taskRouter);

app.listen(3000, () => {
  console.log('API Gateway listening on port 3000');
});
```

2. **Implement JWT authentication**
```typescript
// services/api-gateway/src/middleware/auth.ts
import jwt from 'jsonwebtoken';
import { OdooClient } from '../clients/odoo';

export async function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Missing token' });
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    const user = await OdooClient.call('res.users', 'read', [payload.userId]);
    req.user = user;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

**Deliverables**:
- ✅ API gateway operational
- ✅ JWT authentication implemented
- ✅ API documentation generated (Swagger)

#### Week 8-9: Frontend Development

**Assigned To**: External frontend developer

**Tasks**:
1. **Implement missing features**
   - Expense submission with camera upload
   - Approval workflow UI (approve/reject/delegate)
   - Mobile-responsive design (Tailwind CSS)
   - Real-time notifications (Socket.io)

2. **Add offline capability**
```typescript
// pulse-hub/src/store/middleware/offline.ts
import { createOfflineMiddleware } from '@redux-offline/redux-offline';

const offlineConfig = {
  effect: (effect, action) => {
    return fetch(effect.url, effect.options);
  },
  discard: (error, action) => {
    return error.status >= 400 && error.status < 500;
  },
};

export const offlineMiddleware = createOfflineMiddleware(offlineConfig);
```

**Deliverables**:
- ✅ All missing features implemented
- ✅ Mobile-responsive design completed
- ✅ Offline capability functional

### 6.4 Phase 4: Mobile MVP (Weeks 10-15)

**Goal**: Launch React Native app with 8 MVP features

#### Week 10-11: React Native Project Setup

**Assigned To**: External mobile developer

**Tasks**:
1. **Initialize React Native project**
```bash
npx react-native init InsightPulseMobile --template react-native-template-typescript
cd InsightPulseMobile

# Install dependencies
npm install @react-navigation/native @react-navigation/stack
npm install redux @reduxjs/toolkit react-redux
npm install axios
npm install react-native-camera
npm install @react-native-firebase/app @react-native-firebase/messaging
npm install @react-native-async-storage/async-storage
```

2. **Configure navigation**
```typescript
// src/navigation/AppNavigator.tsx
import { createStackNavigator } from '@react-navigation/stack';
import { DashboardScreen } from '../screens/Dashboard';
import { ExpensesScreen } from '../screens/Expenses';
import { ApprovalsScreen } from '../screens/Approvals';

const Stack = createStackNavigator();

export const AppNavigator = () => (
  <Stack.Navigator>
    <Stack.Screen name="Dashboard" component={DashboardScreen} />
    <Stack.Screen name="Expenses" component={ExpensesScreen} />
    <Stack.Screen name="Approvals" component={ApprovalsScreen} />
  </Stack.Navigator>
);
```

**Deliverables**:
- ✅ React Native project initialized
- ✅ Navigation configured
- ✅ Redux store setup

#### Week 12-13: Core Feature Development

**Assigned To**: External mobile developer

**Tasks**:
1. **Authentication screen**
2. **Dashboard with KPI cards**
3. **Expense submission with camera**
4. **Approval workflow screens**
5. **Task list and detail screens**

**Example: Expense Submission**
```typescript
// src/screens/ExpenseSubmit.tsx
import React, { useState } from 'react';
import { View, Button } from 'react-native';
import { launchCamera } from 'react-native-image-picker';
import { useDispatch } from 'react-redux';
import { submitExpense } from '../store/slices/expenses';

export const ExpenseSubmitScreen = () => {
  const dispatch = useDispatch();

  const handleCaptureReceipt = async () => {
    const result = await launchCamera({ mediaType: 'photo' });

    if (result.assets?.[0]) {
      const formData = new FormData();
      formData.append('file', {
        uri: result.assets[0].uri,
        type: 'image/jpeg',
        name: 'receipt.jpg',
      });

      dispatch(submitExpense(formData));
    }
  };

  return (
    <View>
      <Button title="Capture Receipt" onPress={handleCaptureReceipt} />
    </View>
  );
};
```

**Deliverables**:
- ✅ All 8 MVP features implemented
- ✅ Unit tests written
- ✅ Integration tests passing

#### Week 14-15: Push Notifications & Offline Sync

**Assigned To**: Mobile developer (primary), devops_engineer (FCM setup)

**Tasks**:
1. **Configure Firebase Cloud Messaging**
```bash
# Install Firebase
npm install @react-native-firebase/app @react-native-firebase/messaging

# iOS configuration
cd ios && pod install && cd ..

# Android configuration (edit android/app/build.gradle)
apply plugin: 'com.google.gms.google-services'
```

2. **Implement push notification handler**
```typescript
// src/services/notifications.ts
import messaging from '@react-native-firebase/messaging';

export const initializeNotifications = () => {
  messaging().requestPermission();

  messaging().getToken().then(token => {
    // Send token to backend
    api.post('/api/v1/notifications/register', { token });
  });

  messaging().onMessage(async remoteMessage => {
    // Show in-app notification
    console.log('Notification:', remoteMessage.notification);
  });
};
```

3. **Implement offline sync**
```typescript
// src/store/middleware/offline.ts
import NetInfo from '@react-native-community/netinfo';
import { syncOfflineActions } from '../slices/offline';

NetInfo.addEventListener(state => {
  if (state.isConnected) {
    dispatch(syncOfflineActions());
  }
});
```

**Deliverables**:
- ✅ Push notifications working
- ✅ Offline sync implemented
- ✅ App tested on iOS and Android

### 6.5 Phase 5: Full SaaS Rollout (Weeks 16-23)

**Goal**: Onboard all 8 agencies to production

#### Week 16-18: Tenant Provisioning (RIM, CKVC, BOM)

**Assigned To**: devops_engineer

**Tasks**:
1. **Provision first 3 tenants**
```bash
# In Odoo shell
env['saas.tenant'].create({
    'name': 'RIM Agency',
    'subdomain': 'rim',
    'admin_email': 'admin@rim.insightpulse.ai',
    'plan': 'professional',
}).action_provision()

# Repeat for CKVC and BOM
```

2. **Import initial data**
```bash
# Import users, departments, projects from CSV
psql -d odoo_rim -f data/rim_initial_data.sql
```

3. **Test tenant access**
```bash
# Test RIM tenant
curl -I https://rim.insightpulse.ai/web/login
# Expected: 200 OK

# Test data isolation
curl -H "Authorization: Bearer $RIM_TOKEN" \
  https://rim.insightpulse.ai/api/v1/tasks
# Expected: Only RIM tasks returned
```

**Deliverables**:
- ✅ 3 tenants provisioned and operational
- ✅ Initial data imported
- ✅ Access tested and verified

#### Week 19-21: Tenant Provisioning (JPAL, JLI, JAP, LAS, RMQB)

**Assigned To**: devops_engineer

**Tasks**: Repeat provisioning process for remaining 5 tenants

**Deliverables**:
- ✅ All 8 tenants provisioned
- ✅ DNS and SSL configured for all subdomains
- ✅ Monitoring configured per tenant

#### Week 22-23: Training & Support Setup

**Assigned To**: document_creator (primary), all agents (support)

**Tasks**:
1. **Create user training materials**
   - Video tutorials (15 videos × 3-5 min each)
   - User guides (web app, mobile app, admin)
   - Quick reference cards
   - FAQ documentation

2. **Record admin training sessions**
   - Tenant provisioning
   - User management
   - Module configuration
   - Troubleshooting

3. **Setup support infrastructure**
   - Zendesk or Odoo Helpdesk
   - Support ticket routing
   - Knowledge base
   - Live chat integration

**Deliverables**:
- ✅ Training materials complete
- ✅ Admin training sessions recorded
- ✅ Support infrastructure operational

### 6.6 Timeline Summary

| Phase | Duration | Critical Path | Parallel Work |
|-------|----------|---------------|---------------|
| Phase 1: Stabilization | 2 weeks | Health check fixes → Database optimization | Documentation |
| Phase 2: Multi-Tenancy | 3 weeks | Tenant module → Routing → BI | Testing |
| Phase 3: Web App Parity | 4 weeks | API Gateway → Frontend dev | Documentation |
| Phase 4: Mobile MVP | 6 weeks | React Native dev → Notifications | API enhancements |
| Phase 5: SaaS Rollout | 8 weeks | Tenant provisioning → Training | Support setup |
| **Total** | **23 weeks** | | |

**Buffer**: Add 20% contingency = **27.6 weeks** (~7 months)

---

## 7. Architecture Diagrams

### 7.1 Target Multi-Tenant Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser]
        MOBILE_IOS[iOS App]
        MOBILE_ANDROID[Android App]
    end

    subgraph "DNS Routing"
        WILDCARD[*.insightpulse.ai<br/>Wildcard DNS]
    end

    subgraph "Load Balancer"
        LB[NGINX / Caddy<br/>SSL Termination]
    end

    subgraph "Tenant Routing"
        LB --> |rim.insightpulse.ai| ODOO_RIM_POD
        LB --> |ckvc.insightpulse.ai| ODOO_CKVC_POD
        LB --> |bom.insightpulse.ai| ODOO_BOM_POD
        LB --> |rmqb.insightpulse.ai| ODOO_RMQB_POD
    end

    subgraph "DigitalOcean App Platform"
        ODOO_RIM_POD[Odoo Pod: RIM<br/>2 instances]
        ODOO_CKVC_POD[Odoo Pod: CKVC<br/>2 instances]
        ODOO_BOM_POD[Odoo Pod: BOM<br/>2 instances]
        ODOO_RMQB_POD[Odoo Pod: RMQB<br/>2 instances]
    end

    subgraph "Database Layer - Supabase"
        PGBOUNCER[pgBouncer<br/>Connection Pooler]
        PGBOUNCER --> DB_RIM[(odoo_rim)]
        PGBOUNCER --> DB_CKVC[(odoo_ckvc)]
        PGBOUNCER --> DB_BOM[(odoo_bom)]
        PGBOUNCER --> DB_RMQB[(odoo_rmqb)]
    end

    subgraph "Shared Services"
        API_GATEWAY[API Gateway<br/>Port 3000]
        PADDLEOCR[PaddleOCR-VL<br/>RTX 4090]
        SUPERSET[Apache Superset<br/>Multi-Tenant BI]
        FCM[Firebase Cloud Messaging<br/>Push Notifications]
    end

    WEB --> WILDCARD
    MOBILE_IOS --> WILDCARD
    MOBILE_ANDROID --> WILDCARD

    WILDCARD --> LB

    ODOO_RIM_POD --> PGBOUNCER
    ODOO_CKVC_POD --> PGBOUNCER
    ODOO_BOM_POD --> PGBOUNCER
    ODOO_RMQB_POD --> PGBOUNCER

    ODOO_RIM_POD --> API_GATEWAY
    ODOO_CKVC_POD --> API_GATEWAY
    ODOO_BOM_POD --> API_GATEWAY
    ODOO_RMQB_POD --> API_GATEWAY

    API_GATEWAY --> PADDLEOCR
    API_GATEWAY --> FCM

    SUPERSET --> PGBOUNCER
```

### 7.2 Mobile App Architecture

```mermaid
graph TD
    subgraph "Mobile App Layer"
        APP[React Native App]
        NAVIGATION[React Navigation]
        STATE[Redux Store]
    end

    subgraph "Screens"
        DASHBOARD[Dashboard Screen]
        EXPENSES[Expenses Screen]
        APPROVALS[Approvals Screen]
        TASKS[Tasks Screen]
        SETTINGS[Settings Screen]
    end

    subgraph "Services"
        AUTH_SVC[Auth Service<br/>JWT]
        API_SVC[API Service<br/>Axios]
        OCR_SVC[OCR Service<br/>Camera]
        NOTIF_SVC[Notification Service<br/>FCM]
        OFFLINE_SVC[Offline Service<br/>AsyncStorage]
    end

    subgraph "Backend"
        API_GATEWAY[API Gateway<br/>Port 3000]
        ODOO[Odoo Backend]
    end

    APP --> NAVIGATION
    NAVIGATION --> DASHBOARD
    NAVIGATION --> EXPENSES
    NAVIGATION --> APPROVALS
    NAVIGATION --> TASKS
    NAVIGATION --> SETTINGS

    DASHBOARD --> STATE
    EXPENSES --> STATE
    APPROVALS --> STATE
    TASKS --> STATE

    STATE --> AUTH_SVC
    STATE --> API_SVC
    STATE --> OCR_SVC
    STATE --> NOTIF_SVC
    STATE --> OFFLINE_SVC

    AUTH_SVC --> API_GATEWAY
    API_SVC --> API_GATEWAY
    OCR_SVC --> API_GATEWAY
    NOTIF_SVC --> API_GATEWAY

    API_GATEWAY --> ODOO

    OFFLINE_SVC -.->|Sync when online| API_SVC
```

### 7.3 Data Flow: Expense Submission (Mobile → Odoo)

```mermaid
sequenceDiagram
    participant User
    participant MobileApp
    participant Camera
    participant APIGateway
    participant OCRService
    participant Odoo
    participant Approver

    User->>MobileApp: Tap "New Expense"
    MobileApp->>Camera: Launch camera
    Camera->>User: Capture receipt photo
    User->>Camera: Take photo
    Camera->>MobileApp: Return image URI
    MobileApp->>APIGateway: POST /api/v1/expenses/submit<br/>{file: image.jpg}
    APIGateway->>OCRService: POST /v1/parse<br/>{file: image.jpg}
    OCRService->>OCRService: PaddleOCR-VL inference
    OCRService->>APIGateway: {vendor, amount, date, category}
    APIGateway->>Odoo: XML-RPC create('hr.expense', {...})
    Odoo->>Odoo: Validate expense policy
    Odoo->>Odoo: Route to approval workflow
    Odoo->>APIGateway: {expense_id: 123, status: 'pending'}
    APIGateway->>MobileApp: {success: true, expense_id: 123}
    MobileApp->>User: "Expense submitted!"
    Odoo->>Approver: Push notification<br/>"New expense to approve"
```

---

## 8. Risk Assessment & Mitigation

### 8.1 Technical Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **Service health failures persist** | High | Critical | Phase 1 dedicated to stabilization, skip to Phase 2 only when 0 failures |
| **Database-per-tenant performance issues** | Medium | High | Implement pgBouncer connection pooling, load test before production |
| **Mobile app development delays** | Medium | High | Start Phase 4 in parallel with Phase 3, hire experienced React Native developer |
| **Multi-tenant data leakage** | Low | Critical | Comprehensive RLS testing, security audit before production |
| **OCR service downtime** | Medium | Medium | Implement queue-based processing, fallback to Azure Document Intelligence API |
| **Push notification delivery failures** | Low | Medium | Use FCM + APNs with retry logic, test across multiple devices |
| **Offline sync conflicts** | High | Low | Implement conflict resolution strategy, last-write-wins or manual resolution |
| **Load balancer misconfiguration** | Low | High | Thorough testing of tenant routing, monitor 404/500 errors |

### 8.2 Business Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **User adoption resistance** | Medium | High | Phased rollout, training, change management, pilot with 1-2 agencies first |
| **Budget overrun** | Medium | Medium | Track actual vs. estimated costs weekly, adjust resource allocation |
| **Timeline slippage** | High | Medium | 20% buffer built into timeline, weekly progress reviews, identify blockers early |
| **Key developer departure** | Medium | High | Document all work, conduct code reviews, maintain bus factor >1 |
| **Agency-specific customization requests** | High | Low | Defer non-critical customizations to Phase 6 (post-launch), maintain scope discipline |
| **Compliance issues (data residency)** | Low | High | Confirm data residency requirements per agency, configure regional databases if needed |

### 8.3 Operational Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **Inadequate support resources** | Medium | High | Setup Zendesk, create knowledge base, train 2-3 support staff before launch |
| **Backup failures** | Low | Critical | Automated daily backups, weekly restore tests, 90-day retention |
| **Monitoring blind spots** | Medium | Medium | Comprehensive health checks per tenant, alert rules, on-call rotation |
| **Infrastructure cost escalation** | High | Medium | Right-size DO instances, implement auto-scaling, monitor usage closely |

### 8.4 Success Criteria & KPIs

#### Phase 1 Success Criteria (Stabilization)
- ✅ 0 health check failures (down from 27)
- ✅ All services operational (Odoo, MCP Hub, AI Inference Hub)
- ✅ Database P95 query time <200ms
- ✅ Load testing passed (500 concurrent users)

#### Phase 2 Success Criteria (Multi-Tenancy)
- ✅ 8 tenant databases provisioned
- ✅ DNS routing working for all subdomains
- ✅ Tenant isolation tested (no data leakage)
- ✅ RLS policies validated

#### Phase 3 Success Criteria (Web App Parity)
- ✅ All missing features implemented
- ✅ Mobile-responsive design (98% Lighthouse score)
- ✅ Real-time notifications working
- ✅ Offline mode functional

#### Phase 4 Success Criteria (Mobile MVP)
- ✅ App published to App Store and Play Store
- ✅ All 8 MVP features working
- ✅ Push notifications delivering
- ✅ Offline sync working

#### Phase 5 Success Criteria (SaaS Rollout)
- ✅ All 8 agencies onboarded
- ✅ 90% user adoption (active users per agency)
- ✅ <5 support tickets per week per agency
- ✅ 99.5% uptime SLA met

#### Post-Launch KPIs (90 days)
- **User Adoption**: ≥90% active users per agency
- **System Uptime**: ≥99.5%
- **API Response Time**: P95 <200ms
- **OCR Accuracy**: ≥95% auto-approval rate
- **Mobile App Adoption**: ≥60% of users use mobile app
- **Support Volume**: <5 tickets per week per agency
- **User Satisfaction**: ≥4.5/5.0 average rating

---

## 9. Resource Requirements & Cost Estimates

### 9.1 Team Composition

| Role | FTE | Duration | Rate | Total Cost |
|------|-----|----------|------|------------|
| **Odoo Developer** (Senior) | 1.0 | 23 weeks | $120/hr | $110,400 |
| **Frontend Developer** (React) | 0.5 | 9 weeks (Phase 3) | $100/hr | $18,000 |
| **Mobile Developer** (React Native) | 1.0 | 10 weeks (Phase 4) | $110/hr | $44,000 |
| **DevOps Engineer** (Senior) | 0.5 | 23 weeks | $110/hr | $50,600 |
| **BI Architect** (Part-time) | 0.25 | 5 weeks (Phase 2) | $100/hr | $5,000 |
| **Technical Writer** (Part-time) | 0.25 | 10 weeks (Phase 5) | $80/hr | $8,000 |
| **Project Manager** (Part-time) | 0.25 | 23 weeks | $100/hr | $23,000 |
| **QA Engineer** (Part-time) | 0.25 | 15 weeks (Phases 3-5) | $90/hr | $13,500 |
| **Total Labor** | | | | **$272,500** |

### 9.2 Infrastructure Costs

#### Production Infrastructure (Monthly)

| Service | Quantity | Unit Cost | Total |
|---------|----------|-----------|-------|
| **DigitalOcean App Platform** (basic-xxs) | 8 tenants | $25/mo | $200/mo |
| **Supabase PostgreSQL** (Pro tier) | 8 databases | $25/mo (bulk) | $25/mo |
| **DigitalOcean Spaces** (CDN + Storage) | 1TB | $5/mo | $5/mo |
| **DigitalOcean Load Balancer** | 1 | $12/mo | $12/mo |
| **OpenAI API** (embeddings + completions) | Pay-as-go | ~$50/mo | $50/mo |
| **Firebase Cloud Messaging** (push notifications) | Free | $0/mo | $0/mo |
| **SSL Certificates** (Let's Encrypt) | Free | $0/mo | $0/mo |
| **Monitoring** (DO Monitoring) | Included | $0/mo | $0/mo |
| **Total Infrastructure** | | | **$292/mo** |

**Annual Infrastructure Cost**: $3,504/year

#### Development Infrastructure (One-time)

| Item | Quantity | Unit Cost | Total |
|------|----------|-----------|-------|
| **Development Servers** (staging) | 1 | $100/mo × 6 months | $600 |
| **Load Testing Tools** (k6 Cloud) | 1 | $50/mo × 2 months | $100 |
| **CI/CD Credits** (GitHub Actions) | As needed | ~$50 | $50 |
| **Total Development Infra** | | | **$750** |

### 9.3 Software & Tools

| Tool | Purpose | Cost |
|------|---------|------|
| **Odoo CE** | ERP platform | Free (open source) |
| **OCA Modules** | Enterprise features | Free (open source) |
| **React Native** | Mobile development | Free (open source) |
| **PostgreSQL** | Database | Free (open source) |
| **Apache Superset** | BI dashboards | Free (open source) |
| **GitHub** | Version control | Free (public repos) |
| **Figma** (optional) | Design mockups | $15/mo × 6 months = $90 |
| **Zendesk** (optional) | Support ticketing | $49/mo × 12 months = $588 |
| **Total Software** | | **$678** |

### 9.4 Total Cost Summary

| Category | Amount |
|----------|--------|
| **Labor** (23 weeks) | $272,500 |
| **Infrastructure** (development) | $750 |
| **Infrastructure** (production, 12 months) | $3,504 |
| **Software & Tools** | $678 |
| **Contingency** (20%) | $55,486 |
| **Total Project Cost** | **$332,918** |

**Per-Agency Cost**: $332,918 ÷ 8 agencies = **$41,615 per agency**

**Ongoing Monthly Cost** (post-launch):
- Infrastructure: $292/mo
- Maintenance (10% of labor): ~$5,000/mo
- **Total**: ~$5,292/mo (~$63,500/year)

---

## 10. Recommendations & Next Steps

### 10.1 Critical Immediate Actions (This Week)

**Priority 1**: Fix service health failures (27 active issues)
```bash
# Action items for devops_engineer
1. Diagnose MCP Hub failure (connection refused)
2. Restore AI Inference Hub (GPU driver issues)
3. Fix Odoo database connection pooling (add pgBouncer)
4. Validate all services operational (0 failures target)
```

**Priority 2**: Complete missing documentation
```bash
# Action items for document_creator
1. Update DEPLOYMENT_STATUS.md with current blockers
2. Create TROUBLESHOOTING.md for common issues
3. Document service dependency map
```

**Priority 3**: Finalize mobile app decision
```bash
# Action items for project stakeholders
1. Approve React Native as mobile framework
2. Allocate budget for mobile developer hire
3. Approve 6-week timeline for Phase 4
```

### 10.2 Phased Rollout Strategy

**Recommendation**: Start with 2-agency pilot before full rollout

**Pilot Agencies** (Weeks 16-18):
- **RIM** (largest, most complex requirements)
- **CKVC** (medium size, standard requirements)

**Rationale**:
- De-risk full rollout
- Identify edge cases and customization needs
- Validate multi-tenancy architecture
- Build confidence before scaling to 8 agencies

**Pilot Success Criteria**:
- 0 critical bugs in 2 weeks
- 90% user adoption in pilot agencies
- No data leakage between tenants
- <500ms P95 response time under load

**Full Rollout** (Weeks 19-23):
- Onboard remaining 6 agencies
- Apply lessons learned from pilot
- Stagger onboarding (2 agencies per week)

### 10.3 Alternative Approach: Faster Timeline

**If timeline is critical**, consider this aggressive 16-week plan:

| Phase | Duration | Concurrency | Risk |
|-------|----------|-------------|------|
| Phase 1: Stabilization | 1 week | N/A | High (skip comprehensive testing) |
| Phase 2: Multi-Tenancy | 2 weeks | Parallel with Phase 3 | Medium (integration issues) |
| Phase 3: Web App | 3 weeks | Parallel with Phase 2 | Medium (API-frontend coupling) |
| Phase 4: Mobile App | 5 weeks | Start in parallel with Phase 3 | High (resource contention) |
| Phase 5: Rollout | 5 weeks | Pilot skipped, all 8 agencies at once | Critical (no safety net) |
| **Total** | **16 weeks** | | **Overall Risk: HIGH** |

**Trade-offs**:
- ⚠️ Less testing, higher bug risk
- ⚠️ Team burnout from concurrent phases
- ⚠️ No pilot to validate architecture
- ✅ 30% faster time-to-market
- ✅ Lower total labor cost (~$200K vs. $272K)

**Recommendation**: Only pursue aggressive timeline if:
1. Business critical (e.g., contract deadline)
2. Willing to accept higher technical debt
3. Team has excess capacity for concurrent work
4. Stakeholders approve elevated risk

### 10.4 Long-Term Roadmap (Post-Launch)

**Phase 6**: Advanced Features (Months 7-9)
- Real-time collaboration (WebRTC)
- Advanced BI (predictive analytics)
- AI-powered insights (anomaly detection)
- Mobile app enhancements (GPS, voice notes)

**Phase 7**: Scale & Optimize (Months 10-12)
- Performance tuning (caching, CDN)
- Database optimization (partitioning, sharding)
- Cost optimization (reserved instances, spot instances)
- Security hardening (penetration testing, compliance audit)

**Phase 8**: Enterprise Expansion (Year 2)
- White-label SaaS offering
- Marketplace for 3rd-party modules
- API ecosystem (developer portal)
- International expansion (multi-currency, localization)

---

## Appendix A: Technology Stack Reference

### Current Stack

| Layer | Technology | Version | Status |
|-------|-----------|---------|--------|
| **Operating System** | Ubuntu 22.04 | LTS | ✅ Production |
| **Container Runtime** | Docker | 24.0 | ✅ Production |
| **Orchestration** | Docker Compose | 2.20 | ✅ Production |
| **ERP Platform** | Odoo CE | 19.0 | ✅ Production |
| **Database** | PostgreSQL | 15 | ✅ Production |
| **Database Hosting** | Supabase | Cloud | ✅ Production |
| **Web Server** | Caddy / NGINX | 2.7 | ⚠️ Config issues |
| **App Hosting** | DigitalOcean App Platform | Cloud | ⚠️ Some services down |
| **Frontend** | Next.js | 14.0 | ✅ Production |
| **Backend API** | Express.js | 4.18 | ✅ Production |
| **OCR Service** | PaddleOCR-VL | 900M model | ⚠️ GPU issues |
| **BI Platform** | Apache Superset | 3.0 | ✅ Production |
| **Vector DB** | pgvector | 0.5 | ✅ Production |
| **AI/ML** | OpenAI API | gpt-4o-mini | ✅ Production |

### Target Stack (Post-SaaS Migration)

| Layer | Technology | Version | Changes |
|-------|-----------|---------|---------|
| **Load Balancer** | NGINX | 1.24 | ➕ New (multi-tenant routing) |
| **Connection Pooler** | pgBouncer | 1.21 | ➕ New (500 connections) |
| **Mobile Framework** | React Native | 0.73 | ➕ New (iOS + Android) |
| **Push Notifications** | Firebase Cloud Messaging | Latest | ➕ New (mobile support) |
| **API Gateway** | Express.js (consolidated) | 4.18 | 🔄 Refactor (consolidate 3 services) |
| **Monitoring** | Prometheus + Grafana | Latest | ➕ New (per-tenant metrics) |
| **Log Aggregation** | ELK Stack (optional) | 8.10 | ⏸️ Optional (future) |

---

## Appendix B: Glossary

**Terms**:

- **Multi-Tenancy**: Architecture where single application serves multiple independent customers (tenants)
- **Database-per-Tenant**: Each tenant has own isolated database (vs. shared database with company_id)
- **RLS (Row-Level Security)**: PostgreSQL feature to restrict data access based on user context
- **JWT (JSON Web Token)**: Standard for secure authentication between client and server
- **OAuth2/OIDC**: Industry-standard protocols for authorization and authentication
- **pgBouncer**: Connection pooler for PostgreSQL to handle high concurrent connections
- **OCR (Optical Character Recognition)**: Technology to extract text from images
- **FCM (Firebase Cloud Messaging)**: Google service for push notifications
- **WebSocket**: Protocol for real-time bidirectional communication
- **Offline-First**: App design where offline capability is primary, sync when online
- **Worktree**: Git feature to work on multiple branches simultaneously in separate directories

**Acronyms**:

- **SaaS**: Software as a Service
- **MVP**: Minimum Viable Product
- **API**: Application Programming Interface
- **BI**: Business Intelligence
- **CI/CD**: Continuous Integration / Continuous Deployment
- **DO**: DigitalOcean
- **OCA**: Odoo Community Association
- **CE**: Community Edition (vs. Enterprise Edition)

---

## Appendix C: References & Resources

### Official Documentation
- [Odoo 19.0 Documentation](https://www.odoo.com/documentation/19.0/)
- [OCA GitHub](https://github.com/OCA)
- [React Native Documentation](https://reactnative.dev/docs/getting-started)
- [PostgreSQL Multi-Tenancy](https://www.postgresql.org/docs/15/ddl-rowsecurity.html)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)
- [Supabase Documentation](https://supabase.com/docs)

### Internal Documentation
- [MODULES.md](/Users/tbwa/Documents/GitHub/insightpulse-odoo/MODULES.md) - Module inventory
- [ENTERPRISE_PARITY.md](/Users/tbwa/Documents/GitHub/insightpulse-odoo/docs/ENTERPRISE_PARITY.md) - OCA parity guide
- [SAAS_PARITY_DEPLOYMENT.md](/Users/tbwa/Documents/GitHub/insightpulse-odoo/docs/SAAS_PARITY_DEPLOYMENT.md) - Deployment checklist
- [DEPLOYMENT_STATUS.md](/Users/tbwa/Documents/GitHub/insightpulse-odoo/docs/DEPLOYMENT_STATUS.md) - Current status

### Related PRDs
- [PRD_ENTERPRISE_SAAS_PARITY.md](/Users/tbwa/Documents/GitHub/insightpulse-odoo/docs/PRD_ENTERPRISE_SAAS_PARITY.md) - Original PRD
- [PULSER_HUB_INTEGRATION.md](/Users/tbwa/Documents/GitHub/insightpulse-odoo/docs/PULSER_HUB_INTEGRATION.md) - GitHub app integration

---

**Document Status**: Draft v1.0.0
**Review Status**: Pending stakeholder review
**Next Update**: After Phase 1 completion
**Maintainer**: SuperClaude Multi-Agent Framework
**Contact**: jgtolentino@insightpulse.ai
