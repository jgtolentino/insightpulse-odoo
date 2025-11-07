# OpenUpgrade Migration Template

Template module for creating OpenUpgrade migration scripts in InsightPulse Odoo custom modules.

## DO NOT INSTALL IN PRODUCTION

This is a template only. Copy it to create migrations for your custom modules.

## Quick Start

### 1. Copy Template to Your Module

```bash
# Copy migration scripts to your module
cp -r odoo/custom-addons/__template_upgrade__/migrations/19.0.1.0.0 \
      odoo/custom-addons/my_custom_module/migrations/19.0.1.0.0
```

### 2. Update Migration Scripts

Edit the three migration files:

- **`pre-migration.py`** - Schema changes BEFORE module load
- **`post-migration.py`** - Data updates AFTER module load
- **`end-migration.py`** - Final cleanup and validation

### 3. Test Migration

```bash
# Run OpenUpgrade analysis
python3 scripts/openupgrade_analyze.py \
  --addons-path odoo/custom-addons \
  --module my_custom_module

# Test upgrade in staging environment
docker-compose -f docker-compose.upgrade-test.yml up -d
```

## Migration Script Structure

### Pre-Migration (before module load)

Use for schema changes that need the old structure:

```python
# Rename table columns
_column_renames = {
    'res_partner': [('old_name', 'new_name')],
}

# Rename entire tables
_table_renames = [
    ('old_table', 'new_table'),
]

# Rename models
_model_renames = [
    ('old.model', 'new.model'),
]
```

### Post-Migration (after module load)

Use for data transformations with the new schema:

```python
def migrate(env, version):
    # Fill new required fields
    fill_required_fields(env)

    # Recompute stored fields
    recompute_stored_fields(env)

    # Update security groups
    update_security_groups(env)
```

### End-Migration (final cleanup)

Use for validation and cleanup:

```python
def migrate(env, version):
    # Remove temporary columns
    remove_temporary_columns(env.cr)

    # Validate migration success
    validate_migration(env)

    # Log statistics
    log_migration_stats(env)
```

## Common Migration Patterns

### Rename Field

```python
# pre-migration.py
_field_renames = {
    'res.partner': [('old_field', 'new_field')],
}
```

### Change Field Type

```python
# pre-migration.py
def migrate(env, version):
    # Add new column with correct type
    openupgrade.add_fields(env, [
        ('new_field', 'res.partner', 'res_partner', 'integer', False, 'my_module')
    ])

    # Migrate data
    env.cr.execute("""
        UPDATE res_partner
        SET new_field = old_char_field::integer
        WHERE old_char_field ~ '^[0-9]+$'
    """)
```

### Migrate State Values

```python
# post-migration.py
state_mapping = {
    'draft': 'new',
    'confirm': 'confirmed',
    'done': 'completed',
}

for old, new in state_mapping.items():
    openupgrade.logged_query(
        env.cr,
        "UPDATE sale_order SET state = %s WHERE state = %s",
        (new, old)
    )
```

### Fill Required Fields

```python
# post-migration.py
def fill_required_fields(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_partner
        SET required_field = 'default_value'
        WHERE required_field IS NULL
        """
    )
```

## Version Numbering

Migration directories must match version upgrade paths:

```
migrations/
  19.0.1.0.0/         # Upgrade from any version to 19.0.1.0.0
    pre-migration.py
    post-migration.py
    end-migration.py
  19.0.2.0.0/         # Upgrade from 19.0.1.0.0 to 19.0.2.0.0
    post-migration.py
```

## OCA Module Migrations

For OCA community modules, check existing migrations:

```bash
# Example: Check account module migrations
git clone https://github.com/OCA/OpenUpgrade
ls OpenUpgrade/openupgrade_scripts/scripts/account/19.0.*
```

## Testing Migrations

### Local Testing

```bash
# 1. Backup database
pg_dump -h localhost -U odoo odoo_db > backup_pre_upgrade.sql

# 2. Run upgrade
docker-compose exec odoo odoo -u my_custom_module --stop-after-init

# 3. Verify results
docker-compose exec odoo odoo shell -d odoo_db
>>> env['res.partner'].search_count([])  # Check record counts
```

### CI/CD Testing

See `.github/workflows/openupgrade-test.yml` for automated upgrade testing.

## Resources

- [OpenUpgrade GitHub](https://github.com/OCA/OpenUpgrade)
- [openupgradelib API](https://github.com/OCA/openupgradelib)
- [OCA Migration Scripts](https://github.com/OCA/OpenUpgrade/tree/19.0/openupgrade_scripts)
- [Odoo Upgrade Best Practices](https://www.odoo.com/documentation/19.0/developer/howtos/upgrade.html)

## Support

For InsightPulse-specific migration help:
- Check `scripts/openupgrade_*.py` automation scripts
- Review `.github/workflows/openupgrade-test.yml` CI workflow
- See OCA module upgrade examples in `docs/OPENUPGRADE_GUIDE.md`
