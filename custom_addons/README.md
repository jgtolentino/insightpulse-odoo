# InsightPulse AI Custom Addons

This directory contains custom Odoo modules and OCA community module symlinks for the InsightPulse AI platform.

## Module Naming Convention

All custom modules follow the **`ipai_*`** namespace:

- `ipai_` prefix identifies InsightPulse AI custom modules
- Use lowercase with underscores for separators
- Choose descriptive names that indicate functionality

### Examples:
- `ipai_te_seed` - Travel & Expense seed data
- `ipai_finance_ssc` - Finance Shared Service Center
- `ipai_bir_compliance` - Philippine BIR compliance
- `ipai_mattermost_bridge` - Mattermost webhook integration

## Module Categories

### Custom IPAI Modules

| Module | Description | Status |
|--------|-------------|--------|
| `ipai_te_seed` | Travel & Expense seed data and configuration | Active |
| `ipai_mattermost_bridge` | Webhook ingestion for GitHub/Jira/ServiceNow | Active |
| `ip_expense_mvp` | Mobile expense capture + OCR + dashboard | Active (to be renamed to `ipai_expense_mvp`) |
| `ip_superset_integration` | Superset dashboard integration | Active (to be renamed to `ipai_superset_integration`) |

### Legacy/Non-Standard Modules

| Module | Description | Notes |
|--------|-------------|-------|
| `pulser_webhook` | Legacy webhook handler | Consider migrating to `ipai_*` |
| `hr_offboarding_clearance` | HR offboarding workflow | Consider `ipai_hr_offboarding` |

### OCA Community Modules (Symlinks)

| Directory | Source Repository | Purpose |
|-----------|------------------|---------|
| `account-financial-reporting` | OCA/account-financial-reporting | Financial reports |
| `hr-expense` | OCA/hr-expense | HR Expense extensions |
| `mis-builder` | OCA/mis-builder | MIS Report Builder |
| `multi-company` | OCA/multi-company | Multi-company features |
| `reporting-engine` | OCA/reporting-engine | Reporting framework |
| `server-tools` | OCA/server-tools | Server utilities |
| `server-ux` | OCA/server-ux | UX improvements |

## Directory Structure

```
custom_addons/
├── ipai_*/                    # Custom IPAI modules
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   ├── views/
│   ├── data/
│   ├── security/
│   └── README.md
├── <oca-repo-name>/          # OCA module symlinks
└── README.md                  # This file
```

## Development Guidelines

### Creating a New IPAI Module

1. **Choose a name**: `ipai_<feature_name>`
2. **Create structure**:
   ```bash
   cd custom_addons
   mkdir -p ipai_<name>/{models,views,data,security}
   ```

3. **Create required files**:
   - `__init__.py` - Module initialization
   - `__manifest__.py` - Module metadata
   - `security/ir.model.access.csv` - Access control
   - `README.md` - Documentation

4. **Follow Odoo conventions**:
   - Use OCA coding standards
   - Add proper license headers (LGPL-3)
   - Document dependencies
   - Include demo data for testing

### Installing Modules

**Via Docker (recommended for production):**
```bash
# One-shot install
NET=$(docker inspect insightpulse-db --format '{{range $k,$v := .NetworkSettings.Networks}}{{println $k}}{{end}}' | head -n1)

docker run --rm --network "$NET" \
  -v /opt/odoo/custom_addons:/mnt/extra-addons:ro \
  -e INIT=1 \
  -e HOST=insightpulse-db \
  -e USER=odoo \
  -e PASSWORD=odoo \
  -e PGDATABASE=odoo \
  -e ODOO_INSTALL="module1,module2,ipai_module_name" \
  ghcr.io/jgtolentino/odoo-18-ce:latest
```

**Via Odoo CLI (development):**
```bash
odoo -d odoo --init ipai_module_name
```

**Via Web UI:**
1. Navigate to Apps
2. Update Apps List
3. Search for module
4. Click Install

## OCA Module Management

OCA modules are managed via symlinks created by `scripts/vendor_oca_enhanced.py`:

```bash
# Vendor OCA modules
python3 scripts/vendor_oca_enhanced.py

# This creates symlinks in custom_addons/ pointing to:
# - odoo/addons/oca_<repo_name>/<module_name>
```

### Updating OCA Modules

```bash
# Update OCA repositories
cd odoo/addons
git -C oca_account-financial-reporting pull
git -C oca_mis-builder pull
# etc.

# Re-run vendoring
cd ../..
python3 scripts/vendor_oca_enhanced.py
```

## Testing

### Module Testing Checklist

- [ ] Module installs without errors
- [ ] All dependencies resolved
- [ ] Security rules working (ir.model.access.csv)
- [ ] Views render correctly
- [ ] Data files load properly
- [ ] Demo data works (if applicable)
- [ ] No Python/JavaScript errors in logs
- [ ] BIR compliance validated (for finance modules)

### Test Commands

```bash
# Check module can be loaded
odoo -d odoo -i ipai_module_name --test-enable --stop-after-init

# Run specific tests
odoo -d odoo -i ipai_module_name --test-enable --test-tags /ipai_module_name

# Check for errors
docker logs insightpulse-odoo 2>&1 | grep -i error
```

## Deployment

### Production Deployment

1. **Update repository**:
   ```bash
   cd /opt/odoo/repo
   git pull origin main
   ```

2. **Sync to server**:
   ```bash
   rsync -a /opt/odoo/repo/custom_addons/ /opt/odoo/custom_addons/
   ```

3. **Restart Odoo**:
   ```bash
   docker restart insightpulse-odoo
   ```

4. **Install/Upgrade**:
   - Via Web UI: Apps > Update Apps List > Install
   - Via CLI: One-shot install command

## Troubleshooting

### Common Issues

**Module not appearing in Apps list:**
- Check `__manifest__.py` has correct structure
- Verify `installable: True`
- Update Apps List in Web UI

**Import errors:**
- Check `__init__.py` imports
- Verify all dependencies installed
- Check Python syntax

**Access denied errors:**
- Review `security/ir.model.access.csv`
- Check user groups and permissions
- Verify record rules

**Data file errors:**
- Validate XML syntax
- Check external ID references
- Verify field names match models

## Resources

- [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- [Odoo 18 Documentation](https://www.odoo.com/documentation/18.0/)
- [InsightPulse AI Wiki](https://github.com/jgtolentino/insightpulse-odoo/wiki)

## License

All `ipai_*` modules are licensed under LGPL-3 unless otherwise specified.

OCA modules retain their original licenses (typically AGPL-3 or LGPL-3).
