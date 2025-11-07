#!/usr/bin/env python3
"""
Test database functions for error normalization and fingerprinting
"""
import os
import pytest
import psycopg
from psycopg.rows import dict_row


def get_db_connection():
    """Get database connection using environment variables"""
    required = ['SUPABASE_DB_HOST', 'SUPABASE_DB_USER', 'SUPABASE_DB_PASSWORD',
                'SUPABASE_DB_NAME', 'SUPABASE_DB_PORT']

    missing = [k for k in required if not os.getenv(k)]
    if missing:
        pytest.skip(f"Missing environment variables: {', '.join(missing)}")

    return psycopg.connect(
        host=os.getenv('SUPABASE_DB_HOST'),
        dbname=os.getenv('SUPABASE_DB_NAME'),
        user=os.getenv('SUPABASE_DB_USER'),
        password=os.getenv('SUPABASE_DB_PASSWORD'),
        port=os.getenv('SUPABASE_DB_PORT', '5432'),
        row_factory=dict_row
    )


def test_normalize_error_message():
    """Test error message normalization function"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Test UUID normalization
            cur.execute("select public.normalize_error_message('KeyError: 123e4567-e89b-12d3-a456-426614174000') as n")
            result = cur.fetchone()
            assert '<uuid>' in result['n'].lower()

            # Test integer normalization
            cur.execute("select public.normalize_error_message('Error with id 123456') as n")
            result = cur.fetchone()
            assert '<int>' in result['n'].lower()

            # Test timestamp normalization
            cur.execute("select public.normalize_error_message('Failed at 2025-11-01T10:00:00Z') as n")
            result = cur.fetchone()
            assert '<ts>' in result['n'].lower()

            # Test epoch timestamp normalization
            cur.execute("select public.normalize_error_message('Timestamp: 1699999999999') as n")
            result = cur.fetchone()
            assert '<epoch>' in result['n'].lower()


def test_error_fingerprint():
    """Test error fingerprint generation"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Test fingerprint generation
            cur.execute("""
                select public.error_fingerprint('KeyError', 'controller.x', 'KeyError: missing field') as fp1,
                       public.error_fingerprint('KeyError', 'controller.x', 'KeyError: missing field') as fp2,
                       public.error_fingerprint('ValueError', 'controller.x', 'ValueError: invalid') as fp3
            """)
            result = cur.fetchone()

            # Same inputs should produce same fingerprint
            assert result['fp1'] == result['fp2']

            # Different inputs should produce different fingerprints
            assert result['fp1'] != result['fp3']

            # Fingerprint should be a valid UUID
            assert str(result['fp1']).count('-') == 4


def test_error_fingerprint_stability():
    """Test that fingerprints are stable across variable parts"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # These errors differ only in volatile parts (UUIDs, numbers)
            # They should produce the same fingerprint after normalization
            cur.execute("""
                select public.error_fingerprint(
                    'KeyError',
                    'odoo.addons.sale',
                    'KeyError: partner_id 123456'
                ) as fp1,
                public.error_fingerprint(
                    'KeyError',
                    'odoo.addons.sale',
                    'KeyError: partner_id 789012'
                ) as fp2
            """)
            result = cur.fetchone()

            # Should produce same fingerprint (numbers normalized)
            assert result['fp1'] == result['fp2']


def test_error_signatures_view_exists():
    """Test that error_signatures materialized view exists"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select exists(
                    select 1 from pg_matviews
                    where schemaname = 'public'
                    and matviewname = 'error_signatures'
                ) as exists
            """)
            result = cur.fetchone()
            assert result['exists'] is True


def test_error_candidates_view_exists():
    """Test that error_candidates view exists"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select exists(
                    select 1 from pg_views
                    where schemaname = 'public'
                    and viewname = 'error_candidates'
                ) as exists
            """)
            result = cur.fetchone()
            assert result['exists'] is True


def test_normalization_examples():
    """Test various normalization examples"""
    test_cases = [
        ("KeyError: 'field_123456'", "<int>"),
        ("UUID: 550e8400-e29b-41d4-a716-446655440000", "<uuid>"),
        ("Timestamp: 2025-01-15T14:30:00", "<ts>"),
        ("Error at epoch 1642262400000", "<epoch>"),
    ]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for original, expected_token in test_cases:
                cur.execute("select public.normalize_error_message(%s) as n", (original,))
                result = cur.fetchone()
                assert expected_token in result['n'], \
                    f"Expected '{expected_token}' in normalized version of '{original}', got: {result['n']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
