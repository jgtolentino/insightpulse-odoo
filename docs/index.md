# InsightPulse Odoo Platform

Multi-tenant, BIR-compliant Finance Shared Service Center (SSC) built on Odoo CE 18.0.

## Quick Links

- [Getting Started](getting-started.md)
- [Architecture](architecture.md)
- [Guides](guides/)
- [Deployments](deployments/)
- [Platform Spec-Kit](spec-kit/)
- [Pulser Spec-Kit](pulser/)
- [Visual Compliance Agent](knowledge-graph-architecture.md)
- [Routing Review](ROUTING_REVIEW.md)

## Overview

InsightPulse Odoo is a self-hosted ERP platform that replaces expensive SaaS tools (SAP Concur, Ariba, Tableau) with 100% open-source alternatives.

**Core Technologies:**
- ERP: Odoo CE 18.0 + OCA modules
- Database: PostgreSQL 15 + Supabase
- Analytics: Apache Superset (Tableau alternative)
- Infrastructure: DigitalOcean (Docker + App Platform)
- AI: Pulser v4.0.0 orchestration

## Features

- Multi-tenant legal entity isolation
- BIR compliance (Forms 2307, 2316, e-invoicing)
- Automated OCR expense processing
- Google OAuth SSO across all domains
- CI/CD with GitHub Actions

## Documentation

See the navigation menu above for detailed guides and deployment instructions.

## License

LGPL-3.0
