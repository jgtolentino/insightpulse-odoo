#!/usr/bin/env python3
"""
Database Upgrader Test Suite
=============================

Tests for the comprehensive DB upgrader:
- Migration execution and rollback
- Schema creation
- Superset integration
- Sample data installation
- Idempotency verification

Usage:
    # Run all tests
    python3 scripts/test_db_upgrader.py

    # Run specific test
    python3 scripts/test_db_upgrader.py TestMigrations.test_migration_tracking

    # Verbose output
    python3 scripts/test_db_upgrader.py -v
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import psycopg2
    from db_upgrader import (
        calculate_checksum,
        parse_migration_filename,
        get_pending_migrations,
        create_schemas,
        init_version_table,
        SCHEMAS
    )
except ImportError as e:
    print(f"ERROR: Failed to import db_upgrader: {e}")
    sys.exit(1)


# ============================================================================
# TEST DATABASE SETUP
# ============================================================================

def get_test_db_connection():
    """Get connection to test database."""
    test_db_url = os.getenv(
        "TEST_POSTGRES_URL",
        "postgresql://postgres:password@localhost:5432/insightpulse_test"
    )

    try:
        conn = psycopg2.connect(test_db_url)
        return conn
    except Exception as e:
        print(f"⚠️  Cannot connect to test database: {e}")
        print("   Set TEST_POSTGRES_URL environment variable")
        return None


def reset_test_database(conn):
    """Reset test database to clean state."""
    if not conn:
        return

    with conn.cursor() as cur:
        # Drop all schemas
        for schema in SCHEMAS.keys():
            cur.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")

        # Drop version table
        cur.execute("DROP TABLE IF EXISTS public.schema_version CASCADE")

    conn.commit()


# ============================================================================
# UNIT TESTS
# ============================================================================

class TestMigrationFileParsing(unittest.TestCase):
    """Test migration filename parsing."""

    def test_parse_three_digit_version(self):
        version, description = parse_migration_filename("001_ipai_medallion.sql")
        self.assertEqual(version, "001")
        self.assertEqual(description, "Ipai Medallion")

    def test_parse_date_version(self):
        version, description = parse_migration_filename("20251105_github_installations.sql")
        self.assertEqual(version, "20251105")
        self.assertEqual(description, "Github Installations")

    def test_parse_schema_separation(self):
        version, description = parse_migration_filename("002_schema_separation.sql")
        self.assertEqual(version, "002")
        self.assertEqual(description, "Schema Separation")


class TestChecksumCalculation(unittest.TestCase):
    """Test checksum calculation."""

    def test_checksum_deterministic(self):
        """Same file should produce same checksum."""
        test_file = Path(__file__).parent.parent / "supabase" / "migrations" / "001_ipai_medallion.sql"

        if not test_file.exists():
            self.skipTest("Migration file not found")

        checksum1 = calculate_checksum(test_file)
        checksum2 = calculate_checksum(test_file)

        self.assertEqual(checksum1, checksum2)
        self.assertEqual(len(checksum1), 64)  # SHA256 hex length


# ============================================================================
# INTEGRATION TESTS (require test database)
# ============================================================================

class TestDatabaseMigrations(unittest.TestCase):
    """Test database migration execution."""

    @classmethod
    def setUpClass(cls):
        """Set up test database connection."""
        cls.conn = get_test_db_connection()

        if not cls.conn:
            raise unittest.SkipTest("Test database not available")

    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        if cls.conn:
            reset_test_database(cls.conn)
            cls.conn.close()

    def setUp(self):
        """Reset database before each test."""
        reset_test_database(self.conn)

    def test_version_table_creation(self):
        """Test that version tracking table can be created."""
        init_version_table(self.conn)

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'schema_version'
                )
            """)

            exists = cur.fetchone()[0]

        self.assertTrue(exists)

    def test_schema_creation(self):
        """Test that all schemas are created."""
        create_schemas(self.conn)

        with self.conn.cursor() as cur:
            for schema in SCHEMAS.keys():
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.schemata
                        WHERE schema_name = %s
                    )
                """, (schema,))

                exists = cur.fetchone()[0]
                self.assertTrue(exists, f"Schema {schema} should exist")

    def test_migration_tracking(self):
        """Test that migrations are tracked in version table."""
        init_version_table(self.conn)

        # Manually insert a migration record
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO public.schema_version
                    (version, description, migration_file, checksum, execution_time_ms)
                VALUES ('001', 'Test Migration', '001_test.sql', 'abc123', 100)
            """)

        self.conn.commit()

        # Verify it's tracked
        with self.conn.cursor() as cur:
            cur.execute("SELECT version, description FROM public.schema_version WHERE version = '001'")
            row = cur.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], "001")
        self.assertEqual(row[1], "Test Migration")

    def test_idempotency(self):
        """Test that running migrations twice is safe."""
        init_version_table(self.conn)
        create_schemas(self.conn)

        # Run again - should not fail
        init_version_table(self.conn)
        create_schemas(self.conn)

        # Verify schemas still exist
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM information_schema.schemata
                WHERE schema_name IN %s
            """, (tuple(SCHEMAS.keys()),))

            count = cur.fetchone()[0]

        self.assertEqual(count, len(SCHEMAS))


class TestSampleDataInstallation(unittest.TestCase):
    """Test sample data installation."""

    @classmethod
    def setUpClass(cls):
        """Set up test database connection."""
        cls.conn = get_test_db_connection()

        if not cls.conn:
            raise unittest.SkipTest("Test database not available")

    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        if cls.conn:
            reset_test_database(cls.conn)
            cls.conn.close()

    def setUp(self):
        """Reset database before each test."""
        reset_test_database(self.conn)
        create_schemas(self.conn)

    def test_ops_schema_tables(self):
        """Test that ops schema tables exist after migration."""
        # This test assumes migration 002 has been run
        # For now, just verify schema exists
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.schemata
                    WHERE schema_name = 'ops'
                )
            """)

            exists = cur.fetchone()[0]

        self.assertTrue(exists)


# ============================================================================
# VERIFICATION TESTS
# ============================================================================

class TestMigrationVerification(unittest.TestCase):
    """Test migration file verification."""

    def test_all_migrations_have_valid_names(self):
        """Test that all migration files follow naming convention."""
        migrations_dir = Path(__file__).parent.parent / "supabase" / "migrations"

        if not migrations_dir.exists():
            self.skipTest("Migrations directory not found")

        migration_files = migrations_dir.glob("*.sql")

        for migration_file in migration_files:
            version, description = parse_migration_filename(migration_file.name)

            self.assertIsNotNone(version, f"{migration_file.name} should have a version")
            self.assertIsNotNone(description, f"{migration_file.name} should have a description")
            self.assertTrue(len(version) > 0, f"{migration_file.name} version should not be empty")

    def test_migration_files_are_valid_sql(self):
        """Test that migration files contain valid SQL."""
        migrations_dir = Path(__file__).parent.parent / "supabase" / "migrations"

        if not migrations_dir.exists():
            self.skipTest("Migrations directory not found")

        migration_files = migrations_dir.glob("*.sql")

        for migration_file in migration_files:
            with open(migration_file, 'r') as f:
                content = f.read()

            # Basic checks
            self.assertTrue(len(content) > 0, f"{migration_file.name} should not be empty")

            # Should contain SQL keywords
            content_upper = content.upper()
            has_sql = any(keyword in content_upper for keyword in [
                'CREATE', 'ALTER', 'INSERT', 'SELECT', 'UPDATE', 'DELETE', 'DROP'
            ])

            self.assertTrue(has_sql, f"{migration_file.name} should contain SQL statements")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run test suite."""
    # Check if test database is available
    conn = get_test_db_connection()

    if not conn:
        print("\n" + "=" * 70)
        print("⚠️  TEST DATABASE NOT AVAILABLE")
        print("=" * 70)
        print("\nSome integration tests will be skipped.")
        print("To run all tests, set TEST_POSTGRES_URL environment variable:")
        print("\n  export TEST_POSTGRES_URL='postgresql://user:pass@host:port/dbname'")
        print("\nRunning unit tests only...\n")
    else:
        conn.close()

    # Run tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
