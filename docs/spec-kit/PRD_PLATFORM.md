# Platform Product Requirements Document (PRD)

Product requirements for InsightPulse Odoo platform.

## Document Status
- **Status**: Draft
- **Version**: 1.0.0
- **Last Updated**: 2025-11-09
- **Spec Reference**: spec/platform_spec.json

## Executive Summary

InsightPulse Odoo is a multi-tenant, BIR-compliant Finance Shared Service Center (SSC) platform built on Odoo CE 19, replacing expensive SaaS tools with 100% open-source alternatives.

**Cost Savings**: $50k+ annually by replacing SAP Concur, Ariba, Tableau, and Slack Enterprise

**Tech Stack**:
- ERP: Odoo CE 19 + OCA modules (not Enterprise)
- Database: PostgreSQL 15 + Supabase
- Analytics: Apache Superset (Tableau alternative)
- Infrastructure: DigitalOcean (Docker + App Platform)
- AI: Pulser v4.0.0 orchestration

## Goals and Objectives

### Primary Goals
1. Multi-tenant legal entity isolation with BIR compliance
2. Replace expensive SaaS tools with open-source alternatives
3. Automated OCR expense processing
4. Google OAuth SSO across all domains
5. CI/CD automation with GitHub Actions

### Success Metrics
- Multi-tenancy: Strict `company_id` isolation for all legal entities
- BIR Compliance: Forms 2307, 2316, e-invoicing ready
- Cost Savings: <$1k/month infrastructure costs (vs $4k+ for SaaS)
- Automation: >80% expense reports auto-processed via OCR
- Uptime: >99.5% for production services

## User Personas

### Finance SSC Manager
- **Needs**: BIR-compliant reporting, multi-agency oversight
- **Pain Points**: Manual tax form generation, expense approval delays
- **Solution**: Automated BIR forms, real-time dashboards, email notifications

### Employee
- **Needs**: Quick expense submission, approval status visibility
- **Pain Points**: Manual receipt entry, unclear approval status
- **Solution**: OCR receipt scanning, mobile-friendly UI, real-time status

### Accountant
- **Needs**: Immutable audit trail, accurate tax calculations
- **Pain Points**: Manual journal entries, reconciliation errors
- **Solution**: Automated journal entries, reversals for corrections, audit log

### IT Administrator
- **Needs**: Easy deployment, monitoring, troubleshooting
- **Pain Points**: Complex deployments, unclear errors
- **Solution**: Docker Compose, CI/CD automation, comprehensive logging

## Features and Requirements

### Must-Have (P0)

#### 1. Multi-Tenant Legal Entity Isolation
- Separate database or strict `company_id` field on all models
- Per-company configuration via `ir.config_parameter`
- Separate books, taxes, numbering sequences, reports
- **NOT tenancy**: Internal agencies (org structure/tags only)

#### 2. BIR Compliance
- Immutable accounting records (reversals for corrections, not edits)
- Automated Form 2307 (withholding tax) generation
- Automated Form 2316 (annual withholding) generation
- E-invoicing connector (ready for 2025 BIR rollout)
- Complete audit trail via chatter + mail.activity

#### 3. Google OAuth SSO
- Single provider across all 6 domains (insightpulseai.net, erp, superset, mcp, bkn, chat)
- Redirect URIs: /auth_oauth/signin patterns
- OAuth credentials in spec/platform_spec.json

#### 4. Odoo CE 19 + OCA Modules
- Custom addons in odoo/addons/
- OCA modules from oca/ directory (web, server-tools, account-financial-tools, project, hr)
- **NOT Odoo Enterprise** - CE only

#### 5. CI/CD Automation
- spec-guard.yml - Validate platform_spec.json and file existence
- ci-odoo.yml - Build+test Odoo Docker image
- ci-supabase.yml - Apply Supabase migrations
- ci-superset.yml - Validate Superset dashboards
- cd-odoo-prod.yml - Deploy to production (main branch only)
- docs-ci.yml - Validate docs links and structure
- pages-deploy.yml - Deploy GitHub Pages

### Should-Have (P1)

#### 6. OCR Expense Processing
- PaddleOCR for receipt scanning
- DeepSeek LLM for validation
- Auto-populate expense fields from OCR data
- Confidence threshold: >60%

#### 7. Apache Superset Analytics
- BI dashboards (Tableau alternative)
- Real-time metrics from Odoo + Supabase
- Pre-built dashboards: expenses, approvals, BIR compliance

#### 8. Pulser v4.0.0 AI Orchestration
- Agents: Dash (dashboard), Maya (UX/docs), Echo (signal extraction)
- MCP Coordinator at https://mcp.insightpulseai.net
- Context documents: docs/pulser/PRD_PULSER.md, CLAUDE.md, skills.md

### Nice-to-Have (P2)

#### 9. Slack/Mattermost Integration
- Real-time approval notifications
- Expense submission via chat
- Bot commands for status checks

#### 10. Mobile App
- React Native or Flutter
- OCR receipt capture
- Approval workflows
- Dashboard views

## Technical Specifications

### Hosting Policy

**Primary Mode**: self_hosted

**Providers**: DigitalOcean

**Odoo.sh Policy**: `reference_only`
- ✅ Allowed: High-level overview, constraints, limitations, migration considerations
- ❌ Forbidden: Step-by-step deployment instructions, wizard guides, migration playbooks

**Deployment Targets**:
- ✅ Preferred: DigitalOcean (droplets + App Platform), Docker, this repository
- ❌ Avoid: Odoo.sh (summarize and link only, never deploy)

### Infrastructure

**Droplets**:
- ipai-odoo-erp (SFO2) - 165.227.10.178 (Odoo CE 19)
- ocr-service-droplet (SGP1) - 188.166.237.231 (OCR processing)

**App Platform Apps**:
- odoo-saas-platform
- superset-analytics
- mcp-coordinator

**Reverse Proxy**: Nginx with Let's Encrypt SSL

### Database Schema

**Multi-Tenant Fields** (required on all models):
```python
company_id = fields.Many2one(
    'res.company',
    string='Company',
    required=True,
    default=lambda self: self.env.company,
    index=True
)
```

**BIR Compliance Fields**:
```python
# Audit trail
audit_trail = fields.Text('Audit Trail', readonly=True)
correction_entry_ids = fields.One2many('account.move', 'corrects_entry_id', 'Correction Entries')

# BIR forms
bir_form_2307 = fields.Binary('BIR Form 2307')
bir_form_2316 = fields.Binary('BIR Form 2316')
```

### API Specifications

**RESTful Endpoints**:
- GET /api/v1/expenses - List expenses (company_id filter)
- POST /api/v1/expenses - Create expense (auto-assign company_id)
- GET /api/v1/bir/form_2307/{id} - Download BIR Form 2307
- POST /api/v1/ocr/scan - Upload receipt for OCR processing

**Authentication**: OAuth 2.0 (Google provider)

**Response Format**: JSON
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "company_id": 1,
    "timestamp": "2025-11-09T10:30:00Z"
  }
}
```

## Security Requirements

**Authentication**:
- Google OAuth SSO (single provider)
- Session timeout: 8 hours
- MFA support (optional)

**Authorization**:
- Role-based access control (RBAC) via Odoo groups
- Multi-company record rules (strict `company_id` filtering)
- RLS policies on Supabase tables

**Data Protection**:
- Encryption at rest (PostgreSQL encryption)
- TLS 1.3 for all HTTPS endpoints
- Secrets in environment variables (never hardcoded)

**Audit Trail**:
- All financial transactions logged via mail.thread
- Immutable records (no edits, only reversals)
- User activity tracking

## Compliance

**BIR (Bureau of Internal Revenue, Philippines)**:
- Forms 2307, 2316, 1701, 1702 generation
- Immutable accounting records
- Complete audit trail
- E-invoicing ready (2025 rollout)

**Data Privacy**:
- GDPR-ready (consent management, right to erasure)
- Philippine Data Privacy Act compliance
- Anonymization for non-PII reports

## Non-Functional Requirements

**Performance**:
- Page load: <3s for 95th percentile
- API response: <500ms for 95th percentile
- Database queries: <100ms for most common operations

**Scalability**:
- Support: 10,000 users/company
- Concurrent users: 500
- Database size: >1TB

**Availability**:
- Uptime: >99.5%
- Recovery Time Objective (RTO): <1 hour
- Recovery Point Objective (RPO): <15 minutes

**Maintainability**:
- OCA compliance for all modules
- Comprehensive documentation
- Automated tests (>80% coverage)

## Dependencies

**Required**:
- Odoo CE 19.0
- PostgreSQL 15+
- Python 3.11+
- Docker 20.10+
- DigitalOcean account

**Optional**:
- Apache Superset 3.0+
- PaddleOCR
- DeepSeek LLM API

## Constraints and Assumptions

**Constraints**:
- Budget: <$1k/month infrastructure
- No Odoo Enterprise license
- Self-hosted only (no Odoo.sh)
- Open-source stack only

**Assumptions**:
- DigitalOcean availability in SFO2 and SGP1
- Google OAuth availability
- Philippine internet connectivity
- BIR e-invoicing API stable by 2025

## Risks and Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| BIR e-invoicing delayed | High | Medium | Build pluggable connector, wait for official release |
| DigitalOcean outage | High | Low | Multi-region deployment, backup to AWS |
| OCR accuracy <60% | Medium | Medium | Manual review workflow, DeepSeek LLM validation |
| OCA module incompatibility | Medium | Medium | Pin versions, thorough testing |
| Database migration issues | High | Low | Backup before migrate, dry-run testing |

## Success Criteria

**Phase 1 (Q1 2025)**: Foundation
- ✅ Spec-kit documentation complete
- ✅ CI/CD workflows operational
- ✅ Multi-tenancy isolation working
- ✅ BIR compliance foundations

**Phase 2 (Q2 2025)**: MVP
- OCR expense processing live
- Google OAuth SSO working
- Apache Superset dashboards deployed
- Production deployment on DigitalOcean

**Phase 3 (Q3 2025)**: Scale
- 10+ companies migrated
- >80% OCR auto-approval rate
- <$1k/month infrastructure costs
- >99.5% uptime

## References

- [Platform Spec](../../spec/platform_spec.json) - Canonical specification
- [Architecture](../architecture.md) - System architecture
- [Deployment Guide](../deployments/overview.md) - Deployment instructions
- [Pulser PRD](../pulser/PRD_PULSER.md) - AI orchestration requirements

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## Approval

**Product Owner**: Jake Tolentino
**Technical Lead**: Jake Tolentino
**Status**: Draft
**Next Review**: 2025-12-01
