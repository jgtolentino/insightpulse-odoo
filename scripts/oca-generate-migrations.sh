#!/usr/bin/env bash
# OpenUpgrade Migration Preparation
# Purpose: Generate migration scripts for Odoo version upgrades
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OPENUPGRADELIB="$REPO_ROOT/.oca-tools/openupgradelib"
ADDONS_DIR="$REPO_ROOT/apps/odoo/addons"
FROM_VERSION="${1:-17.0}"
TO_VERSION="${2:-18.0}"

if [ ! -d "$OPENUPGRADELIB" ]; then
  echo "❌ openupgradelib not installed. Run: ./scripts/install-oca-tools.sh"
  exit 1
fi

echo "🔄 OpenUpgrade Migration Prep"
echo "   From: Odoo $FROM_VERSION"
echo "   To:   Odoo $TO_VERSION"
echo ""

# Create migrations directory structure
MIGRATIONS_ROOT="$REPO_ROOT/migrations"
mkdir -p "$MIGRATIONS_ROOT/$TO_VERSION"

echo "📁 Creating migration structure..."

# For each module, create migration scripts
for manifest in $(find "$ADDONS_DIR" -name __manifest__.py); do
  module_dir=$(dirname "$manifest")
  module_name=$(basename "$module_dir")
  migration_dir="$module_dir/migrations/$TO_VERSION"

  # Check if module needs migration
  version=$(python3 -c "
import ast
manifest = ast.literal_eval(open('$manifest').read())
print(manifest.get('version', '0.0.0.0.0'))
" 2>/dev/null)

  # Only create migration for modules with correct version format
  if [[ ! "$version" =~ ^${TO_VERSION//./\\.} ]]; then
    echo "⚠️ Skipping $module_name (version: $version, needs update to $TO_VERSION.x.y.z)"
    continue
  fi

  echo "📦 $module_name"

  # Create migration directory
  mkdir -p "$migration_dir"

  # 1. pre-migration.py (runs before module update)
  if [ ! -f "$migration_dir/pre-migration.py" ]; then
    cat > "$migration_dir/pre-migration.py" <<PREMIGRATION
# Copyright $(date +%Y) Jake Tolentino <jake@insightpulseai.net>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Pre-migration script for $module_name to Odoo $TO_VERSION."""
    cr = env.cr

    # Example: Rename fields
    # openupgrade.rename_fields(
    #     env, [("${module_name}", "${module_name}", "old_field", "new_field")]
    # )

    # Example: Rename models
    # openupgrade.rename_models(
    #     cr, [("old.model.name", "new.model.name")]
    # )

    # Example: Rename tables
    # openupgrade.rename_tables(
    #     cr, [("old_table_name", "new_table_name")]
    # )

    # Example: Drop constraints before migration
    # openupgrade.drop_constraint(
    #     cr, "${module_name}_table", "constraint_name"
    # )

    openupgrade.logged_query(
        cr,
        """
        -- Add pre-migration SQL here
        -- Example: ALTER TABLE ${module_name} ADD COLUMN IF NOT EXISTS new_field VARCHAR;
        """
    )
PREMIGRATION
    echo "   ✅ Created pre-migration.py"
  fi

  # 2. post-migration.py (runs after module update)
  if [ ! -f "$migration_dir/post-migration.py" ]; then
    cat > "$migration_dir/post-migration.py" <<POSTMIGRATION
# Copyright $(date +%Y) Jake Tolentino <jake@insightpulseai.net>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Post-migration script for $module_name to Odoo $TO_VERSION."""
    cr = env.cr

    # Example: Migrate data
    # openupgrade.logged_query(
    #     cr,
    #     """
    #     UPDATE ${module_name}
    #     SET new_field = old_field
    #     WHERE old_field IS NOT NULL;
    #     """
    # )

    # Example: Update records
    # records = env["${module_name}"].search([])
    # for record in records:
    #     record.write({"new_field": record.old_field})

    # Example: Rebuild database indexes
    # openupgrade.logged_query(
    #     cr,
    #     """
    #     CREATE INDEX IF NOT EXISTS ${module_name}_new_field_idx
    #     ON ${module_name} (new_field);
    #     """
    # )

    # Example: Clean up old data
    # openupgrade.drop_columns(
    #     cr, [("${module_name}_table", "obsolete_column")]
    # )
POSTMIGRATION
    echo "   ✅ Created post-migration.py"
  fi

  # 3. end-migration.py (final cleanup)
  if [ ! -f "$migration_dir/end-migration.py" ]; then
    cat > "$migration_dir/end-migration.py" <<ENDMIGRATION
# Copyright $(date +%Y) Jake Tolentino <jake@insightpulseai.net>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """End-migration script for $module_name to Odoo $TO_VERSION."""
    # Final cleanup, logging, notifications
    openupgrade.load_data(
        env.cr, "${module_name}", "migrations/$TO_VERSION/noupdate_changes.xml"
    )
ENDMIGRATION
    echo "   ✅ Created end-migration.py"
  fi

  # 4. Create analysis file
  cat > "$migration_dir/upgrade_analysis.txt" <<ANALYSIS
# OpenUpgrade Analysis for $module_name ($FROM_VERSION → $TO_VERSION)
# Generated: $(date -u +%Y-%m-%d)

## Models Changed
- [ ] TODO: List models that need migration

## Fields Changed
- [ ] TODO: List field renames/type changes

## Views Changed
- [ ] TODO: List view updates needed

## Data Migration Required
- [ ] TODO: Describe data migration steps

## Breaking Changes
- [ ] TODO: List any breaking API changes

## Testing Checklist
- [ ] Unit tests updated
- [ ] Integration tests pass
- [ ] Manual smoke test completed
- [ ] Performance validated
- [ ] Rollback tested

## References
- OpenUpgrade docs: https://github.com/OCA/OpenUpgrade
- Odoo $TO_VERSION release notes: https://www.odoo.com/documentation/$TO_VERSION/
ANALYSIS
  echo "   📝 Created upgrade_analysis.txt"
  echo ""
done

# Create global migration helper
cat > "$MIGRATIONS_ROOT/$TO_VERSION/README.md" <<README
# Odoo $FROM_VERSION → $TO_VERSION Migration

**Generated:** $(date -u +%Y-%m-%d)

## Pre-Migration Checklist

- [ ] Full database backup created
- [ ] Staging environment tested
- [ ] All addons analyzed (see module-specific upgrade_analysis.txt)
- [ ] Dependencies verified compatible with $TO_VERSION
- [ ] Rollback plan documented

## Migration Steps

1. **Backup Database**
   \`\`\`bash
   pg_dump -Fc odoo_prod > backup_pre_upgrade_\$(date +%Y%m%d).dump
   \`\`\`

2. **Update Odoo Core**
   \`\`\`bash
   cd apps/odoo
   git fetch origin
   git checkout $TO_VERSION
   pip install -r requirements.txt
   \`\`\`

3. **Update OCA Modules**
   \`\`\`bash
   ./scripts/oca-update-deps.sh update
   \`\`\`

4. **Run OpenUpgrade**
   \`\`\`bash
   ./apps/odoo/odoo-bin -d odoo_prod -u all --stop-after-init
   \`\`\`

5. **Verify Migration**
   \`\`\`bash
   ./scripts/validate-all.sh
   pytest tests/ -v
   \`\`\`

## Rollback Plan

If migration fails:

1. Stop Odoo service
2. Restore database:
   \`\`\`bash
   pg_restore -d odoo_prod -c backup_pre_upgrade_*.dump
   \`\`\`
3. Revert to Odoo $FROM_VERSION
4. Restart service

## Support Resources

- OpenUpgrade Matrix Chat: #openupgrade:matrix.org
- OCA Mailing List: community@odoo-community.org
- InsightPulse AI Support: support@insightpulseai.net
README

echo "✅ Migration structure created"
echo ""
echo "📍 Migrations location: $MIGRATIONS_ROOT/$TO_VERSION"
echo ""
echo "📝 Next steps:"
echo "   1. Review each module's upgrade_analysis.txt"
echo "   2. Implement migration logic in pre/post-migration.py"
echo "   3. Test on staging: ./apps/odoo/odoo-bin -d staging -u all --test-enable"
echo "   4. Create database backup before production migration"
echo ""
echo "📚 Resources:"
echo "   - OpenUpgrade Guide: https://github.com/OCA/OpenUpgrade/wiki"
echo "   - openupgradelib API: https://github.com/OCA/openupgradelib"
echo ""
