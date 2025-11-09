# Hosting Policy

Official hosting and deployment policy for InsightPulse Odoo platform.

## Canonical Hosting Policy

**Primary Mode**: `self_hosted`

**Providers**: DigitalOcean

**Orchestration**: Docker + GitHub Actions

## Deployment Targets

### ✅ Preferred Targets

1. **DigitalOcean Droplets**
   - ipai-odoo-erp (SFO2) - 165.227.10.178
   - ocr-service-droplet (SGP1) - 188.166.237.231

2. **DigitalOcean App Platform**
   - odoo-saas-platform
   - superset-analytics
   - mcp-coordinator

3. **Docker (Local Development)**
   - docker-compose.yml
   - Local testing and development

4. **This Repository**
   - All deployment scripts in scripts/deploy/
   - Infrastructure as Code

### ❌ Avoid Targets

**Odoo.sh**: Reference only, not for deployment

**Usage**: `reference_only`

**Allowed Topics**:
- High-level overview
- Constraints and limitations
- Migration considerations
- Architecture comparison

**Forbidden Topics**:
- Step-by-step deployment instructions
- Wizard-like setup guides
- Full migration playbooks
- Copy-paste shell scripts for Odoo.sh

## Domain Configuration

**Base Domain**: insightpulseai.net

**Subdomains**:
- `erp.insightpulseai.net` - Odoo ERP
- `superset.insightpulseai.net` - Analytics
- `mcp.insightpulseai.net` - MCP Coordinator
- `bkn.insightpulseai.net` - BKN service
- `chat.insightpulseai.net` - Chat interface

**Reverse Proxy**:
- Type: nginx-or-equivalent
- Odoo upstream: http://127.0.0.1:8069
- HTTPS: Required (Let's Encrypt)

## OAuth Configuration

**Provider**: Google (project: claude-mcp-bridge)

**Authorized Origins**:
- https://insightpulseai.net
- https://erp.insightpulseai.net
- https://superset.insightpulseai.net
- https://mcp.insightpulseai.net
- https://bkn.insightpulseai.net
- https://chat.insightpulseai.net

**Redirect URIs**:
- https://erp.insightpulseai.net/auth_oauth/signin
- https://insightpulseai.net/auth_oauth/signin
- https://erp.insightpulseai.net/web/login

## Deployment Workflow

### Development
```bash
# Local development
make dev
docker compose up -d

# Access at http://localhost:8069
```

### Production
```bash
# CI/CD via GitHub Actions
# Triggered on push to main

# Manual deployment
scripts/deploy/deploy-all.sh

# Target: DigitalOcean droplet ipai-odoo-erp
```

## Infrastructure as Code

All infrastructure configuration is version-controlled:

- **Docker**: docker-compose.yml, Dockerfile
- **Deployment**: scripts/deploy/
- **CI/CD**: .github/workflows/
- **Spec**: spec/platform_spec.json (canonical source)

## AI Assistant Policy

**Deployment Guidance**:
- ✅ Preferred targets: DigitalOcean, Docker, this repository
- ❌ Avoid targets: Odoo.sh
- Odoo.sh handling: Summarize and link only

**Before touching infra/auth/deployment**:
Always read `spec/platform_spec.json` first

## Odoo.sh Reference Documentation

**Base**: https://www.odoo.com/documentation/19.0/

**Topics** (reference only):
- Create project: /administration/odoo_sh/getting_started/create.html
- Containers: /administration/odoo_sh/advanced/containers.html
- Submodules: /administration/odoo_sh/advanced/submodules.html
- FAQ: /administration/odoo_sh/advanced/frequent_technical_questions.html

**Usage**: Summarize and link, never provide step-by-step deployment instructions

## Compliance

**Spec Guard**: All deployments must pass spec validation

```bash
# Validation command
python scripts/validate_spec.py

# CI workflow
.github/workflows/spec-guard.yml
```

**Exit Codes**:
- 0: All validations passed
- 1: Schema validation failed
- 2: Referenced files missing
- 3: JSON parsing error

## Security

- HTTPS required for all public endpoints
- OAuth credentials in environment variables (never hardcoded)
- Secrets managed via GitHub Secrets (production)
- `.env` file for local development (gitignored)

## Multi-Tenancy

**Definition**: Legal entity isolation

**Implementation**:
- Separate database OR strict `company_id` isolation
- Per-company configuration via `ir.config_parameter`
- Separate books, taxes, numbering, reports

**NOT Tenancy**: Internal agencies (organizational structure)

## References

- [Platform Spec](../spec-kit/PRD_PLATFORM.md) - Canonical specification
- [Architecture](../architecture.md) - System architecture
- [Deployment Guide](../deployments/overview.md) - Deployment instructions
- [CI/CD Workflows](workflows-ci-cd.md) - GitHub Actions

## Governance

**Required**: Spec-kit compliance

**Review Rules**:
- Require docs update
- Require CI green
- Minimum 2 reviewers

**Versioning**: Semantic versioning (SemVer)
