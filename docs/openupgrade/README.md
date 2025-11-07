# OpenUpgrade Integration Guide

Complete guide for managing Odoo module upgrades using OpenUpgrade framework in InsightPulse.

## Overview

OpenUpgrade provides automated migration scripts for upgrading Odoo modules between major versions (e.g., 18.0 → 19.0).

**Benefits:**
- ✅ Automated database schema migrations
- ✅ OCA community-maintained migration scripts
- ✅ Pre/post-migration hooks for custom logic
- ✅ Version control for upgrade paths
- ✅ Testing framework for validating upgrades

---

## Quick Start

### 1. Analyze Your Modules

Check which modules need migrations:

```bash
# Analyze all custom modules
python3 scripts/openupgrade_analyze.py --all

# Analyze specific module
python3 scripts/openupgrade_analyze.py --module insightpulse_finance_ssc

# View report
open docs/openupgrade/analysis.html
```

### 2. Fetch OCA Migration Scripts

Download migration scripts for OCA dependencies:

```bash
# Fetch all OCA module migrations
python3 scripts/openupgrade_fetch_oca.py --all

# Fetch specific module
python3 scripts/openupgrade_fetch_oca.py --module account

# Migration scripts saved to: odoo/oca-migrations/
```

### 3. Create Custom Module Migrations

Copy template to your module:

```bash
# Copy migration template
cp -r odoo/custom-addons/__template_upgrade__/migrations/19.0.1.0.0 \
      odoo/custom-addons/my_custom_module/migrations/19.0.1.0.0

# Edit migration scripts
nano odoo/custom-addons/my_custom_module/migrations/19.0.1.0.0/pre-migration.py
nano odoo/custom-addons/my_custom_module/migrations/19.0.1.0.0/post-migration.py
```

### 4. Test Upgrade

Test your migrations in isolated environment:

```bash
# Test specific module
./scripts/openupgrade_test.sh my_custom_module 18.0 19.0

# Test all modules
./scripts/openupgrade_test.sh all 18.0 19.0

# Keep test database for inspection
KEEP_TEST_DB=1 ./scripts/openupgrade_test.sh my_custom_module
```

### 5. Run Production Upgrade

**IMPORTANT: Backup first!**

```bash
# 1. Backup production database
pg_dump -h localhost -U odoo odoo_production > backup_$(date +%Y%m%d).sql

# 2. Stop Odoo services
docker-compose stop odoo

# 3. Run OpenUpgrade
docker-compose run --rm odoo \
  odoo -d odoo_production \
  -u all \
  --stop-after-init

# 4. Verify upgrade
docker-compose up odoo
```

---

## Migration Script Structure

### Pre-Migration (`pre-migration.py`)

Runs **BEFORE** module loading. Use for schema changes:

```python
from openupgradelib import openupgrade

# Rename columns
_column_renames = {
    'res_partner': [('old_field', 'new_field')],
}

# Rename tables
_table_renames = [
    ('old_table', 'new_table'),
]

@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_tables(cr, _table_renames)
```

### Post-Migration (`post-migration.py`)

Runs **AFTER** module loading. Use for data updates:

```python
from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    # Fill new required fields
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_partner
        SET new_required_field = 'default_value'
        WHERE new_required_field IS NULL
        """
    )

    # Recompute stored fields
    partners = env['res.partner'].search([])
    partners._compute_display_name()
```

### End-Migration (`end-migration.py`)

Runs at the **END**. Use for cleanup and validation:

```python
from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    # Remove temporary columns
    openupgrade.drop_columns(
        env.cr,
        [('res_partner', 'temp_field')]
    )

    # Validate migration
    env.cr.execute("""
        SELECT COUNT(*)
        FROM res_partner
        WHERE required_field IS NULL
    """)

    if env.cr.fetchone()[0] > 0:
        raise ValueError("Migration validation failed")
```

---

## Common Migration Patterns

### Rename Field

```python
# pre-migration.py
_field_renames = {
    'res.partner': [('old_name', 'new_name')],
}

@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
```

### Change Field Type (Char → Integer)

```python
# pre-migration.py
@openupgrade.migrate()
def migrate(env, version):
    # Create new integer field
    openupgrade.add_fields(env, [
        ('new_int_field', 'res.partner', 'res_partner', 'integer', False, 'my_module')
    ])

    # Migrate valid data
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_partner
        SET new_int_field = old_char_field::integer
        WHERE old_char_field ~ '^[0-9]+$'
        """
    )
```

### Change Selection Values

```python
# post-migration.py
state_mapping = {
    'draft': 'new',
    'confirm': 'confirmed',
    'done': 'completed',
}

@openupgrade.migrate()
def migrate(env, version):
    for old_state, new_state in state_mapping.items():
        openupgrade.logged_query(
            env.cr,
            "UPDATE sale_order SET state = %s WHERE state = %s",
            (new_state, old_state)
        )
```

### Many2many Field Migration

```python
# pre-migration.py
@openupgrade.migrate()
def migrate(env, version):
    # Rename many2many table
    openupgrade.rename_tables(env.cr, [
        ('old_m2m_rel', 'new_m2m_rel')
    ])

    # Rename columns in relation table
    openupgrade.rename_columns(env.cr, {
        'new_m2m_rel': [
            ('old_id_1', 'new_id_1'),
            ('old_id_2', 'new_id_2'),
        ]
    })
```

### Delete Obsolete Data

```python
# end-migration.py
@openupgrade.migrate()
def migrate(env, version):
    # Delete obsolete XML IDs
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ['my_module.obsolete_record_1', 'my_module.obsolete_record_2']
    )

    # Delete obsolete models
    if openupgrade.table_exists(env.cr, 'obsolete_model'):
        openupgrade.logged_query(
            env.cr,
            "DROP TABLE obsolete_model CASCADE"
        )
```

---

## OCA Module Migrations

### Finding OCA Migrations

Check if OCA module has migrations:

```bash
# Example: Check account module
python3 scripts/openupgrade_fetch_oca.py --module account

# View downloaded scripts
ls odoo/oca-migrations/account/19.0.*
```

### Common OCA Modules with Migrations

| Module | Description | Migration Available |
|--------|-------------|---------------------|
| `account` | Accounting | ✅ Yes |
| `sale` | Sales Management | ✅ Yes |
| `purchase` | Purchase Management | ✅ Yes |
| `stock` | Inventory | ✅ Yes |
| `hr` | Human Resources | ✅ Yes |
| `project` | Project Management | ✅ Yes |
| `website` | Website Builder | ✅ Yes |

### Using OCA Migrations

OCA migrations are automatically applied when upgrading:

```bash
# Upgrade with OCA migrations
docker-compose run --rm odoo \
  odoo -d odoo_db \
  --addons-path /mnt/extra-addons,/mnt/oca-migrations \
  -u account,sale \
  --stop-after-init
```

---

## CI/CD Integration

### GitHub Actions Workflow

Automated upgrade testing runs on every PR:

```yaml
# .github/workflows/openupgrade-test.yml
name: OpenUpgrade Migration Test

on:
  pull_request:
    paths:
      - 'odoo/custom-addons/**'

jobs:
  test-upgrade:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Test module upgrade
        run: ./scripts/openupgrade_test.sh my_module
```

### Manual Trigger

Test specific module via GitHub Actions:

```bash
# Go to: https://github.com/jgtolentino/insightpulse-odoo/actions
# Select: OpenUpgrade Migration Test
# Click: Run workflow
# Input: module_name = my_custom_module
```

---

## Troubleshooting

### Migration Fails with "Column does not exist"

**Problem:** Pre-migration tried to access column that was already removed.

**Solution:** Check version history and adjust migration order:

```python
# Check if column exists before accessing
if openupgrade.column_exists(env.cr, 'res_partner', 'old_field'):
    # Migrate data
    pass
```

### Post-migration Fails with "Required field is NULL"

**Problem:** New required field not filled during migration.

**Solution:** Fill defaults in post-migration:

```python
# post-migration.py
openupgrade.logged_query(
    env.cr,
    """
    UPDATE res_partner
    SET required_field = COALESCE(old_field, 'default_value')
    WHERE required_field IS NULL
    """
)
```

### OCA Module Migration Not Found

**Problem:** Dependency has no OpenUpgrade migration scripts.

**Solution:** Check if module changed names or create custom migration:

```bash
# Search OpenUpgrade repo
git clone https://github.com/OCA/OpenUpgrade.git /tmp/openupgrade
find /tmp/openupgrade -name "*module_name*"

# If not found, create custom migration
cp -r odoo/custom-addons/__template_upgrade__/migrations/19.0.1.0.0 \
      odoo/custom-addons/vendor_module/migrations/19.0.1.0.0
```

### Upgrade Timeout

**Problem:** Migration takes too long and times out.

**Solution:** Increase timeout or run in batches:

```bash
# Increase timeout (10 hours)
docker-compose run --rm odoo \
  timeout 36000 odoo -d odoo_db -u my_module --stop-after-init

# Or migrate in batches
docker-compose run --rm odoo odoo -d odoo_db -u module1 --stop-after-init
docker-compose run --rm odoo odoo -d odoo_db -u module2 --stop-after-init
```

---

## Version Numbering

Follow Odoo's version scheme:

```
{odoo_version}.{module_version}

Examples:
- 19.0.1.0.0  # First version for Odoo 19
- 19.0.1.1.0  # Patch update
- 19.0.2.0.0  # Minor update requiring migration
```

Migration directory structure:

```
my_module/
  migrations/
    19.0.1.0.0/         # Upgrade from any version → 19.0.1.0.0
      pre-migration.py
      post-migration.py
    19.0.2.0.0/         # Upgrade from 19.0.1.0.0 → 19.0.2.0.0
      post-migration.py
```

---

## Best Practices

### 1. Always Backup First

```bash
# Full backup before upgrade
pg_dump -h localhost -U odoo odoo_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Test restore
gunzip < backup_*.sql.gz | psql -h localhost -U odoo odoo_test
```

### 2. Test in Staging

```bash
# 1. Clone production to staging
pg_dump -h prod -U odoo odoo_prod | psql -h staging -U odoo odoo_staging

# 2. Test upgrade
./scripts/openupgrade_test.sh all 18.0 19.0

# 3. Verify functionality
# 4. Then upgrade production
```

### 3. Use Logged Queries

Always use `openupgrade.logged_query()` for tracking:

```python
# Good
openupgrade.logged_query(
    env.cr,
    "UPDATE res_partner SET active = TRUE WHERE active IS NULL"
)

# Bad (not logged)
env.cr.execute("UPDATE res_partner SET active = TRUE")
```

### 4. Handle Missing Data

Account for edge cases:

```python
# Check for NULL before converting
openupgrade.logged_query(
    env.cr,
    """
    UPDATE sale_order
    SET amount_total = COALESCE(old_amount, 0.0)
    WHERE amount_total IS NULL
    """
)
```

### 5. Document Your Migrations

Add comments explaining complex migrations:

```python
@openupgrade.migrate()
def migrate(env, version):
    """
    Migrate payment terms from char field to many2one.

    Old structure: 'Net 30 days' (char)
    New structure: Link to account.payment.term (many2one)

    Strategy:
    1. Parse old char values
    2. Find/create matching payment terms
    3. Link to new many2one field
    """
    migrate_payment_terms(env)
```

---

## Resources

- [OpenUpgrade GitHub](https://github.com/OCA/OpenUpgrade)
- [openupgradelib API](https://github.com/OCA/openupgradelib)
- [OCA Migration Scripts](https://github.com/OCA/OpenUpgrade/tree/19.0/openupgrade_scripts)
- [Odoo Upgrade Guide](https://www.odoo.com/documentation/19.0/developer/howtos/upgrade.html)

---

## Support

For InsightPulse-specific upgrade help:

1. **Analyze modules:** `python3 scripts/openupgrade_analyze.py --all`
2. **Check CI results:** [GitHub Actions](https://github.com/jgtolentino/insightpulse-odoo/actions)
3. **Review examples:** `odoo/custom-addons/__template_upgrade__/`
4. **Ask in PR:** Tag `@jgtolentino` for review

Happy upgrading! 🚀
