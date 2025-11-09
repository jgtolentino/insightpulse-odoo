# Instance Map – Odoo, Supabase, Superset

**Last Updated:** 2025-11-09
**Canonical Source:** `config/instance-matrix.yaml` (machine-readable)

This document describes all **Odoo**, **Supabase**, and **Superset** instances across environments and how they are used.

---

## Table of Contents

1. [Overview](#overview)
2. [Environments](#environments)
3. [Instance Matrix](#instance-matrix)
4. [Roles & Responsibilities](#roles--responsibilities)
5. [Automation Hooks](#automation-hooks)
6. [Health Checks](#health-checks)

---

## Overview

InsightPulse AI operates three distinct systems across multiple environments:

1. **Odoo ERP** - System of record for all business entities
2. **Supabase PostgreSQL** - Application/automation database + analytics warehouse
3. **Apache Superset** - BI metadata and dashboard definitions

Each environment (local, staging, production) has dedicated instances with explicit separation.

### Architecture Diagram

```mermaid
graph TB
    subgraph Production
        ProdOdoo[Odoo ERP<br/>erp.insightpulseai.net]
        ProdSupabase[(Supabase PostgreSQL<br/>spdtwktxdalcfigzeqrz)]
        ProdSuperset[Apache Superset<br/>superset.insightpulseai.net]

        ProdOdoo -->|System of Record| ProdSupabase
        ProdSuperset -->|Data Source| ProdSupabase
    end

    subgraph Staging
        StgOdoo[Odoo ERP<br/>staging-erp]
        StgSupabase[(Supabase PostgreSQL<br/>staging-project)]
        StgSuperset[Apache Superset<br/>staging-superset]

        StgOdoo -->|System of Record| StgSupabase
        StgSuperset -->|Data Source| StgSupabase
    end

    subgraph Local
        LocalOdoo[Odoo ERP<br/>localhost:8069]
        LocalSupabase[(Local PostgreSQL<br/>localhost:5432)]
        LocalSuperset[Apache Superset<br/>localhost:8088]

        LocalOdoo -->|System of Record| LocalSupabase
        LocalSuperset -->|Data Source| LocalSupabase
    end

    style ProdOdoo fill:#e1f5ff
    style ProdSupabase fill:#ffe1f5
    style ProdSuperset fill:#fff5e1
```

---

## Environments

We model three main environments:

### 1. Local Environment

**Purpose:** Developer experimentation, local feature branches, testing

**Infrastructure:**
- Docker Compose (`docker-compose.yml`)
- All services run on localhost
- No external dependencies required

### 2. Staging Environment

**Purpose:** Pre-production validation, realistic data testing, integration testing

**Infrastructure:**
- DigitalOcean App Platform (apps)
- DigitalOcean Droplets (VMs)
- Supabase managed service (staging project)

### 3. Production Environment

**Purpose:** Live Finance SSC, customer-facing BI, mission-critical operations

**Infrastructure:**
- DigitalOcean Droplet: 165.227.10.178 (Odoo primary)
- DigitalOcean App Platform (Superset)
- Supabase managed service (spdtwktxdalcfigzeqrz)

---

## Instance Matrix

### Local Environment

#### Odoo (Local)

| Property | Value |
|----------|-------|
| **Role** | ERP - System of Record |
| **URL** | http://localhost:8069 |
| **Database** | `postgres://odoo:odoo@localhost:5432/odoo_local` |
| **Environment Variable** | `ODOO_DB_URL_LOCAL` |
| **Docker Service** | `odoo` (via `docker-compose.yml`) |
| **Health Check** | GET http://localhost:8069/web/login → HTTP 200 |
| **Backup Strategy** | Docker volume snapshots |
| **Owner** | Development Team |

**Documentation:**
- `docs/DOCKER_SETUP.md`
- `QUICKSTART.md`
- `README-DOCKER-SETUP.md`

#### Supabase (Local)

| Property | Value |
|----------|-------|
| **Role** | App/Automation DB + Analytics Warehouse |
| **URL** | http://localhost:54323 (Supabase Studio - optional) |
| **Database** | `postgres://postgres:postgres@localhost:5432/postgres` |
| **Environment Variable** | `SUPABASE_DB_URL_LOCAL` |
| **Docker Service** | `supabase-db` or external PostgreSQL |
| **Health Check** | `psql "$SUPABASE_DB_URL_LOCAL" -c "SELECT 1;"` |
| **Schemas** | `public`, `auth`, `analytics`, `scout` |
| **Backup Strategy** | pg_dump daily |
| **Owner** | Development Team |

**Purpose:**
- Application/automation tables (auth, ETL, task queues)
- Analytics tables derived from Odoo (scouts, expenses, transactions)
- Vector/RAG metadata (pgvector)

#### Superset (Local)

| Property | Value |
|----------|-------|
| **Role** | BI Metadata (dashboards, charts, datasets) |
| **URL** | http://localhost:8088 |
| **Metadata Database** | `postgres://superset:superset@localhost:5432/superset_meta` |
| **Environment Variable** | `SUPERSET_META_DB_URL_LOCAL` |
| **Docker Service** | `superset` (via `docker-compose.yml`) |
| **Health Check** | GET http://localhost:8088/health → HTTP 200 |
| **Data Source** | Local Supabase (localhost:5432) |
| **Backup Strategy** | Metadata exports via Superset CLI |
| **Owner** | Development Team |

**Purpose:**
- BI metadata only (no business data)
- Dashboard definitions, chart configurations
- Dataset metadata, SQL Lab queries
- User permissions and RLS policies

---

### Staging Environment

#### Odoo (Staging)

| Property | Value |
|----------|-------|
| **Role** | ERP - Pre-Production Validation |
| **URL** | https://staging-erp.insightpulseai.net (placeholder) |
| **Database** | `$ODOO_DB_URL_STAGING` |
| **Environment Variable** | `ODOO_DB_URL_STAGING` |
| **Infrastructure** | DigitalOcean Droplet (staging-odoo) |
| **Health Check** | GET https://staging-erp.insightpulseai.net/web/login → HTTP 200 |
| **Backup Strategy** | Automated daily backups to DO Spaces |
| **Owner** | DevOps Team |

**Purpose:**
- Mirrors critical modules from production
- Used for upgrade + migration testing
- Realistic data shape (anonymized production data)

#### Supabase (Staging)

| Property | Value |
|----------|-------|
| **Role** | App/Automation DB + Analytics Warehouse |
| **Project Reference** | `$SUPABASE_PROJECT_REF_STAGING` |
| **Database URL** | `$SUPABASE_DB_URL_STAGING` |
| **Environment Variable** | `SUPABASE_DB_URL_STAGING` |
| **Infrastructure** | Supabase managed service (staging project) |
| **Health Check** | `psql "$SUPABASE_DB_URL_STAGING" -c "SELECT 1;"` |
| **Schemas** | Mirrors production schema from DBML |
| **Backup Strategy** | Supabase automated PITR |
| **Owner** | DevOps Team |

**Purpose:**
- Read-only copy of production migrations (schema only)
- Testing analytics queries against near-real data
- Agent development and testing

#### Superset (Staging)

| Property | Value |
|----------|-------|
| **Role** | BI Metadata - Pre-Production Validation |
| **URL** | https://staging-superset.insightpulseai.net (placeholder) |
| **Metadata Database** | `$SUPERSET_META_DB_URL_STAGING` |
| **Environment Variable** | `SUPERSET_META_DB_URL_STAGING` |
| **Infrastructure** | DigitalOcean App Platform |
| **Health Check** | GET https://staging-superset.insightpulseai.net/health → HTTP 200 |
| **Data Source** | Staging Supabase |
| **Backup Strategy** | Metadata exports |
| **Owner** | DevOps Team |

**Purpose:**
- Validate new dashboards before production
- Test RLS policies with realistic data
- Train users on new BI features

---

### Production Environment

#### Odoo (Production)

| Property | Value |
|----------|-------|
| **Role** | ERP - System of Record (PRODUCTION) |
| **URL** | https://erp.insightpulseai.net |
| **Database** | `$ODOO_DB_URL_PRODUCTION` |
| **Environment Variable** | `ODOO_DB_URL_PRODUCTION` |
| **Infrastructure** | DigitalOcean Droplet (ipai-odoo-erp / 165.227.10.178) |
| **Odoo Version** | 19.0 CE (deployed from source) |
| **Health Check** | GET https://erp.insightpulseai.net/web/login → HTTP 200 |
| **Backup Strategy** | Automated daily backups + PITR enabled |
| **Owner** | Operations Team |
| **SLA** | 99.9% uptime |

**Purpose:**
- System of record for all ERP entities
- Multi-tenant legal entity isolation
- BIR compliance (Forms 2307, 2316, e-invoicing)

**Documentation:**
- `docs/PRODUCTION_DEPLOYMENT.md`
- `docs/MODULE_INSTALLATION_GUIDE.md`
- `DEPLOYMENT_GUIDE.md`

#### Supabase (Production)

| Property | Value |
|----------|-------|
| **Role** | App/Automation DB + Analytics Warehouse |
| **Project Reference** | `spdtwktxdalcfigzeqrz` |
| **Database URL (Direct)** | `postgres://postgres.spdtwktxdalcfigzeqrz:***@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres` |
| **Database URL (Pooler)** | `postgres://postgres.spdtwktxdalcfigzeqrz:***@aws-1-us-east-1.pooler.supabase.com:6543/postgres` |
| **Environment Variable** | `SUPABASE_DB_URL_PRODUCTION` |
| **Infrastructure** | Supabase managed service (AWS us-east-1) |
| **Health Check** | `psql "$SUPABASE_DB_URL_PRODUCTION" -c "SELECT 1;"` |
| **Schemas** | `public`, `auth`, `analytics`, `scout`, `warehouse` |
| **Backup Strategy** | Supabase automated PITR + custom backups |
| **Owner** | Operations Team |
| **SLA** | 99.95% uptime (Supabase SLA) |

**Purpose:**
- Application/automation schemas (DBML-driven)
- Main analytics database for Superset
- RLS enforcement for multi-tenant data
- Vector search metadata (pgvector)

**When to Use:**
- **Direct Connection (5432):** Migrations, admin tasks, `psql` operations
- **Connection Pooler (6543):** High-concurrency applications (Odoo, Superset)

**Documentation:**
- `docs/INFRASTRUCTURE_ARCHITECTURE.md`
- `warehouse/` (analytics schemas)

#### Superset (Production)

| Property | Value |
|----------|-------|
| **Role** | BI Metadata + Executive Dashboards |
| **URL** | https://superset.insightpulseai.net |
| **Metadata Database** | `$SUPERSET_META_DB_URL_PRODUCTION` |
| **Environment Variable** | `SUPERSET_META_DB_URL_PRODUCTION` |
| **Infrastructure** | DigitalOcean App Platform (superset-analytics / 73af11cb-dab2-4cb1-9770-291c536531e6) |
| **Health Check** | GET https://superset.insightpulseai.net/health → HTTP 200 |
| **Data Source** | Production Supabase (spdtwktxdalcfigzeqrz) |
| **Backup Strategy** | Metadata exports + automated snapshots |
| **Owner** | Operations Team |
| **SLA** | 99.5% uptime |

**Purpose:**
- BI interface for CFO/Executive dashboards
- Scout transaction analytics
- Expense management reporting
- Financial KPI tracking

**Dashboard Categories:**
- Finance SSC Overview
- Multi-Agency Operations
- BIR Compliance Reports
- Expense Analytics
- Scout Transaction Analysis

---

## Roles & Responsibilities

### Odoo Instances

**System of Record:**
- All business entities (customers, vendors, invoices, expenses)
- Multi-tenant isolation via `company_id`
- BIR compliance enforcement (immutable audit trail)

**Schema Management:**
- Controlled by Odoo ORM + modules
- DBML: Read-only snapshot (`dbml/odoo/odoo_readonly.dbml`)
- Never modify Odoo DB schema directly (use Odoo migrations)

**Health Check:**
- HTTP 200 on `/web/login`
- Database reachable (`$ODOO_DB_URL_*`)
- Odoo service running (`systemctl status odoo` on droplet)

### Supabase Instances

**Application + Analytics Database:**
- App/automation schemas (`auth`, `analytics`, `scout`)
- Analytics warehouse (derived from Odoo data)
- Vector/RAG metadata (pgvector)

**Schema Management:**
- DBML-driven (`dbml/supabase/*.dbml`)
- Migrations auto-generated from DBML
- RLS policies enforced for all tenant data

**Health Check:**
- Database port reachable (5432 direct, 6543 pooler)
- Migrations applied from DBML-generated SQL
- RLS policies active on all tables

### Superset Instances

**BI Metadata Store:**
- Dashboard definitions, chart configurations
- Dataset metadata, SQL Lab queries
- User permissions, RLS policies
- **No business data** (only metadata)

**Data Source:**
- Primary: Supabase PostgreSQL (analytics warehouse)
- Secondary: Direct Odoo connections (read-only views)

**Health Check:**
- HTTP 200 on `/health` or `/login/`
- Metadata database reachable (`$SUPERSET_META_DB_URL_*`)
- Superset service running

---

## Automation Hooks

CI, agents, and scripts use `config/instance-matrix.yaml` to:

### Schema Validation

**Supabase Schema Checks:**
```bash
# Compare DBML → Supabase schema
make dbml-drift-check

# Apply migrations
make supabase-migrate
```

**Odoo Schema Snapshots:**
```bash
# Generate Odoo schema DBML
make odoo-schema-snapshot

# Compare with previous snapshot
make odoo-schema-diff
```

**Superset Metadata Checks:**
```bash
# Export metadata
make superset-metadata-export

# Validate metadata
make superset-metadata-validate
```

### Health Monitoring

**Per-Instance Health:**
```bash
# Local environment
make instance-health-local

# Staging environment
make instance-health-staging

# Production environment
make instance-health-production
```

**Global Automation Health:**
```bash
# Full automation health check (includes instance health)
make automation-health
```

### Deployment Workflows

**Environment-Specific Deployments:**
```bash
# Deploy to staging
make deploy-staging

# Deploy to production (requires approval)
make deploy-production
```

**Multi-Instance Coordination:**
1. **Odoo Deployment:**
   - Deploy Odoo modules
   - Run Odoo migrations
   - Verify Odoo health

2. **Supabase Sync:**
   - Apply DBML migrations
   - Sync Odoo data to analytics warehouse
   - Verify Supabase health

3. **Superset Refresh:**
   - Update Superset metadata
   - Refresh cached datasets
   - Verify Superset health

---

## Health Checks

### Automated Health Monitoring

**Script:** `scripts/health/check-instance-health.sh`

**Usage:**
```bash
# Check local instances
./scripts/health/check-instance-health.sh local

# Check production instances
./scripts/health/check-instance-health.sh production
```

**What It Checks:**

1. **Odoo HTTP Connectivity:**
   ```bash
   curl -fsS "${ODOO_URL}/web/login" >/dev/null
   ```

2. **Supabase Database Connectivity:**
   ```bash
   psql "${SUPABASE_DB_URL}" -c "SELECT 1;"
   ```

3. **Superset Metadata Database Connectivity:**
   ```bash
   psql "${SUPERSET_META_DB_URL}" -c "SELECT 1;"
   ```

### Environment Variables Required

**Local:**
- `ODOO_DB_URL_LOCAL`
- `SUPABASE_DB_URL_LOCAL`
- `SUPERSET_META_DB_URL_LOCAL`

**Staging:**
- `ODOO_DB_URL_STAGING`
- `SUPABASE_DB_URL_STAGING`
- `SUPERSET_META_DB_URL_STAGING`

**Production:**
- `ODOO_DB_URL_PRODUCTION`
- `SUPABASE_DB_URL_PRODUCTION`
- `SUPERSET_META_DB_URL_PRODUCTION`

**Storage:**
- **Local:** `.env.local` (git-ignored)
- **CI/CD:** GitHub Secrets
- **Production:** Environment variables on droplet

---

## Adding New Environments

When adding a new environment (e.g., `sandbox`, `customer-X`):

### Step 1: Update Instance Matrix

Edit `config/instance-matrix.yaml`:

```yaml
environments:
  # ... existing environments ...

  sandbox:
    odoo:
      role: "erp"
      url: "https://sandbox-erp.insightpulseai.net"
      db_url_env: "ODOO_DB_URL_SANDBOX"
    supabase:
      role: "app+analytics"
      project_ref_env: "SUPABASE_PROJECT_REF_SANDBOX"
      db_url_env: "SUPABASE_DB_URL_SANDBOX"
    superset:
      role: "bi-metadata"
      url: "https://sandbox-superset.insightpulseai.net"
      metadata_db_url_env: "SUPERSET_META_DB_URL_SANDBOX"
```

### Step 2: Update This Document

Add new environment section with instance details.

### Step 3: Configure Environment Variables

**Local/CI:**
```bash
export ODOO_DB_URL_SANDBOX="postgres://..."
export SUPABASE_DB_URL_SANDBOX="postgres://..."
export SUPERSET_META_DB_URL_SANDBOX="postgres://..."
```

**GitHub Secrets:**
- `ODOO_DB_URL_SANDBOX`
- `SUPABASE_DB_URL_SANDBOX`
- `SUPERSET_META_DB_URL_SANDBOX`

### Step 4: Add Health Check Target

Edit `Makefile`:

```makefile
instance-health-sandbox:
    bash scripts/health/check-instance-health.sh sandbox
```

### Step 5: Test

```bash
make instance-health-sandbox
```

---

## Migration Between Environments

### Data Migration: Production → Staging

**Purpose:** Refresh staging with anonymized production data

**Process:**

1. **Backup Production:**
   ```bash
   pg_dump "$ODOO_DB_URL_PRODUCTION" | gzip > prod_backup.sql.gz
   ```

2. **Anonymize Data:**
   ```bash
   gunzip -c prod_backup.sql.gz | \
     sed 's/real-email@example.com/test@example.com/g' | \
     psql "$ODOO_DB_URL_STAGING"
   ```

3. **Sync to Supabase Staging:**
   ```bash
   # Run ETL pipeline to sync Odoo → Supabase
   make etl-sync-staging
   ```

4. **Refresh Superset Staging:**
   ```bash
   # Clear cached datasets
   make superset-cache-clear-staging
   ```

### Schema Migration: DBML → All Environments

**Process:**

1. **Update DBML Schema:**
   ```bash
   # Edit DBML files in dbml/supabase/
   nano dbml/supabase/analytics.dbml
   ```

2. **Generate Migration SQL:**
   ```bash
   make dbml-generate-sql
   ```

3. **Apply to Local:**
   ```bash
   psql "$SUPABASE_DB_URL_LOCAL" < migrations/001_analytics_update.sql
   ```

4. **Test Locally:**
   ```bash
   make instance-health-local
   ```

5. **Apply to Staging:**
   ```bash
   psql "$SUPABASE_DB_URL_STAGING" < migrations/001_analytics_update.sql
   ```

6. **Verify Staging:**
   ```bash
   make instance-health-staging
   ```

7. **Apply to Production (with approval):**
   ```bash
   # Requires manual approval
   psql "$SUPABASE_DB_URL_PRODUCTION" < migrations/001_analytics_update.sql
   ```

---

## Troubleshooting

### Issue: Instance Health Check Fails

**Symptoms:**
- `make instance-health` fails
- Connection timeouts

**Solutions:**

1. **Verify environment variables:**
   ```bash
   echo "$ODOO_DB_URL_LOCAL"
   echo "$SUPABASE_DB_URL_LOCAL"
   echo "$SUPERSET_META_DB_URL_LOCAL"
   ```

2. **Check service status:**
   ```bash
   # Local (Docker)
   docker-compose ps

   # Production (Droplet)
   ssh root@165.227.10.178
   systemctl status odoo
   systemctl status nginx
   ```

3. **Test connectivity manually:**
   ```bash
   # Odoo HTTP
   curl -I https://erp.insightpulseai.net/web/login

   # Supabase DB
   psql "$SUPABASE_DB_URL_PRODUCTION" -c "SELECT 1;"

   # Superset
   curl -I https://superset.insightpulseai.net/health
   ```

### Issue: Wrong Database Connection

**Symptoms:**
- Production data showing in staging
- Schema mismatches

**Solutions:**

1. **Verify instance matrix:**
   ```bash
   cat config/instance-matrix.yaml | grep -A10 "production:"
   ```

2. **Check environment variable precedence:**
   ```bash
   # Which env var is set?
   env | grep -E "ODOO_DB_URL|SUPABASE_DB_URL|SUPERSET_META_DB_URL"
   ```

3. **Use explicit environment parameter:**
   ```bash
   # Force production
   ./scripts/health/check-instance-health.sh production
   ```

---

## References

- **Instance Matrix:** `config/instance-matrix.yaml`
- **Health Check Script:** `scripts/health/check-instance-health.sh`
- **Automation Health:** `docs/AUTOMATION_STATUS.md`
- **Infrastructure Architecture:** `docs/INFRASTRUCTURE_ARCHITECTURE.md`

---

**Maintainer:** InsightPulse AI Operations Team
**Support:** jgtolentino_rn@yahoo.com
**Last Reviewed:** 2025-11-09
**Next Review:** 2025-12-09
