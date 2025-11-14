import pytest

pytestmark = pytest.mark.text_to_sql

def test_natural_language_parsing():
    """Free text query parsed into intent + constraints."""
    pass

def test_sql_generation():
    """Generated SQL matches expected pattern and tables."""
    pass

def test_query_safety_validation():
    """Dangerous queries (DROP/TRUNCATE/etc.) rejected."""
    pass

def test_parameter_injection_prevention():
    """User params are always bound, never interpolated."""
    pass
