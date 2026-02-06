#!/usr/bin/env python3
"""
InsightPulse Database Upgrader
===============================

Comprehensive database migration tool for:
- Supabase schema migrations (superset, ops, analytics, ai)
- Superset dashboard initialization
- Sample data installation
- App installation workflow
- Rollback capabilities

Usage:
    python3 scripts/db_upgrader.py upgrade --env production
    python3 scripts/db_upgrader.py install-sample-data --schema all
    python3 scripts/db_upgrader.py rollback --to-version 002
    python3 scripts/db_upgrader.py status
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================

ROOT_DIR = Path(__file__).parent.parent
MIGRATIONS_DIR = ROOT_DIR / "supabase" / "migrations"
SUPERSET_DATASETS_DIR = ROOT_DIR / "superset" / "datasets"
SAMPLE_DATA_DIR = ROOT_DIR / "scripts" / "sample_data"
PACKAGES_DB_DIR = ROOT_DIR / "packages" / "db" / "sql"

# Schema definitions
SCHEMAS = {
    "superset": "Apache Superset metadata tables (dashboards, charts, datasets)",
    "ops": "InsightPulse application operations data",
    "analytics": "Data warehouse analytics views and materialized views",
    "ai": "AI training data, embeddings, and model metadata",
    "scout_bronze": "Raw ingestion layer (ELT bronze)",
    "scout_silver": "Cleaned and validated data (ELT silver)",
    "scout_gold": "Business metrics and aggregates (ELT gold)",
}

# Migration version tracking table
VERSION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS public.schema_version (
    version TEXT PRIMARY KEY,
    description TEXT,
    migration_file TEXT NOT NULL,
    checksum TEXT NOT NULL,
    installed_by TEXT DEFAULT CURRENT_USER,
    installed_at TIMESTAMPTZ DEFAULT NOW(),
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_schema_version_installed_at
    ON public.schema_version(installed_at DESC);

COMMENT ON TABLE public.schema_version IS
    'Migration version tracking - similar to Flyway/Liquibase';
"""


# ============================================================================
# DATABASE CONNECTION
# ============================================================================


def get_db_connection(env: str = "development") -> psycopg2.extensions.connection:
    """
    Get database connection from environment variables.

    Environment variables:
        POSTGRES_URL: Full connection string (preferred)
        SUPABASE_DB_URL: Supabase pooler URL
        DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD: Individual components
    """
    # Try POSTGRES_URL first
    conn_string = os.getenv("POSTGRES_URL")

    # Try SUPABASE_DB_URL
    if not conn_string:
        conn_string = os.getenv("SUPABASE_DB_URL")

    # Build from components
    if not conn_string:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        dbname = os.getenv("DB_NAME", "postgres")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "")

        conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    # Add SSL mode if production
    if env == "production" and "sslmode" not in conn_string:
        conn_string += "?sslmode=require"

    try:
        conn = psycopg2.connect(conn_string)
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print(
            f"Connection string pattern: {conn_string.split('@')[1] if '@' in conn_string else 'invalid'}"
        )
        sys.exit(1)


# ============================================================================
# MIGRATION TRACKING
# ============================================================================


def init_version_table(conn: psycopg2.extensions.connection):
    """Initialize schema_version tracking table."""
    with conn.cursor() as cur:
        cur.execute(VERSION_TABLE_SQL)
    conn.commit()
    print("✅ Version tracking table initialized")


def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of migration file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        sha256.update(f.read())
    return sha256.hexdigest()


def get_applied_versions(conn: psycopg2.extensions.connection) -> Dict[str, Dict]:
    """Get list of applied migration versions."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT version, description, migration_file, checksum,
                   installed_at, execution_time_ms, success
            FROM public.schema_version
            ORDER BY installed_at ASC
        """)

        return {
            row[0]: {
                "description": row[1],
                "migration_file": row[2],
                "checksum": row[3],
                "installed_at": row[4],
                "execution_time_ms": row[5],
                "success": row[6],
            }
            for row in cur.fetchall()
        }


def record_migration(
    conn: psycopg2.extensions.connection,
    version: str,
    description: str,
    migration_file: str,
    checksum: str,
    execution_time_ms: int,
    success: bool = True,
):
    """Record migration execution in version table."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.schema_version
                (version, description, migration_file, checksum, execution_time_ms, success)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (version) DO UPDATE SET
                checksum = EXCLUDED.checksum,
                execution_time_ms = EXCLUDED.execution_time_ms,
                success = EXCLUDED.success,
                installed_at = NOW()
        """,
            (
                version,
                description,
                migration_file,
                checksum,
                execution_time_ms,
                success,
            ),
        )
    conn.commit()


# ============================================================================
# SCHEMA MANAGEMENT
# ============================================================================


def create_schemas(conn: psycopg2.extensions.connection):
    """Create all required schemas if they don't exist."""
    with conn.cursor() as cur:
        for schema, description in SCHEMAS.items():
            cur.execute(f"""
                CREATE SCHEMA IF NOT EXISTS {schema};
                COMMENT ON SCHEMA {schema} IS '{description}';
            """)

            # Grant permissions
            cur.execute(f"""
                GRANT USAGE ON SCHEMA {schema} TO postgres, authenticated, service_role;
                GRANT ALL ON SCHEMA {schema} TO postgres, service_role;
            """)

        print(f"✅ Created {len(SCHEMAS)} schemas")
    conn.commit()


# ============================================================================
# MIGRATION EXECUTION
# ============================================================================


def parse_migration_filename(filename: str) -> Tuple[str, str]:
    """
    Parse migration filename to extract version and description.

    Supports formats:
        001_ipai_medallion.sql -> (001, "IPAI Medallion")
        002_schema_separation.sql -> (002, "Schema Separation")
        20251105_github_installations.sql -> (20251105, "GitHub Installations")
    """
    # Remove .sql extension
    name = filename.replace(".sql", "")

    # Try different patterns
    patterns = [
        r"^(\d{3})_(.+)$",  # 001_name
        r"^(\d{8})_(.+)$",  # 20251105_name
        r"^(\d+)_(.+)$",  # any_digits_name
    ]

    for pattern in patterns:
        match = re.match(pattern, name)
        if match:
            version = match.group(1)
            description = match.group(2).replace("_", " ").title()
            return version, description

    # Fallback
    return name, name.replace("_", " ").title()


def get_pending_migrations(
    conn: psycopg2.extensions.connection,
) -> List[Tuple[str, Path]]:
    """
    Get list of pending migrations that haven't been applied yet.

    Returns:
        List of (version, file_path) tuples
    """
    applied = get_applied_versions(conn)
    pending = []

    # Find all migration files
    if not MIGRATIONS_DIR.exists():
        print(f"⚠️  Migrations directory not found: {MIGRATIONS_DIR}")
        return pending

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    for file_path in migration_files:
        version, description = parse_migration_filename(file_path.name)

        # Check if already applied
        if version in applied:
            # Verify checksum
            current_checksum = calculate_checksum(file_path)
            if current_checksum != applied[version]["checksum"]:
                print(f"⚠️  Migration {version} checksum mismatch!")
                print(f"   Applied: {applied[version]['checksum'][:8]}...")
                print(f"   Current: {current_checksum[:8]}...")
                print(f"   This migration was modified after being applied.")
        else:
            pending.append((version, file_path))

    return pending


def execute_migration(
    conn: psycopg2.extensions.connection,
    version: str,
    file_path: Path,
    dry_run: bool = False,
) -> bool:
    """
    Execute a single migration file.

    Returns:
        True if successful, False otherwise
    """
    version_display, description = parse_migration_filename(file_path.name)

    print(
        f"\n{'[DRY RUN] ' if dry_run else ''}Applying migration {version}: {description}"
    )
    print(f"  File: {file_path.name}")

    # Read migration SQL
    with open(file_path, "r") as f:
        sql = f.read()

    if dry_run:
        print(f"  SQL preview (first 200 chars):")
        print(f"  {sql[:200]}...")
        return True

    # Calculate checksum
    checksum = calculate_checksum(file_path)

    # Execute migration
    start_time = datetime.now()

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()

        execution_time = (datetime.now() - start_time).total_seconds() * 1000

        # Record success
        record_migration(
            conn,
            version,
            description,
            file_path.name,
            checksum,
            int(execution_time),
            success=True,
        )

        print(f"  ✅ Success ({int(execution_time)}ms)")
        return True

    except Exception as e:
        conn.rollback()

        execution_time = (datetime.now() - start_time).total_seconds() * 1000

        # Record failure
        record_migration(
            conn,
            version,
            f"FAILED: {description}",
            file_path.name,
            checksum,
            int(execution_time),
            success=False,
        )

        print(f"  ❌ Failed: {e}")
        return False


# ============================================================================
# SUPERSET INTEGRATION
# ============================================================================


def init_superset_metadata(conn: psycopg2.extensions.connection):
    """
    Initialize Superset metadata tables by running `superset db upgrade`.

    This is safe to run multiple times (idempotent).
    """
    print("\n🔧 Initializing Superset metadata...")

    # Check if superset command is available
    try:
        result = subprocess.run(
            ["superset", "db", "upgrade"], capture_output=True, text=True, timeout=120
        )

        if result.returncode == 0:
            print("✅ Superset metadata initialized")
            return True
        else:
            print(f"⚠️  Superset db upgrade failed: {result.stderr}")
            return False

    except FileNotFoundError:
        print("⚠️  Superset command not found. Skipping metadata initialization.")
        print("   Run this manually: superset db upgrade")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Superset db upgrade timed out")
        return False


def create_analytics_views(conn: psycopg2.extensions.connection):
    """
    Create analytics schema views and materialized views for Superset.

    These are the datasets that Superset dashboards will query.
    """
    print("\n📊 Creating analytics views for Superset...")

    if not SUPERSET_DATASETS_DIR.exists():
        print(f"⚠️  Datasets directory not found: {SUPERSET_DATASETS_DIR}")
        return False

    dataset_files = sorted(SUPERSET_DATASETS_DIR.glob("*.sql"))

    if not dataset_files:
        print("⚠️  No dataset files found")
        return False

    success_count = 0

    for dataset_file in dataset_files:
        try:
            print(f"  Creating {dataset_file.name}...")

            with open(dataset_file, "r") as f:
                sql = f.read()

            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()

            success_count += 1

        except Exception as e:
            print(f"  ⚠️  Failed to create {dataset_file.name}: {e}")
            conn.rollback()

    print(f"✅ Created {success_count}/{len(dataset_files)} analytics views")
    return success_count > 0


# ============================================================================
# SAMPLE DATA
# ============================================================================


def install_sample_data(conn: psycopg2.extensions.connection, schema: str = "all"):
    """
    Install sample data for testing and demo purposes.

    Args:
        schema: Which schema to populate ("all", "ops", "analytics", etc.)
    """
    print(f"\n🎲 Installing sample data (schema: {schema})...")

    # Create sample data directory if it doesn't exist
    SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    sample_data_definitions = {
        "ops": {
            "task_queue": [
                {
                    "kind": "DEPLOY_WEB",
                    "payload": {"branch": "main", "commit": "abc123"},
                    "status": "completed",
                    "pr_number": 101,
                },
                {
                    "kind": "ODOO_BUILD",
                    "payload": {"module": "sale_management", "version": "19.0"},
                    "status": "completed",
                    "pr_number": 102,
                },
                {
                    "kind": "DOCS_SYNC",
                    "payload": {"source": "notion", "pages_synced": 25},
                    "status": "processing",
                    "pr_number": None,
                },
            ],
            "workflow_runs": [
                {
                    "workflow_name": "deploy-production",
                    "status": "success",
                    "duration_seconds": 180,
                },
                {
                    "workflow_name": "deploy-production",
                    "status": "success",
                    "duration_seconds": 175,
                },
                {
                    "workflow_name": "test-suite",
                    "status": "success",
                    "duration_seconds": 420,
                },
                {
                    "workflow_name": "test-suite",
                    "status": "failure",
                    "duration_seconds": 380,
                },
            ],
        },
        "analytics": {
            # Analytics sample data would come from Odoo exports
            # For now, we'll create placeholder data
        },
    }

    schemas_to_populate = (
        [schema] if schema != "all" else sample_data_definitions.keys()
    )

    for schema_name in schemas_to_populate:
        if schema_name not in sample_data_definitions:
            continue

        print(f"\n  Populating {schema_name} schema...")

        for table_name, rows in sample_data_definitions[schema_name].items():
            if not rows:
                continue

            try:
                # Get column names from first row
                columns = list(rows[0].keys())
                placeholders = ", ".join(["%s"] * len(columns))
                columns_sql = ", ".join(columns)

                sql = f"""
                    INSERT INTO {schema_name}.{table_name} ({columns_sql})
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING
                """

                with conn.cursor() as cur:
                    for row in rows:
                        values = [row[col] for col in columns]
                        cur.execute(sql, values)

                conn.commit()
                print(f"    ✅ {table_name}: {len(rows)} rows")

            except Exception as e:
                print(f"    ⚠️  Failed to populate {table_name}: {e}")
                conn.rollback()

    print(f"\n✅ Sample data installation complete")


# ============================================================================
# APP INSTALLATION
# ============================================================================


def install_odoo_apps(app_list: List[str], odoo_url: str, api_key: str):
    """
    Install Odoo apps via RPC API.

    Args:
        app_list: List of Odoo module names to install
        odoo_url: Odoo instance URL (e.g., https://erp.insightpulseai.net)
        api_key: Odoo API key for authentication
    """
    print(f"\n📦 Installing Odoo apps...")

    try:
        pass
    except ImportError:
        print("⚠️  xmlrpc not available, skipping Odoo app installation")
        return False

    # TODO: Implement Odoo RPC app installation
    # This would use odoo.client or direct XML-RPC calls

    print("⚠️  Odoo app installation not yet implemented")
    print("   Apps to install:", ", ".join(app_list))

    return False


# ============================================================================
# STATUS & REPORTING
# ============================================================================


def print_migration_status(conn: psycopg2.extensions.connection):
    """Print current migration status."""
    print("\n" + "=" * 70)
    print("DATABASE MIGRATION STATUS")
    print("=" * 70)

    # Get applied versions
    applied = get_applied_versions(conn)

    if not applied:
        print("\n⚠️  No migrations have been applied yet")
        return

    print(f"\nApplied migrations: {len(applied)}")
    print(
        "\n{:<12} {:<30} {:<12} {:<10}".format(
            "VERSION", "DESCRIPTION", "DATE", "STATUS"
        )
    )
    print("-" * 70)

    for version, info in sorted(applied.items()):
        status = "✅" if info["success"] else "❌"
        date_str = info["installed_at"].strftime("%Y-%m-%d")
        description = info["description"][:28]

        print(f"{version:<12} {description:<30} {date_str:<12} {status:<10}")

    # Check for pending migrations
    pending = get_pending_migrations(conn)

    if pending:
        print(f"\n⚠️  Pending migrations: {len(pending)}")
        for version, file_path in pending:
            print(f"   - {version}: {file_path.name}")
    else:
        print(f"\n✅ All migrations are up to date")

    print("\n" + "=" * 70)


# ============================================================================
# MAIN CLI
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="InsightPulse Database Upgrader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Show current migration status
    python3 scripts/db_upgrader.py status

    # Run all pending migrations
    python3 scripts/db_upgrader.py upgrade

    # Dry run (show what would be executed)
    python3 scripts/db_upgrader.py upgrade --dry-run

    # Initialize Superset metadata and analytics views
    python3 scripts/db_upgrader.py init-superset

    # Install sample data
    python3 scripts/db_upgrader.py install-sample-data --schema all

    # Full setup (migrations + superset + sample data)
    python3 scripts/db_upgrader.py full-setup
        """,
    )

    parser.add_argument(
        "command",
        choices=[
            "status",
            "upgrade",
            "init-superset",
            "install-sample-data",
            "full-setup",
            "rollback",
        ],
        help="Command to execute",
    )

    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        default="development",
        help="Environment to target",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be executed without making changes",
    )

    parser.add_argument(
        "--schema",
        default="all",
        help="Schema to operate on (for sample data installation)",
    )

    parser.add_argument("--to-version", help="Target version for rollback")

    args = parser.parse_args()

    # Get database connection
    print(f"🔌 Connecting to {args.env} database...")
    conn = get_db_connection(args.env)

    try:
        # Initialize version tracking
        init_version_table(conn)

        # Execute command
        if args.command == "status":
            print_migration_status(conn)

        elif args.command == "upgrade":
            create_schemas(conn)
            pending = get_pending_migrations(conn)

            if not pending:
                print("\n✅ No pending migrations")
                return 0

            print(f"\nFound {len(pending)} pending migration(s)")

            for version, file_path in pending:
                success = execute_migration(conn, version, file_path, args.dry_run)
                if not success and not args.dry_run:
                    print(f"\n❌ Migration failed, stopping")
                    return 1

            print(f"\n✅ All migrations completed successfully")

        elif args.command == "init-superset":
            create_schemas(conn)
            init_superset_metadata(conn)
            create_analytics_views(conn)

        elif args.command == "install-sample-data":
            install_sample_data(conn, args.schema)

        elif args.command == "full-setup":
            print("\n🚀 Running full database setup...")

            # 1. Create schemas
            create_schemas(conn)

            # 2. Run migrations
            pending = get_pending_migrations(conn)
            if pending:
                print(f"\n📋 Applying {len(pending)} migration(s)...")
                for version, file_path in pending:
                    execute_migration(conn, version, file_path, args.dry_run)

            # 3. Initialize Superset
            if not args.dry_run:
                init_superset_metadata(conn)
                create_analytics_views(conn)

            # 4. Install sample data
            if not args.dry_run:
                install_sample_data(conn, "all")

            print("\n✅ Full setup complete!")
            print_migration_status(conn)

        elif args.command == "rollback":
            print("\n⚠️  Rollback not yet implemented")
            print("   Database rollbacks require careful planning.")
            print("   For now, restore from backup or manually revert changes.")
            return 1

        return 0

    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
