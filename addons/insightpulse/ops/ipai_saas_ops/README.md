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

## Odoo Studio Compatibility

**Studio Support**: ✅ Full customization support with provisioning restrictions

**Safe to Customize**:
- Add custom fields (SLA tier, region, custom metadata)
- Create custom views (kanban for tenants, graph for usage trends)
- Add automated actions (welcome emails, usage alerts)
- Custom reports for billing and analytics
- Tenant-specific dashboards

**Recommended Automations**:
- Welcome email to new tenants
- Usage threshold alerts (75%, 90%, 100%)
- Backup failure notifications
- Monthly usage reports
- Tenant health check notifications

**Restricted Operations** (Admin/Code only):
- Tenant provisioning logic (create_tenant method)
- Backup encryption/decryption
- Database operations
- Multi-company assignment

See [docs/STUDIO_GUIDE.md](../../../../docs/STUDIO_GUIDE.md) for SaaS-specific monitoring and alerting patterns.

## Models

- `saas.tenant`: Tenant lifecycle management
- `saas.backup`: Backup automation with retention policies
- `saas.usage`: Multi-dimensional usage tracking

## Security

- SaaS Ops User: Read-only access
- SaaS Ops Admin: Full CRUD and provisioning

## Dependencies

- ipai_core, base
