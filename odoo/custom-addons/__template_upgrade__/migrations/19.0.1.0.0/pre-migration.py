"""
Pre-migration script for module upgrade to 19.0.1.0.0

This script runs BEFORE the Odoo module is loaded.
Use it for:
- Renaming tables/columns
- Dropping obsolete constraints
- Creating temporary tables
- Data transformations that need old schema
"""

from openupgradelib import openupgrade

# Column renames: {table_name: [(old_name, new_name), ...]}
_column_renames = {
    # Example: 'res_partner': [('old_field', 'new_field')],
}

# Table renames: [(old_name, new_name), ...]
_table_renames = [
    # Example: ('old_table_name', 'new_table_name'),
]

# Model renames: [(old_name, new_name), ...]
_model_renames = [
    # Example: ('old.model.name', 'new.model.name'),
]

# Field renames: {model: [(old_name, new_name), ...]}
_field_renames = {
    # Example: 'res.partner': [('old_field', 'new_field')],
}

# XML ID renames: [(old_id, new_id), ...]
_xmlid_renames = [
    # Example: ('module.old_xml_id', 'module.new_xml_id'),
]


@openupgrade.migrate()
def migrate(env, version):
    """
    Main migration entry point.

    Args:
        env: Odoo environment
        version: Version being migrated from
    """
    cr = env.cr

    # Rename columns
    if _column_renames:
        openupgrade.rename_columns(cr, _column_renames)

    # Rename tables
    if _table_renames:
        openupgrade.rename_tables(cr, _table_renames)

    # Rename models
    if _model_renames:
        openupgrade.rename_models(cr, _model_renames)

    # Rename fields
    if _field_renames:
        openupgrade.rename_fields(env, _field_renames)

    # Rename XML IDs
    if _xmlid_renames:
        openupgrade.rename_xmlids(cr, _xmlid_renames)

    # Custom migration logic
    # Example: migrate_custom_data(env)


def migrate_custom_data(env):
    """
    Custom data migration logic.

    Example: Transform data from old format to new format
    """
    cr = env.cr

    # Example: Update boolean field from char
    # openupgrade.logged_query(
    #     cr,
    #     """
    #     UPDATE res_partner
    #     SET new_boolean_field = CASE
    #         WHEN old_char_field = 'yes' THEN TRUE
    #         ELSE FALSE
    #     END
    #     """
    # )

    pass
