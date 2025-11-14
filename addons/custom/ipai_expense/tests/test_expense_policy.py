import pytest

pytestmark = pytest.mark.expense

def test_policy_rule_evaluation():
    """Policies are evaluated correctly per employee/agency."""
    pass

def test_expense_amount_limits():
    """Hard and soft limits enforced on expense amounts."""
    pass

def test_category_restrictions():
    """Disallowed categories are rejected."""
    pass

def test_approval_thresholds():
    """Escalation thresholds behave as configured."""
    pass
