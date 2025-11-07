"""
Post-migration script for module upgrade to 19.0.1.0.0

This script runs AFTER the Odoo module is loaded.
Use it for:
- Filling new required fields
- Recomputing stored fields
- Updating ir.model.data records
- Calling module methods
- Data cleanup
"""

from openupgradelib import openupgrade

# Default values for new required fields
_field_defaults = {
    # Example: ('res.partner', 'new_required_field', 'default_value'),
}


@openupgrade.migrate()
def migrate(env, version):
    """
    Main post-migration entry point.

    Args:
        env: Odoo environment
        version: Version being migrated from
    """
    cr = env.cr

    # Fill new required fields with defaults
    fill_required_fields(env)

    # Recompute stored fields
    recompute_stored_fields(env)

    # Custom post-migration logic
    # Example: update_security_groups(env)
    # Example: migrate_workflow_data(env)


def fill_required_fields(env):
    """
    Fill new required fields with default values.
    """
    for model_name, field_name, default_value in _field_defaults:
        if model_name in env:
            model = env[model_name]
            field = model._fields.get(field_name)

            if field and field.required:
                # Check if field is empty
                records = model.search([(field_name, '=', False)])

                if records:
                    openupgrade.logged_query(
                        env.cr,
                        f"""
                        UPDATE {model._table}
                        SET {field_name} = %s
                        WHERE {field_name} IS NULL
                        """,
                        (default_value,)
                    )


def recompute_stored_fields(env):
    """
    Recompute stored computed fields that depend on renamed fields.
    """
    # Example: Recompute partner display_name
    # if 'res.partner' in env:
    #     partners = env['res.partner'].search([])
    #     partners._compute_display_name()

    pass


def update_security_groups(env):
    """
    Update security groups and access rights after module changes.
    """
    # Example: Add new groups to existing users
    # new_group = env.ref('module_name.group_new_feature')
    # admin_group = env.ref('base.group_system')
    # admin_users = env['res.users'].search([('groups_id', 'in', admin_group.id)])
    # admin_users.write({'groups_id': [(4, new_group.id)]})

    pass


def migrate_workflow_data(env):
    """
    Migrate workflow/state data if state fields changed.
    """
    # Example: Map old states to new states
    # state_mapping = {
    #     'draft': 'new',
    #     'confirm': 'confirmed',
    #     'done': 'completed',
    # }
    #
    # for old_state, new_state in state_mapping.items():
    #     openupgrade.logged_query(
    #         env.cr,
    #         """
    #         UPDATE sale_order
    #         SET state = %s
    #         WHERE state = %s
    #         """,
    #         (new_state, old_state)
    #     )

    pass


def cleanup_obsolete_data(env):
    """
    Clean up obsolete records, attachments, or data.
    """
    # Example: Remove obsolete ir.model.data records
    # openupgrade.delete_records_safely_by_xml_id(
    #     env,
    #     ['module_name.obsolete_record_1', 'module_name.obsolete_record_2']
    # )

    pass
