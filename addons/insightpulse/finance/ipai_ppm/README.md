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
