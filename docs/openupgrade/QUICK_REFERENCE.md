# OpenUpgrade Quick Reference

Cheat sheet for common OpenUpgrade operations in InsightPulse.

## Analysis Commands

```bash
# Analyze all custom modules
python3 scripts/openupgrade_analyze.py --all

# Analyze specific module
python3 scripts/openupgrade_analyze.py --module insightpulse_finance_ssc

# View HTML report
open docs/openupgrade/analysis.html
```

## Fetch OCA Migrations

```bash
# Download all OCA dependencies
python3 scripts/openupgrade_fetch_oca.py --all

# Download specific module
python3 scripts/openupgrade_fetch_oca.py --module account

# Force re-download
python3 scripts/openupgrade_fetch_oca.py --module sale --force
```

## Create Migration Scripts

```bash
# Copy template
cp -r odoo/custom-addons/__template_upgrade__/migrations/19.0.1.0.0 \
      odoo/custom-addons/MY_MODULE/migrations/19.0.1.0.0

# Edit scripts
nano odoo/custom-addons/MY_MODULE/migrations/19.0.1.0.0/pre-migration.py
nano odoo/custom-addons/MY_MODULE/migrations/19.0.1.0.0/post-migration.py
nano odoo/custom-addons/MY_MODULE/migrations/19.0.1.0.0/end-migration.py
```

## Test Migrations

```bash
# Test single module
./scripts/openupgrade_test.sh MY_MODULE 18.0 19.0

# Test all modules
./scripts/openupgrade_test.sh all 18.0 19.0

# Keep test DB for inspection
KEEP_TEST_DB=1 ./scripts/openupgrade_test.sh MY_MODULE
```

## Production Upgrade

```bash
# 1. Backup
pg_dump -h localhost -U odoo odoo_prod > backup_$(date +%Y%m%d).sql

# 2. Stop Odoo
docker-compose stop odoo

# 3. Upgrade
docker-compose run --rm odoo \
  odoo -d odoo_prod -u all --stop-after-init

# 4. Start
docker-compose up -d odoo
```

## Common openupgradelib Functions

### Schema Changes (pre-migration)

```python
from openupgradelib import openupgrade

# Rename columns
openupgrade.rename_columns(cr, {
    'res_partner': [('old_name', 'new_name')]
})

# Rename tables
openupgrade.rename_tables(cr, [
    ('old_table', 'new_table')
])

# Rename models
openupgrade.rename_models(cr, [
    ('old.model', 'new.model')
])

# Rename fields
openupgrade.rename_fields(env, {
    'res.partner': [('old_field', 'new_field')]
})

# Add columns
openupgrade.add_fields(env, [
    ('new_field', 'res.partner', 'res_partner', 'integer', False, 'module_name')
])

# Check if column exists
if openupgrade.column_exists(cr, 'res_partner', 'old_field'):
    # Migrate...
```

### Data Updates (post-migration)

```python
# Safe UPDATE query
openupgrade.logged_query(
    cr,
    """
    UPDATE res_partner
    SET new_field = old_field
    WHERE new_field IS NULL
    """
)

# Map values
openupgrade.map_values(
    cr,
    openupgrade.get_legacy_name('state'),
    'state',
    [('draft', 'new'), ('confirm', 'confirmed')],
    table='sale_order'
)

# Delete records safely
openupgrade.delete_records_safely_by_xml_id(
    env,
    ['module.obsolete_record']
)
```

### Cleanup (end-migration)

```python
# Drop columns
openupgrade.drop_columns(cr, [
    ('res_partner', 'old_field')
])

# Check table exists
if openupgrade.table_exists(cr, 'obsolete_table'):
    cr.execute("DROP TABLE obsolete_table")
```

## Version Patterns

```
{odoo_version}.{major}.{minor}.{patch}.{fix}

19.0.1.0.0  # First release for Odoo 19
19.0.1.1.0  # Patch (no migration needed)
19.0.2.0.0  # Minor (migration required)
```

## Migration Directory Structure

```
my_module/
├── __manifest__.py (version: 19.0.2.0.0)
├── migrations/
│   ├── 19.0.1.0.0/
│   │   ├── pre-migration.py
│   │   └── post-migration.py
│   └── 19.0.2.0.0/
│       ├── pre-migration.py
│       ├── post-migration.py
│       └── end-migration.py
```

## CI/CD Workflow

### Automatic Testing

Every PR automatically tests upgrades:
- `.github/workflows/openupgrade-test.yml`

### Manual Testing

```bash
# Via GitHub Actions
gh workflow run openupgrade-test.yml \
  -f module_name=my_module \
  -f from_version=18.0 \
  -f to_version=19.0
```

## Troubleshooting

### Check logs

```bash
# View upgrade logs
docker-compose logs odoo | grep -i "openupgrade"

# Check specific migration
docker-compose exec odoo cat /var/log/odoo/odoo.log | grep "my_module"
```

### Rollback

```bash
# Stop Odoo
docker-compose stop odoo

# Restore backup
gunzip < backup.sql.gz | psql -h localhost -U odoo odoo_prod

# Start Odoo
docker-compose up -d odoo
```

### Debug migration

```python
# Add debug logging in migration script
import logging
_logger = logging.getLogger(__name__)

@openupgrade.migrate()
def migrate(env, version):
    _logger.info("Starting migration from %s", version)
    # ...
    _logger.info("Migration completed successfully")
```

## openupgradelib API Reference

| Function | Usage | Phase |
|----------|-------|-------|
| `rename_columns()` | Rename DB columns | pre |
| `rename_tables()` | Rename DB tables | pre |
| `rename_models()` | Rename ir.model records | pre |
| `rename_fields()` | Rename fields in ir.model.fields | pre |
| `rename_xmlids()` | Rename XML IDs | pre |
| `add_fields()` | Add new columns | pre |
| `logged_query()` | Execute SQL with logging | any |
| `map_values()` | Map old values to new | post |
| `delete_records_safely_by_xml_id()` | Delete records | end |
| `drop_columns()` | Drop columns | end |
| `column_exists()` | Check column exists | any |
| `table_exists()` | Check table exists | any |

## File Locations

```
insightpulse-odoo/
├── odoo/custom-addons/
│   └── __template_upgrade__/        # Migration template
├── odoo/oca-migrations/             # Downloaded OCA migrations
├── scripts/
│   ├── openupgrade_analyze.py       # Analysis tool
│   ├── openupgrade_fetch_oca.py     # OCA downloader
│   └── openupgrade_test.sh          # Test script
├── docs/openupgrade/
│   ├── README.md                    # Full guide
│   ├── QUICK_REFERENCE.md           # This file
│   └── analysis.html                # Analysis report
└── .github/workflows/
    └── openupgrade-test.yml         # CI/CD workflow
```

## Support

- Full Guide: `docs/openupgrade/README.md`
- Template: `odoo/custom-addons/__template_upgrade__/`
- CI Results: [GitHub Actions](https://github.com/jgtolentino/insightpulse-odoo/actions)
