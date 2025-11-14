import pytest

pytestmark = pytest.mark.expense

def test_policy_rule_evaluation():
    """Policies are evaluated correctly per employee/agency."""

def test_expense_amount_limits():
    """Hard and soft limits enforced on expense amounts."""

def test_category_restrictions():
    """Disallowed categories are rejected."""

def test_approval_thresholds():
    """Escalation thresholds behave as configured."""
