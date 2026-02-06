#!/usr/bin/env python3
"""
BIR Schema Validation Script
Validates that migration 004 was applied successfully
"""

import os
import sys

import psycopg2

# Supabase connection URL from environment
POSTGRES_URL = os.getenv("POSTGRES_URL")

if not POSTGRES_URL:
    print("❌ ERROR: POSTGRES_URL environment variable not set")
    print("   Set it using: export POSTGRES_URL='your_connection_string'")
    sys.exit(1)


def check_table_exists(cursor, table_name: str) -> bool:
    """Check if table exists"""
    cursor.execute(f"SELECT to_regclass('{table_name}');")
    result = cursor.fetchone()
    return result[0] is not None


def check_rls_enabled(cursor, table_name: str) -> bool:
    """Check if Row Level Security is enabled"""
    cursor.execute(f"""
        SELECT relrowsecurity
        FROM pg_class
        WHERE oid = '{table_name}'::regclass;
    """)
    result = cursor.fetchone()
    return result[0] if result else False


def check_index_exists(cursor, index_name: str) -> bool:
    """Check if index exists"""
    cursor.execute(f"""
        SELECT indexname
        FROM pg_indexes
        WHERE indexname = '{index_name}';
    """)
    result = cursor.fetchone()
    return result is not None


def check_policy_exists(cursor, table_name: str, policy_name: str) -> bool:
    """Check if RLS policy exists"""
    cursor.execute(f"""
        SELECT polname
        FROM pg_policy
        WHERE polrelid = '{table_name}'::regclass
        AND polname = '{policy_name}';
    """)
    result = cursor.fetchone()
    return result is not None


def validate_schema():
    """Main validation function"""
    print("🔍 Validating BIR schema (Migration 004)...\n")

    try:
        # Connect to Supabase PostgreSQL
        conn = psycopg2.connect(POSTGRES_URL)
        cursor = conn.cursor()

        errors = []
        warnings = []

        # 1. Check tables exist
        print("📋 Checking tables...")
        tables = [
            "scout.transactions",
            "scout.vat_transactions",
            "scout.bir_batch_generation",
        ]

        for table in tables:
            if check_table_exists(cursor, table):
                print(f"   ✅ {table} exists")
            else:
                errors.append(f"Table {table} does not exist")
                print(f"   ❌ {table} MISSING")

        # 2. Check RLS enabled
        print("\n🔒 Checking Row Level Security...")
        for table in tables:
            if check_rls_enabled(cursor, table):
                print(f"   ✅ RLS enabled on {table}")
            else:
                errors.append(f"RLS not enabled on {table}")
                print(f"   ❌ RLS DISABLED on {table}")

        # 3. Check key indexes exist
        print("\n📊 Checking indexes...")
        indexes = [
            "idx_transactions_company_date",
            "idx_transactions_type",
            "idx_vat_transactions_company_period",
            "idx_bir_batch_company",
        ]

        for index in indexes:
            if check_index_exists(cursor, index):
                print(f"   ✅ {index}")
            else:
                warnings.append(f"Index {index} not found (may affect performance)")
                print(f"   ⚠️  {index} MISSING")

        # 4. Check RLS policies
        print("\n🛡️  Checking RLS policies...")
        policies = [
            ("scout.transactions", "transaction_tenant_policy"),
            ("scout.transactions", "transaction_service_role_policy"),
            ("scout.vat_transactions", "vat_transaction_tenant_policy"),
            ("scout.vat_transactions", "vat_transaction_service_role_policy"),
            ("scout.bir_batch_generation", "bir_batch_tenant_policy"),
            ("scout.bir_batch_generation", "bir_batch_service_role_policy"),
        ]

        for table, policy in policies:
            if check_policy_exists(cursor, table, policy):
                print(f"   ✅ {policy} on {table}")
            else:
                errors.append(f"Policy {policy} not found on {table}")
                print(f"   ❌ {policy} MISSING on {table}")

        # 5. Check trigger function exists
        print("\n⚙️  Checking trigger function...")
        cursor.execute("""
            SELECT proname
            FROM pg_proc
            WHERE proname = 'update_updated_at_column'
            AND pronamespace = 'scout'::regnamespace;
        """)
        if cursor.fetchone():
            print("   ✅ scout.update_updated_at_column() exists")
        else:
            warnings.append("Trigger function update_updated_at_column() not found")
            print("   ⚠️  update_updated_at_column() MISSING")

        # Summary
        print("\n" + "=" * 60)
        if errors:
            print(f"\n❌ VALIDATION FAILED: {len(errors)} error(s)")
            for error in errors:
                print(f"   • {error}")
            if warnings:
                print(f"\n⚠️  {len(warnings)} warning(s):")
                for warning in warnings:
                    print(f"   • {warning}")
            cursor.close()
            conn.close()
            sys.exit(1)
        else:
            print("\n✅ VALIDATION PASSED: All BIR schema checks successful")
            if warnings:
                print(f"\n⚠️  {len(warnings)} warning(s) (non-critical):")
                for warning in warnings:
                    print(f"   • {warning}")
            cursor.close()
            conn.close()
            sys.exit(0)

    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    validate_schema()
