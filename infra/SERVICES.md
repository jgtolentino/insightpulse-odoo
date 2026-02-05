# Services Inventory & Health Monitoring

Single Source of Truth (SSOT) for all InsightPulseAI deployed services, apps, and URLs with automated health checking.

## Overview

The services inventory provides:
- **Canonical service definitions** in `infra/services.yaml`
- **Automated health checks** via `scripts/health_check_services.sh`
- **CI/CD monitoring** via `.github/workflows/health-check.yml`
- **DNS and TLS validation**
- **Incident alerting**

## Services Inventory (SSOT)

Location: `infra/services.yaml`

### Service Categories

1. **Core Infrastructure**
   - Root Website (`insightpulseai.com`)
   - Auth Gateway (`auth.insightpulseai.com`)

2. **ERP & Business Apps**
   - Odoo ERP (`erp.insightpulseai.com`)

3. **Automation & Orchestration**
   - n8n Workflows (`n8n.insightpulseai.com`)
   - MCP Hub (`mcp.insightpulseai.com`)

4. **Analytics & BI**
   - Apache Superset (`superset.insightpulseai.com`)

5. **Data Platform**
   - Supabase (managed external service)

6. **Email & Communications**
   - Mailgun (`mg.insightpulseai.com`)
   - Zoho Mail (mailboxes)

7. **Frontend Apps** (planned)
   - Scout Dashboard (`scout.insightpulseai.com`)
   - CES Intelligence (`ces.insightpulseai.com`)

## Health Check Automation

### Manual Execution

```bash
# Run health check
bash scripts/health_check_services.sh

# Output:
# ✓ Root Website - 200 OK (0.234s)
# ✓ Auth Gateway - 403 OK (0.456s)
# ✓ Odoo ERP - 303 OK (1.123s)
# ...
# Summary: 6 passed, 0 warnings, 0 failed
```

### Automated Monitoring

Health checks run automatically:
- **Every 30 minutes** via GitHub Actions
- **On service config changes** (push to `infra/services.yaml`)
- **On demand** via workflow dispatch

### GitHub Actions Workflow

Location: `.github/workflows/health-check.yml`

Features:
- Runs health check script
- Creates incident issues on failure
- Supports manual triggers
- Continuous monitoring

## Service Configuration

### Adding a New Service

Edit `infra/services.yaml`:

```yaml
services:
  your_category:
    - name: "Your Service"
      url: "https://your-service.insightpulseai.com"
      type: "web"  # web, api, app, automation, bi, auth, etc.
      criticality: "high"  # critical, high, medium, low
      health_check:
        method: "GET"
        expected_status: [200, 301]
        timeout: 10
      owner: "team-name"
      description: "Service description"
      runtime: "digitalocean"  # or vercel, supabase-managed, etc.
```

### Criticality Levels

- **Critical**: Core services (auth, ERP, data platform)
  - Downtime requires immediate response
  - 24/7 monitoring
  - Page on-call team

- **High**: Important services (automation, analytics)
  - Downtime requires timely response
  - Business hours monitoring
  - Notify team

- **Medium**: Nice-to-have services
  - Downtime acceptable
  - Monitor for trends

- **Low**: Development/staging services
  - Informational only

## DNS & TLS Management

### DNS Provider

- **Primary**: DigitalOcean DNS
- **Records**: Managed via Terraform or doctl CLI
- **Validation**: Automated via health check script

### SSL Certificates

- **Provider**: Let's Encrypt
- **Renewal**: Automatic
- **Monitoring**: Certificate expiry checks in health script

### DNS Configuration

Example A/CNAME records:

```
insightpulseai.com          → A     <ip-address>
auth.insightpulseai.com     → A     <ip-address>
erp.insightpulseai.com      → A     <droplet-ip>
n8n.insightpulseai.com      → A     <droplet-ip>
mcp.insightpulseai.com      → A     <droplet-ip>
superset.insightpulseai.com → A     <droplet-ip>
```

## Deployment Targets

### DigitalOcean Droplets

| Droplet | Services | Size | Region |
|---------|----------|------|--------|
| erp-prod | Odoo ERP | s-4vcpu-8gb | sgp1 |
| automation-prod | n8n, MCP Hub | s-2vcpu-4gb | sgp1 |
| analytics-prod | Superset | s-2vcpu-4gb | sgp1 |

### Vercel Projects

| Project | Domain | Framework |
|---------|--------|-----------|
| insightpulse-landing | insightpulseai.com | Next.js |

### Supabase Projects

| Project | Region | Plan |
|---------|--------|------|
| insightpulse-prod | Singapore | Pro |

## Monitoring & Alerting

### Health Check Cadence

- **Production services**: Every 30 minutes
- **Critical services**: Additional monitoring via UptimeRobot
- **SSL certificates**: Daily expiry checks

### Alerting Channels

1. **Slack** (immediate)
   - Critical failures
   - SSL expiry warnings

2. **Email** (ops@insightpulseai.com)
   - Daily health summary
   - Weekly trends

3. **GitHub Issues** (tracking)
   - Auto-created on repeated failures
   - Labeled `incident`, `automated`

### Response SLAs

| Criticality | Response Time | Resolution Target |
|-------------|---------------|-------------------|
| Critical | < 15 minutes | < 1 hour |
| High | < 1 hour | < 4 hours |
| Medium | < 4 hours | < 1 day |
| Low | Best effort | N/A |

## Integration with CI/CD

### Pre-Deployment Validation

```yaml
# .github/workflows/deploy.yml
jobs:
  pre-deploy:
    steps:
      - name: Health check before deploy
        run: bash scripts/health_check_services.sh
```

### Post-Deployment Verification

```bash
# After deployment
bash scripts/health_check_services.sh

# Verify specific service
curl -sS -o /dev/null -w "%{http_code}" https://erp.insightpulseai.com
```

### Rollback Triggers

Automatic rollback if:
- Critical service health check fails post-deployment
- Response time exceeds 5s for 3 consecutive checks
- SSL certificate invalid

## Maintenance Windows

### Production Deployments

- **Allowed**: Mon-Thu 10:00-16:00 SGT
- **Forbidden**: Fri-Sun, public holidays
- **Emergency**: Any time with approval

### Scheduled Maintenance

- **Window**: Saturday 02:00-06:00 SGT
- **Notification**: 48 hours advance
- **Status page**: Update during maintenance

## Troubleshooting

### Service Unreachable

```bash
# Check DNS
dig +short A erp.insightpulseai.com

# Check SSL
echo | openssl s_client -connect erp.insightpulseai.com:443

# Check HTTP
curl -I https://erp.insightpulseai.com
```

### Health Check False Positives

Adjust expected status codes in `infra/services.yaml`:

```yaml
health_check:
  expected_status: [200, 301, 302, 303]  # Add more as needed
```

### Adding Custom Health Checks

Extend `scripts/health_check_services.sh`:

```bash
# Custom check example
if curl -sS https://erp.insightpulseai.com/web/health | grep -q "ok"; then
  echo "✓ Custom health endpoint OK"
fi
```

## Governance

### Change Management

1. **Propose**: Edit `infra/services.yaml`
2. **Review**: PR review by platform team
3. **Approve**: Requires 1 approval
4. **Deploy**: Merge triggers health check validation
5. **Monitor**: Verify health checks pass

### Service Ownership

Each service has an `owner` field:
- Responsible for availability
- Notified on failures
- Approves changes

### Documentation

Update these docs when:
- Adding/removing services
- Changing criticality levels
- Modifying health check logic
- Updating DNS configuration

## Related Documentation

- [MONOREPO_STRUCTURE.md](../MONOREPO_STRUCTURE.md) - Repository layout
- [Deployment Guide](../DEPLOYMENT_GUIDE.md) - Deployment procedures
- [Runbooks](../docs/runbooks/) - Incident response procedures
- [Architecture](../ARCHITECTURE.md) - System architecture

## Future Enhancements

- [ ] Synthetic monitoring (Selenium/Playwright)
- [ ] Performance metrics (response times, throughput)
- [ ] Geographic health checks (multi-region)
- [ ] Status page generation (automated)
- [ ] Terraform integration for DNS
- [ ] APM integration (Sentry, Datadog)
