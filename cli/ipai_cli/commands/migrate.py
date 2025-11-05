# -*- coding: utf-8 -*-
"""Database Migration Commands"""

import click
import subprocess
import os


@click.command()
@click.argument('action', type=click.Choice(['apply', 'status', 'rollback']))
@click.option('--file', type=click.Path(exists=True), help='Migration SQL file')
@click.option('--all', 'apply_all', is_flag=True, help='Apply all pending migrations')
@click.pass_context
def migrate(ctx, action, file, apply_all):
    """
    Manage database migrations

    \b
    Examples:
      ipai migrate apply --file packages/db/sql/00_task_bus.sql
      ipai migrate status
      ipai migrate apply --all
    """
    postgres_url = ctx.obj['POSTGRES_URL']

    if not postgres_url:
        click.echo("❌ POSTGRES_URL not configured", err=True)
        sys.exit(1)

    if action == 'apply':
        if not file and not apply_all:
            click.echo("❌ Either --file or --all is required", err=True)
            sys.exit(1)

        if file:
            _apply_migration(postgres_url, file)
        elif apply_all:
            _apply_all_migrations(postgres_url)

    elif action == 'status':
        _migration_status(postgres_url)

    elif action == 'rollback':
        if not file:
            click.echo("❌ --file is required for rollback", err=True)
            sys.exit(1)
        _rollback_migration(postgres_url, file)


def _apply_migration(postgres_url, file):
    """Apply single migration file"""
    click.echo(f"📝 Applying migration: {file}")

    cmd = ['psql', postgres_url, '-f', file]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        click.echo(f"❌ Migration failed: {result.stderr}", err=True)
        sys.exit(1)

    click.echo("✅ Migration applied successfully")
    click.echo(result.stdout)


def _apply_all_migrations(postgres_url):
    """Apply all migrations in packages/db/sql/"""
    import glob

    migration_dir = 'packages/db/sql'
    if not os.path.exists(migration_dir):
        click.echo(f"❌ Migration directory not found: {migration_dir}", err=True)
        sys.exit(1)

    files = sorted(glob.glob(f'{migration_dir}/*.sql'))

    if not files:
        click.echo("⚠️ No migration files found")
        return

    click.echo(f"📝 Found {len(files)} migration files")

    for file in files:
        _apply_migration(postgres_url, file)


def _migration_status(postgres_url):
    """Show migration status"""
    click.echo("📊 Migration Status")

    # Query for custom migration tracking table if exists
    query = """
    SELECT
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
    FROM pg_tables
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    ORDER BY schemaname, tablename;
    """

    cmd = ['psql', postgres_url, '-c', query]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        click.echo(result.stdout)
    else:
        click.echo(f"❌ Query failed: {result.stderr}", err=True)


def _rollback_migration(postgres_url, file):
    """Rollback migration (if rollback script exists)"""
    rollback_file = file.replace('.sql', '_rollback.sql')

    if not os.path.exists(rollback_file):
        click.echo(f"❌ Rollback file not found: {rollback_file}", err=True)
        sys.exit(1)

    click.echo(f"⏪ Rolling back migration: {rollback_file}")

    cmd = ['psql', postgres_url, '-f', rollback_file]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        click.echo(f"❌ Rollback failed: {result.stderr}", err=True)
        sys.exit(1)

    click.echo("✅ Rollback completed successfully")
