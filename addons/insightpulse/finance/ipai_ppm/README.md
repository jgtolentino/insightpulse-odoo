# InsightPulse PPM Core

**Version**: 19.0.1.0.0
**Author**: InsightPulse AI
**License**: LGPL-3

## Overview

Comprehensive Program/Project/Budget/Risk Management system for Odoo 19.0 Enterprise.

## Features

- **Program Management**: Multi-project program coordination
- **Roadmap Planning**: Gantt-based milestone tracking
- **Risk Management**: Comprehensive risk assessment and mitigation
- **Budget Tracking**: Real-time budget monitoring and utilization

## Odoo Studio Compatibility

**Studio Support**: ✅ Full customization support - Highly recommended for PPM workflows

**Safe to Customize**:
- Add custom fields (KPIs, status indicators, client tags)
- Create custom views (kanban for programs, timeline for milestones)
- Add automated actions (milestone notifications, risk alerts)
- Custom dashboards and pivot tables
- PDF report templates

**Recommended Automations**:
- Email stakeholders on program state changes
- Milestone approaching notifications (7 days before)
- Risk escalation when severity > 7
- Budget utilization alerts (>80%, >100%)
- Weekly program status reports

**Protected Fields** (DO NOT modify):
- Budget utilization calculations
- Risk scoring algorithms
- State transition logic

See [docs/STUDIO_GUIDE.md](../../../../docs/STUDIO_GUIDE.md) for PPM-specific customization patterns and dashboard examples.

## Models

- `ppm.program`: Programs with state workflow
- `ppm.roadmap`: Milestones with Gantt views
- `ppm.risk`: Risk assessment with scoring
- `ppm.budget`: Budget tracking with utilization metrics

## Security

- PPM User: Read-only access
- PPM Manager: Full CRUD access

## Dependencies

- ipai_core, project, account
