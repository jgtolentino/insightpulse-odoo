# InsightPulse Troubleshooting Guide

This comprehensive troubleshooting guide covers all services in the InsightPulse stack. Each runbook provides decision trees for rapid incident response.

## Quick Links

- [Odoo](./odoo.md) - ERP system troubleshooting
- [Supabase](./supabase.md) - Database and backend services
- [Superset](./superset.md) - Business intelligence and analytics
- [Docker](./docker.md) - Container runtime issues
- [DigitalOcean App Platform](./do.md) - Cloud infrastructure

## Using This Guide

Each runbook follows a consistent structure:

1. **Detect** - How to identify the issue (alerts, metrics, symptoms)
2. **Check** - Diagnostic steps to confirm the problem
3. **Heal** - Immediate remediation steps
4. **Verify** - How to confirm the fix worked
5. **Prevent** - Long-term guardrails to avoid recurrence

## Alert Severity Levels

- **P0 (Critical)** - Service down or severely degraded, immediate response required
- **P1 (High)** - Major functionality impaired, response within 1 hour
- **P2 (Medium)** - Degraded performance, response within 4 hours

## Getting Help

- Check error catalog: `ops/error-catalog/`
- Review Prometheus alerts: `monitoring/prometheus/alerts_*.yml`
- Run auto-heal handlers: `auto-healing/handlers/`
- Escalate to on-call: See `monitoring/alertmanager/alertmanager.yml`
