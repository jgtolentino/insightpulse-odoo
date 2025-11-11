# Validation Reports

This directory contains comprehensive validation reports for the InsightPulse AI Odoo stack.

## Quick Start

Run the complete validation suite:
```bash
make validate
```

Or run individual checks:
```bash
make hc       # Health check
make routing  # Routing validation
make oauth    # OAuth validation
make report   # Show status report
```

## Reports

### VALIDATION_REPORT.md
**Comprehensive validation report** covering:
- Container health and networking
- HTTP/HTTPS routing
- Database connectivity
- OAuth/SSO provider configuration
- Branding and URL configuration
- Security validation
- Performance metrics

### FINAL_STATUS.md
**Quick status summary** with:
- Overall validation status
- What's working now
- Open items and priorities
- Quick re-run commands

## Validation Scripts

Located in `scripts/` directory:

### healthcheck.sh
Complete stack health validation:
- Container status (all 10 containers)
- Port accessibility (8069, 80, 8080, 8065, 5678)
- HTTPS accessibility
- Database presence and connectivity
- OAuth provider configuration
- Company branding verification
- Base URL configuration
- Log accessibility

**Usage:**
```bash
bash scripts/healthcheck.sh
```

**Exit Code:**
- 0: All checks passed
- 1: One or more checks failed

### validate_routing.sh
URL and endpoint testing:
- Root path (/)
- Login page (/web/login)
- OAuth endpoints
- HTTP status codes
- Redirect validation

**Usage:**
```bash
bash scripts/validate_routing.sh
```

### validate_oauth.sh
OAuth provider verification:
- Provider enablement status
- Button text correctness
- Redirect URI configuration
- Keycloak client configuration
- Google OAuth setup

**Usage:**
```bash
bash scripts/validate_oauth.sh
```

## Validation Criteria

### ✅ Pass Criteria
- All containers running and healthy
- Ports accessible (8069, 80, etc.)
- HTTPS accessible at https://erp.insightpulseai.net
- Database "insightpulse" present and queryable
- 3 OAuth providers enabled (Keycloak SSO, Google, Odoo.com)
- Company branding set to "InsightPulse AI"
- Base URL configured as HTTPS
- OAuth buttons displaying correct text

### ❌ Fail Criteria
- Any container down or unhealthy
- Ports not accessible
- HTTPS connection fails
- Database missing or inaccessible
- OAuth providers not configured
- Branding not applied
- Base URL still HTTP

## Production Readiness Checklist

Current Status: **95% Production Ready**

### ✅ Completed
- [x] Container orchestration
- [x] HTTPS configuration
- [x] Database setup
- [x] OAuth/SSO providers
- [x] Company branding
- [x] URL routing
- [x] Security basics

### ⏳ Pending
- [ ] Keycloak SSL certificate (HIGH PRIORITY - 45 min)
- [ ] SMTP/Email configuration (HIGH PRIORITY - 1 hour)
- [ ] Superset deployment fix (MEDIUM - 1-2 hours)

## Running Validations in CI/CD

Add to `.github/workflows/validate.yml`:
```yaml
name: Stack Validation

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Health Check
        run: bash scripts/healthcheck.sh
        
      - name: Routing Validation
        run: bash scripts/validate_routing.sh
        
      - name: OAuth Validation
        run: bash scripts/validate_oauth.sh
        
      - name: Generate Report
        if: always()
        run: |
          echo "## Validation Report" >> $GITHUB_STEP_SUMMARY
          cat docs/reports/FINAL_STATUS.md >> $GITHUB_STEP_SUMMARY
```

## Troubleshooting

### Health Check Fails
1. Check container status: `docker ps`
2. Check logs: `docker logs odoo19`
3. Restart containers: `docker restart odoo19`

### Routing Fails
1. Check Nginx config
2. Verify DNS resolution
3. Check firewall rules

### OAuth Fails
1. Verify Keycloak is running
2. Check OAuth provider configuration in database
3. Verify redirect URIs in Keycloak admin console

## Validation History

| Date | Status | Notes |
|------|--------|-------|
| 2025-11-12 00:30 UTC | ✅ PASSED | Initial validation after OAuth configuration |

## Next Steps

After all validations pass:
1. Install Keycloak SSL certificate
2. Configure SMTP settings
3. Fix Superset deployment
4. Schedule regular validation runs
5. Set up monitoring and alerting

## Contact

For validation issues or questions:
- Documentation: https://docs.insightpulseai.net
- Issues: Check `docs/reports/VALIDATION_REPORT.md` for detailed diagnostics
