# Live Module Inventory Reports

Automated snapshots of live Odoo module inventory from production system.

## Overview

This directory contains timestamped snapshots of the module registry from the live Odoo deployment at `insightpulseai.net/odoo`. Reports are generated automatically via CI/CD and can be generated manually for troubleshooting.

## Files

### CSV Reports (`live_modules_YYYY-MM-DDTHHMMZ.csv`)
Complete module inventory with fields:
- `technical_name` - Module identifier
- `name` - Human-readable name
- `author` - Module author/organization
- `website` - Source URL (GitHub, OCA, etc.)
- `latest_version` - Version string
- `state` - Installation state (installed, uninstalled, to upgrade, etc.)
- `category` - Functional category

### Markdown Summaries (`live_modules_YYYY-MM-DDTHHMMZ.md`)
Human-readable summary with:
- Total module counts by state
- Category breakdown
- Top 10 most recently updated modules
- Timestamp and source information

## Generation

### Automatic (CI/CD)
The `.github/workflows/parity-live-sync.yml` workflow runs daily at 18:00 UTC (02:00 PH time next day) to:
1. Authenticate to live Odoo instance
2. Export module registry via JSON-RPC
3. Generate CSV and Markdown reports
4. Commit to repository
5. Update `docs/ENTERPRISE_PARITY.md`

### Manual
```bash
# Set credentials (DO NOT commit these)
export ODOO_URL="https://insightpulseai.net/odoo"
export ODOO_DB="odoo_prod"
export ODOO_LOGIN="admin@example.com"
export ODOO_PASSWORD="password"

# Generate snapshot
python3 scripts/export-live-modules.py

# Sync to documentation
bash scripts/sync-live-to-docs.sh

# Commit
git add reports/ docs/ENTERPRISE_PARITY.md
git commit -m "docs(parity): manual module inventory snapshot"
```

## Security

**IMPORTANT**: Credentials are stored in GitHub Secrets and never committed to the repository. The workflow uses:
- `ODOO_URL` - Live Odoo instance URL
- `ODOO_DB` - Database name
- `ODOO_LOGIN` - Admin user email
- `ODOO_PASSWORD` - Admin password

## Retention

- CSV/Markdown files retained indefinitely in git history
- Workflow artifacts retained for 90 days
- Older snapshots can be pruned manually if needed

## Usage

### Track Enterprise Parity Progress
```bash
# Compare snapshots over time
git diff HEAD~7:reports/live_modules_*.md reports/live_modules_*.md

# Count installed modules
grep "Installed:" reports/live_modules_*.md | tail -1
```

### Module Audit
```bash
# Find all installed modules
grep "installed" reports/live_modules_latest.csv | wc -l

# List modules by category
grep "installed" reports/live_modules_latest.csv | cut -d, -f7 | sort | uniq -c
```

### Troubleshooting
```bash
# Check for broken modules
grep "uninstallable" reports/live_modules_latest.csv

# Find modules pending upgrade
grep "to upgrade" reports/live_modules_latest.csv
```

## Related Files

- `scripts/export-live-modules.py` - Python exporter script
- `scripts/sync-live-to-docs.sh` - Documentation sync script
- `.github/workflows/parity-live-sync.yml` - CI/CD workflow
- `docs/ENTERPRISE_PARITY.md` - Main parity documentation
