# Changelog

All notable changes to the InsightPulse Odoo platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Spec-kit documentation (PRD, planning, tasks, CHANGELOG, doc.yaml)
- Canonical platform specification (spec/platform_spec.json)
- JSON Schema validation (spec/platform_spec.schema.json)
- Spec validation script (scripts/validate_spec.py)
- Spec Guard GitHub Action (.github/workflows/spec-guard.yml)
- CI/CD workflow skeletons (ci-supabase, ci-superset, cd-odoo-prod, docs-ci, pages-deploy)
- Documentation scaffolding (getting-started, architecture, guides, deployments)
- Odoo.sh policy enforcement (reference_only)

### Changed
- CLAUDE.md updated with Canonical Platform Specification section
- CLAUDE.md updated with Odoo.sh policy (reference_only)

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- Odoo.sh policy prevents step-by-step deployment guides

## [1.0.0] - 2025-11-09

### Added
- Initial spec-kit framework
- Platform specification canonical source of truth
- Multi-tenant legal entity isolation design
- BIR compliance requirements (Forms 2307, 2316, e-invoicing)
- Google OAuth SSO configuration
- DigitalOcean deployment targets
- Apache Superset analytics integration
- Pulser v4.0.0 AI orchestration

### Changed
- None (initial release)

### Security
- Google OAuth SSO across all 6 domains
- Multi-company record rules for data isolation
- Immutable accounting records (BIR compliance)

## Version History

- **1.0.0** (2025-11-09): Initial release with spec-kit and CI/CD foundation
- **Unreleased**: Ongoing development (Phase 1.1)

## Migration Guide

### Upgrading to 1.0.0

**From scratch**:
1. Clone repository
2. Run `docker compose up -d`
3. Access http://localhost:8069
4. Configure Google OAuth (see spec/platform_spec.json)

**Production deployment**:
1. Read docs/deployments/overview.md
2. Set up DigitalOcean droplets
3. Run scripts/deploy/deploy-all.sh
4. Verify via health checks

## Breaking Changes

- None yet (initial release)

## Deprecation Notices

- Odoo.sh deployment: Reference only, not for active deployment

## Contributors

- Jake Tolentino (Product Owner, Tech Lead)

## References

- [PRD](PRD_PLATFORM.md) - Product requirements
- [Planning](planning.md) - Milestones and KPIs
- [Tasks](tasks.md) - Detailed task breakdown
- [Platform Spec](../../spec/platform_spec.json) - Canonical specification
