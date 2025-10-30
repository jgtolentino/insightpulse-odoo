# InsightPulse SaaS Ops

**Version**: 19.0.1.0.0
**Author**: InsightPulse AI
**License**: LGPL-3

## Overview

Self-service tenant creation and automated backup management for multi-tenant SaaS deployments.

## Features

- **Tenant Management**: Self-service tenant provisioning
- **Automated Backups**: Scheduled and manual backup support
- **Usage Tracking**: Multi-metric usage monitoring
- **Dashboard**: Real-time tenant health monitoring

## Models

- `saas.tenant`: Tenant lifecycle management
- `saas.backup`: Backup automation with retention policies
- `saas.usage`: Multi-dimensional usage tracking

## Security

- SaaS Ops User: Read-only access
- SaaS Ops Admin: Full CRUD and provisioning

## Dependencies

- ipai_core, base
