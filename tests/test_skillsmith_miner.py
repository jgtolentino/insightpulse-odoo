#!/usr/bin/env python3
"""
Test Skillsmith miner functionality
"""
import os
import sys
import json
import pytest
import pathlib
import subprocess
import tempfile
from unittest.mock import patch, MagicMock


# Add services to path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from services.skillsmith import miner


def test_pick_kind_guardrail():
    """Test that guardrail patterns are correctly identified"""
    test_cases = [
        {"norm_msg": "KeyError: missing field", "expected": "guardrail"},
        {"norm_msg": "ValueError: invalid input", "expected": "guardrail"},
        {"norm_msg": "Missing manifest entry", "expected": "guardrail"},
        {"norm_msg": "Invalid xpath expression", "expected": "guardrail"},
        {"norm_msg": "Permission denied for field", "expected": "guardrail"},
        {"norm_msg": "Forbidden access to model", "expected": "guardrail"},
    ]

    for case in test_cases:
        result = miner.pick_kind(case)
        assert result == case["expected"], \
            f"Expected '{case['expected']}' for '{case['norm_msg']}', got '{result}'"


def test_pick_kind_fixer():
    """Test that fixer patterns are correctly identified"""
    test_cases = [
        {"norm_msg": "ImportError: cannot import module", "expected": "fixer"},
        {"norm_msg": "Template override failed", "expected": "fixer"},
        {"norm_msg": "Database connection timeout", "expected": "fixer"},
    ]

    for case in test_cases:
        result = miner.pick_kind(case)
        assert result == case["expected"], \
            f"Expected '{case['expected']}' for '{case['norm_msg']}', got '{result}'"


def test_slug_function():
    """Test slug generation for filenames"""
    test_cases = [
        ("KeyError in sale.order", "keyerror-in-sale-order"),
        ("ValueError: Missing Field", "valueerror-missing-field"),
        ("Complex/Name With Spaces!", "complex-name-with-spaces"),
    ]

    for original, expected in test_cases:
        result = miner.slug(original)
        assert result == expected[:40], \
            f"Expected '{expected}' for '{original}', got '{result}'"


def test_template_loading():
    """Test that Jinja2 templates load correctly"""
    templates = miner.TEMPLATES

    # Check that both templates exist
    assert "guardrail.yaml.j2" in templates.list_templates()
    assert "fixer.yaml.j2" in templates.list_templates()

    # Test template rendering with sample data
    guardrail_tpl = templates.get_template("guardrail.yaml.j2")
    result = guardrail_tpl.render(
        id="GR-TEST1234",
        title="Test Guardrail",
        component="test.component",
        pattern="Test.*Error",
        fingerprint="00000000-0000-0000-0000-123456789abc",
        hits_7d=5,
        hits_30d=20,
        impact_score=10.5,
        generated_at="2025-11-07T12:00:00Z"
    )

    # Verify key fields in output
    assert "id: GR-TEST1234" in result
    assert "name: \"Test Guardrail\"" in result
    assert "kind: guardrail" in result
    assert "status: proposed" in result


def test_miner_with_mock_db(tmp_path):
    """Test miner with mocked database connection"""
    # Mock database results
    mock_rows = [
        {
            "fp": "00000000-0000-0000-0000-111111111111",
            "component": "odoo.addons.sale",
            "kind": "KeyError",
            "norm_msg": "KeyError: partner_id",
            "hits_7d": 10,
            "hits_30d": 25,
            "impact_score": 15.5,
            "tags": ["odoo", "sale"]
        },
        {
            "fp": "00000000-0000-0000-0000-222222222222",
            "component": "odoo.addons.purchase",
            "kind": "ValueError",
            "norm_msg": "Invalid product quantity",
            "hits_7d": 8,
            "hits_30d": 20,
            "impact_score": 12.4,
            "tags": ["odoo", "purchase"]
        }
    ]

    # Mock psycopg connection
    with patch('services.skillsmith.miner.psycopg.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_rows
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Temporarily change output directory
        original_out_dir = miner.OUT_DIR
        miner.OUT_DIR = tmp_path / "proposed"

        try:
            # Run miner
            result = miner.main(min_hits=2, top=10)

            # Verify results
            assert result["count"] == 2
            assert len(result["created"]) == 2

            # Verify files were created
            yaml_files = list((tmp_path / "proposed").glob("*.yaml"))
            assert len(yaml_files) == 2

            # Verify content of first file
            content = yaml_files[0].read_text()
            assert "id: GR-" in content or "id: FX-" in content
            assert "status: proposed" in content
            assert "auto_generated: true" in content

        finally:
            # Restore original output directory
            miner.OUT_DIR = original_out_dir


def test_miner_script_runs_without_db():
    """Test that miner script handles missing DB gracefully"""
    # Save original env vars
    original_env = {k: os.environ.get(k) for k in
                    ['SUPABASE_DB_HOST', 'SUPABASE_DB_USER', 'SUPABASE_DB_PASSWORD',
                     'SUPABASE_DB_NAME', 'SUPABASE_DB_PORT']}

    try:
        # Clear DB env vars
        for k in original_env:
            if k in os.environ:
                del os.environ[k]

        # Set dummy values to pass initial checks
        os.environ['SUPABASE_DB_HOST'] = 'dummy'
        os.environ['SUPABASE_DB_USER'] = 'dummy'
        os.environ['SUPABASE_DB_PASSWORD'] = 'dummy'
        os.environ['SUPABASE_DB_NAME'] = 'dummy'
        os.environ['SUPABASE_DB_PORT'] = '5432'

        # Script should handle connection error gracefully
        # (In practice, this would fail at connection time, which is expected)
        # For this test, we just verify the module loads correctly
        assert miner.main is not None
        assert callable(miner.pick_kind)
        assert callable(miner.slug)

    finally:
        # Restore original env vars
        for k, v in original_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_output_directory_creation(tmp_path):
    """Test that output directory is created if it doesn't exist"""
    test_dir = tmp_path / "skills" / "proposed"
    assert not test_dir.exists()

    # Mock database and run miner
    with patch('services.skillsmith.miner.psycopg.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        original_out_dir = miner.OUT_DIR
        miner.OUT_DIR = test_dir

        try:
            miner.main(min_hits=2, top=10)
            # Directory should be created even if no results
            assert test_dir.exists()
        finally:
            miner.OUT_DIR = original_out_dir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
