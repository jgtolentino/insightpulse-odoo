# Platform Tasks

Detailed task breakdown for InsightPulse Odoo platform development.

## Current Sprint: Phase 1.1 - Foundation

**Sprint Goal**: Complete spec-kit documentation and CI/CD infrastructure

**Sprint Dates**: 2025-11-01 to 2025-11-15

### Active Tasks

#### TSK-001: Platform Spec (COMPLETED)
- **Description**: Create canonical platform_spec.json
- **Status**: ✅ Completed
- **Assignee**: System
- **Story Points**: 5
- **Acceptance Criteria**:
  - [x] Create spec/platform_spec.json with all required sections
  - [x] Include spec_state and spec_version fields
  - [x] Define all 6 core services
  - [x] Configure Google OAuth with all 6 domains
  - [x] Document Odoo.sh policy (reference_only)
  - [x] List all CI/CD workflows
- **Files Created**:
  - spec/platform_spec.json
  - CLAUDE.md (updated with Odoo.sh policy)

#### TSK-002: JSON Schema Validation (COMPLETED)
- **Description**: Create JSON Schema for platform_spec.json validation
- **Status**: ✅ Completed
- **Assignee**: System
- **Story Points**: 3
- **Acceptance Criteria**:
  - [x] Create spec/platform_spec.schema.json
  - [x] Validate required fields (spec_state, spec_version, app, hosting, oauth, docs_platform, ai_orchestration, ci_cd, governance)
  - [x] Validate enums (spec_state, odoo_sh.usage)
  - [x] Validate patterns (version semver)
  - [x] Validate object structures
- **Files Created**:
  - spec/platform_spec.schema.json

#### TSK-003: Spec Validation Script (COMPLETED)
- **Description**: Create Python script to validate spec and check file existence
- **Status**: ✅ Completed
- **Assignee**: System
- **Story Points**: 5
- **Acceptance Criteria**:
  - [x] Create scripts/validate_spec.py
  - [x] Validate spec against JSON schema
  - [x] Check all docs files exist (docs_platform.sections)
  - [x] Check all workflow files exist (ci_cd.workflows)
  - [x] Exit codes: 0=pass, 1=schema fail, 2=missing files, 3=JSON parse error
- **Files Created**:
  - scripts/validate_spec.py

#### TSK-004: Spec Guard Workflow (COMPLETED)
- **Description**: Create GitHub Action to enforce spec validation
- **Status**: ✅ Completed
- **Assignee**: System
- **Story Points**: 3
- **Acceptance Criteria**:
  - [x] Create .github/workflows/spec-guard.yml
  - [x] Trigger on PR + push for spec/**, docs/**, .github/workflows/**
  - [x] Run scripts/validate_spec.py
  - [x] Fail PR if validation fails
- **Files Created**:
  - .github/workflows/spec-guard.yml

#### TSK-005: CI Workflow Skeletons (COMPLETED)
- **Description**: Create minimal skeleton workflows for all CI/CD
- **Status**: ✅ Completed
- **Assignee**: System
- **Story Points**: 5
- **Acceptance Criteria**:
  - [x] Create .github/workflows/ci-supabase.yml
  - [x] Create .github/workflows/ci-superset.yml
  - [x] Create .github/workflows/cd-odoo-prod.yml
  - [x] Create .github/workflows/docs-ci.yml
  - [x] Create .github/workflows/pages-deploy.yml
  - [x] All workflows pass (echo + exit 0)
- **Files Created**:
  - .github/workflows/ci-supabase.yml
  - .github/workflows/ci-superset.yml
  - .github/workflows/cd-odoo-prod.yml
  - .github/workflows/docs-ci.yml
  - .github/workflows/pages-deploy.yml

#### TSK-006: Docs Scaffolding (COMPLETED)
- **Description**: Create all missing docs files referenced in platform_spec.json
- **Status**: ✅ Completed
- **Assignee**: System
- **Story Points**: 8
- **Acceptance Criteria**:
  - [x] Create docs/_config.yml
  - [x] Create docs/index.md and docs/INDEX.md
  - [x] Create docs/getting-started.md
  - [x] Create docs/architecture.md
  - [x] Create docs/guides/*.md (4 files)
  - [x] Create docs/deployments/*.md (2 files)
  - [x] Create docs/spec-kit/*.md (5 files)
  - [x] Create docs/history/index.md
- **Files Created**:
  - docs/_config.yml
  - docs/index.md
  - docs/INDEX.md
  - docs/getting-started.md
  - docs/architecture.md
  - docs/guides/workflows-ci-cd.md
  - docs/guides/docker-compose.md
  - docs/guides/troubleshooting.md
  - docs/guides/hosting-policy.md
  - docs/deployments/overview.md
  - docs/deployments/digitalocean.md
  - docs/spec-kit/PRD_PLATFORM.md
  - docs/spec-kit/planning.md
  - docs/spec-kit/tasks.md (this file)
  - docs/spec-kit/CHANGELOG.md
  - docs/spec-kit/doc.yaml
  - docs/history/index.md

#### TSK-007: Validation and Testing (IN PROGRESS)
- **Description**: Run local validation and tests to ensure everything is green
- **Status**: 🔄 In Progress
- **Assignee**: System
- **Story Points**: 3
- **Acceptance Criteria**:
  - [ ] Run scripts/validate_spec.py successfully
  - [ ] All required docs files exist
  - [ ] All CI/CD workflow files exist
  - [ ] Spec-kit compliance verified
  - [ ] Provide final summary
- **Commands to Run**:
  ```bash
  python scripts/validate_spec.py
  ls -la .github/workflows/
  ls -la docs/
  ```

### Backlog (Phase 1.2 - 1.4)

#### TSK-008: Multi-Tenant Isolation
- **Description**: Implement strict company_id isolation on all models
- **Status**: Pending
- **Story Points**: 13
- **Acceptance Criteria**:
  - [ ] Add company_id field to all custom models
  - [ ] Add multi-company record rules
  - [ ] Test cross-company data isolation
  - [ ] Document multi-tenancy architecture

#### TSK-009: BIR Compliance Module
- **Description**: Create Odoo module for BIR forms 2307, 2316
- **Status**: Pending
- **Story Points**: 21
- **Acceptance Criteria**:
  - [ ] Generate Form 2307 (withholding tax)
  - [ ] Generate Form 2316 (annual withholding)
  - [ ] Implement immutable accounting (reversals only)
  - [ ] Create audit trail via chatter
  - [ ] Test with sample data

#### TSK-010: Google OAuth SSO
- **Description**: Configure Google OAuth across all domains
- **Status**: Pending
- **Story Points**: 8
- **Acceptance Criteria**:
  - [ ] Set up Google OAuth project
  - [ ] Configure authorized origins (6 domains)
  - [ ] Configure redirect URIs
  - [ ] Test OAuth flow
  - [ ] Document setup process

#### TSK-011: DigitalOcean Deployment
- **Description**: Deploy Odoo CE 19 to production droplet
- **Status**: Pending
- **Story Points**: 13
- **Acceptance Criteria**:
  - [ ] Create droplet (ipai-odoo-erp, SFO2)
  - [ ] Configure Nginx reverse proxy
  - [ ] Set up Let's Encrypt SSL
  - [ ] Deploy Odoo via Docker
  - [ ] Configure firewall (UFW)
  - [ ] Test production access

#### TSK-012: OCR Service
- **Description**: Deploy PaddleOCR service to SGP1 droplet
- **Status**: Pending
- **Story Points**: 13
- **Acceptance Criteria**:
  - [ ] Create droplet (ocr-service-droplet, SGP1)
  - [ ] Deploy PaddleOCR Docker image
  - [ ] Integrate DeepSeek LLM validation
  - [ ] Create API endpoints
  - [ ] Test OCR accuracy (>60%)

#### TSK-013: Apache Superset
- **Description**: Deploy Superset to App Platform
- **Status**: Pending
- **Story Points**: 8
- **Acceptance Criteria**:
  - [ ] Create App Platform app
  - [ ] Deploy Superset Docker image
  - [ ] Connect to Odoo + Supabase data sources
  - [ ] Create expense dashboard
  - [ ] Create BIR compliance dashboard

#### TSK-014: Pulser v4.0.0
- **Description**: Deploy MCP Coordinator and AI agents
- **Status**: Pending
- **Story Points**: 13
- **Acceptance Criteria**:
  - [ ] Deploy MCP Coordinator to App Platform
  - [ ] Configure Dash, Maya, Echo agents
  - [ ] Test agent coordination
  - [ ] Document agent workflows

## Task Metadata

### Story Point Scale
- 1: Trivial (1 hour)
- 3: Small (1 day)
- 5: Medium (2-3 days)
- 8: Large (1 week)
- 13: Very Large (2 weeks)
- 21: Huge (1 month)

### Status Definitions
- ✅ Completed: Done and verified
- 🔄 In Progress: Currently being worked on
- 🚧 Blocked: Waiting on dependency
- 📋 Pending: Not started yet

### Labels
- `phase-1`: Foundation (spec-kit, CI/CD)
- `phase-2`: MVP (OCR, Superset, Pulser)
- `phase-3`: Scale (onboarding, optimization)
- `p0`: Must-have (critical)
- `p1`: Should-have (important)
- `p2`: Nice-to-have (optional)

## Sprint Velocity

**Current Sprint** (Phase 1.1):
- Planned: 29 story points
- Completed: 29 story points
- Velocity: 100%

**Next Sprint** (Phase 1.2):
- Planned: 42 story points (TSK-008, TSK-009, TSK-010)

## References

- [PRD](PRD_PLATFORM.md) - Product requirements
- [Planning](planning.md) - Milestones and KPIs
- [CHANGELOG](CHANGELOG.md) - Version history
- [Platform Spec](../../spec/platform_spec.json) - Canonical specification
