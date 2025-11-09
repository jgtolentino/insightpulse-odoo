# System Architecture

InsightPulse Odoo platform architecture overview.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  insightpulseai.net Domains                 │
├─────────────────────────────────────────────────────────────┤
│  erp.  │  superset.  │  mcp.  │  bkn.  │  chat.            │
└────┬────────────┬──────────┬──────────┬──────────┬──────────┘
     │            │          │          │          │
     ▼            ▼          ▼          ▼          ▼
┌─────────┐  ┌─────────┐  ┌─────┐  ┌─────┐  ┌─────┐
│ Odoo CE │  │Superset │  │ MCP │  │ BKN │  │Chat │
│   19    │  │Analytics│  │Coord│  │     │  │     │
└────┬────┘  └────┬────┘  └──┬──┘  └─────┘  └─────┘
     │            │           │
     └────────────┴───────────┴─────────────┐
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │  PostgreSQL   │
                                    │  + Supabase   │
                                    └───────────────┘
```

## Core Services

### 1. Odoo CE 19 (ERP Core)
- **URL**: https://erp.insightpulseai.net
- **Port**: 8069
- **Purpose**: Multi-tenant ERP with custom + OCA modules
- **Add-ons**: Custom addons + OCA (web, server-tools, account-financial-tools, project, hr)

### 2. PostgreSQL + Supabase
- **Type**: postgres+api
- **Schema**: supabase/schema/
- **Migrations**: supabase/migrations/
- **Purpose**: Primary database + API layer

### 3. Apache Superset (Analytics)
- **URL**: https://superset.insightpulseai.net
- **Purpose**: BI dashboards (Tableau alternative)
- **Dashboards**: apps/superset/dashboards/

### 4. MCP Coordinator
- **URL**: https://mcp.insightpulseai.net
- **Purpose**: AI agent coordination

### 5. Pulser v4.0.0 (AI Orchestrator)
- **Service**: services/pulser/
- **Agents**: Dash (dashboard), Maya (UX/docs), Echo (signal extraction)

## Multi-Tenancy Model

**Legal Entity Isolation:**
- Separate database or strict `company_id` isolation
- Per-company configuration via `ir.config_parameter`
- Separate books, taxes, numbering, reports

**NOT Tenancy:**
- Agencies (internal units) stored as org structure/tags
- No cross-db split for agencies
- Security via role/rules only

## Authentication

**Google OAuth SSO:**
- Provider: Google (project: claude-mcp-bridge)
- Authorized origins: All 6 domains
- Redirect URIs: `/auth_oauth/signin` patterns

## Deployment

### Development
- `make dev` or `docker compose up -d`
- Localhost / 127.0.0.1
- Compose file: docker-compose.yml

### Production
- **Provider**: DigitalOcean
- **Droplets**:
  - ipai-odoo-erp (SFO2) - 165.227.10.178
  - ocr-service-droplet (SGP1) - 188.166.237.231
- **App Platform**:
  - odoo-saas-platform
  - superset-analytics
  - mcp-coordinator
- **CD**: GitHub Actions → scripts/deploy/deploy-all.sh

## BIR Compliance

- **Immutable accounting**: Reversals for corrections
- **Forms**: 2307, 2316 generation
- **Audit trail**: Chatter + mail.activity
- **E-invoice**: Pluggable connector (2025 BIR rollout ready)

## AI Orchestration

**Pulser v4.0.0:**
- Entry doc: docs/pulser/PRD_PULSER.md
- Claude context: CLAUDE.md
- Skills: skills.md
- Agents: Dash, Maya, Echo (see spec/platform_spec.json)

## Odoo.sh Policy

**Usage**: `reference_only`
- ✅ Allowed: High-level overview, constraints, limitations
- ❌ Forbidden: Step-by-step deployment, wizard guides, migration playbooks

**Deployment Targets**:
- ✅ Preferred: DigitalOcean, Docker, this repository
- ❌ Avoid: Odoo.sh

## Next Steps

- See [Deployment Overview](deployments/overview.md)
- See [Platform Spec](spec-kit/PRD_PLATFORM.md)
- See [Pulser Spec](pulser/PRD_PULSER.md)
